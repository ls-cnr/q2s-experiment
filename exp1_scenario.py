import random
from q2s_utils import (
    load_plans,
    load_contributions,
    calculate_plan_impact,
    set_quality_goals_for_scenario,
    check_plan_validity,
    filter_valid_plans
)
from q2s_matrix import (
    calculate_q2s_matrix,
    calculate_extended_q2s_matrix,
    q2s_selection_strategy_extended
)
from exp1_log import (
    print_plan_impacts,
    print_quality_goals,
    print_ext_q2s_matrix
)

def process_scenario(config, scenario, alpha, verbose=False):
    """
    Process a scenario with the given configuration and constraints.

    Args:
        config (dict): Configuration loaded from JSON
        scenario (dict): Scenario with constraints and perturbation levels
        alpha (float): Alpha value for Q2S score calculation
        verbose (bool): Whether to print detailed information

    Returns:
        dict: Results of the scenario including success rates and margins

    Example:
        Input scenario:
        {
            "cost_constraint": 270,
            "effort_constraint": 6,
            "time_constraint": 9,
            "perturbation_level": {
                "cost": "low_neg",
                "effort": "no",
                "time": "high_neg"
            },
            "alpha": 0.5
        }

        Output:
        {
            "ScorePlan_ID": "Plan3",
            "ScorePlan_success": True,
            "ScorePlan_margins": 0.1542,
            "AvgPlan_ID": "Plan7",
            "AvgPlan_success": False,
            "AvgPlan_margins": 0,
            "MinPlan_ID": "Plan12",
            "MinPlan_success": True,
            "MinPlan_margins": 0.2135,
            "RndPlan_ID": "Plan5",
            "RndPlan_success": False,
            "RndPlan_margins": 0,
            "num_valid_plans": 8
        }
    """
    if verbose:
        print("\n" + "="*80)
        print(f"Processing scenario with alpha={alpha}")
        print("="*80)

    # 1. Load plans and contributions
    plans = load_plans(config["file_paths"]["plans"])
    contributions = load_contributions(config["file_paths"]["contributions"])

    if plans is None or contributions is None:
        print("Failed to load plans or contributions")
        return None

    # 2. Calculate impact for all plans
    plan_impacts = {}
    for plan_id, plan in plans.items():
        impact = calculate_plan_impact(plan, contributions)
        plan_impacts[plan_id] = impact

    if verbose:
        print_plan_impacts(plan_impacts)

    # 3. Set non-perturbed quality goals
    constraint_options = get_constraint_options(scenario)
    quality_goals = set_quality_goals_for_scenario(config["quality_goals"], constraint_options, False)

    if verbose:
        print_quality_goals(quality_goals)

    # 4. Filter valid plans
    valid_plans = filter_valid_plans(plans, plan_impacts, quality_goals)

    if verbose:
        print(f"\nFound {len(valid_plans)} valid plans out of {len(plans)} total plans.")

    if not valid_plans:
        print("No valid plans found for this scenario.")
        return {
            "ScorePlan_ID": None,
            "ScorePlan_success": False,
            "ScorePlan_margins": 0,
            "AvgPlan_ID": None,
            "AvgPlan_success": False,
            "AvgPlan_margins": 0,
            "MinPlan_ID": None,
            "MinPlan_success": False,
            "MinPlan_margins": 0,
            "RndPlan_ID": None,
            "RndPlan_success": False,
            "RndPlan_margins": 0,
            "num_valid_plans": 0
        }

    # 5. Calculate Q2S matrix and extended matrix
    q2s_matrix = calculate_q2s_matrix(valid_plans, plan_impacts, quality_goals)
    q2s_matrix_extended = calculate_extended_q2s_matrix(q2s_matrix, alpha)

    if verbose:
        print_ext_q2s_matrix(q2s_matrix_extended)

    # 6. Apply selection strategies

    # 6.1 Q2S strategy (using Score)
    q2s_plan_id = q2s_selection_strategy_extended(q2s_matrix_extended)

    # 6.2 AvgSat strategy (find plan with highest AvgSat)
    avg_plan_id = None
    highest_avg = float('-inf')
    for plan_id in q2s_matrix_extended["plans"]:
        avg_sat = q2s_matrix_extended["matrix"][plan_id]["AvgSat"]
        if avg_sat > highest_avg:
            highest_avg = avg_sat
            avg_plan_id = plan_id

    # 6.3 MinSat strategy (find plan with highest MinSat)
    min_plan_id = None
    highest_min = float('-inf')
    for plan_id in q2s_matrix_extended["plans"]:
        min_sat = q2s_matrix_extended["matrix"][plan_id]["MinSat"]
        if min_sat > highest_min:
            highest_min = min_sat
            min_plan_id = plan_id

    # 6.4 Random strategy (select random valid plan)
    rnd_plan_id = random.choice(list(valid_plans.keys()))

    if verbose:
        print("\nSelected plans:")
        print(f"  Q2S strategy: {q2s_plan_id}")
        print(f"  AvgSat strategy: {avg_plan_id}")
        print(f"  MinSat strategy: {min_plan_id}")
        print(f"  Random strategy: {rnd_plan_id}")

    # 7. Set perturbed quality goals
    perturbed_quality_goals = set_quality_goals_for_scenario(config["quality_goals"], constraint_options, True)

    if verbose:
        print("\nPerturbed quality goals:")
        print_quality_goals(perturbed_quality_goals)

    # 8. Check if selected plans are still valid with perturbed constraints
    q2s_success, q2s_margins = check_plan_with_margins(q2s_plan_id, plan_impacts, perturbed_quality_goals)
    avg_success, avg_margins = check_plan_with_margins(avg_plan_id, plan_impacts, perturbed_quality_goals)
    min_success, min_margins = check_plan_with_margins(min_plan_id, plan_impacts, perturbed_quality_goals)
    random_success, random_margins = check_plan_with_margins(rnd_plan_id, plan_impacts, perturbed_quality_goals)

    if verbose:
        print("\nResults after perturbation:")
        print(f"  Q2S strategy: Success={q2s_success}, Margins={q2s_margins}")
        print(f"  AvgSat strategy: Success={avg_success}, Margins={avg_margins}")
        print(f"  MinSat strategy: Success={min_success}, Margins={min_margins}")
        print(f"  Random strategy: Success={random_success}, Margins={random_margins}")

    # 9. Return results
    return {
        "ScorePlan_ID": q2s_plan_id,
        "ScorePlan_success": q2s_success,
        "ScorePlan_margins": q2s_margins,
        "AvgPlan_ID": avg_plan_id,
        "AvgPlan_success": avg_success,
        "AvgPlan_margins": avg_margins,
        "MinPlan_ID": min_plan_id,
        "MinPlan_success": min_success,
        "MinPlan_margins": min_margins,
        "RndPlan_ID": rnd_plan_id,
        "RndPlan_success": random_success,
        "RndPlan_margins": random_margins,
        "num_valid_plans": len(valid_plans)
    }

