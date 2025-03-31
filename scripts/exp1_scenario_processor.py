import csv
import os
import sys
import argparse
from datetime import datetime

# Import utility functions from existing modules
from q2s_utils import (
    load_json_config, load_plans, load_contributions,
    get_file_paths, get_quality_goals_mapping, get_perturbation_values,
    get_simulation_settings, calculate_all_plan_impacts,
    create_quality_goals_from_scenario, calculate_q2s_matrix
)

# Import processing functions
from exp1_processor import process_scenario

def write_result_to_csv(result, output_file):
    """Helper function to write a single result to CSV file."""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

    # Define fieldnames for CSV
    fieldnames = [
        "id", "event_size", "cost_constraint", "effort_constraint", "time_constraint",
        "perturbation_level_cost", "perturbation_level_effort", "perturbation_level_time",
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
def process_all_scenarios(config_file):
    """
    Process all scenarios based on configuration.

    Args:
        config_file: Path to the configuration file.
    """
    # Load the configuration
    config = load_json_config(config_file)
    if not config:
        print(f"Error: Failed to load configuration from {config_file}")
        return []

    # Get file paths
    file_paths = get_file_paths(config=config)
    if not file_paths:
        print("Error: No file paths found in configuration")
        return []

    # Get simulation settings
    simulation_settings = get_simulation_settings(config=config)
    if not simulation_settings:
        print("Warning: No simulation settings found in configuration, using defaults")
        simulation_settings = {
            "output_directory": "data",
            "scenarios_filename": "scenarios.csv",
            "results_filename": "exp1_results.csv"
        }

    # Get perturbation values
    perturbation_values = get_perturbation_values(config=config)
    if not perturbation_values:
        print("Error: No perturbation values found in configuration")
        return []

    # Get quality goals mapping
    quality_goals_mapping = get_quality_goals_mapping(config=config)
    if not quality_goals_mapping:
        print("Error: No quality goals mapping found in configuration")
        return []

    # Convert the simple mapping to the format expected by process_scenario
    qg_mapping = {}
    for qg_id, domain_var in quality_goals_mapping.items():
        qg_mapping[qg_id] = {"name": qg_id, "domain_variable": domain_var}

    # Setup input and output files
    output_dir = simulation_settings.get("output_directory", "data")
    scenarios_filename = simulation_settings.get("scenarios_filename", "scenarios.csv")
    results_filename = simulation_settings.get("results_filename", "exp1_results.csv")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Full paths for input and output files
    input_file = os.path.join(output_dir, scenarios_filename)
    output_file = os.path.join(output_dir, results_filename)

    print(f"Input scenarios file: {input_file}")
    print(f"Output results file: {output_file}")

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found")
        print("Run scenario generator first to create the scenarios file")
        return []

    # Load plans and contributions
    plans_file = file_paths.get("plans")
    contributions_file = file_paths.get("contributions")

    print(f"Loading plans from: {plans_file}")
    plans = load_plans(file_path=plans_file)
    if not plans:
        print(f"Error: Failed to load plans from {plans_file}")
        return []

    print(f"Loading contributions from: {contributions_file}")
    contributions = load_contributions(file_path=contributions_file)
    if not contributions:
        print(f"Error: Failed to load contributions from {contributions_file}")
        return []

    # Read scenarios from CSV
    scenarios = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                scenario = {
                    "id": int(row["id"]),
                    "event_size": row["event_size"],
                    "cost_constraint": float(row["cost_constraint"]),
                    "effort_constraint": float(row["effort_constraint"]),
                    "time_constraint": float(row["time_constraint"]),
                    "alpha": float(row["alpha"]),
                    "perturbation_level_cost": row["perturbation_level_cost"],
                    "perturbation_level_effort": row["perturbation_level_effort"],
                    "perturbation_level_time": row["perturbation_level_time"]
                }
                scenarios.append(scenario)
    except Exception as e:
        print(f"Error reading scenarios from {input_file}: {e}")
        return []

    print(f"Loaded {len(scenarios)} scenarios from {input_file}")

    # Prepare CSV file with header
    fieldnames = [
        "id", "event_size", "cost_constraint", "effort_constraint", "time_constraint",
        "perturbation_level_cost", "perturbation_level_effort", "perturbation_level_time",
        "alpha", "Q2S_success", "Q2S_margins", "Avg_success", "Avg_margins",
        "Min_success", "Min_margins", "Random_success", "Random_margins",
        "num_valid_plans"
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    # Process each scenario with progress reporting
    results = []
    total_scenarios = len(scenarios)

    print(f"\nProcessing {total_scenarios} scenarios...")
    print("=" * 50)

    for i, scenario in enumerate(scenarios):
        # Calculate and display progress
        #progress = (i / total_scenarios) * 100
        #progress_bar = "#" * int(progress / 2) + "-" * (50 - int(progress / 2))
        #print(f"\r[{progress_bar}] {progress:.1f}% - Processing scenario {scenario['id']} ({i+1}/{total_scenarios})", end="")

        if i==1:
            # Process the scenario
            scenario_results = process_scenario(
                scenario,
                plans,
                contributions,
                qg_mapping,
                perturbation_values,
                verbose=False
            )

            results.append(scenario_results)

            # Write to CSV after each scenario (in case of interruption)
            with open(output_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow({k: v for k, v in scenario_results.items() if k in fieldnames})

    #print("\r" + " " * 80)  # Clear progress line
    #print("=" * 50)
    print(f"Processing complete! Results saved to {output_file}")

    return results

def main():
    """Main function to process scenarios."""
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Process scenarios for Q2S experiment')
    parser.add_argument('config_file', help='Path to the JSON configuration file')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    config_file = args.config_file

    # Check if the config file exists
    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' not found.")
        sys.exit(1)

    print(f"Using configuration from: {config_file}")

    print("Starting Q2S experiment: processing all scenarios...")
    start_time = datetime.now()

    # Process all scenarios using the configuration file
    results = process_all_scenarios(config_file)

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    print(f"\nQ2S experiment completed in {elapsed_time}")
    print(f"Processed {len(results)} scenarios")

if __name__ == "__main__":
    main()
