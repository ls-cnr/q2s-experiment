#!/usr/bin/env python3
"""
Test script for the Q2S scenario processing function.
This script tests the scenario processing functionality with a specific scenario.
"""

import json
from q2s_utils import load_json_config
from exp1_scenario import process_scenario, get_constraint_options

def main():
    print("Testing scenario processing...\n")

    # 1. Load configuration
    config_file = "data/meeting_scheduler.json"
    config = load_json_config(config_file)
    if config is None:
        print("Failed to load configuration. Exiting...")
        return

    # 2. Define test scenario
    test_scenario = {
        "cost_constraint": 270,
        "effort_constraint": 6,
        "time_constraint": 9,
        "perturbation_level": {
            "cost_constraint": -10,
            "effort_constraint": 0,
            "time_constraint": 3
        },
        "alpha": 0.5
    }

    # 3. Print scenario details
    print("Test Scenario:")
    print(json.dumps(test_scenario, indent=2))
    print("\n" + "-"*80)

    # 4. Get constraint options for the scenario
    constraint_options = get_constraint_options(test_scenario)
    print("\nGenerated Constraint Options:")
    print(json.dumps(constraint_options, indent=2))
    print("\n" + "-"*80)

    # 5. Process the scenario
    print("\nProcessing scenario...")
    alpha = test_scenario.get("alpha", 0.5)
    results = process_scenario(config, test_scenario, alpha, verbose=True)

    # 6. Print results
    if results:
        print("\n" + "="*80)
        print("Scenario Processing Results:")
        print("="*80)
        print(json.dumps(results, indent=2))

        # 7. Print summary
        print("\nSummary:")
        print(f"  Total valid plans: {results['num_valid_plans']}")
        print("\nStrategy success rates:")
        print(f"  Q2S (Score) strategy: {results['ScorePlan_success']} (margins: {results['ScorePlan_margins']:.4f})")
        print(f"  AvgSat strategy: {results['AvgPlan_success']} (margins: {results['AvgPlan_margins']:.4f})")
        print(f"  MinSat strategy: {results['MinPlan_success']} (margins: {results['MinPlan_margins']:.4f})")
        print(f"  Random strategy: {results['RndPlan_success']} (margins: {results['RndPlan_margins']:.4f})")
    else:
        print("\nNo results returned from scenario processing.")

    print("\nTesting completed.")

if __name__ == "__main__":
    main()
