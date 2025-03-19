import csv
import os
import random
import numpy as np
from datetime import datetime
import pandas as pd

# ---------------------------------------------------------------------------
# DATA LOADING FUNCTIONS
# ---------------------------------------------------------------------------

def load_plans(file_path="data/exp1_plans.csv"):
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

def load_contributions(file_path="data/exp1_contributions.csv"):
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

def load_quality_goals(file_path="data/exp1_quality_goals.csv"):
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
# PERTURBATION VALUES
# ---------------------------------------------------------------------------

# Fixed perturbation values based on type and level
PERTURBATION_VALUE = {
    "org": {
        "pos": -1,        # 1 more organizer (reduces time and effort)
        "no": 0,          # No change
        "low_neg": 1,     # 1 fewer organizer
        "high_neg": 2     # 2 fewer organizers
    },
    "time": {
        "pos": -24,       # 1 day less (in hours)
        "no": 0,          # No change
        "low_neg": 24,    # 1 extra day (in hours)
        "high_neg": 48    # 2 extra days (in hours)
    },
    "cost": {
        "pos": -50,       # 50 euros less
        "no": 0,          # No change
        "low_neg": 50,    # 50 euros more
        "high_neg": 100   # 100 euros more
    }
}

# Number of simulation runs per scenario for random strategy
NUM_RANDOM_RUNS = 10

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

def calculate_quality_goals_for_scenario(scenario, base_quality_goals):
    """
    Adjust quality goals based on scenario parameters.
    Returns a dictionary of quality goals with their constraint values.
    """
    event_size = scenario["event_size"]
    organizers = scenario["organizers"]

    # Create a copy of the base quality goals
    quality_goals = {}
    for qg_id, goal in base_quality_goals.items():
        quality_goals[qg_id] = goal.copy()

    # Apply event size modifiers
    EVENT_SIZE_MODIFIERS = {
        "small": {"Cost": 1.0, "Time Spent": 1.0, "Effort": 1.0},
        "medium": {"Cost": 2.0, "Time Spent": 1.5, "Effort": 2.0},
        "big": {"Cost": 3.0, "Time Spent": 2.0, "Effort": 3.0}
    }

    size_mod = EVENT_SIZE_MODIFIERS[event_size]

    # Adjust constraints based on event size and organizers
    for qg_id, goal in quality_goals.items():
        domain_var = goal["domain_variable"]
        if domain_var in size_mod:
            goal["max_value"] *= size_mod[domain_var]

            # Adjust time-related constraints based on number of organizers
            if domain_var == "Time Spent":
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

def filter_valid_plans(scenario, all_plan_impacts, base_quality_goals):
    """
    Filter plans that satisfy all quality goals for the given scenario.
    Returns a dictionary of valid plans with their impacts.
    """
    quality_goals = calculate_quality_goals_for_scenario(scenario, base_quality_goals)

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

def avg_only_strategy(q2s_matrix):
    """
    Select plan using only the average satisfaction.
    """
    if not q2s_matrix:
        return None, 0

    plan_scores = {}
    for plan_id, distances in q2s_matrix.items():
        distance_values = list(distances.values())
        if not distance_values:  # Skip if no distance values
            continue

        avg_sat = sum(distance_values) / len(distance_values)
        plan_scores[plan_id] = avg_sat

    # Return the plan with the highest average satisfaction
    if not plan_scores:  # Check if plan_scores is empty
        return None, 0

    best_plan_id = max(plan_scores, key=plan_scores.get)
    return best_plan_id, plan_scores[best_plan_id]

def min_only_strategy(q2s_matrix):
    """
    Select plan using only the minimum satisfaction.
    """
    if not q2s_matrix:
        return None, 0

    plan_scores = {}
    for plan_id, distances in q2s_matrix.items():
        distance_values = list(distances.values())
        if not distance_values:  # Skip if no distance values
            continue

        min_sat = min(distance_values)
        plan_scores[plan_id] = min_sat

    # Return the plan with the highest minimum satisfaction
    if not plan_scores:  # Check if plan_scores is empty
        return None, 0

    best_plan_id = max(plan_scores, key=plan_scores.get)
    return best_plan_id, plan_scores[best_plan_id]

