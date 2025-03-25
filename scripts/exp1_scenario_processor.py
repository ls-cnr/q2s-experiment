import csv
import os
import random
import numpy as np
from datetime import datetime
import pandas as pd

from q2s_utils import (
    load_plans, load_contributions, load_quality_goals,
    calculate_plan_impact, calculate_all_plan_impacts,
    calculate_quality_goals_for_scenario, check_plan_validity, filter_valid_plans,
    calculate_q2s_matrix, q2s_selection_strategy
)

# ---------------------------------------------------------------------------
# EXP1 SPECIFIC CONSTANTS
# ---------------------------------------------------------------------------

EXP1_EVENT_SIZE_MODIFIERS = {
    "small": {"TotalCost": 1.0, "TimeSpent": 1.0, "TotalEffort": 1.0},
    "medium": {"TotalCost": 2.0, "TimeSpent": 1.5, "TotalEffort": 2.0},
    "big": {"TotalCost": 3.0, "TimeSpent": 2.0, "TotalEffort": 3.0}
}

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
# PLAN SELECTION STRATEGIES (EXP1 SPECIFIC)
# ---------------------------------------------------------------------------

def avg_only_strategy(q2s_matrix, verbose=False):
    """
    Select plan using only the average satisfaction.
    """
    if not q2s_matrix:
        if verbose:
            print("  WARNING: Empty Q2S matrix passed to avg_only_strategy")
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
        if verbose:
            print("  WARNING: No valid plan scores in avg_only_strategy")
        return None, 0

    best_plan_id = max(plan_scores, key=plan_scores.get)
    if verbose:
        print(f"  AvgSat strategy selected plan {best_plan_id} with score {plan_scores[best_plan_id]:.4f}")
    return best_plan_id, plan_scores[best_plan_id]

def min_only_strategy(q2s_matrix, verbose=False):
    """
    Select plan using only the minimum satisfaction.
    """
    if not q2s_matrix:
        if verbose:
            print("  WARNING: Empty Q2S matrix passed to min_only_strategy")
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
        if verbose:
            print("  WARNING: No valid plan scores in min_only_strategy")
        return None, 0

    best_plan_id = max(plan_scores, key=plan_scores.get)
    if verbose:
        print(f"  MinSat strategy selected plan {best_plan_id} with score {plan_scores[best_plan_id]:.4f}")
    return best_plan_id, plan_scores[best_plan_id]

def random_strategy(q2s_matrix, verbose=False):
    """
    Select a random plan from valid plans.
    """
    if not q2s_matrix:
        if verbose:
            print("  WARNING: Empty Q2S matrix passed to random_strategy")
        return None, 0

    plan_ids = list(q2s_matrix.keys())
    if not plan_ids:  # Check if no plans available
        if verbose:
            print("  WARNING: No valid plans in random_strategy")
        return None, 0

    plan_id = random.choice(plan_ids)
    distance_values = list(q2s_matrix[plan_id].values())
    if not distance_values:  # Check if no distance values
        if verbose:
            print(f"  Random strategy selected plan {plan_id} but no distance values found")
        return plan_id, 0

    avg_sat = sum(distance_values) / len(distance_values)
    if verbose:
        print(f"  Random strategy selected plan {plan_id} with avg score {avg_sat:.4f}")
    return plan_id, avg_sat

# ---------------------------------------------------------------------------
# PERTURBATION APPLICATION
# ---------------------------------------------------------------------------

