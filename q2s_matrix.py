
def calculate_q2s_matrix(valid_plans, plan_impacts, quality_goals):
    """
    Calculate the Q2S (Quality to Satisfaction) matrix for a set of valid plans.

    For each plan-quality goal combination, the matrix contains a satisfaction distance (d_ij)
    calculated as: (constraint_value - actual_value) / constraint_value

    Args:
        valid_plans (dict): Dictionary of valid plans
        plan_impacts (dict): Dictionary of plan impacts, keyed by plan ID
        quality_goals (list): List of quality goals with constraints

    Returns:
        dict: Q2S matrix containing satisfaction distances for each plan and quality goal

    Example:
        Input valid_plans:
        {
            "Plan0": {"id": "Plan0", "goals": {...}},
            "Plan1": {"id": "Plan1", "goals": {...}}
        }

        Input plan_impacts:
        {
            "Plan0": [
            {"domain_variable": "TotalCost", "value": 200},
            {"domain_variable": "TotalEffort", "value": 4},
            {"domain_variable": "TimeSpent", "value": 7}
            ],
            "Plan1": [
            {"domain_variable": "TotalCost", "value": 220},
            {"domain_variable": "TotalEffort", "value": 3},
            {"domain_variable": "TimeSpent", "value": 8}
            ]
        }

        Input quality_goals:
        [
            {"id": "QG0", "domain_variable": "TotalCost", "relation_type": "max", "constraint": 270},
            {"id": "QG1", "domain_variable": "TotalEffort", "relation_type": "max", "constraint": 6},
            {"id": "QG2", "domain_variable": "TimeSpent", "relation_type": "max", "constraint": 9}
        ]

        Output:
        {
            "matrix": {
            "Plan0": {
                "QG0": 0.259,  # (270-200)/270
                "QG1": 0.333,  # (6-4)/6
                "QG2": 0.222   # (9-7)/9
            },
            "Plan1": {
                "QG0": 0.185,  # (270-220)/270
                "QG1": 0.500,  # (6-3)/6
                "QG2": 0.111   # (9-8)/9
            }
            },
            "plans": ["Plan0", "Plan1"],
            "quality_goals": ["QG0", "QG1", "QG2"]
        }
    """
    # Create a map of domain variables to their corresponding quality goals for quick lookup
    domain_var_to_qg = {}
    for qg in quality_goals:
        domain_var_to_qg[qg["domain_variable"]] = qg

    # Initialize the Q2S matrix
    q2s_matrix = {
        "matrix": {},
        "plans": list(valid_plans.keys()),
        "quality_goals": [qg["id"] for qg in quality_goals]
    }

    # Calculate the satisfaction distances for each plan and quality goal
    for plan_id in valid_plans.keys():
        # Get the impact for this plan
        impact = plan_impacts[plan_id]

        # Create a map of domain variables to their actual values for this plan
        impact_map = {item["domain_variable"]: item["value"] for item in impact}

        # Initialize the matrix row for this plan
        q2s_matrix["matrix"][plan_id] = {}

        # Calculate satisfaction distance for each quality goal
        for qg in quality_goals:
            qg_id = qg["id"]
            domain_var = qg["domain_variable"]
            constraint = qg["constraint"]
            relation_type = qg["relation_type"]

            # Get the actual value for this domain variable
            if domain_var in impact_map:
                actual_value = impact_map[domain_var]

                # Calculate the satisfaction distance based on the relation type
                if relation_type == "max":
                    # For "max" constraints, the distance is (constraint - actual) / constraint
                    distance = (constraint - actual_value) / constraint

                    # Round to 3 decimal places for readability
                    distance = round(distance, 3)

                    # Store the distance in the matrix
                    q2s_matrix["matrix"][plan_id][qg_id] = distance
                else:
                    print(f"Warning: Unsupported relation type '{relation_type}' in quality goal '{qg_id}'")
            else:
                print(f"Warning: Domain variable '{domain_var}' not found in impact for plan '{plan_id}'")

    return q2s_matrix


