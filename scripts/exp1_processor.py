from exp1_utils import (
    avg_only_strategy,
    min_only_strategy,
    random_strategy,
    evaluate_plan_under_perturbation
)

from q2s_utils import (
    calculate_all_plan_impacts,
    create_quality_goals_from_scenario,
    calculate_q2s_matrix,
    q2s_selection_strategy
)

from exp1_log import (
    print_scenario_header,
    print_plan_impacts,
    print_quality_goals,
    print_valid_plans_info,
    print_q2s_matrix,
    print_strategy_results_table_header,
    print_strategy_result_row,
    print_random_strategy_result,
    print_warning_empty_matrix,
    print_no_valid_plans,
    print_scenario_complete
)

# ---------------------------------------------------------------------------
# MAIN PROCESSING FUNCTION
# ---------------------------------------------------------------------------

def process_scenario(scenario, plans, contributions, quality_goals_mapping, perturbation_values, verbose=True):
    """
    Process a single scenario with the given data.

    Args:
        scenario: Dictionary with scenario parameters
        plans: Dictionary of plans
        contributions: Dictionary of contributions
        quality_goals_mapping: Mapping of quality goals to domain variables
        perturbation_values: Dictionary with perturbation values for different dimensions
        verbose: Whether to print detailed information

    Returns:
        Dictionary with results of processing the scenario
    """
    # Print scenario header
    print_scenario_header(scenario, verbose)

    # Initialize result dictionary with scenario parameters
    result = {
        "id": scenario["id"],
        "event_size": scenario["event_size"],
        "cost_constraint": scenario["cost_constraint"],
        "effort_constraint": scenario["effort_constraint"],
        "time_constraint": scenario["time_constraint"],
        "alpha": scenario["alpha"],
        "perturbation_level_cost": scenario["perturbation_level_cost"],
        "perturbation_level_effort": scenario["perturbation_level_effort"],
        "perturbation_level_time": scenario["perturbation_level_time"]
    }

    # Calculate impacts for all plans
    all_plan_impacts = calculate_all_plan_impacts(plans, contributions)
    print_plan_impacts(all_plan_impacts, verbose)

    # Create quality goals from scenario constraints
    quality_goals = create_quality_goals_from_scenario(
        scenario,
        quality_goals_mapping
    )
    print_quality_goals(quality_goals, verbose)

    # Filter valid plans
    valid_plans = {}
    for plan_id, impacts in all_plan_impacts.items():
        # Check if plan satisfies all constraints
        if all(
            impacts[goal["domain_variable"]] <= goal["max_value"]
            for goal in quality_goals.values()
            if goal["domain_variable"] in impacts
        ):
            valid_plans[plan_id] = {"name": plan_id, "impact": impacts}

    print_valid_plans_info(valid_plans, all_plan_impacts, verbose)
    result["num_valid_plans"] = len(valid_plans)

    # If no valid plans, return early with zeros for metrics
    if not valid_plans:
        print_no_valid_plans(scenario["id"], verbose)
        if not verbose:
            print(f"No valid plans for scenario {scenario['id']}")

        result.update({
            "Q2S_success": 0,
            "Q2S_margins": 0,
            "Avg_success": 0,
            "Avg_margins": 0,
            "Min_success": 0,
            "Min_margins": 0,
            "Random_success": 0,
            "Random_margins": 0
        })

        return result

    # Calculate Q2S matrix
    q2s_matrix = calculate_q2s_matrix(valid_plans, quality_goals)
    print_q2s_matrix(q2s_matrix, scenario, verbose)

    # Check if matrix is empty
    if not q2s_matrix:
        print_warning_empty_matrix(quality_goals, all_plan_impacts, verbose)

        result.update({
            "Q2S_success": 0,
            "Q2S_margins": 0,
            "Avg_success": 0,
            "Avg_margins": 0,
            "Min_success": 0,
            "Min_margins": 0,
            "Random_success": 0,
            "Random_margins": 0
        })

        return result

    # Start strategy evaluation
    print_strategy_results_table_header(verbose)

    # 1. Q2S Strategy
    q2s_plan_id, q2s_score = q2s_selection_strategy(q2s_matrix, scenario["alpha"])

    if q2s_plan_id:
        q2s_success, q2s_margins = evaluate_plan_under_perturbation(
            q2s_plan_id,
            valid_plans[q2s_plan_id],
            quality_goals,
            scenario,
            perturbation_values,
            verbose and False  # Less verbose for internal details
        )
    else:
        q2s_success, q2s_margins = 0, 0

    print_strategy_result_row("Q2S", q2s_plan_id, q2s_score, q2s_success, q2s_margins, verbose)

    # 2. AvgSat Strategy
    avg_plan_id, avg_score = avg_only_strategy(q2s_matrix, verbose and False)

    if avg_plan_id:
        avg_success, avg_margins = evaluate_plan_under_perturbation(
            avg_plan_id,
            valid_plans[avg_plan_id],
            quality_goals,
            scenario,
            perturbation_values,
            verbose and False
        )
    else:
        avg_success, avg_margins = 0, 0

    print_strategy_result_row("AvgSat", avg_plan_id, avg_score, avg_success, avg_margins, verbose)

    # 3. MinSat Strategy
    min_plan_id, min_score = min_only_strategy(q2s_matrix, verbose and False)

    if min_plan_id:
        min_success, min_margins = evaluate_plan_under_perturbation(
            min_plan_id,
            valid_plans[min_plan_id],
            quality_goals,
            scenario,
            perturbation_values,
            verbose and False
        )
    else:
        min_success, min_margins = 0, 0

    print_strategy_result_row("MinSat", min_plan_id, min_score, min_success, min_margins, verbose)

    # 4. Random Strategy (average of multiple runs)
    random_success_sum = 0
    random_margins_sum = 0
    num_random_runs = 10  # Hardcoded number of random runs

    for i in range(num_random_runs):
        random_plan_id, _ = random_strategy(q2s_matrix, False)  # Less verbose for random runs

        if random_plan_id:
            run_success, run_margins = evaluate_plan_under_perturbation(
                random_plan_id,
                valid_plans[random_plan_id],
                quality_goals,
                scenario,
                perturbation_values,
                False
            )

            random_success_sum += run_success
            random_margins_sum += run_margins

    # Calculate averages for random strategy
    random_success = random_success_sum / num_random_runs if num_random_runs > 0 else 0
    random_margins = random_margins_sum / num_random_runs if num_random_runs > 0 else 0

    print_random_strategy_result(num_random_runs, random_success, random_margins, verbose)

    # Update result with strategy evaluations
    result.update({
        "Q2S_success": q2s_success,
        "Q2S_margins": q2s_margins,
        "Avg_success": avg_success,
        "Avg_margins": avg_margins,
        "Min_success": min_success,
        "Min_margins": min_margins,
        "Random_success": random_success,
        "Random_margins": random_margins,
        "selected_plans": {
            "Q2S": q2s_plan_id,
            "Avg": avg_plan_id,
            "Min": min_plan_id
        }
    })

    print_scenario_complete(verbose)
    if not verbose:
        print(f"Scenario {scenario['id']} processed. Valid plans: {len(valid_plans)}")

    return result
