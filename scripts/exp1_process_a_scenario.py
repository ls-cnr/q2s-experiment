import os
import argparse
import sys
from datetime import datetime

from q2s_utils import (
    load_plans, load_contributions, get_quality_goals_mapping,
    load_json_config, get_file_paths, get_perturbation_values,
    get_simulation_settings
)

from exp1_scenario_processor import process_scenario

def process_a_scenario(scenario_id=39, config_file=None, verbose=True):
    """
    Process a single scenario from configuration file.

    Args:
        scenario_id: ID of the scenario to process (default: 39)
        config_file: Path to the configuration file (required)
        verbose: Whether to print detailed information

    Returns:
        Result dictionary from processing the scenario
    """
    if config_file is None:
        raise ValueError("Config file path is required")

    print(f"Starting Q2S test with scenario ID {scenario_id} using configuration from {config_file}...")
    start_time = datetime.now()

    # Load configuration
    config = load_json_config(config_file)
    if not config:
        print(f"Error: Could not load configuration from {config_file}")
        return None

    # Create scenario with the selected ID
    scenario = {
        "id": scenario_id,
        "event_size": "small",
        "cost_constraint": 210,
        "effort_constraint": 4,
        "time_constraint": 9,
        "alpha": 0.5,
        "perturbation_level_cost": "low_neg",
        "perturbation_level_effort": "low_neg",
        "perturbation_level_time": "low_neg"
    }

    print(f"Created test scenario with ID {scenario_id}")

    # Load data using paths from config
    file_paths = get_file_paths(config)
    if not file_paths:
        print("Error: Could not get file paths from configuration")
        return None

    plans_path = file_paths.get("plans")
    contributions_path = file_paths.get("contributions")

    if not plans_path:
        print("Error: Missing 'plans' path in configuration")
        return None

    if not contributions_path:
        print("Error: Missing 'contributions' path in configuration")
        return None

    print(f"Loading plans from: {plans_path}")
    plans = load_plans(plans_path)

    print(f"Loading contributions from: {contributions_path}")
    contributions = load_contributions(contributions_path)

    print(f"Loading quality goals from configuration")
    quality_goals_mapping = get_quality_goals_mapping(config)

    if not plans:
        print(f"Error: Failed to load plans from {plans_path}")
        return None

    if not contributions:
        print(f"Error: Failed to load contributions from {contributions_path}")
        return None

    if not quality_goals_mapping:
        print("Error: Failed to load quality goals mapping from configuration")
        return None

    # Get settings from config
    settings = get_simulation_settings(config)
    if not settings:
        print("Error: Could not get simulation settings from configuration")
        return None

    # Get perturbation values from config and inject them into the processor module
    perturbation_values = get_perturbation_values(config)
    if not perturbation_values:
        print("Error: Could not get perturbation values from configuration")
        return None

    num_random_runs = settings.get("num_random_runs")
    if not num_random_runs:
        print("Error: Missing 'num_random_runs' in simulation settings")
        return None

    import exp1_scenario_processor as processor
    processor.PERTURBATION_VALUE = perturbation_values
    processor.NUM_RANDOM_RUNS = num_random_runs

    print(f"Using perturbation values from configuration")
    print(f"Number of random runs: {num_random_runs}")

    # Process the scenario with verbose output, without file output
    result = process_scenario(
        scenario,
        plans,
        contributions,
        quality_goals_mapping,
        verbose=verbose,
        output_file=None
    )

    end_time = datetime.now()
    print(f"\nTest processing completed in {end_time - start_time}")

    return result

def main():
    """Main function to process a single test scenario from command line."""
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Process a single Q2S scenario')
    parser.add_argument('config_file', help='Path to the JSON configuration file')
    parser.add_argument('--id', type=int, default=39, help='Scenario ID to process (default: 39)')
    parser.add_argument('--quiet', action='store_true', help='Run in quiet mode (less verbose output)')
    args = parser.parse_args()

    config_file = args.config_file
    scenario_id = args.id
    verbose = not args.quiet

    # Check if the config file exists
    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' not found.")
        sys.exit(1)

    # Process the scenario
    result = process_a_scenario(scenario_id, config_file, verbose)

    if result is None:
        print("Error processing scenario.")
        sys.exit(1)

    # Print a summary of the result
    print("\nProcessing summary:")
    print(f"Scenario {scenario_id} - {result.get('num_valid_plans', 0)} valid plans")

    # Print strategy results if we have valid plans
    if result.get('num_valid_plans', 0) > 0:
        print("\nStrategy success rates:")
        print(f"Q2S: {result.get('Q2S_success', 0)*100:.1f}% (margin: {result.get('Q2S_margins', 0):.4f})")
        print(f"Avg: {result.get('Avg_success', 0)*100:.1f}% (margin: {result.get('Avg_margins', 0):.4f})")
        print(f"Min: {result.get('Min_success', 0)*100:.1f}% (margin: {result.get('Min_margins', 0):.4f})")
        print(f"Random: {result.get('Random_success', 0)*100:.1f}% (margin: {result.get('Random_margins', 0):.4f})")

if __name__ == "__main__":
    main()