def calculate_extended_q2s_matrix(q2s_matrix, alpha):
    """
    Calculate an extended Q2S matrix that includes AvgSat, MinSat, and Score for each plan.

    Args:
        q2s_matrix (dict): Q2S matrix containing satisfaction distances
        alpha (float): Weight parameter between 0 and 1 for score calculation

    Returns:
        dict: Extended Q2S matrix with additional columns

    Example:
        Input q2s_matrix:
        {
          "matrix": {
            "Plan0": {
              "QG0": 0.259,
              "QG1": 0.333,
              "QG2": 0.222
            },
            "Plan1": {
              "QG0": 0.185,
              "QG1": 0.500,
              "QG2": 0.111
            }
          },
          "plans": ["Plan0", "Plan1"],
          "quality_goals": ["QG0", "QG1", "QG2"]
        }

        Input alpha: 0.5

        Output:
        {
          "matrix": {
            "Plan0": {
              "QG0": 0.259,
              "QG1": 0.333,
              "QG2": 0.222,
              "AvgSat": 0.271,
              "MinSat": 0.222,
              "Score": 0.247
            },
            "Plan1": {
              "QG0": 0.185,
              "QG1": 0.500,
              "QG2": 0.111,
              "AvgSat": 0.265,
              "MinSat": 0.111,
              "Score": 0.188
            }
          },
          "plans": ["Plan0", "Plan1"],
          "quality_goals": ["QG0", "QG1", "QG2"],
          "extended_columns": ["AvgSat", "MinSat", "Score"]
        }
    """
    # Validate input
    if not 0 <= alpha <= 1:
        raise ValueError("Alpha must be between 0 and 1")

    # Create a deep copy of the Q2S matrix to avoid modifying the original
    import copy
    extended_matrix = copy.deepcopy(q2s_matrix)

    # Add the extended columns to the list
    extended_matrix["extended_columns"] = ["AvgSat", "MinSat", "Score"]

    # Calculate extended values for each plan
    for plan_id in extended_matrix["plans"]:
        # Get the satisfaction distances for this plan
        plan_values = extended_matrix["matrix"].get(plan_id, {})
        plan_distances = [value for key, value in plan_values.items()
                          if key in extended_matrix["quality_goals"]]

        if not plan_distances:
            print(f"Warning: No satisfaction distances for plan '{plan_id}'")
            # Set default values
            extended_matrix["matrix"].setdefault(plan_id, {})
            extended_matrix["matrix"][plan_id]["AvgSat"] = 0
            extended_matrix["matrix"][plan_id]["MinSat"] = 0
            extended_matrix["matrix"][plan_id]["Score"] = 0
            continue

        # Calculate average satisfaction (AvgSat)
        avg_sat = sum(plan_distances) / len(plan_distances)
        # Round to 3 decimal places
        avg_sat = round(avg_sat, 3)

        # Calculate minimum satisfaction (MinSat)
        min_sat = min(plan_distances)

        # Calculate the score using the Hurwicz criterion
        score = alpha * avg_sat + (1 - alpha) * min_sat
        # Round to 3 decimal places
        score = round(score, 3)

        # Add the extended values to the matrix
        extended_matrix["matrix"][plan_id]["AvgSat"] = avg_sat
        extended_matrix["matrix"][plan_id]["MinSat"] = min_sat
        extended_matrix["matrix"][plan_id]["Score"] = score

    return extended_matrix

