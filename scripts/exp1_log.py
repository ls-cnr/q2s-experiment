import numpy as np

# ---------------------------------------------------------------------------
# LOGGING FUNCTIONS
# ---------------------------------------------------------------------------

def print_scenario_header(scenario, verbose=True):
    """Print header information about the scenario being processed."""
    if not verbose:
        return

    scenario_id = scenario["id"]
    event_size = scenario["event_size"]
    cost_constraint = scenario["cost_constraint"]
    effort_constraint = scenario["effort_constraint"]
    time_constraint = scenario["time_constraint"]
    alpha = scenario["alpha"]
    perturbation_level_cost = scenario["perturbation_level_cost"]
    perturbation_level_effort = scenario["perturbation_level_effort"]
    perturbation_level_time = scenario["perturbation_level_time"]

    print(f"\n\n===== PROCESSING SCENARIO {scenario_id} =====")
    print(f"Parameters: event_size={event_size}, " +
          f"cost_constraint={cost_constraint}, effort_constraint={effort_constraint}, " +
          f"time_constraint={time_constraint}, alpha={alpha}")
    print(f"Perturbations: cost={perturbation_level_cost}, " +
          f"effort={perturbation_level_effort}, time={perturbation_level_time}")

def print_plan_impacts(all_plan_impacts, verbose=True):
    """Print detailed table of plan impacts."""
    if not verbose:
        return

    print("\nCalculating plan impacts...")
    print("\nAll Plan Impacts:")

    # Get all unique domain variables
    all_domain_vars = set()
    for impacts in all_plan_impacts.values():
        all_domain_vars.update(impacts.keys())
    all_domain_vars = sorted(list(all_domain_vars))

    # Calculate column widths
    plan_id_width = 10
    var_width = 12

    # Print header row
    print("+" + "-" * (plan_id_width + 2) + "+" + "+".join(["-" * (var_width + 2) for _ in all_domain_vars]) + "+")

    # Print column names
    header = f"| {'Plan ID':<{plan_id_width}} |"
    for var in all_domain_vars:
        header += f" {var:<{var_width}} |"
    print(header)

    # Print separator line
    print("+" + "-" * (plan_id_width + 2) + "+" + "+".join(["-" * (var_width + 2) for _ in all_domain_vars]) + "+")

    # Print data for each plan
    for plan_id, impacts in all_plan_impacts.items():
        row = f"| {plan_id:<{plan_id_width}} |"
        for var in all_domain_vars:
            impact = impacts.get(var, 0)
            row += f" {impact:<{var_width}.2f} |"
        print(row)

    # Print final row
    print("+" + "-" * (plan_id_width + 2) + "+" + "+".join(["-" * (var_width + 2) for _ in all_domain_vars]) + "+")

    print(f"\nCalculated impacts for {len(all_plan_impacts)} plans")

def print_quality_goals(quality_goals, verbose=True):
    """Print quality goals information."""
    if not verbose:
        return

    print("\nAdjusted Quality Goals for this scenario:")
    for qg_id, goal in quality_goals.items():
        print(f"  {qg_id}: {goal['domain_variable']} ≤ {goal['max_value']}")

def print_valid_plans_info(valid_plans, all_plan_impacts, verbose=True):
    """Print information about valid plans."""
    if not verbose:
        return

    print(f"\nFiltered down to {len(valid_plans)} valid plans out of {len(all_plan_impacts)}")
    if valid_plans:
        print("Valid Plans:")
        for plan_id in list(valid_plans.keys())[:10]:  # Show first 10 plans
            print(f"  {plan_id}")
        if len(valid_plans) > 10:
            print(f"  ... and {len(valid_plans) - 10} more plans")

