import csv
import os
import random
import numpy as np
from datetime import datetime
import pandas as pd

from q2s_utils import (
    load_plans, load_contributions, get_quality_goals_mapping,
    calculate_all_plan_impacts,
    check_plan_validity, filter_valid_plans,
    calculate_q2s_matrix, q2s_selection_strategy
)

import exp1_utils

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
def process_all_scenarios(input_file="data/scenarios.csv", output_file="data/results.csv"):
    """
    Process all scenarios from the input CSV file and write results to the output CSV file.
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

    # Load data from CSV files
    plans = load_plans("data/exp1_plans.csv")
    contributions = load_contributions("data/exp1_contributions.csv")
    quality_goals_mapping = load_quality_goals_mapping("data/exp1_quality_goals.csv")

    if not plans or not contributions or not quality_goals_mapping:
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
                "cost_constraint": int(row["cost_constraint"]),
                "effort_constraint": int(row["effort_constraint"]),
                "time_constraint": int(row["time_constraint"]),
                "alpha": float(row["alpha"]),
                "perturbation_level_cost": row["perturbation_level_cost"],
                "perturbation_level_effort": row["perturbation_level_effort"],
                "perturbation_level_time": row["perturbation_level_time"]
            }
            scenarios.append(scenario)

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
        progress = (i / total_scenarios) * 100
        progress_bar = "#" * int(progress / 2) + "-" * (50 - int(progress / 2))
        print(f"\r[{progress_bar}] {progress:.1f}% - Processing scenario {scenario['id']} ({i+1}/{total_scenarios})", end="")

        # Process the scenario
        scenario_results = process_scenario(scenario, plans, contributions, quality_goals_mapping)
        results.append(scenario_results)

        # Write to CSV after each scenario (in case of interruption)
        with open(output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow({k: v for k, v in scenario_results.items() if k in fieldnames})

    print("\r" + " " * 80)  # Clear progress line
    print("=" * 50)
    print(f"Processing complete! Results saved to {output_file}")

    return results

def execute_processor():
    print("Starting Q2S experiment: processing all scenarios...")
    start_time = datetime.now()

    # Definisci i percorsi di input e output
    input_file = "data/scenarios.csv"
    output_file = "data/exp1_results.csv"

    # Verifica se il file di input esiste
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        print("Creating a test scenario file instead...")

        # Se il file di input non esiste, crea un file di test con alcuni scenari
        with open(input_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "event_size", "organizers", "time", "budget", "alpha",
                            "perturbation_level_org", "perturbation_level_time", "perturbation_level_cost"])
            # Aggiungi alcuni scenari di test
            writer.writerow([1, "small", 1, 2, 100, 0.3, "pos", "no", "low_neg"])
            writer.writerow([2, "small", 1, 2, 100, 0.5, "no", "no", "no"])
            writer.writerow([3, "medium", 2, 6, 200, 0.5, "low_neg", "low_neg", "low_neg"])
            writer.writerow([4, "big", 3, 14, 500, 0.7, "high_neg", "high_neg", "high_neg"])

    # Esegui l'elaborazione di tutti gli scenari
    results = process_all_scenarios(input_file, output_file)

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    print(f"\nQ2S experiment completed in {elapsed_time}")
    print(f"Processed {len(results)} scenarios")
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    #test_processor()
    execute_processor()
