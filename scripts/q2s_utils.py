import pandas as pd

# ---------------------------------------------------------------------------
# DATA LOADING FUNCTIONS
# ---------------------------------------------------------------------------

def load_plans(file_path):
    """
    Load plans from CSV file.
    Returns a dictionary mapping plan IDs to lists of goals.
    """
    plans = {}

    try:
        df = pd.read_csv(file_path)
        # First column is plan ID, rest are goals
        for _, row in df.iterrows():
            plan_id = row['PLANS']
            goals = []
            for col in df.columns[1:]:  # Skip the first column (PLANS)
                if row[col] == 1:
                    goals.append(col)
            plans[plan_id] = {"name": plan_id, "goals": goals}

        print(f"Loaded {len(plans)} plans from {file_path}")
        return plans
    except Exception as e:
        print(f"Error loading plans: {e}")
        return {}

def load_contributions(file_path):
    """
    Load goal contributions to domain variables from CSV file.
    Returns a dictionary mapping domain variables to dictionaries of goal contributions.
    """
    contributions = {}

    try:
        df = pd.read_csv(file_path)
        # First column is domain variable, rest are goals
        for _, row in df.iterrows():
            domain_var = row['DomainVariable']
            goal_contributions = {}
            for col in df.columns[1:]:  # Skip the first column (DomainVariable)
                if pd.notna(row[col]):  # Check if the value is not NaN
                    goal_contributions[col] = float(row[col])
            contributions[domain_var] = goal_contributions

        print(f"Loaded contributions for {len(contributions)} domain variables from {file_path}")
        return contributions
    except Exception as e:
        print(f"Error loading contributions: {e}")
        return {}

def load_quality_goals(file_path):
    """
    Load quality goals from CSV file.
    Returns a dictionary mapping quality goal IDs to their domain variables and constraints.
    """
    quality_goals = {}

    try:
        df = pd.read_csv(file_path)
        # Each row defines a quality goal
        for _, row in df.iterrows():
            qg_id = row['Quality Goals']
            domain_var = row['Domain Variable']
            constraint = float(row['QG constraints'])
            quality_goals[qg_id] = {
                "name": qg_id,
                "domain_variable": domain_var,
                "max_value": constraint,
                "type": "max"  # Assuming all constraints are upper bounds
            }

        print(f"Loaded {len(quality_goals)} quality goals from {file_path}")
        return quality_goals
    except Exception as e:
        print(f"Error loading quality goals: {e}")
        return {}

# ---------------------------------------------------------------------------
# PLAN IMPACT CALCULATION
# ---------------------------------------------------------------------------

def calculate_plan_impact(plan, contributions):
    """
    Calculate the impact of a plan on domain variables.
    Returns a dictionary mapping domain variables to their values.
    """
    impacts = {}
    goals = plan["goals"]

    for domain_var, goal_contributions in contributions.items():
        total = 0
        for goal, contribution in goal_contributions.items():
            if goal in goals:
                total += contribution
        impacts[domain_var] = total

    return impacts

def calculate_all_plan_impacts(plans, contributions):
    """
    Calculate impacts for all plans.
    Returns a dictionary mapping plan IDs to their impact dictionaries.
    """
    all_impacts = {}

    for plan_id, plan in plans.items():
        impacts = calculate_plan_impact(plan, contributions)
        all_impacts[plan_id] = impacts

    return all_impacts

# ---------------------------------------------------------------------------
# QUALITY GOAL CALCULATION AND PLAN FILTERING
# ---------------------------------------------------------------------------

