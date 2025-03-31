import csv
import os
import sys
import itertools
import argparse
from datetime import datetime
from q2s_utils import (
    get_scenario_generator_options,
    get_simulation_settings,
    load_json_config
)

def generate_scenarios(config_file):
    """
    Generate scenarios for Q2S Experiment 1 with direct quality constraints
    instead of indirect parameters like organizers and budget.

    Args:
        config_file: Path to the configuration file.
    """
    # Load options from config file
    options = get_scenario_generator_options(config_file=config_file)

    if options is None:
        print("Error: No options found in configuration file.")
        return None

    # Extract options
    event_size_options = options.get("event_size_options", ["medium"])
    cost_constraint_options = options.get("cost_constraint_options", [200])
    effort_constraint_options = options.get("effort_constraint_options", [3])
    time_constraint_options = options.get("time_constraint_options", [6])
    alpha_options = options.get("alpha_options", [0.5])
    perturbation_level_cost = options.get("perturbation_level_cost", ["no", "low_neg"])
    perturbation_level_effort = options.get("perturbation_level_effort", ["no", "low_neg"])
    perturbation_level_time = options.get("perturbation_level_time", ["no", "low_neg"])

    # Generate all combinations of factors
    all_combinations = list(itertools.product(
        event_size_options,
        cost_constraint_options,
        effort_constraint_options,
        time_constraint_options,
        alpha_options,
        perturbation_level_cost,
        perturbation_level_effort,
        perturbation_level_time
    ))

    print(f"Generated {len(all_combinations)} combinations of factors")

    # Create scenarios as rows for CSV
    # First create the headers
    headers = ["id", "event_size", "cost_constraint", "effort_constraint", "time_constraint", "alpha",
               "perturbation_level_cost", "perturbation_level_effort", "perturbation_level_time"]

    # Then create the rows
    rows = []
    for i, combo in enumerate(all_combinations):
        event_size, cost_constraint, effort_constraint, time_constraint, alpha, pert_cost, pert_effort, pert_time = combo

        # Create a row for CSV
        row = [
            i + 1,                # id
            event_size,           # event_size
            cost_constraint,      # cost_constraint
            effort_constraint,    # effort_constraint
            time_constraint,      # time_constraint
            alpha,                # alpha
            pert_cost,            # perturbation_level_cost
            pert_effort,          # perturbation_level_effort
            pert_time             # perturbation_level_time
        ]

        rows.append(row)

    return headers, rows

def save_to_csv(headers, rows, filename=None):
    """Save scenarios to a CSV file."""
    if filename is None:
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"q2s_scenarios_{timestamp}.csv"

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

    # Save to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"Saved {len(rows)} scenarios to {filename}")
    return filename

def main():
    """Main function to generate and save scenarios."""
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Generate scenarios for Q2S experiment')
    parser.add_argument('config_file', help='Path to the JSON configuration file')
    args = parser.parse_args()

    config_file = args.config_file

    # Check if the config file exists
    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' not found.")
        sys.exit(1)

    print(f"Using configuration from: {config_file}")

    # Verify we can load the JSON
    try:
        config = load_json_config(config_file)
        if not config:
            print(f"Error: Configuration file '{config_file}' is empty or invalid.")
            sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration file: {e}")
        sys.exit(1)

    print("Generating scenarios for Q2S Experiment 1 with direct constraints...")

    if not config:
        print("Error: No configuration found.")
        sys.exit(1)

    # Generate scenarios using config
    headers, rows = generate_scenarios(config_file)

    # Get output settings from config
    settings = get_simulation_settings(config_file=config_file)

    # Extract output directory and filename
    output_dir = settings.get("output_directory", "data")
    scenarios_filename = settings.get("scenarios_filename", "scenarios.csv")

    print(f"Output directory: {output_dir}")
    print(f"Scenarios filename: {scenarios_filename}")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Save all scenarios to a CSV file
    output_path = os.path.join(output_dir, scenarios_filename)
    save_to_csv(headers, rows, output_path)

    print(f"Scenario generation complete. Saved to {output_path}")

    # Calculate and print the total number of scenarios
    total_combinations = len(rows)
    print(f"Total number of scenario combinations: {total_combinations}")

    # Check file size
    file_size_bytes = os.path.getsize(output_path)
    file_size_mb = file_size_bytes / (1024 * 1024)
    print(f"CSV file size: {file_size_mb:.2f} MB")

if __name__ == "__main__":
    main()
