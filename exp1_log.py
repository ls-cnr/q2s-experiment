def print_q2s_matrix(q2s_matrix):
    """
    Print the basic Q2S matrix with quality goals only.

    Args:
        q2s_matrix (dict): Q2S matrix with quality goals
        verbose (bool): Whether to print the matrix
    """

    print("\nBasic Q2S Matrix:")

    # Check if matrix is empty
    if not q2s_matrix["plans"]:
        print("No plans in the Q2S matrix.")
        return

    # Get list of quality goals
    qg_ids = q2s_matrix["quality_goals"]

    # Calculate column widths
    plan_id_width = 10
    qg_width = 10

    # Print top header row
    print("+" + "-" * (plan_id_width + 2) + "+" +
          "+".join(["-" * (qg_width + 2) for _ in qg_ids]) + "+")

    # Print column names
    header = f"| {'Plan ID':<{plan_id_width}} |"
    for qg_id in qg_ids:
        header += f" {qg_id:<{qg_width}} |"
    print(header)

    # Print separator line
    print("+" + "-" * (plan_id_width + 2) + "+" +
          "+".join(["-" * (qg_width + 2) for _ in qg_ids]) + "+")

    # Print data for each plan
    for plan_id in q2s_matrix["plans"]:
        plan_data = q2s_matrix["matrix"].get(plan_id, {})

        row = f"| {plan_id:<{plan_id_width}} |"

        # Add each quality goal value
        for qg_id in qg_ids:
            value = plan_data.get(qg_id, float('nan'))
            if not isinstance(value, str) and not (isinstance(value, float) and value != value):  # Check for NaN
                row += f" {value:<{qg_width}.4f} |"
            else:
                row += f" {'N/A':<{qg_width}} |"

        print(row)

    # Print final row
    print("+" + "-" * (plan_id_width + 2) + "+" +
          "+".join(["-" * (qg_width + 2) for _ in qg_ids]) + "+")

def print_ext_q2s_matrix(q2s_matrix_extended):
    """
    Print detailed Q2S matrix including quality goals and extended statistics.

    Args:
        q2s_matrix_extended (dict): Extended Q2S matrix with quality goals and statistics
        verbose (bool): Whether to print the matrix
    """
    print("\nQ2S Matrix (extended):")

    # Check if matrix is empty
    if not q2s_matrix_extended["plans"]:
        print("No plans in the Q2S matrix.")
        return

    # Get lists of quality goals and extended columns
    qg_ids = q2s_matrix_extended["quality_goals"]
    extended_cols = q2s_matrix_extended.get("extended_columns", [])

    # Calculate column widths
    plan_id_width = 10
    qg_width = 10
    stat_width = 10

    # Print top header row
    print("+" + "-" * (plan_id_width + 2) + "+" +
          "+".join(["-" * (qg_width + 2) for _ in qg_ids]) + "+" +
          "+".join(["-" * (stat_width + 2) for _ in extended_cols]) + "+")

    # Print column names
    header = f"| {'Plan ID':<{plan_id_width}} |"
    for qg_id in qg_ids:
        header += f" {qg_id:<{qg_width}} |"
    for col in extended_cols:
        header += f" {col:<{stat_width}} |"
    print(header)

    # Print separator line
    print("+" + "-" * (plan_id_width + 2) + "+" +
          "+".join(["-" * (qg_width + 2) for _ in qg_ids]) + "+" +
          "+".join(["-" * (stat_width + 2) for _ in extended_cols]) + "+")

    # Print data for each plan
    for plan_id in q2s_matrix_extended["plans"]:
        plan_data = q2s_matrix_extended["matrix"].get(plan_id, {})

        row = f"| {plan_id:<{plan_id_width}} |"

        # Add each quality goal value
        for qg_id in qg_ids:
            value = plan_data.get(qg_id, float('nan'))
            if not isinstance(value, str) and not (isinstance(value, float) and value != value):  # Check for NaN
                row += f" {value:<{qg_width}.4f} |"
            else:
                row += f" {'N/A':<{qg_width}} |"

        # Add extended statistics values
        for col in extended_cols:
            value = plan_data.get(col, float('nan'))
            if not isinstance(value, str) and not (isinstance(value, float) and value != value):  # Check for NaN
                row += f" {value:<{stat_width}.4f} |"
            else:
                row += f" {'N/A':<{stat_width}} |"

        print(row)

    # Print final row
    print("+" + "-" * (plan_id_width + 2) + "+" +
          "+".join(["-" * (qg_width + 2) for _ in qg_ids]) + "+" +
          "+".join(["-" * (stat_width + 2) for _ in extended_cols]) + "+")



def print_plan_impacts(plan_impacts):
    """
    Print detailed table of plan impacts.

    Args:
        plan_impacts (dict): Dictionary of plan impacts, keyed by plan ID,
                            where each impact is a list of domain variable dictionaries

    Example:
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
    """
    print("\nPlan Impacts:")

    if not plan_impacts:
        print("No plan impacts to display.")
        return

    # Convert the list of domain variable dictionaries to a map for each plan
    formatted_impacts = {}
    all_domain_vars = set()

    for plan_id, impact_list in plan_impacts.items():
        impact_map = {}
        for item in impact_list:
            domain_var = item["domain_variable"]
            value = item["value"]
            impact_map[domain_var] = value
            all_domain_vars.add(domain_var)

        formatted_impacts[plan_id] = impact_map

    # Sort domain variables for consistent display
    all_domain_vars = sorted(list(all_domain_vars))

    # Calculate column widths
    plan_id_width = 10
    var_width = 12

    # Print header row
    print("+" + "-" * (plan_id_width + 2) + "+" +
          "+".join(["-" * (var_width + 2) for _ in all_domain_vars]) + "+")

    # Print column names
    header = f"| {'Plan ID':<{plan_id_width}} |"
    for var in all_domain_vars:
        header += f" {var:<{var_width}} |"
    print(header)

    # Print separator line
    print("+" + "-" * (plan_id_width + 2) + "+" +
          "+".join(["-" * (var_width + 2) for _ in all_domain_vars]) + "+")

    # Print data for each plan
    for plan_id, impacts in formatted_impacts.items():
        row = f"| {plan_id:<{plan_id_width}} |"
        for var in all_domain_vars:
            impact = impacts.get(var, 0)
            row += f" {impact:<{var_width}.2f} |"
        print(row)

    # Print final row
    print("+" + "-" * (plan_id_width + 2) + "+" +
          "+".join(["-" * (var_width + 2) for _ in all_domain_vars]) + "+")

    print(f"\nDisplayed impacts for {len(plan_impacts)} plans")


def print_quality_goals(quality_goals):
    """
    Print detailed information about quality goals.

    Args:
        quality_goals (list): List of quality goal dictionaries with constraint values

    Example:
        Input quality_goals:
        [
          {
            "id": "QG0",
            "domain_variable": "TotalCost",
            "relation_type": "max",
            "constraint": 270
          },
          {
            "id": "QG1",
            "domain_variable": "TotalEffort",
            "relation_type": "max",
            "constraint": 6
          }
        ]
    """
    print("\nQuality Goals for this scenario:")

    for goal in quality_goals:
        qg_id = goal["id"]
        domain_var = goal["domain_variable"]
        relation = goal["relation_type"]
        constraint = goal["constraint"]

        # Format the relation symbol
        relation_symbol = "≤" if relation == "max" else "≥" if relation == "min" else "="

        print(f"  {qg_id}: {domain_var} {relation_symbol} {constraint}")