def print_q2s_matrix(q2s_matrix, scenario, verbose=True):
    """Print detailed Q2S matrix."""
    if not verbose:
        return

    print("\nCalculating Q2S matrix...")
    print(f"\nQ2S Matrix has {len(q2s_matrix)} plans")

    if not q2s_matrix:
        return

    print("\nQ2S Matrix:")

    # Collect all unique quality goal IDs
    all_qg_ids = set()
    for distances in q2s_matrix.values():
        all_qg_ids.update(distances.keys())
    all_qg_ids = sorted(list(all_qg_ids))

    # Calculate column widths
    plan_id_width = 10
    qg_width = 10
    stat_width = 10

    # Print top header row
    print("+" + "-" * (plan_id_width + 2) + "+" +
        "+".join(["-" * (qg_width + 2) for _ in all_qg_ids]) + "+" +
        "+".join(["-" * (stat_width + 2) for _ in range(3)]) + "+")

    # Print column names
    header = f"| {'Plan ID':<{plan_id_width}} |"
    for qg_id in all_qg_ids:
        header += f" {qg_id:<{qg_width}} |"
    header += f" {'Avg':<{stat_width}} | {'Min':<{stat_width}} | {'Score':<{stat_width}} |"
    print(header)

    # Print separator line
    print("+" + "-" * (plan_id_width + 2) + "+" +
        "+".join(["-" * (qg_width + 2) for _ in all_qg_ids]) + "+" +
        "+".join(["-" * (stat_width + 2) for _ in range(3)]) + "+")

    # Print data for each plan, adding statistic columns
    for plan_id, distances in q2s_matrix.items():
        row = f"| {plan_id:<{plan_id_width}} |"

        # Add each quality goal
        distance_values = []
        for qg_id in all_qg_ids:
            distance = distances.get(qg_id, float('nan'))
            if not isinstance(distance, str) and not (isinstance(distance, float) and distance != distance):  # Check for NaN
                row += f" {distance:<{qg_width}.4f} |"
                distance_values.append(distance)
            else:
                row += f" {'N/A':<{qg_width}} |"

        # Calculate and add Avg, Min and Score
        if distance_values:
            avg_sat = sum(distance_values) / len(distance_values)
            min_sat = min(distance_values)
            score = scenario["alpha"] * avg_sat + (1 - scenario["alpha"]) * min_sat

            row += f" {avg_sat:<{stat_width}.4f} | {min_sat:<{stat_width}.4f} | {score:<{stat_width}.4f} |"
        else:
            row += f" {'N/A':<{stat_width}} | {'N/A':<{stat_width}} | {'N/A':<{stat_width}} |"

        print(row)

    # Print final row
    print("+" + "-" * (plan_id_width + 2) + "+" +
        "+".join(["-" * (qg_width + 2) for _ in all_qg_ids]) + "+" +
        "+".join(["-" * (stat_width + 2) for _ in range(3)]) + "+")

def print_strategy_results_table_header(verbose=True):
    """Print header of the strategy results table."""
    if not verbose:
        return

    print("\nApplying selection strategies...")
    print("\n┌─────────────┬──────────────┬─────────┬────────────┬────────────┐")
    print("│ Strategy    │ Selected Plan │ Score   │ Success    │ Margin     │")
    print("├─────────────┼──────────────┼─────────┼────────────┼────────────┤")

def print_strategy_result_row(strategy_name, plan_id, score, success, margin, verbose=True):
    """Print a row in the strategy results table."""
    if not verbose:
        return

    if plan_id:
        print(f"│ {strategy_name:<11} │ {plan_id:<12} │ {score:.4f} │ {success:<10} │ {margin:.4f}    │")
    else:
        print(f"│ {strategy_name:<11} │ None         │ 0.0000  │ 0          │ 0.0000     │")

def print_random_strategy_result(num_runs, success, margin, verbose=True):
    """Print the random strategy result row."""
    if not verbose:
        return

    print(f"│ Random      │ (avg {num_runs} runs) │ N/A     │ {success:.4f}    │ {margin:.4f}    │")
    print("└─────────────┴──────────────┴─────────┴────────────┴────────────┘")

def print_warning_empty_matrix(quality_goals, all_plan_impacts, verbose=True):
    """Print warning when Q2S matrix is empty."""
    if not verbose:
        return

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

def print_no_valid_plans(scenario_id, verbose=True):
    """Print message when no valid plans are found."""
    if not verbose:
        return

    print(f"No valid plans for scenario {scenario_id} - aborting")

def print_scenario_complete(verbose=True):
    """Print message when scenario processing is complete."""
    if not verbose:
        return

    print("\nScenario processing complete!")