def random_strategy(q2s_matrix):
    """
    Select a random plan from valid plans.
    """
    if not q2s_matrix:
        return None, 0

    plan_ids = list(q2s_matrix.keys())
    if not plan_ids:  # Check if no plans available
        return None, 0

    plan_id = random.choice(plan_ids)
    distance_values = list(q2s_matrix[plan_id].values())
    if not distance_values:  # Check if no distance values
        return plan_id, 0

    avg_sat = sum(distance_values) / len(distance_values)

    return plan_id, avg_sat

# ---------------------------------------------------------------------------
# PERTURBATION APPLICATION
# ---------------------------------------------------------------------------

def apply_perturbation(plan_impacts, scenario):
    """
    Apply perturbations based on scenario parameters.
    """
    # Deep copy the impacts to avoid modifying the original
    perturbed_impacts = dict(plan_impacts)

    # Get perturbation values for each dimension
    org_perturbation = PERTURBATION_VALUE["org"][scenario["perturbation_level_org"]]
    time_perturbation = PERTURBATION_VALUE["time"][scenario["perturbation_level_time"]]
    cost_perturbation = PERTURBATION_VALUE["cost"][scenario["perturbation_level_cost"]]

    # Apply perturbations to domain variables
    for var in perturbed_impacts:
        if "Time" in var:  # Time-related variable
            perturbed_impacts[var] += time_perturbation
        elif "Cost" in var:  # Cost-related variable
            perturbed_impacts[var] += cost_perturbation
        elif "Effort" in var:  # Effort might be affected by organizers
            # Simulate change in effort based on change in organizers
            if org_perturbation != 0:
                perturbed_impacts[var] *= (1 + 0.15 * org_perturbation)

    return perturbed_impacts

def evaluate_plan_under_perturbation(plan_id, plan, quality_goals, scenario):
    """
    Evaluate a plan under perturbation.
    """
    # Apply perturbation to plan impacts
    perturbed_impacts = apply_perturbation(plan["impact"], scenario)

    # Check if perturbed plan still satisfies constraints
    valid = True
    margins = []

    for qg_id, goal in quality_goals.items():
        domain_var = goal["domain_variable"]
        if domain_var in perturbed_impacts:
            impact_value = perturbed_impacts[domain_var]

            if goal["type"] == "max":
                margin = (goal["max_value"] - impact_value) / goal["max_value"]
                margins.append(margin)
                if impact_value > goal["max_value"]:
                    valid = False

    success_rate = 1 if valid else 0
    avg_margin = sum(margins) / len(margins) if margins else 0

    return success_rate, avg_margin

# ---------------------------------------------------------------------------
# SCENARIO PROCESSING
# ---------------------------------------------------------------------------

