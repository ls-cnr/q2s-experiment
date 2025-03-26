import csv
import os
import itertools
from datetime import datetime

def generate_scenarios():
    """
    Generate scenarios for Q2S Experiment 1 with direct quality constraints
    instead of indirect parameters like organizers and budget.
    """
    # Define factor values
    event_size_options = ["medium"]
    #event_size_options = ["small", "medium", "big"]

    # Sostituito organizers, time, budget con vincoli diretti
    cost_constraint_options = [340, 250, 200]  # euro
    effort_constraint_options = [14,12,10]  # unità di sforzo
    time_constraint_options = [13,11,9]  # giorni

    alpha_options = [0.3, 0.5, 0.7]  # alpha values for Q2S

    # Define perturbation levels for each quality dimension
    # pos = positive (improvement), no = no change, low_neg/high_neg = negative impacts
    perturbation_level_cost = ["pos", "no", "low_neg", "high_neg", "catastrofic"]
    perturbation_level_effort = ["pos", "no", "low_neg", "high_neg", "catastrofic"]
    perturbation_level_time = ["pos", "no", "low_neg", "high_neg", "catastrofic"]

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
    print("Generating scenarios for Q2S Experiment 1 with direct constraints...")
    headers, rows = generate_scenarios()

    # Create output directory
    os.makedirs("data", exist_ok=True)

    # Save all scenarios to a CSV file
    filename = os.path.join("data", "scenarios.csv")
    save_to_csv(headers, rows, filename)

    print("Scenario generation complete.")

    # Calculate and print the total number of scenarios
    total_combinations = len(rows)
    print(f"Total number of scenario combinations: {total_combinations}")

    # Check file size
    file_size_bytes = os.path.getsize(filename)
    file_size_mb = file_size_bytes / (1024 * 1024)
    print(f"CSV file size: {file_size_mb:.2f} MB")

if __name__ == "__main__":
    main()
