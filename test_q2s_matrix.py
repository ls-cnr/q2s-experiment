#!/usr/bin/env python3
"""
Test script for Q2S matrix calculation and printing.
This script demonstrates how to calculate and display Q2S matrices.
"""

import json
from q2s_utils import (
    load_json_config,
    load_plans,
    load_contributions,
    calculate_plan_impact,
    set_quality_goals_for_scenario,
    check_plan_validity,
    filter_valid_plans
)
from q2s_matrix import (
    calculate_q2s_matrix,
    calculate_extended_q2s_matrix,
    q2s_selection_strategy_extended
)
from exp1_log import print_q2s_matrix, print_ext_q2s_matrix, print_plan_impacts, print_quality_goals

def main():
    print("Testing Q2S Matrix calculation and display...\n")

    # 1. Load configuration, plans, and contributions
    config_file = "data/meeting_scheduler.json"
    config = load_json_config(config_file)
    if config is None:
        print("Failed to load configuration. Exiting...")
        return

    plans_file = config["file_paths"]["plans"]
    plans = load_plans(plans_file)
    if plans is None:
        print(f"Failed to load plans from {plans_file}. Exiting...")
        return

    contributions_file = config["file_paths"]["contributions"]
    contributions = load_contributions(contributions_file)
    if contributions is None:
        print(f"Failed to load contributions from {contributions_file}. Exiting...")
        return

    print(f"Successfully loaded configuration, {len(plans)} plans, and contributions for {len(contributions)} domain variables.\n")

    # 2. Create a sample scenario
    alpha = 0.5  # Sample alpha value

    # Create sample constraint options
    constraint_options = []
    for constraint in config["scenario_generator"]["constraint_options"]:
        constraint_options.append({
            "domain_variable": constraint["domain_variable"],
            "value": constraint["values"][0],  # Use the first value
            "perturbation": constraint["perturbation"][0]  # Use the first perturbation
        })

    # Set quality goals for the scenario
    quality_goals = set_quality_goals_for_scenario(config["quality_goals"], constraint_options, False)
    print("Created quality goals for the scenario:\n")
    print_quality_goals(quality_goals)

    # 3. Calculate plan impacts and filter valid plans
    print(f"Calculating impact for {len(plans)} plans...")
    plan_impacts = {}
    for plan_id, plan in plans.items():
        impact = calculate_plan_impact(plan, contributions)
        plan_impacts[plan_id] = impact

    # Test the print_plan_impacts function
    print_plan_impacts(plan_impacts)


    # Filter valid plans
    valid_plans = filter_valid_plans(plans, plan_impacts, quality_goals)
    print(f"Found {len(valid_plans)} valid plans out of {len(plans)} total plans.\n")

    # 4. Calculate Q2S matrix
    print("Calculating Q2S matrix...")
    q2s_matrix = calculate_q2s_matrix(valid_plans, plan_impacts, quality_goals)

    # 5. Print the basic Q2S matrix
    print_q2s_matrix(q2s_matrix)

    # 6. Calculate extended Q2S matrix
    print("\nCalculating extended Q2S matrix...")
    q2s_matrix_extended = calculate_extended_q2s_matrix(q2s_matrix, alpha)

    # 7. Print the extended Q2S matrix
    print_ext_q2s_matrix(q2s_matrix_extended)

    # 8. Select the best plan
    best_plan = q2s_selection_strategy_extended(q2s_matrix_extended)
    print(f"\nSelected best plan using Q2S strategy with alpha={alpha}: {best_plan}")

    # 9. Print details of the best plan
    if best_plan:
        print("\nDetails of the selected plan:")
        print(f"  Plan ID: {best_plan}")
        print(f"  Goals: {', '.join([goal for goal, value in valid_plans[best_plan]['goals'].items() if value == 1])}")
        print(f"  Score: {q2s_matrix_extended['matrix'][best_plan]['Score']}")
        print(f"  AvgSat: {q2s_matrix_extended['matrix'][best_plan]['AvgSat']}")
        print(f"  MinSat: {q2s_matrix_extended['matrix'][best_plan]['MinSat']}")

    print("\nTesting completed.")

if __name__ == "__main__":
    main()
