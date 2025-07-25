#!/usr/bin/env python3
"""
Q2S Experiment Simulator
This script simulates all scenario combinations based on a configuration file
and writes the results to a CSV file.
"""

import os
import sys
import csv
import json
import itertools
from q2s_utils import load_json_config
from exp1_scenario import process_scenario, get_constraint_options

def generate_all_scenarios(config):
    """
    Generate all possible scenario combinations based on the configuration.

    Args:
        config (dict): Configuration loaded from JSON

    Returns:
        list: List of scenario dictionaries
    """
    # Extract options from config
    alpha_options = config["scenario_generator"]["alpha_options"]
    constraint_options = config["scenario_generator"]["constraint_options"]

    # Prepare all combinations of constraint values and perturbations
    domain_variables = []
    domain_values = []
    domain_perturbations = []

    for constraint in constraint_options:
        domain_var = constraint["domain_variable"]
        domain_variables.append(domain_var)

        # Add all possible values for this constraint
        domain_values.append(constraint["values"])

        # Add all possible perturbation levels for this constraint
        domain_perturbations.append([p["value"] for p in constraint["perturbation"]])

    # Generate all combinations
    scenarios = []
    scenario_id = 1

    # Iterate through all combinations of alphas
    for alpha in alpha_options:
        # Iterate through all combinations of constraint values
        for values in itertools.product(*domain_values):
            # Iterate through all combinations of perturbation levels
            for perturbations in itertools.product(*domain_perturbations):
                # Create a new scenario
                scenario = {
                    "id": scenario_id,
                    "alpha": alpha
                }

                # Add constraint values
                for i, domain_var in enumerate(domain_variables):
                    scenario[domain_var] = values[i]

                # Add perturbation value
                perturbation_level = {}
                for i, domain_var in enumerate(domain_variables):
                    perturbation_level[domain_var] = str(perturbations[i])


                scenario["perturbation_level"] = perturbation_level

                scenarios.append(scenario)
                scenario_id += 1

    return scenarios

def simulate_all_scenarios(config_file):
    """
    Simulate all scenarios defined in the configuration file.

    Args:
        config_file (str): Path to the configuration file

    Returns:
        bool: True if simulation was successful, False otherwise
    """
    # Load configuration
    config = load_json_config(config_file)
    if config is None:
        print(f"Failed to load configuration from {config_file}")
        return False

    # Generate all possible scenarios
    print("Generating all possible scenarios...")
    scenarios = generate_all_scenarios(config)
    print(f"Generated {len(scenarios)} scenarios")

    # Create output directory if it doesn't exist
    output_dir = config["simulation_settings"]["output_directory"]
    os.makedirs(output_dir, exist_ok=True)

    # Prepare output file
    output_file = os.path.join(output_dir, config["simulation_settings"]["scenarios_filename"])

    # Process each scenario
    print(f"Processing scenarios and writing results to {output_file}...")

    # Get domain variables for CSV header
    domain_variables = [c["domain_variable"] for c in config["scenario_generator"]["constraint_options"]]

    # Create CSV file and write header
    with open(output_file, 'w', newline='') as csvfile:
        # Prepare CSV header
        header = ["ID", "alpha"]
        # Add constraint columns
        header.extend(domain_variables)
        # Add perturbation level columns
        header.extend([f"{var}_perturbation" for var in domain_variables])
        # Add results columns
        header.extend([
            "num_valid_plans",
            "ScorePlan_ID", "ScorePlan_success", "ScorePlan_margins",
            "AvgPlan_ID", "AvgPlan_success", "AvgPlan_margins",
            "MinPlan_ID", "MinPlan_success", "MinPlan_margins",
            "RndPlan_ID", "RndPlan_success", "RndPlan_margins"
        ])

        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()

        # Process each scenario
        total_scenarios = len(scenarios)
        for i, scenario in enumerate(scenarios):
            # Print progress
            if (i + 1) % 10 == 0 or (i + 1) == total_scenarios:
                print(f"Processing scenario {i + 1}/{total_scenarios}...")

            # Process scenario
            alpha = scenario["alpha"]
            results = process_scenario(config, scenario, alpha, verbose=False)

            if results is None:
                print(f"Failed to process scenario {scenario['id']}")
                continue

            # Prepare row for CSV
            row = {
                "ID": scenario["id"],
                "alpha": alpha
            }

            # Add constraint values
            for var in domain_variables:
                row[var] = scenario[var]

            # Add perturbation levels
            for var in domain_variables:
                row[f"{var}_perturbation"] = scenario["perturbation_level"][var]

            # Add results
            row["num_valid_plans"] = results["num_valid_plans"]
            row["ScorePlan_ID"] = results["ScorePlan_ID"]
            row["ScorePlan_success"] = 1 if results["ScorePlan_success"] else 0
            row["ScorePlan_margins"] = results["ScorePlan_margins"]
            row["AvgPlan_ID"] = results["AvgPlan_ID"]
            row["AvgPlan_success"] = 1 if results["AvgPlan_success"] else 0
            row["AvgPlan_margins"] = results["AvgPlan_margins"]
            row["MinPlan_ID"] = results["MinPlan_ID"]
            row["MinPlan_success"] = 1 if results["MinPlan_success"] else 0
            row["MinPlan_margins"] = results["MinPlan_margins"]
            row["RndPlan_ID"] = results["RndPlan_ID"]
            row["RndPlan_success"] = 1 if results["RndPlan_success"] else 0
            row["RndPlan_margins"] = results["RndPlan_margins"]

            # Write row to CSV
            writer.writerow(row)

    print(f"Simulation completed. Results written to {output_file}")
    return True

def main():
    """Main function to handle command line arguments and run the simulation."""
    if len(sys.argv) != 2:
        print("Usage: python exp1_simulator.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    print(f"Starting Q2S simulation with configuration from {config_file}")
    success = simulate_all_scenarios(config_file)

    if success:
        print("Simulation completed successfully.")
    else:
        print("Simulation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
