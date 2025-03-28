import pandas as pd
import json
import os


# ---------------------------------------------------------------------------
# JSON CONFIG LOADING
# ---------------------------------------------------------------------------

def load_json_config(config_file):
    """
    Load configuration from JSON file.
    Returns the entire configuration dictionary.
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"Loaded configuration from {config_file}")
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {}

# ---------------------------------------------------------------------------
# DATA LOADING FUNCTIONS
# ---------------------------------------------------------------------------
def get_file_paths(config=None, config_file=None):
    """
    Get file paths for data sources from config.

    Args:
        config: Configuration dictionary (optional)
        config_file: Path to the configuration file (optional)
    """
    if config is None and config_file is not None:
        config = load_json_config(config_file)

    if config is None:
        return None

    return config.get("file_paths")

def get_quality_goals_mapping(config=None, config_file=None):
    """
    Get quality goals mapping from config.

    Args:
        config: Configuration dictionary (optional)
        config_file: Path to the configuration file (optional)
    """
    if config is None and config_file is not None:
        config = load_json_config(config_file)

    if config is None:
        return None

    return config.get("quality_goals")

def get_event_size_modifiers(config=None, config_file=None):
    """
    Get event size modifiers from config.

    Args:
        config: Configuration dictionary (optional)
        config_file: Path to the configuration file (optional)
    """
    if config is None and config_file is not None:
        config = load_json_config(config_file)

    if config is None:
        return None

    return config.get("event_size_modifiers")

def get_scenario_generator_options(config=None, config_file=None):
    """
    Get scenario generator options from config.

    Args:
        config: Configuration dictionary (optional)
        config_file: Path to the configuration file (optional)
    """
    if config is None and config_file is not None:
        config = load_json_config(config_file)

    if config is None:
        return None

    return config.get("scenario_generator")

def get_perturbation_values(config=None, config_file=None):
    """
    Get perturbation values from config.

    Args:
        config: Configuration dictionary (optional)
        config_file: Path to the configuration file (optional)
    """
    if config is None and config_file is not None:
        config = load_json_config(config_file)

    if config is None:
        return None

    return config.get("perturbation_values")

def get_simulation_settings(config=None, config_file=None):
    """
    Get simulation settings from config.

    Args:
        config: Configuration dictionary (optional)
        config_file: Path to the configuration file (optional)
    """
    if config is None and config_file is not None:
        config = load_json_config(config_file)

    if config is None:
        return None

    return config.get("simulation_settings")
# ---------------------------------------------------------------------------
# DATA LOADING FUNCTIONS
# ---------------------------------------------------------------------------

# Default event size modifiers - use from config instead
# EXP1_EVENT_SIZE_MODIFIERS = get_event_size_modifiers()


def load_plans(file_path=None, config_file=None):
    """
    Load plans from CSV file.
    Returns a dictionary mapping plan IDs to lists of goals.

    Args:
        file_path: Path to the plans CSV file. If None, path is taken from config file.
        config_file: Path to the configuration file.
    """
    # Get file path from config if not provided
    if file_path is None and config_file is not None:
        file_paths = get_file_paths(config_file=config_file)
        if file_paths is None:
            print(f"Error: Could not get file paths from configuration file {config_file}")
            return {}

        file_path = file_paths.get("plans")
        if file_path is None:
            print("Error: No 'plans' path specified in configuration")
            return {}

    if file_path is None:
        print("Error: No file path provided for plans")
        return {}

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

def load_contributions(file_path=None, config_file=None):
    """
    Load goal contributions to domain variables from CSV file.
    Returns a dictionary mapping domain variables to dictionaries of goal contributions.

    Args:
        file_path: Path to the contributions CSV file. If None, path is taken from config file.
        config_file: Path to the configuration file.
    """
    # Get file path from config if not provided
    if file_path is None and config_file is not None:
        file_paths = get_file_paths(config_file=config_file)
        if file_paths is None:
            print(f"Error: Could not get file paths from configuration file {config_file}")
            return {}

        file_path = file_paths.get("contributions")
        if file_path is None:
            print("Error: No 'contributions' path specified in configuration")
            return {}

    if file_path is None:
        print("Error: No file path provided for contributions")
        return {}

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

def create_quality_goals_from_scenario(scenario, quality_goals_mapping, event_size_modifiers=None, config_file=None):
    """
    Create quality goals directly from scenario constraints.
    Returns a dictionary of quality goals with their constraint values.

    Args:
        scenario: Dictionary with scenario parameters including direct constraints
        quality_goals_mapping: Mapping between quality goal IDs and domain variables
        event_size_modifiers: Optional dictionary of modifiers for different event sizes
        config_file: Path to the configuration file
    """
    event_size = scenario["event_size"]

    # Create quality goals using scenario constraints
    quality_goals = {}

    # Map from domain variable types to scenario constraint fields
    constraint_mapping = {
        "TotalCost": "cost_constraint",
        "TotalEffort": "effort_constraint",
        "TimeSpent": "time_constraint"
    }

    # Default event size modifiers if none provided
    if event_size_modifiers is None:
        # Create default modifiers if they're not available from config
        event_size_modifiers = {
            "small": {"TotalCost": 1.0, "TimeSpent": 1.0, "TotalEffort": 1.0},
            "medium": {"TotalCost": 2.0, "TimeSpent": 1.5, "TotalEffort": 2.0},
            "big": {"TotalCost": 3.0, "TimeSpent": 2.0, "TotalEffort": 3.0}
        }

    # Make sure the event size exists in modifiers
    if event_size not in event_size_modifiers:
        print(f"Warning: Event size '{event_size}' not found in modifiers, using 'small' defaults")
        size_mod = event_size_modifiers.get("small", {"TotalCost": 1.0, "TimeSpent": 1.0, "TotalEffort": 1.0})
    else:
        size_mod = event_size_modifiers[event_size]

    # Create quality goals based on the mapping and scenario constraints
    for qg_id, domain_var in quality_goals_mapping.items():
        # Find the corresponding constraint field
        constraint_field = None
        for var_type, field in constraint_mapping.items():
            if var_type in domain_var:
                constraint_field = field
                break

        if not constraint_field or constraint_field not in scenario:
            print(f"Warning: Could not find constraint for {domain_var} in scenario")
            continue

        # Get the constraint value from scenario
        constraint_value = scenario[constraint_field]

        # Apply event size modifier if available for this domain variable
        if domain_var in size_mod:
            constraint_value *= size_mod[domain_var]

        # Create the quality goal
        quality_goals[qg_id] = {
            "name": qg_id,
            "domain_variable": domain_var,
            "max_value": constraint_value,
            "type": "max"  # Assuming all constraints are upper bounds
        }

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

def filter_valid_plans(scenario, all_plan_impacts, quality_goals_mapping, event_size_modifiers=None):
    """
    Filter plans that satisfy all quality goals for the given scenario.
    Returns a dictionary of valid plans with their impacts.

    Updated to use quality_goals_mapping and create_quality_goals_from_scenario
    """
    quality_goals = create_quality_goals_from_scenario(scenario, quality_goals_mapping, event_size_modifiers)

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