def process_scenario(scenario, plans, contributions, base_quality_goals):
    """
    Process a single scenario and evaluate different plan selection strategies.
    """
    # Extract scenario parameters
    scenario_id = scenario["id"]
    event_size = scenario["event_size"]
    organizers = scenario["organizers"]
    time = scenario["time"]
    budget = scenario["budget"]
    alpha = scenario["alpha"]
    perturbation_level_org = scenario["perturbation_level_org"]
    perturbation_level_time = scenario["perturbation_level_time"]
    perturbation_level_cost = scenario["perturbation_level_cost"]

    print(f"Processing scenario {scenario_id}...")

    # Calculate impacts for all plans
    all_plan_impacts = calculate_all_plan_impacts(plans, contributions)

    # Step 1: Calculate quality goals and filter valid plans
    valid_plans, quality_goals = filter_valid_plans(scenario, all_plan_impacts, base_quality_goals)

    # If no valid plans, return failed results
    if not valid_plans:
        print(f"No valid plans for scenario {scenario_id}")
        return {
            "id": scenario_id,
            "event_size": event_size,
            "organizers": organizers,
            "time": time,
            "budget": budget,
            "perturbation_level_org": perturbation_level_org,
            "perturbation_level_time": perturbation_level_time,
            "perturbation_level_cost": perturbation_level_cost,
            "alpha": alpha,
            "Q2S_success": 0,
            "Q2S_margins": 0,
            "Avg_success": 0,
            "Avg_margins": 0,
            "Min_success": 0,
            "Min_margins": 0,
            "Random_success": 0,
            "Random_margins": 0,
            "num_valid_plans": 0
        }

    # Step 2: Calculate Q2S matrix
    q2s_matrix = calculate_q2s_matrix(valid_plans, quality_goals)

    # Step 3: Apply Q2S strategy
    q2s_plan_id, q2s_score = q2s_selection_strategy(q2s_matrix, alpha)
    if q2s_plan_id:
        q2s_success, q2s_margins = evaluate_plan_under_perturbation(
            q2s_plan_id, valid_plans[q2s_plan_id], quality_goals, scenario
        )
    else:
        q2s_success, q2s_margins = 0, 0

    # Step 4: Apply AvgSat strategy
    avg_plan_id, avg_score = avg_only_strategy(q2s_matrix)
    if avg_plan_id:
        avg_success, avg_margins = evaluate_plan_under_perturbation(
            avg_plan_id, valid_plans[avg_plan_id], quality_goals, scenario
        )
    else:
        avg_success, avg_margins = 0, 0

    # Step 5: Apply MinSat strategy
    min_plan_id, min_score = min_only_strategy(q2s_matrix)
    if min_plan_id:
        min_success, min_margins = evaluate_plan_under_perturbation(
            min_plan_id, valid_plans[min_plan_id], quality_goals, scenario
        )
    else:
        min_success, min_margins = 0, 0

    # Step 6: Apply Random strategy
    # Run multiple trials to get an average for random selection
    random_successes = []
    random_margins = []

    for _ in range(NUM_RANDOM_RUNS):  # Multiple random trials
        random_plan_id, _ = random_strategy(q2s_matrix)
        if random_plan_id:
            success, margin = evaluate_plan_under_perturbation(
                random_plan_id, valid_plans[random_plan_id], quality_goals, scenario
            )
            random_successes.append(success)
            random_margins.append(margin)

    random_success = sum(random_successes) / len(random_successes) if random_successes else 0
    random_margin = sum(random_margins) / len(random_margins) if random_margins else 0

    # Step 7: Return results
    results = {
        "id": scenario_id,
        "event_size": event_size,
        "organizers": organizers,
        "time": time,
        "budget": budget,
        "perturbation_level_org": perturbation_level_org,
        "perturbation_level_time": perturbation_level_time,
        "perturbation_level_cost": perturbation_level_cost,
        "alpha": alpha,
        "Q2S_success": q2s_success,
        "Q2S_margins": q2s_margins,
        "Avg_success": avg_success,
        "Avg_margins": avg_margins,
        "Min_success": min_success,
        "Min_margins": min_margins,
        "Random_success": random_success,
        "Random_margins": random_margin,
        "num_valid_plans": len(valid_plans),
        "selected_plans": {
            "Q2S": q2s_plan_id,
            "Avg": avg_plan_id,
            "Min": min_plan_id
        }
    }

    print(f"Scenario {scenario_id} processed. Valid plans: {len(valid_plans)}")
    return results

# ---------------------------------------------------------------------------
# MAIN PROCESSING FUNCTION
# ---------------------------------------------------------------------------

