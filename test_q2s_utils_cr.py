#!/usr/bin/env python3
"""
Test script for Q2S utilities functions.
This script tests the functions for loading configuration, plans and contributions,
as well as the plan impact calculation, quality goals setting, and plan validity checking.
"""

import json
from q2s_utils import (
    load_json_config,
    load_plans,
    load_contributions,
    calculate_plan_impact,
    set_quality_goals_for_scenario,
    check_plan_validity
)

def main():
    print("Testing Q2S utility functions...\n")

    # Test loading configuration
    print("1. Testing load_json_config...")
    config_file = "data/cleaner_robot.json"
    config = load_json_config(config_file)
    if config is not None:
        print(f"Configuration loaded successfully: {config_file}")
        print(json.dumps(config, indent=2)[:500] + "...\n")  # Print first 500 chars of formatted JSON
    else:
        print(f"Failed to load configuration: {config_file}\n")

    # Test loading plans
    print("2. Testing load_plans...")
    plans_file = "data/exp1_cr_plans.csv"
    plans = load_plans(plans_file)
    if plans is not None:
        print(f"Plans loaded successfully: {plans_file}")
        print(f"Number of plans: {len(plans)}")
        # Print the first plan as an example
        first_plan_id = next(iter(plans))
        print(f"Example (first plan - {first_plan_id}):")
        print(json.dumps(plans[first_plan_id], indent=2) + "\n")
    else:
        print(f"Failed to load plans: {plans_file}\n")

    # Test loading contributions
    print("3. Testing load_contributions...")
    contributions_file = "data/exp1_cr_contributions.csv"
    contributions = load_contributions(contributions_file)
    if contributions is not None:
        print(f"Contributions loaded successfully: {contributions_file}")
        print(f"Number of domain variables: {len(contributions)}")
        # Print an example for the first domain variable
        if contributions:
            first_var = next(iter(contributions))
            print(f"Example (contributions for {first_var}):")
            print(json.dumps(contributions[first_var], indent=2) + "\n")
    else:
        print(f"Failed to load contributions: {contributions_file}\n")

    # Test calculating plan impact
    print("4. Testing calculate_plan_impact...")
    if plans is not None and contributions is not None:
        # Get the first plan for testing
        first_plan = plans[next(iter(plans))]

        # Calculate the impact
        impact = calculate_plan_impact(first_plan, contributions)

        print(f"Plan impact calculated for {first_plan['id']}:")
        print(json.dumps(impact, indent=2) + "\n")
    else:
        print("Skipping plan impact calculation due to missing plans or contributions\n")

    # Test setting quality goals for a scenario
    print("5. Testing set_quality_goals_for_scenario...")
    if config is not None:
        # Get quality goals definition and first constraint option
        quality_goals_def = config["quality_goals"]

        # Create a sample constraint options
        constraint_options = []
        for constraint in config["scenario_generator"]["constraint_options"]:
            constraint_options.append({
                "domain_variable": constraint["domain_variable"],
                "value": constraint["values"][0],  # Use the first value
                "perturbation": constraint["perturbation"][0]  # Use the first perturbation
            })

        # Set quality goals without perturbation
        print("Quality goals without perturbation:")
        qg_without_perturbation = set_quality_goals_for_scenario(quality_goals_def, constraint_options, False)
        print(json.dumps(qg_without_perturbation, indent=2))

        # Set quality goals with perturbation
        print("\nQuality goals with perturbation:")
        qg_with_perturbation = set_quality_goals_for_scenario(quality_goals_def, constraint_options, True)
        print(json.dumps(qg_with_perturbation, indent=2) + "\n")
    else:
        print("Skipping quality goals setting due to missing configuration\n")

    # Test checking plan validity
    print("6. Testing check_plan_validity...")
    if impact is not None and qg_without_perturbation is not None:
        # Check if the plan is valid
        is_valid = check_plan_validity(impact, qg_without_perturbation)

        print(f"Is plan {first_plan['id']} valid? {is_valid}\n")

        # Let's demonstrate an invalid scenario by creating a very strict constraint
        strict_qg = qg_without_perturbation.copy()
        # Find the TotalCost constraint and set it to a very low value
        for i, qg in enumerate(strict_qg):
            if qg["domain_variable"] == "TotalCost":
                strict_qg[i] = {**qg, "constraint": 10}  # Set a very low constraint

        is_valid_strict = check_plan_validity(impact, strict_qg)

        print(f"Is plan {first_plan['id']} valid with strict constraints? {is_valid_strict}\n")
    else:
        print("Skipping plan validity check due to missing impact or quality goals\n")

    print("Testing completed.")

if __name__ == "__main__":
    main()