def calculate_quality_goals_for_scenario(scenario, base_quality_goals, event_size_modifiers=None):
    """
    Adjust quality goals based on scenario parameters.
    Returns a dictionary of quality goals with their constraint values.

    Args:
        scenario: Dictionary with scenario parameters
        base_quality_goals: Base quality goals to adjust
        event_size_modifiers: Optional dictionary of modifiers for different event sizes
    """
    event_size = scenario["event_size"]
    organizers = scenario["organizers"]

    # Create a copy of the base quality goals
    quality_goals = {}
    for qg_id, goal in base_quality_goals.items():
        quality_goals[qg_id] = goal.copy()

    # Default event size modifiers if none provided
    if event_size_modifiers is None:
        event_size_modifiers = {
            "small": {"TotalCost": 1.0, "TimeSpent": 1.0, "TotalEffort": 1.0},
            "medium": {"TotalCost": 2.0, "TimeSpent": 1.5, "TotalEffort": 2.0},
            "big": {"TotalCost": 3.0, "TimeSpent": 2.0, "TotalEffort": 3.0}
        }

    size_mod = event_size_modifiers[event_size]

    # Adjust constraints based on event size and organizers
    for qg_id, goal in quality_goals.items():
        domain_var = goal["domain_variable"]
        if domain_var in size_mod:
            goal["max_value"] *= size_mod[domain_var]

            # Adjust time-related constraints based on number of organizers
            if "Time" in domain_var:
                goal["max_value"] /= organizers

    return quality_goals

def check_plan_validity(plan_impacts, quality_goals):
    """Check if a plan satisfies all quality constraints."""
    for qg_id, goal in quality_goals.items():
        domain_var = goal["domain_variable"]
        if domain_var in plan_impacts:
            impact_value = plan_impacts[domain_var]
            if goal["type"] == "max" and impact_value > goal["max_value"]:
                return False
    return True

def filter_valid_plans(scenario, all_plan_impacts, base_quality_goals, event_size_modifiers=None):
    """
    Filter plans that satisfy all quality goals for the given scenario.
    Returns a dictionary of valid plans with their impacts.
    """
    quality_goals = calculate_quality_goals_for_scenario(scenario, base_quality_goals, event_size_modifiers)

    valid_plans = {}
    for plan_id, impacts in all_plan_impacts.items():
        # Check if plan satisfies all constraints
        if check_plan_validity(impacts, quality_goals):
            valid_plans[plan_id] = {"name": plan_id, "impact": impacts}

    return valid_plans, quality_goals

# ---------------------------------------------------------------------------
# Q2S MATRIX CALCULATION
# ---------------------------------------------------------------------------

def calculate_q2s_matrix(valid_plans, quality_goals):
    """
    Calculate the Q2S matrix for valid plans and quality goals.
    Returns a dictionary mapping plan_ids to lists of distances.
    """
    q2s_matrix = {}

    for plan_id, plan in valid_plans.items():
        plan_distances = {}
        for qg_id, goal in quality_goals.items():
            domain_var = goal["domain_variable"]
            if domain_var in plan["impact"]:
                impact_value = plan["impact"][domain_var]

                if goal["type"] == "max":
                    # For max constraints, higher distance is better
                    distance = (goal["max_value"] - impact_value) / goal["max_value"]
                else:
                    # For min constraints, would be (impact_value - goal["min_value"]) / goal["min_value"]
                    # But we don't have min constraints in this example
                    distance = 0

                plan_distances[qg_id] = distance

        if plan_distances:  # Only add to matrix if we have distances
            q2s_matrix[plan_id] = plan_distances

    return q2s_matrix

# ---------------------------------------------------------------------------
# PLAN SELECTION STRATEGIES
# ---------------------------------------------------------------------------

def q2s_selection_strategy(q2s_matrix, alpha=0.5):
    """
    Select plan using Q2S strategy: alpha*AvgSat + (1-alpha)*MinSat
    """
    if not q2s_matrix:
        return None, 0

    plan_scores = {}
    for plan_id, distances in q2s_matrix.items():
        distance_values = list(distances.values())
        if not distance_values:  # Skip if no distance values
            continue

        avg_sat = sum(distance_values) / len(distance_values)
        min_sat = min(distance_values)

        # Calculate score using Hurwicz criterion
        score = alpha * avg_sat + (1 - alpha) * min_sat
        plan_scores[plan_id] = score

    # Return the plan with the highest score
    if not plan_scores:  # Check if plan_scores is empty
        return None, 0

    best_plan_id = max(plan_scores, key=plan_scores.get)
    return best_plan_id, plan_scores[best_plan_id]