def process_all_scenarios(input_file="data/all_scenarios_upd.csv", output_file="data/all_scenarios_results_upd.csv"):
    """
    Process all scenarios from the input CSV file and write results to the output CSV file.
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

    # Load data from CSV files
    plans = load_plans()
    contributions = load_contributions()
    base_quality_goals = load_quality_goals()

    if not plans or not contributions or not base_quality_goals:
        print("Error: Failed to load required data. Exiting.")
        return []

    # Read scenarios from CSV
    scenarios = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            scenario = {
                "id": int(row["id"]),
                "event_size": row["event_size"],
                "organizers": int(row["organizers"]),
                "time": int(row["time"]),
                "budget": int(row["budget"]),
                "alpha": float(row["alpha"]),
                "perturbation_level_org": row["perturbation_level_org"],
                "perturbation_level_time": row["perturbation_level_time"],
                "perturbation_level_cost": row["perturbation_level_cost"]
            }
            scenarios.append(scenario)

    print(f"Loaded {len(scenarios)} scenarios from {input_file}")

    # Process each scenario
    results = []
    for scenario in scenarios:
        scenario_results = process_scenario(scenario, plans, contributions, base_quality_goals)
        results.append(scenario_results)

    # Write results to CSV
    fieldnames = [
        "id", "event_size", "organizers", "time", "budget",
        "perturbation_level_org", "perturbation_level_time", "perturbation_level_cost",
        "alpha", "Q2S_success", "Q2S_margins", "Avg_success", "Avg_margins",
        "Min_success", "Min_margins", "Random_success", "Random_margins",
        "num_valid_plans"
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{k: v for k, v in r.items() if k in fieldnames} for r in results])

    print(f"Results saved to {output_file}")
    return results

def process_test_scenarios(input_file="data/all_scenarios_upd.csv", output_file="data/test_scenarios_results.csv", num_test_scenarios=2, start_row=10):
    """
    Process only a small number of scenarios for testing purposes with verbose output.

    Args:
        input_file: Path to the input CSV file with scenarios
        output_file: Path to write test results
        num_test_scenarios: Number of scenarios to process for testing
        start_row: Starting row index in the CSV file (0-based)

    Returns:
        List of results for the processed scenarios
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

    # Load data from CSV files with verbose output
    print("\n===== LOADING DATA =====")
    plans = load_plans()
    print("\nLoaded Plans:")
    for plan_id, plan in list(plans.items())[:5]:  # Show first 5 plans
        print(f"  {plan_id}: {plan['goals']}")
    if len(plans) > 5:
        print(f"  ... and {len(plans) - 5} more plans")

    contributions = load_contributions()
    print("\nLoaded Contributions:")
    for domain_var, goal_contributions in contributions.items():
        print(f"  {domain_var}:")
        for goal, value in list(goal_contributions.items())[:3]:  # Show first 3 contributions
            print(f"    {goal}: {value}")
        if len(goal_contributions) > 3:
            print(f"    ... and {len(goal_contributions) - 3} more contributions")

    base_quality_goals = load_quality_goals()
    print("\nLoaded Quality Goals:")
    for qg_id, goal in base_quality_goals.items():
        print(f"  {qg_id}: {goal['domain_variable']} ≤ {goal['max_value']}")

    if not plans or not contributions or not base_quality_goals:
        print("Error: Failed to load required data. Exiting.")
        return []

    # Read scenarios from CSV
    all_scenarios = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Skip rows before the start_row
            if i < start_row:
                continue

            # Convert numeric fields
            scenario = {
                "id": int(row["id"]),
                "event_size": row["event_size"],
                "organizers": int(row["organizers"]),
                "time": int(row["time"]),
                "budget": int(row["budget"]),
                "alpha": float(row["alpha"]),
                "perturbation_level_org": row["perturbation_level_org"],
                "perturbation_level_time": row["perturbation_level_time"],
                "perturbation_level_cost": row["perturbation_level_cost"]
            }
            all_scenarios.append(scenario)

            # Break after collecting num_test_scenarios
            if len(all_scenarios) >= num_test_scenarios:
                break

    print(f"\nLoaded {len(all_scenarios)} test scenarios from {input_file} starting at row {start_row+1}")

    # Process each scenario with verbose output
    results = []
    for scenario_index, scenario in enumerate(all_scenarios):
        print(f"\n\n===== PROCESSING SCENARIO {scenario['id']} (Test {scenario_index+1}/{len(all_scenarios)}) =====")
        print(f"Parameters: event_size={scenario['event_size']}, organizers={scenario['organizers']}, " +
              f"time={scenario['time']}, budget={scenario['budget']}, alpha={scenario['alpha']}")
        print(f"Perturbations: org={scenario['perturbation_level_org']}, " +
              f"time={scenario['perturbation_level_time']}, cost={scenario['perturbation_level_cost']}")

        # Calculate impacts for all plans
        print("\nCalculating plan impacts...")
        all_plan_impacts = calculate_all_plan_impacts(plans, contributions)

        # Print all plan impacts
        print("\nAll Plan Impacts:")
        print(f"{'Plan ID':<10} | {'Variable':<15} | {'Impact':<10}")
        print("-" * 40)
        for plan_id, impacts in all_plan_impacts.items():
            for var_name, impact in impacts.items():
                print(f"{plan_id:<10} | {var_name:<15} | {impact:<10.2f}")

        print(f"\nCalculated impacts for {len(all_plan_impacts)} plans")

        # Calculate quality goals for this scenario
        quality_goals = calculate_quality_goals_for_scenario(scenario, base_quality_goals)

        # Print adjusted quality goals
        print("\nAdjusted Quality Goals for this scenario:")
        for qg_id, goal in quality_goals.items():
            print(f"  {qg_id}: {goal['domain_variable']} ≤ {goal['max_value']}")

        # Filter valid plans
        valid_plans = {}
        for plan_id, impacts in all_plan_impacts.items():
            # Check if plan satisfies all constraints
            if check_plan_validity(impacts, quality_goals):
                valid_plans[plan_id] = {"name": plan_id, "impact": impacts}

        print(f"\nFiltered down to {len(valid_plans)} valid plans")
        if valid_plans:
            print("Valid Plans:")
            for plan_id in valid_plans:
                print(f"  {plan_id}")

        # If no valid plans, continue to next scenario
        if not valid_plans:
            print(f"No valid plans for scenario {scenario['id']} - skipping")
            results.append({
                "id": scenario["id"],
                "event_size": scenario["event_size"],
                "organizers": scenario["organizers"],
                "time": scenario["time"],
                "budget": scenario["budget"],
                "perturbation_level_org": scenario["perturbation_level_org"],
                "perturbation_level_time": scenario["perturbation_level_time"],
                "perturbation_level_cost": scenario["perturbation_level_cost"],
                "alpha": scenario["alpha"],
                "Q2S_success": 0,
                "Q2S_margins": 0,
                "Avg_success": 0,
                "Avg_margins": 0,
                "Min_success": 0,
                "Min_margins": 0,
                "Random_success": 0,
                "Random_margins": 0,
                "num_valid_plans": 0
            })
            continue

        # Calculate Q2S matrix - DEBUGGING VERBOSE VERSION
        q2s_matrix = {}
        print("\nCalculating Q2S matrix...")
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
                        plan_distances[qg_id] = distance
                    else:
                        # For min constraints (if implemented in the future)
                        plan_distances[qg_id] = 0

            if plan_distances:  # Only add to matrix if we have distances
                q2s_matrix[plan_id] = plan_distances

        print(f"\nQ2S Matrix has {len(q2s_matrix)} plans")
        if not q2s_matrix:
            print("WARNING: Q2S matrix is empty! Check domain variables in quality goals match variables in contributions.")

            # Print expected domain variables
            print("\nExpected domain variables from quality goals:")
            expected_vars = [goal["domain_variable"] for goal in quality_goals.values()]
            print(f"  {expected_vars}")

            print("\nAvailable variables in plan impacts:")
            if all_plan_impacts:
                first_plan = next(iter(all_plan_impacts.values()))
                print(f"  {list(first_plan.keys())}")
            else:
                print("  No plan impacts available")

            continue  # Skip rest of processing

        # Print just a summary of the Q2S matrix
        print("\nQ2S Matrix Summary:")
        if len(q2s_matrix) > 0:
            # Show sample of first plan
            sample_plan_id = next(iter(q2s_matrix.keys()))
            print(f"  Sample ({sample_plan_id}):")
            for qg_id, distance in q2s_matrix[sample_plan_id].items():
                print(f"    {qg_id}: {distance:.4f}")

            # Show average distances for all plans
            avg_distances = {}
            for qg_id in next(iter(q2s_matrix.values())).keys():
                avg_distances[qg_id] = sum(plan[qg_id] for plan in q2s_matrix.values()) / len(q2s_matrix)

            print(f"  Average distances across all {len(q2s_matrix)} plans:")
            for qg_id, avg in avg_distances.items():
                print(f"    {qg_id}: {avg:.4f}")

        # Apply strategies
        print("\nApplying selection strategies...")

        # Q2S strategy
        q2s_plan_id, q2s_score = q2s_selection_strategy(q2s_matrix, scenario["alpha"])
        if q2s_plan_id:
            print(f"  Q2S strategy selected plan {q2s_plan_id} with score {q2s_score:.4f}")
            q2s_success, q2s_margins = evaluate_plan_under_perturbation(
                q2s_plan_id, valid_plans[q2s_plan_id], quality_goals, scenario
            )
            print(f"    Success: {q2s_success}, Margins: {q2s_margins:.4f}")
        else:
            print("  Q2S strategy could not select a plan")
            q2s_success, q2s_margins = 0, 0

        # AvgSat strategy
        avg_plan_id, avg_score = avg_only_strategy(q2s_matrix)
        if avg_plan_id:
            print(f"  AvgSat strategy selected plan {avg_plan_id} with score {avg_score:.4f}")
            avg_success, avg_margins = evaluate_plan_under_perturbation(
                avg_plan_id, valid_plans[avg_plan_id], quality_goals, scenario
            )
            print(f"    Success: {avg_success}, Margins: {avg_margins:.4f}")
        else:
            print("  AvgSat strategy could not select a plan")
            avg_success, avg_margins = 0, 0

        # MinSat strategy
        min_plan_id, min_score = min_only_strategy(q2s_matrix)
        if min_plan_id:
            print(f"  MinSat strategy selected plan {min_plan_id} with score {min_score:.4f}")
            min_success, min_margins = evaluate_plan_under_perturbation(
                min_plan_id, valid_plans[min_plan_id], quality_goals, scenario
            )
            print(f"    Success: {min_success}, Margins: {min_margins:.4f}")
        else:
            print("  MinSat strategy could not select a plan")
            min_success, min_margins = 0, 0

        # Random strategy (with multiple trials)
        print(f"  Running {NUM_RANDOM_RUNS} random selection trials...")
        random_successes = []
        random_margins = []

        for i in range(NUM_RANDOM_RUNS):
            random_plan_id, _ = random_strategy(q2s_matrix)
            if random_plan_id:
                success, margin = evaluate_plan_under_perturbation(
                    random_plan_id, valid_plans[random_plan_id], quality_goals, scenario
                )
                random_successes.append(success)
                random_margins.append(margin)

        random_success = sum(random_successes) / len(random_successes) if random_successes else 0
        random_margin = sum(random_margins) / len(random_margins) if random_margins else 0
        print(f"  Random strategy average: Success: {random_success:.4f}, Margins: {random_margin:.4f}")

        # Compile results
        scenario_results = {
            "id": scenario["id"],
            "event_size": scenario["event_size"],
            "organizers": scenario["organizers"],
            "time": scenario["time"],
            "budget": scenario["budget"],
            "perturbation_level_org": scenario["perturbation_level_org"],
            "perturbation_level_time": scenario["perturbation_level_time"],
            "perturbation_level_cost": scenario["perturbation_level_cost"],
            "alpha": scenario["alpha"],
            "Q2S_success": q2s_success,
            "Q2S_margins": q2s_margins,
            "Avg_success": avg_success,
            "Avg_margins": avg_margins,
            "Min_success": min_success,
            "Min_margins": min_margins,
            "Random_success": random_success,
            "Random_margins": random_margin,
            "num_valid_plans": len(valid_plans),
            "selected_plans": {
                "Q2S": q2s_plan_id,
                "Avg": avg_plan_id,
                "Min": min_plan_id
            }
        }

        results.append(scenario_results)
        print(f"\nScenario {scenario['id']} processed successfully.")

    # Write results to CSV
    fieldnames = [
        "id", "event_size", "organizers", "time", "budget",
        "perturbation_level_org", "perturbation_level_time", "perturbation_level_cost",
        "alpha", "Q2S_success", "Q2S_margins", "Avg_success", "Avg_margins",
        "Min_success", "Min_margins", "Random_success", "Random_margins",
        "num_valid_plans"
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{k: v for k, v in r.items() if k in fieldnames} for r in results])

    print(f"\nTest results saved to {output_file}")
    return results

if __name__ == "__main__":
    print("Starting Q2S Experiment 1 verbose test processing...")
    start_time = datetime.now()

    # Process test scenarios starting from row 10
    results = process_test_scenarios(start_row=10)

    end_time = datetime.now()
    print(f"\nTest processing completed in {end_time - start_time}")
