import csv
import os
import itertools
from datetime import datetime

def generate_scenarios():
    """
    Generate scenarios for Q2S Experiment 1 with separate perturbation levels for each quality dimension.
    """
    # Define factor values
    event_size_options = ["small", "medium", "big"]
    organizers_options = [1, 2, 3]
    time_options = [2, 6, 14]  # days
    budget_options = [100, 200, 500]  # euros
    alpha_options = [0.3, 0.5, 0.7]  # alpha values for Q2S

    # Define perturbation levels for each quality dimension
    # pos = positive (improvement), no = no change, low_neg/high_neg = negative impacts
    perturbation_level_org = ["pos", "no", "low_neg", "high_neg"]
    perturbation_level_time = ["pos", "no", "low_neg", "high_neg"]
    perturbation_level_cost = ["pos", "no", "low_neg", "high_neg"]

    # Generate all combinations of factors
    all_combinations = list(itertools.product(
        event_size_options,
        organizers_options,
        time_options,
        budget_options,
        alpha_options,
        perturbation_level_org,
        perturbation_level_time,
        perturbation_level_cost
    ))

    print(f"Generated {len(all_combinations)} combinations of factors")

    # Create scenarios as rows for CSV
    # First create the headers
    headers = ["id", "event_size", "organizers", "time", "budget", "alpha",
               "perturbation_level_org", "perturbation_level_time", "perturbation_level_cost"]

    # Then create the rows
    rows = []
    for i, combo in enumerate(all_combinations):
        event_size, organizers, time, budget, alpha, pert_org, pert_time, pert_cost = combo

        # Create a row for CSV
        row = [
            i + 1,                # id
            event_size,           # event_size
            organizers,           # organizers
            time,                 # time
            budget,               # budget
            alpha,                # alpha
            pert_org,             # perturbation_level_org
            pert_time,            # perturbation_level_time
            pert_cost             # perturbation_level_cost
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
    print("Generating scenarios for Q2S Experiment 1...")
    headers, rows = generate_scenarios()

    # Create output directory
    os.makedirs("data", exist_ok=True)

    # Save all scenarios to a CSV file
    filename = os.path.join("data", "all_scenarios_upd.csv")
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
