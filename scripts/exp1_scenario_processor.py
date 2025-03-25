import csv
import os
import random
import numpy as np
from datetime import datetime
import pandas as pd

from q2s_utils import (
    load_plans, load_contributions, load_quality_goals_mapping,
    calculate_all_plan_impacts,
    check_plan_validity, filter_valid_plans,
    calculate_q2s_matrix, q2s_selection_strategy
)

# ---------------------------------------------------------------------------
# EXP1 SPECIFIC CONSTANTS
# ---------------------------------------------------------------------------

PERTURBATION_VALUE = {
    "effort": {  #
        "pos": -1,        # Miglioramento nello sforzo
        "no": 0,          # Nessun cambiamento
        "low_neg": 1,     # Piccolo impatto negativo sullo sforzo
        "high_neg": 2     # Grande impatto negativo sullo sforzo
    },
    "time": {
        "pos": -24,       # 1 giorno in meno (in ore)
        "no": 0,          # Nessun cambiamento
        "low_neg": 24,    # 1 giorno in più (in ore)
        "high_neg": 48    # 2 giorni in più (in ore)
    },
    "cost": {
        "pos": -50,       # 50 euro in meno
        "no": 0,          # Nessun cambiamento
        "low_neg": 50,    # 50 euro in più
        "high_neg": 100   # 100 euro in più
    }
}

# Number of simulation runs per scenario for random strategy
NUM_RANDOM_RUNS = 10

# ---------------------------------------------------------------------------
# PLAN SELECTION STRATEGIES (EXP1 SPECIFIC)
# ---------------------------------------------------------------------------

def avg_only_strategy(q2s_matrix, verbose=False):
    """
    Select plan using only the average satisfaction.
    """
    if not q2s_matrix:
        if verbose:
            print("  WARNING: Empty Q2S matrix passed to avg_only_strategy")
        return None, 0

    plan_scores = {}
    for plan_id, distances in q2s_matrix.items():
        distance_values = list(distances.values())
        if not distance_values:  # Skip if no distance values
            continue

        avg_sat = sum(distance_values) / len(distance_values)
        plan_scores[plan_id] = avg_sat

    # Return the plan with the highest average satisfaction
    if not plan_scores:  # Check if plan_scores is empty
        if verbose:
            print("  WARNING: No valid plan scores in avg_only_strategy")
        return None, 0

    best_plan_id = max(plan_scores, key=plan_scores.get)
    if verbose:
        print(f"  AvgSat strategy selected plan {best_plan_id} with score {plan_scores[best_plan_id]:.4f}")
    return best_plan_id, plan_scores[best_plan_id]

def min_only_strategy(q2s_matrix, verbose=False):
    """
    Select plan using only the minimum satisfaction.
    """
    if not q2s_matrix:
        if verbose:
            print("  WARNING: Empty Q2S matrix passed to min_only_strategy")
        return None, 0

    plan_scores = {}
    for plan_id, distances in q2s_matrix.items():
        distance_values = list(distances.values())
        if not distance_values:  # Skip if no distance values
            continue

        min_sat = min(distance_values)
        plan_scores[plan_id] = min_sat

    # Return the plan with the highest minimum satisfaction
    if not plan_scores:  # Check if plan_scores is empty
        if verbose:
            print("  WARNING: No valid plan scores in min_only_strategy")
        return None, 0

    best_plan_id = max(plan_scores, key=plan_scores.get)
    if verbose:
        print(f"  MinSat strategy selected plan {best_plan_id} with score {plan_scores[best_plan_id]:.4f}")
    return best_plan_id, plan_scores[best_plan_id]

def random_strategy(q2s_matrix, verbose=False):
    """
    Select a random plan from valid plans.
    """
    if not q2s_matrix:
        if verbose:
            print("  WARNING: Empty Q2S matrix passed to random_strategy")
        return None, 0

    plan_ids = list(q2s_matrix.keys())
    if not plan_ids:  # Check if no plans available
        if verbose:
            print("  WARNING: No valid plans in random_strategy")
        return None, 0

    plan_id = random.choice(plan_ids)
    distance_values = list(q2s_matrix[plan_id].values())
    if not distance_values:  # Check if no distance values
        if verbose:
            print(f"  Random strategy selected plan {plan_id} but no distance values found")
        return plan_id, 0

    avg_sat = sum(distance_values) / len(distance_values)
    if verbose:
        print(f"  Random strategy selected plan {plan_id} with avg score {avg_sat:.4f}")
    return plan_id, avg_sat

# ---------------------------------------------------------------------------
# PERTURBATION APPLICATION
# ---------------------------------------------------------------------------