def apply_perturbation(plan_impacts, scenario, verbose=False):
    """
    Apply perturbations based on scenario parameters.
    """
    # Deep copy the impacts to avoid modifying the original
    perturbed_impacts = dict(plan_impacts)

    # Get perturbation values for each dimension
    org_perturbation = PERTURBATION_VALUE["org"][scenario["perturbation_level_org"]]
    time_perturbation = PERTURBATION_VALUE["time"][scenario["perturbation_level_time"]]
    cost_perturbation = PERTURBATION_VALUE["cost"][scenario["perturbation_level_cost"]]

    if verbose:
        print(f"  Applying perturbations: org={org_perturbation}, time={time_perturbation}, cost={cost_perturbation}")

    # Apply perturbations to domain variables
    for var in perturbed_impacts:
        original_value = perturbed_impacts[var]
        if "Time" in var:  # Time-related variable
            perturbed_impacts[var] += time_perturbation
        elif "Cost" in var:  # Cost-related variable
            perturbed_impacts[var] += cost_perturbation
        elif "Effort" in var:  # Effort might be affected by organizers
            # Simulate change in effort based on change in organizers
            if org_perturbation != 0:
                perturbed_impacts[var] *= (1 + 0.15 * org_perturbation)

        if verbose and perturbed_impacts[var] != original_value:
            print(f"    {var}: {original_value:.2f} -> {perturbed_impacts[var]:.2f}")

    return perturbed_impacts

def evaluate_plan_under_perturbation(plan_id, plan, quality_goals, scenario, verbose=False):
    """
    Evaluate a plan under perturbation.
    """
    if verbose:
        print(f"  Evaluating plan {plan_id} under perturbation...")

    # Apply perturbation to plan impacts
    perturbed_impacts = apply_perturbation(plan["impact"], scenario, verbose)

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
                    if verbose:
                        print(f"    {qg_id}: Constraint violated! {impact_value:.2f} > {goal['max_value']:.2f}")
                elif verbose:
                    print(f"    {qg_id}: Constraint satisfied. {impact_value:.2f} <= {goal['max_value']:.2f} (margin: {margin:.4f})")

    success_rate = 1 if valid else 0
    avg_margin = sum(margins) / len(margins) if margins else 0

    if verbose:
        print(f"    Plan is {'valid' if valid else 'invalid'} under perturbation")
        print(f"    Average margin: {avg_margin:.4f}")

    return success_rate, avg_margin

# ---------------------------------------------------------------------------
# SCENARIO PROCESSING
# ---------------------------------------------------------------------------