def q2s_selection_strategy_extended(q2s_matrix_extended):
    """
    Select the best plan using the Q2S selection strategy based on the Score column
    from an extended Q2S matrix.

    Args:
        q2s_matrix_extended (dict): Extended Q2S matrix containing Score column

    Returns:
        str: ID of the selected plan (the one with the highest Score)

    Example:
        Input q2s_matrix_extended:
        {
          "matrix": {
            "Plan0": {
              "QG0": 0.259,
              "QG1": 0.333,
              "QG2": 0.222,
              "AvgSat": 0.271,
              "MinSat": 0.222,
              "Score": 0.247
            },
            "Plan1": {
              "QG0": 0.185,
              "QG1": 0.500,
              "QG2": 0.111,
              "AvgSat": 0.265,
              "MinSat": 0.111,
              "Score": 0.188
            }
          },
          "plans": ["Plan0", "Plan1"],
          "quality_goals": ["QG0", "QG1", "QG2"],
          "extended_columns": ["AvgSat", "MinSat", "Score"]
        }

        Output: "Plan0"  # Because it has the highest Score
    """
    # Verify the extended matrix has the necessary structure
    if ("extended_columns" not in q2s_matrix_extended or
            "Score" not in q2s_matrix_extended["extended_columns"]):
        raise ValueError("The provided matrix is not a valid extended Q2S matrix with Score column")

    if not q2s_matrix_extended["plans"]:
        print("Warning: No plans in the extended Q2S matrix")
        return None

    # Initialize variables to track the best plan
    best_plan = None
    highest_score = float('-inf')

    # Find the plan with the highest Score
    for plan_id in q2s_matrix_extended["plans"]:
        plan_data = q2s_matrix_extended["matrix"].get(plan_id, {})

        # Check if this plan has a Score
        if "Score" not in plan_data:
            print(f"Warning: No Score found for plan '{plan_id}'")
            continue

        # Get the Score for this plan
        score = plan_data["Score"]

        # Update the best plan if this one has a higher score
        if score > highest_score:
            highest_score = score
            best_plan = plan_id

    if best_plan is None:
        print("Warning: Could not select a best plan")

    return best_plan


def q2s_selection_strategy_old(q2s_matrix, alpha):
    """
    Select the best plan using the Q2S selection strategy.

    The strategy calculates a score for each plan using:
    Score = alpha * AvgSat + (1-alpha) * MinSat
    where AvgSat is the average satisfaction distance across all quality goals
    and MinSat is the minimum satisfaction distance.

    Args:
        q2s_matrix (dict): Q2S matrix containing satisfaction distances
        alpha (float): Weight parameter between 0 and 1, balancing average vs. minimum satisfaction

    Returns:
        str: ID of the selected plan (the one with the highest score)

    Example:
        Input q2s_matrix:
        {
          "matrix": {
            "Plan0": {
              "QG0": 0.259,
              "QG1": 0.333,
              "QG2": 0.222
            },
            "Plan1": {
              "QG0": 0.185,
              "QG1": 0.500,
              "QG2": 0.111
            }
          },
          "plans": ["Plan0", "Plan1"],
          "quality_goals": ["QG0", "QG1", "QG2"]
        }

        Input alpha: 0.5

        Output: "Plan0"  # Because its score is higher
    """
    # Validate input
    if not 0 <= alpha <= 1:
        raise ValueError("Alpha must be between 0 and 1")

    if not q2s_matrix["plans"]:
        print("Warning: No plans in the Q2S matrix")
        return None

    # Dictionary to store scores for each plan
    scores = {}

    # Calculate scores for each plan
    for plan_id in q2s_matrix["plans"]:
        # Get the satisfaction distances for this plan
        plan_distances = list(q2s_matrix["matrix"][plan_id].values())

        if not plan_distances:
            print(f"Warning: No satisfaction distances for plan '{plan_id}'")
            continue

        # Calculate average satisfaction (AvgSat)
        avg_sat = sum(plan_distances) / len(plan_distances)

        # Calculate minimum satisfaction (MinSat)
        min_sat = min(plan_distances)

        # Calculate the score using the Hurwicz criterion
        score = alpha * avg_sat + (1 - alpha) * min_sat

        # Store the score
        scores[plan_id] = score

    if not scores:
        print("Warning: No scores could be calculated")
        return None

    # Find the plan with the highest score
    best_plan = None
    highest_score = float('-inf')

    for plan_id, score in scores.items():
        if score > highest_score:
            highest_score = score
            best_plan = plan_id

    # Return the best plan ID
    return best_plan