def apply_perturbation(plan_impacts, scenario, verbose=False):
    """
    Apply perturbations based on scenario parameters.
    """
    # Deep copy the impacts to avoid modifying the original
    perturbed_impacts = dict(plan_impacts)

    # Get perturbation values for each dimension
    # Renamed from org to effort
    effort_perturbation = PERTURBATION_VALUE["effort"][scenario["perturbation_level_effort"]]
    time_perturbation = PERTURBATION_VALUE["time"][scenario["perturbation_level_time"]]
    cost_perturbation = PERTURBATION_VALUE["cost"][scenario["perturbation_level_cost"]]

    if verbose:
        print(f"  Applying perturbations: effort={effort_perturbation}, time={time_perturbation}, cost={cost_perturbation}")

    # Apply perturbations to domain variables
    for var in perturbed_impacts:
        original_value = perturbed_impacts[var]

        # Apply the appropriate perturbation based on domain variable type
        if "Cost" in var:  # Cost-related variable
            perturbed_impacts[var] += cost_perturbation
        elif "Time" in var:  # Time-related variable
            perturbed_impacts[var] += time_perturbation
        elif "Effort" in var:  # Effort-related variable
            # Apply as multiplier for effort (similar to previous implementation)
            if effort_perturbation != 0:
                perturbed_impacts[var] *= (1 + 0.15 * effort_perturbation)

        if verbose and perturbed_impacts[var] != original_value:
            print(f"    {var}: {original_value:.2f} -> {perturbed_impacts[var]:.2f}")

    return perturbed_impacts

def evaluate_plan_under_perturbation(plan_id, plan, quality_goals, scenario, verbose=False):
    """
    Evaluate a plan under perturbation.
    """
    if verbose:
        print(f"  Evaluating plan {plan_id} under perturbation...")

    # Apply perturbation to plan impacts
    perturbed_impacts = apply_perturbation(plan["impact"], scenario, verbose)

    # Check if perturbed plan still satisfies constraints
    valid = True
    margins = []

    for qg_id, goal in quality_goals.items():
        domain_var = goal["domain_variable"]
        if domain_var in perturbed_impacts:
            impact_value = perturbed_impacts[domain_var]

            if goal["type"] == "max":
                margin = (goal["max_value"] - impact_value) / goal["max_value"]
                margins.append(margin)
                if impact_value > goal["max_value"]:
                    valid = False
                    if verbose:
                        print(f"    {qg_id}: Constraint violated! {impact_value:.2f} > {goal['max_value']:.2f}")
                elif verbose:
                    print(f"    {qg_id}: Constraint satisfied. {impact_value:.2f} <= {goal['max_value']:.2f} (margin: {margin:.4f})")

    success_rate = 1 if valid else 0
    avg_margin = sum(margins) / len(margins) if margins else 0

    if verbose:
        print(f"    Plan is {'valid' if valid else 'invalid'} under perturbation")
        print(f"    Average margin: {avg_margin:.4f}")

    return success_rate, avg_margin

# ---------------------------------------------------------------------------
# SCENARIO PROCESSING
# ---------------------------------------------------------------------------