def process_scenario(scenario, plans, contributions, base_quality_goals, verbose=False, output_file=None):
    """
    Process a single scenario and evaluate different plan selection strategies.

    Args:
        scenario: Dictionary with scenario parameters
        plans: Dictionary of plans
        contributions: Dictionary of contributions
        base_quality_goals: Dictionary of base quality goals
        verbose: Whether to print verbose output
        output_file: Optional path to write results to CSV

    Returns:
        Dictionary with results
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

    if verbose:
        print(f"\n\n===== PROCESSING SCENARIO {scenario_id} =====")
        print(f"Parameters: event_size={event_size}, organizers={organizers}, " +
              f"time={time}, budget={budget}, alpha={alpha}")
        print(f"Perturbations: org={perturbation_level_org}, " +
              f"time={perturbation_level_time}, cost={perturbation_level_cost}")
    else:
        print(f"Processing scenario {scenario_id}...")

    # Calculate impacts for all plans
    if verbose:
        print("\nCalculating plan impacts...")
    all_plan_impacts = calculate_all_plan_impacts(plans, contributions)

    # Print plan impacts details if verbose
    if verbose:
        print("\nAll Plan Impacts:")
        print(f"{'Plan ID':<10} | {'Variable':<15} | {'Impact':<10}")
        print("-" * 40)
        for plan_id, impacts in list(all_plan_impacts.items())[:5]:  # Show first 5 plans
            for var_name, impact in impacts.items():
                print(f"{plan_id:<10} | {var_name:<15} | {impact:<10.2f}")
        if len(all_plan_impacts) > 5:
            print(f"... and {len(all_plan_impacts) - 5} more plans")
        print(f"\nCalculated impacts for {len(all_plan_impacts)} plans")

    # Step 1: Calculate quality goals and filter valid plans
    valid_plans, quality_goals = filter_valid_plans(
        scenario, all_plan_impacts, base_quality_goals, EXP1_EVENT_SIZE_MODIFIERS
    )

    # Print quality goals if verbose
    if verbose:
        print("\nAdjusted Quality Goals for this scenario:")
        for qg_id, goal in quality_goals.items():
            print(f"  {qg_id}: {goal['domain_variable']} ≤ {goal['max_value']}")

        print(f"\nFiltered down to {len(valid_plans)} valid plans")
        if valid_plans:
            print("Valid Plans:")
            for plan_id in list(valid_plans.keys())[:10]:  # Show first 10 plans
                print(f"  {plan_id}")
            if len(valid_plans) > 10:
                print(f"  ... and {len(valid_plans) - 10} more plans")

    # If no valid plans, return failed results
    if not valid_plans:
        if verbose:
            print(f"No valid plans for scenario {scenario_id} - aborting")
        else:
            print(f"No valid plans for scenario {scenario_id}")

        result = {
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

        # Write to file if specified
        if output_file:
            write_result_to_csv(result, output_file)
            if verbose:
                print(f"\nFailed result saved to {output_file}")

        return result

    # Step 2: Calculate Q2S matrix
    if verbose:
        print("\nCalculating Q2S matrix...")

    q2s_matrix = calculate_q2s_matrix(valid_plans, quality_goals)

    if verbose:
        print(f"\nQ2S Matrix has {len(q2s_matrix)} plans")
        if q2s_matrix:
            print("Q2S Matrix (sample):")
            for plan_id in list(q2s_matrix.keys())[:3]:  # Show first 3 plans
                print(f"  {plan_id}:")
                for qg_id, distance in q2s_matrix[plan_id].items():
                    print(f"    {qg_id}: {distance:.4f}")
            if len(q2s_matrix) > 3:
                print(f"  ... and {len(q2s_matrix) - 3} more plans")

    # Check if matrix is empty
    if not q2s_matrix:
        if verbose:
            print("WARNING: Q2S matrix is empty! Check domain variables in quality goals match variables in contributions.")
            print("\nExpected domain variables from quality goals:")
            expected_vars = [goal["domain_variable"] for goal in quality_goals.values()]
            print(f"  {expected_vars}")
            print("\nAvailable variables in plan impacts:")
            if all_plan_impacts:
                first_plan = next(iter(all_plan_impacts.values()))
                print(f"  {list(first_plan.keys())}")
            else:
                print("  No plan impacts available")

        result = {
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
            "num_valid_plans": len(valid_plans)
        }

        # Write to file if specified
        if output_file:
            write_result_to_csv(result, output_file)
            if verbose:
                print(f"\nFailed result saved to {output_file}")

        return result

    # Apply strategies
    if verbose:
        print("\nApplying selection strategies...")

    # Step 3: Apply Q2S strategy
    q2s_plan_id, q2s_score = q2s_selection_strategy(q2s_matrix, alpha)
    if q2s_plan_id:
        if verbose:
            print(f"  Q2S strategy selected plan {q2s_plan_id} with score {q2s_score:.4f}")
        q2s_success, q2s_margins = evaluate_plan_under_perturbation(
            q2s_plan_id, valid_plans[q2s_plan_id], quality_goals, scenario, verbose
        )
        if verbose:
            print(f"    Success: {q2s_success}, Margins: {q2s_margins:.4f}")
    else:
        if verbose:
            print("  Q2S strategy could not select a plan")
        q2s_success, q2s_margins = 0, 0

    # Step 4: Apply AvgSat strategy
    avg_plan_id, avg_score = avg_only_strategy(q2s_matrix, verbose)
    if avg_plan_id:
        avg_success, avg_margins = evaluate_plan_under_perturbation(
            avg_plan_id, valid_plans[avg_plan_id], quality_goals, scenario, verbose
        )
        if verbose:
            print(f"    Success: {avg_success}, Margins: {avg_margins:.4f}")
    else:
        if verbose:
            print("  AvgSat strategy could not select a plan")
        avg_success, avg_margins = 0, 0

    # Step 5: Apply MinSat strategy
    min_plan_id, min_score = min_only_strategy(q2s_matrix, verbose)
    if min_plan_id:
        min_success, min_margins = evaluate_plan_under_perturbation(
            min_plan_id, valid_plans[min_plan_id], quality_goals, scenario, verbose
        )
        if verbose:
            print(f"    Success: {min_success}, Margins: {min_margins:.4f}")
    else:
        if verbose:
            print("  MinSat strategy could not select a plan")
        min_success, min_margins = 0, 0

    # Step 6: Apply Random strategy
    # Run multiple trials to get an average for random selection
    if verbose:
        print(f"  Running {NUM_RANDOM_RUNS} random selection trials...")

    random_successes = []
    random_margins = []

    for i in range(NUM_RANDOM_RUNS):  # Multiple random trials
        random_plan_id, _ = random_strategy(q2s_matrix, verbose and i == 0)  # Only verbose for first run
        if random_plan_id:
            success, margin = evaluate_plan_under_perturbation(
                random_plan_id, valid_plans[random_plan_id], quality_goals, scenario, verbose and i == 0
            )
            random_successes.append(success)
            random_margins.append(margin)

    random_success = sum(random_successes) / len(random_successes) if random_successes else 0
    random_margin = sum(random_margins) / len(random_margins) if random_margins else 0

    if verbose:
        print(f"  Random strategy average across {NUM_RANDOM_RUNS} runs: Success: {random_success:.4f}, Margins: {random_margin:.4f}")

    # Step 7: Compile results
    result = {
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

    # Write to file if specified
    if output_file:
        write_result_to_csv(result, output_file)
        if verbose:
            print(f"\nResult saved to {output_file}")

    if verbose:
        print("\nScenario processing complete!")
    else:
        print(f"Scenario {scenario_id} processed. Valid plans: {len(valid_plans)}")

    return result

def write_result_to_csv(result, output_file):
    """Helper function to write a single result to CSV file."""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

    # Define fieldnames for CSV
    fieldnames = [
        "id", "event_size", "organizers", "time", "budget",
        "perturbation_level_org", "perturbation_level_time", "perturbation_level_cost",
        "alpha", "Q2S_success", "Q2S_margins", "Avg_success", "Avg_margins",
        "Min_success", "Min_margins", "Random_success", "Random_margins",
        "num_valid_plans"
    ]

    # Write single result to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({k: v for k, v in result.items() if k in fieldnames})

# ---------------------------------------------------------------------------
# MAIN PROCESSING FUNCTION
# ---------------------------------------------------------------------------

def process_all_scenarios(input_file="data/exp1_scenarios.csv", output_file="data/exp1_results.csv"):
    """
    Process all scenarios from the input CSV file and write results to the output CSV file.
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

    # Load data from CSV files
    plans = load_plans("data/exp1_plans.csv")
    contributions = load_contributions("data/exp1_contributions.csv")
    base_quality_goals = load_quality_goals("data/exp1_quality_goals.csv")

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

    # Write all results to CSV
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

if __name__ == "__main__":
    print("Starting Q2S test with hardcoded scenario...")
    start_time = datetime.now()

    # Create hardcoded scenario
    hardcoded_scenario = {
        "id": 39,
        "event_size": "small",
        "organizers": 1,
        "time": 2,
        "budget": 100,
        "alpha": 0.5,
        "perturbation_level_org": "low_neg",
        "perturbation_level_time": "no",
        "perturbation_level_cost": "low_neg"
    }

    # Load data
    plans = load_plans("data/exp1_plans.csv")
    contributions = load_contributions("data/exp1_contributions.csv")
    base_quality_goals = load_quality_goals("data/exp1_quality_goals.csv")

    # Process the hardcoded scenario with verbose output
    result = process_scenario(
        hardcoded_scenario,
        plans,
        contributions,
        base_quality_goals,
        verbose=True,
        output_file="data/exp1_test_scenario_result.csv"
    )

    end_time = datetime.now()
    print(f"\nTest processing completed in {end_time - start_time}")