def check_plan_with_margins(plan_id, plan_impacts, perturbed_quality_goals):
    """
    Check if a plan is valid with perturbed constraints and calculate margins.

    Args:
        plan_id (str): ID of the plan to check
        plan_impacts (dict): Dictionary of plan impacts
        perturbed_quality_goals (list): List of quality goals with perturbed constraints

    Returns:
        tuple: (is_valid, avg_margin) - whether the plan is valid and its average margin
    """
    if plan_id is None:
        return False, 0

    plan_impact = plan_impacts[plan_id]
    is_valid = check_plan_validity(plan_impact, perturbed_quality_goals)

    if not is_valid:
        return False, 0

    # Calculate margins (average remaining satisfaction distance)
    margins = []
    for goal in perturbed_quality_goals:
        domain_var = goal["domain_variable"]
        constraint = goal["constraint"]

        # Find the actual value for this domain variable
        actual_value = None
        for item in plan_impact:
            if item["domain_variable"] == domain_var:
                actual_value = item["value"]
                break

        if actual_value is not None and constraint > 0:  # Avoid division by zero
            margin = (constraint - actual_value) / constraint
            margins.append(margin)

    avg_margin = sum(margins) / len(margins) if margins else 0
    return True, round(avg_margin, 4)


def get_constraint_options(scenario):
    """
    Convert a scenario into constraint options format.

    Args:
        scenario (dict): Scenario with constraints and perturbation levels

    Returns:
        list: List of constraint options with values and perturbations

    Example:
        Input scenario:
        {
            "cost_constraint": 270,
            "effort_constraint": 6,
            "time_constraint": 9,
            "perturbation_level": {
                "cost_constraint": "-10",
                "effort_constraint": "0",
                "time_constraint": "3"
            },
            "alpha": 0.5
        }

        Output constraint_options:
        [
          {"domain_variable": "cost_constraint", "value": 270, "perturbation": {"value": -10}},
          {"domain_variable": "effort_constraint", "value": 6, "perturbation": {"value": 0}},
          {"domain_variable": "time_constraint", "value": 9, "perturbation": {"value": 3}}
        ]
    """
    constraint_options = []
    perturbation_levels = scenario.get("perturbation_level", {})

    # Find all constraint keys (those ending with "_constraint")
    constraint_keys = [key for key in scenario.keys() if key.endswith("_constraint")]

    for key in constraint_keys:
        # Get constraint value
        value = scenario.get(key)

        # Get perturbation value (or default to 0 if not specified)
        perturb_value_str = perturbation_levels.get(key, "0")

        # Convert perturbation value to integer or float
        try:
            perturb_value = int(perturb_value_str)
        except ValueError:
            try:
                perturb_value = float(perturb_value_str)
            except ValueError:
                print(f"Warning: Invalid perturbation value '{perturb_value_str}' for {key}, using 0")
                perturb_value = 0

        # Create constraint option
        constraint_option = {
            "domain_variable": key,
            "value": value,
            "perturbation": {"value": perturb_value}
        }

        constraint_options.append(constraint_option)

    return constraint_options