def process_scenario(scenario, plans, contributions, quality_goals_mapping, verbose=False, output_file=None):
    """
    Process a single scenario and evaluate different plan selection strategies.
    """
    # Extract scenario parameters
    scenario_id = scenario["id"]
    event_size = scenario["event_size"]
    cost_constraint = scenario["cost_constraint"]
    effort_constraint = scenario["effort_constraint"]
    time_constraint = scenario["time_constraint"]
    alpha = scenario["alpha"]
    perturbation_level_cost = scenario["perturbation_level_cost"]
    perturbation_level_effort = scenario["perturbation_level_effort"]
    perturbation_level_time = scenario["perturbation_level_time"]

    if verbose:
        print(f"\n\n===== PROCESSING SCENARIO {scenario_id} =====")
        print(f"Parameters: event_size={event_size}, " +
              f"cost_constraint={cost_constraint}, effort_constraint={effort_constraint}, " +
              f"time_constraint={time_constraint}, alpha={alpha}")
        print(f"Perturbations: cost={perturbation_level_cost}, " +
              f"effort={perturbation_level_effort}, time={perturbation_level_time}")
    else:
        print(f"Processing scenario {scenario_id}...")

    # Calculate impacts for all plans
    if verbose:
        print("\nCalculating plan impacts...")
    all_plan_impacts = calculate_all_plan_impacts(plans, contributions)

    # Print plan impacts details if verbose
    if verbose:
        print("\nAll Plan Impacts:")

        # Ottieni tutte le variabili di dominio uniche
        all_domain_vars = set()
        for impacts in all_plan_impacts.values():
            all_domain_vars.update(impacts.keys())
        all_domain_vars = sorted(list(all_domain_vars))

        # Calcola le larghezze delle colonne
        plan_id_width = 10
        var_width = 12
        total_width = plan_id_width + (var_width + 3) * len(all_domain_vars)

        # Stampa la riga di intestazione
        print("+" + "-" * (plan_id_width + 2) + "+" + "+".join(["-" * (var_width + 2) for _ in all_domain_vars]) + "+")

        # Stampa i nomi delle colonne
        header = f"| {'Plan ID':<{plan_id_width}} |"
        for var in all_domain_vars:
            header += f" {var:<{var_width}} |"
        print(header)

        # Stampa la linea separatrice
        print("+" + "-" * (plan_id_width + 2) + "+" + "+".join(["-" * (var_width + 2) for _ in all_domain_vars]) + "+")

        # Stampa i dati per ogni piano
        for plan_id, impacts in all_plan_impacts.items():
            row = f"| {plan_id:<{plan_id_width}} |"
            for var in all_domain_vars:
                impact = impacts.get(var, 0)
                row += f" {impact:<{var_width}.2f} |"
            print(row)

        # Stampa la riga finale
        print("+" + "-" * (plan_id_width + 2) + "+" + "+".join(["-" * (var_width + 2) for _ in all_domain_vars]) + "+")

        print(f"\nCalculated impacts for {len(all_plan_impacts)} plans")

    # Step 1: Calculate quality goals and filter valid plans
    valid_plans, quality_goals = filter_valid_plans(
        scenario, all_plan_impacts, quality_goals_mapping, None
    )

    # Print quality goals if verbose
    if verbose:
        print("\nAdjusted Quality Goals for this scenario:")
        for qg_id, goal in quality_goals.items():
            print(f"  {qg_id}: {goal['domain_variable']} ≤ {goal['max_value']}")

        print(f"\nFiltered down to {len(valid_plans)} valid plans")
        if valid_plans:
            print("Valid Plans:")
            for plan_id in list(valid_plans.keys())[:10]:  # Show first 10 plans
                print(f"  {plan_id}")
            if len(valid_plans) > 10:
                print(f"  ... and {len(valid_plans) - 10} more plans")

    # If no valid plans, return failed results
    if not valid_plans:
        if verbose:
            print(f"No valid plans for scenario {scenario_id} - aborting")
        else:
            print(f"No valid plans for scenario {scenario_id}")

        result = {
            "id": scenario_id,
            "event_size": event_size,
            "cost_constraint": cost_constraint,
            "effort_constraint": effort_constraint,
            "time_constraint": time_constraint,
            "perturbation_level_cost": perturbation_level_cost,
            "perturbation_level_effort": perturbation_level_effort,
            "perturbation_level_time": perturbation_level_time,
            "alpha": alpha,
            "Q2S_success": 0,
            "Q2S_margins": 0,
            "Avg_success": 0,
            "Avg_margins": 0,
            "Min_success": 0,
            "Min_margins": 0,
            "Random_success": 0,
            "Random_margins": 0,
            "num_valid_plans": 0
        }

        # Write to file if specified
        if output_file:
            write_result_to_csv(result, output_file)
            if verbose:
                print(f"\nFailed result saved to {output_file}")

        return result

    # Step 2: Calculate Q2S matrix
    if verbose:
        print("\nCalculating Q2S matrix...")

    q2s_matrix = calculate_q2s_matrix(valid_plans, quality_goals)

    if verbose:
        print(f"\nQ2S Matrix has {len(q2s_matrix)} plans")
        if q2s_matrix:
            print("\nQ2S Matrix:")

            # Raccogli tutti i quality goal IDs unici
            all_qg_ids = set()
            for distances in q2s_matrix.values():
                all_qg_ids.update(distances.keys())
            all_qg_ids = sorted(list(all_qg_ids))

            # Calcola le larghezze delle colonne
            plan_id_width = 10
            qg_width = 10
            stat_width = 10

            # Stampa la riga di intestazione superiore
            print("+" + "-" * (plan_id_width + 2) + "+" +
                "+".join(["-" * (qg_width + 2) for _ in all_qg_ids]) + "+" +
                "+".join(["-" * (stat_width + 2) for _ in range(3)]) + "+")

            # Stampa i nomi delle colonne
            header = f"| {'Plan ID':<{plan_id_width}} |"
            for qg_id in all_qg_ids:
                header += f" {qg_id:<{qg_width}} |"
            header += f" {'Avg':<{stat_width}} | {'Min':<{stat_width}} | {'Score':<{stat_width}} |"
            print(header)

            # Stampa la linea separatrice
            print("+" + "-" * (plan_id_width + 2) + "+" +
                "+".join(["-" * (qg_width + 2) for _ in all_qg_ids]) + "+" +
                "+".join(["-" * (stat_width + 2) for _ in range(3)]) + "+")

            # Stampa i dati per ogni piano, aggiungendo le colonne statistiche
            for plan_id, distances in q2s_matrix.items():
                row = f"| {plan_id:<{plan_id_width}} |"

                # Aggiungi ogni quality goal
                distance_values = []
                for qg_id in all_qg_ids:
                    distance = distances.get(qg_id, float('nan'))
                    if not np.isnan(distance):
                        row += f" {distance:<{qg_width}.4f} |"
                        distance_values.append(distance)
                    else:
                        row += f" {'N/A':<{qg_width}} |"

                # Calcola e aggiungi Avg, Min e Score
                if distance_values:
                    avg_sat = sum(distance_values) / len(distance_values)
                    min_sat = min(distance_values)
                    score = scenario["alpha"] * avg_sat + (1 - scenario["alpha"]) * min_sat

                    row += f" {avg_sat:<{stat_width}.4f} | {min_sat:<{stat_width}.4f} | {score:<{stat_width}.4f} |"
                else:
                    row += f" {'N/A':<{stat_width}} | {'N/A':<{stat_width}} | {'N/A':<{stat_width}} |"

                print(row)

            # Stampa la riga finale
            print("+" + "-" * (plan_id_width + 2) + "+" +
                "+".join(["-" * (qg_width + 2) for _ in all_qg_ids]) + "+" +
                "+".join(["-" * (stat_width + 2) for _ in range(3)]) + "+")

            # Aggiungi legenda per il calcolo dello Score
            #print(f"\nScore = α * Avg + (1-α) * Min, where α = {scenario['alpha']}")

    # Check if matrix is empty
    if not q2s_matrix:
        if verbose:
            print("WARNING: Q2S matrix is empty! Check domain variables in quality goals match variables in contributions.")
            print("\nExpected domain variables from quality goals:")
            expected_vars = [goal["domain_variable"] for goal in quality_goals.values()]
            print(f"  {expected_vars}")
            print("\nAvailable variables in plan impacts:")
            if all_plan_impacts:
                first_plan = next(iter(all_plan_impacts.values()))
                print(f"  {list(first_plan.keys())}")
            else:
                print("  No plan impacts available")

        result = {
            "id": scenario_id,
            "event_size": event_size,
            "cost_constraint": cost_constraint,
            "effort_constraint": effort_constraint,
            "time_constraint": time_constraint,
            "perturbation_level_cost": perturbation_level_cost,
            "perturbation_level_effort": perturbation_level_effort,
            "perturbation_level_time": perturbation_level_time,
            "alpha": alpha,
            "Q2S_success": 0,
            "Q2S_margins": 0,
            "Avg_success": 0,
            "Avg_margins": 0,
            "Min_success": 0,
            "Min_margins": 0,
            "Random_success": 0,
            "Random_margins": 0,
            "num_valid_plans": len(valid_plans)
        }

        # Write to file if specified
        if output_file:
            write_result_to_csv(result, output_file)
            if verbose:
                print(f"\nFailed result saved to {output_file}")

        return result

    # Apply strategies
    if verbose:
        print("\nApplying selection strategies...")
        # Intestazione tabella
        print("\n┌─────────────┬──────────────┬─────────┬────────────┬────────────┐")
        print("│ Strategy    │ Selected Plan │ Score   │ Success    │ Margin     │")
        print("├─────────────┼──────────────┼─────────┼────────────┼────────────┤")

    # Step 3: Apply Q2S strategy
    q2s_plan_id, q2s_score = q2s_selection_strategy(q2s_matrix, alpha)
    if q2s_plan_id:
        q2s_success, q2s_margins = evaluate_plan_under_perturbation(
            q2s_plan_id, valid_plans[q2s_plan_id], quality_goals, scenario, verbose and False  # Non visualizzare dettagli interni
        )
        if verbose:
            print(f"│ Q2S         │ {q2s_plan_id:<12} │ {q2s_score:.4f} │ {q2s_success:<10} │ {q2s_margins:.4f}    │")
    else:
        if verbose:
            print("│ Q2S         │ None         │ 0.0000  │ 0          │ 0.0000     │")
        q2s_success, q2s_margins = 0, 0

    # Step 4: Apply AvgSat strategy
    avg_plan_id, avg_score = avg_only_strategy(q2s_matrix, verbose and False)
    if avg_plan_id:
        avg_success, avg_margins = evaluate_plan_under_perturbation(
            avg_plan_id, valid_plans[avg_plan_id], quality_goals, scenario, verbose and False
        )
        if verbose:
            print(f"│ AvgSat      │ {avg_plan_id:<12} │ {avg_score:.4f} │ {avg_success:<10} │ {avg_margins:.4f}    │")
    else:
        if verbose:
            print("│ AvgSat      │ None         │ 0.0000  │ 0          │ 0.0000     │")
        avg_success, avg_margins = 0, 0

    # Step 5: Apply MinSat strategy
    min_plan_id, min_score = min_only_strategy(q2s_matrix, verbose and False)
    if min_plan_id:
        min_success, min_margins = evaluate_plan_under_perturbation(
            min_plan_id, valid_plans[min_plan_id], quality_goals, scenario, verbose and False
        )
        if verbose:
            print(f"│ MinSat      │ {min_plan_id:<12} │ {min_score:.4f} │ {min_success:<10} │ {min_margins:.4f}    │")
    else:
        if verbose:
            print("│ MinSat      │ None         │ 0.0000  │ 0          │ 0.0000     │")
        min_success, min_margins = 0, 0

    # Step 6: Apply Random strategy
    # Run multiple trials to get an average for random selection
    random_successes = []
    random_margins = []

    for i in range(NUM_RANDOM_RUNS):  # Multiple random trials
        random_plan_id, _ = random_strategy(q2s_matrix, verbose and False)  # Nessun output verboso per i trial random
        if random_plan_id:
            success, margin = evaluate_plan_under_perturbation(
                random_plan_id, valid_plans[random_plan_id], quality_goals, scenario, verbose and False
            )
            random_successes.append(success)
            random_margins.append(margin)

    random_success = sum(random_successes) / len(random_successes) if random_successes else 0
    random_margin = sum(random_margins) / len(random_margins) if random_margins else 0

    if verbose:
        # Per la strategia Random, mostriamo solo i risultati medi, non un piano specifico
        print(f"│ Random      │ (avg {NUM_RANDOM_RUNS} runs) │ N/A     │ {random_success:.4f}    │ {random_margin:.4f}    │")
        print("└─────────────┴──────────────┴─────────┴────────────┴────────────┘")

    # Step 7: Compile results
    result = {
        "id": scenario_id,
        "event_size": event_size,
        "cost_constraint": cost_constraint,
        "effort_constraint": effort_constraint,
        "time_constraint": time_constraint,
        "perturbation_level_cost": perturbation_level_cost,
        "perturbation_level_effort": perturbation_level_effort,
        "perturbation_level_time": perturbation_level_time,
        "alpha": alpha,
        "Q2S_success": q2s_success,
        "Q2S_margins": q2s_margins,
        "Avg_success": avg_success,
        "Avg_margins": avg_margins,
        "Min_success": min_success,
        "Min_margins": min_margins,
        "Random_success": random_success,
        "Random_margins": random_margin,
        "num_valid_plans": len(valid_plans),
        "selected_plans": {
            "Q2S": q2s_plan_id,
            "Avg": avg_plan_id,
            "Min": min_plan_id
        }
    }

    # Write to file if specified
    if output_file:
        write_result_to_csv(result, output_file)
        if verbose:
            print(f"\nResult saved to {output_file}")

    if verbose:
        print("\nScenario processing complete!")
    else:
        print(f"Scenario {scenario_id} processed. Valid plans: {len(valid_plans)}")

    return result

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

def test_processor():
    print("Starting Q2S test with hardcoded scenario...")
    start_time = datetime.now()

    # Create hardcoded scenario with the new format
    hardcoded_scenario = {
        "id": 39,
        "event_size": "small",
        "cost_constraint": 200,
        "effort_constraint": 4,
        "time_constraint": 6,
        "alpha": 0.5,
        "perturbation_level_cost": "low_neg",
        "perturbation_level_effort": "low_neg",
        "perturbation_level_time": "no"
    }

    # Load data
    plans = load_plans("data/exp1_plans.csv")
    contributions = load_contributions("data/exp1_contributions.csv")
    quality_goals_mapping = load_quality_goals_mapping("data/exp1_quality_goals.csv")

    # Process the hardcoded scenario with verbose output
    result = process_scenario(
        hardcoded_scenario,
        plans,
        contributions,
        quality_goals_mapping,
        verbose=True,
        output_file="data/exp1_test_scenario_result.csv"
    )

    end_time = datetime.now()
    print(f"\nTest processing completed in {end_time - start_time}")

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
