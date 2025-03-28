import random
import numpy as np

# ---------------------------------------------------------------------------
# PLAN SELECTION STRATEGIES (EXP1 SPECIFIC)
# ---------------------------------------------------------------------------

def avg_only_strategy(q2s_matrix, verbose=False):
    """
    Select plan using only the average satisfaction.

    Args:
        q2s_matrix: Dictionary mapping plan IDs to dictionaries of distances
        verbose: Whether to print detailed information

    Returns:
        Tuple of (selected plan ID, score)
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

    Args:
        q2s_matrix: Dictionary mapping plan IDs to dictionaries of distances
        verbose: Whether to print detailed information

    Returns:
        Tuple of (selected plan ID, score)
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

    Args:
        q2s_matrix: Dictionary mapping plan IDs to dictionaries of distances
        verbose: Whether to print detailed information

    Returns:
        Tuple of (selected plan ID, score)
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

def apply_perturbation(plan_impacts, scenario, perturbation_values, verbose=False):
    """
    Apply perturbations based on scenario parameters.

    Args:
        plan_impacts: Dictionary with plan impacts
        scenario: Dictionary with scenario parameters
        perturbation_values: Dictionary with perturbation values
        verbose: Whether to print detailed information

    Returns:
        Dictionary with perturbed impacts
    """
    # Deep copy the impacts to avoid modifying the original
    perturbed_impacts = dict(plan_impacts)

    # Get perturbation values for each dimension
    effort_perturbation = perturbation_values["effort"][scenario["perturbation_level_effort"]]
    time_perturbation = perturbation_values["time"][scenario["perturbation_level_time"]]
    cost_perturbation = perturbation_values["cost"][scenario["perturbation_level_cost"]]

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
            perturbed_impacts[var] += effort_perturbation

        if verbose and perturbed_impacts[var] != original_value:
            print(f"    {var}: {original_value:.2f} -> {perturbed_impacts[var]:.2f}")

    return perturbed_impacts

def evaluate_plan_under_perturbation(plan_id, plan, quality_goals, scenario, perturbation_values, verbose=False):
    """
    Evaluate a plan under perturbation.

    Args:
        plan_id: ID of the plan to evaluate
        plan: Dictionary with plan details
        quality_goals: Dictionary with quality goal constraints
        scenario: Dictionary with scenario parameters
        perturbation_values: Dictionary with perturbation values
        verbose: Whether to print detailed information

    Returns:
        Tuple of (success rate, average margin)
    """
    if verbose:
        print(f"  Evaluating plan {plan_id} under perturbation...")

    # Apply perturbation to plan impacts
    perturbed_impacts = apply_perturbation(plan["impact"], scenario, perturbation_values, verbose)

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
