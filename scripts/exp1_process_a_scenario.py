import os
from datetime import datetime

from q2s_utils import (
    load_plans, load_contributions
)

from exp1_processor import (
    process_scenario
)

def print_result_summary(scenario_id, valid_plans_count, result, verbose=True):
    """Print summary of results."""
    if not verbose:
        return

    print("\nProcessing summary:")
    print(f"Scenario {scenario_id} - {valid_plans_count} valid plans")

    if valid_plans_count > 0:
        print("\nStrategy success rates:")
        print(f"Q2S: {result.get('Q2S_success', 0)*100:.1f}% (margin: {result.get('Q2S_margins', 0):.4f})")
        print(f"Avg: {result.get('Avg_success', 0)*100:.1f}% (margin: {result.get('Avg_margins', 0):.4f})")
        print(f"Min: {result.get('Min_success', 0)*100:.1f}% (margin: {result.get('Min_margins', 0):.4f})")
        print(f"Random: {result.get('Random_success', 0)*100:.1f}% (margin: {result.get('Random_margins', 0):.4f})")


def main():
    """Main function to process a single test scenario."""
    print("Starting Q2S test with hardcoded scenario...")
    start_time = datetime.now()

    # Create hardcoded scenario
    scenario = {
        "id": 39,
        "event_size": "medium",
        "cost_constraint": 270,
        "effort_constraint": 6,
        "time_constraint": 9,
        "alpha": 0.5,
        "perturbation_level_cost": "pos",
        "perturbation_level_effort": "low_neg",
        "perturbation_level_time": "no"
    }

    print(f"Created test scenario with ID {scenario['id']}")

    # Hardcoded file paths
    plans_path = "data/exp1_ms_plans.csv"
    contributions_path = "data/exp1_ms_contributions.csv"

    print(f"Loading plans from: {plans_path}")
    plans = load_plans(plans_path)

    print(f"Loading contributions from: {contributions_path}")
    contributions = load_contributions(contributions_path)

    # Hardcoded quality goals mapping
    quality_goals_mapping = {
        "QG0": "TotalCost",
        "QG1": "TotalEffort",
        "QG2": "TimeSpent"
    }

    # Define perturbation values
    perturbation_values = {
        "cost": {
            "pos": -20,
            "no": 0,
            "low_neg": 10,
            "high_neg": 75,
            "catastrofic": 100
        },
        "effort": {
            "pos": -1,
            "no": 0,
            "low_neg": 2,
            "high_neg": 4,
            "catastrofic": 6
        },
        "time": {
            "pos": -3,
            "no": 0,
            "low_neg": 2,
            "high_neg": 5,
            "catastrofic": 10
        }
    }

    if not plans:
        print(f"Error: Failed to load plans from {plans_path}")
        return

    if not contributions:
        print(f"Error: Failed to load contributions from {contributions_path}")
        return

    # Process the scenario with verbose output
    result = process_scenario(
        scenario,
        plans,
        contributions,
        quality_goals_mapping,
        perturbation_values,
        verbose=True
    )

    end_time = datetime.now()
    print(f"\nTest processing completed in {end_time - start_time}")

    # Print a summary of the result
    print_result_summary(
        scenario['id'],
        result.get('num_valid_plans', 0),
        result,
        verbose=True
    )

if __name__ == "__main__":
    main()
