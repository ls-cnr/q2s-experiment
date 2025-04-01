import json
import pandas as pd
import os

def load_json_config(config_filename):
    """
    Load a JSON configuration file.

    Args:
        config_filename (str): Path to the JSON configuration file

    Returns:
        dict: The loaded configuration, or None if the file doesn't exist or is invalid
    """
    try:
        # Check if file exists
        if not os.path.isfile(config_filename):
            print(f"Configuration file not found: {config_filename}")
            return None

        # Open and parse the JSON file
        with open(config_filename, 'r', encoding='utf-8') as file:
            config = json.load(file)

        return config

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON configuration: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error loading configuration: {e}")
        return None



def load_plans(file_path):
    """
    Load plans from a CSV file.

    Args:
        file_path (str): Path to the CSV file containing plans

    Returns:
        dict: A dictionary of plans, or None if the file doesn't exist
        Example:
            Input CSV:
            PLANS,G1,G5,G7,G8,G9,G10,G11,G12,G13,G14
            Plan0,1,1,0,1,0,0,1,0,1,0
            Plan1,1,1,0,1,0,0,1,0,0,1

            Output:
            {
            "Plan0": {
                "id": "Plan0",
                "goals": {"G1": 1, "G5": 1, "G7": 0, "G8": 1, "G9": 0, "G10": 0, "G11": 1, "G12": 0, "G13": 1, "G14": 0}
            },
            "Plan1": {
                "id": "Plan1",
                "goals": {"G1": 1, "G5": 1, "G7": 0, "G8": 1, "G9": 0, "G10": 0, "G11": 1, "G12": 0, "G13": 0, "G14": 1}
            },
            ...
            }
    """
    try:
        # Check if file exists
        if not os.path.isfile(file_path):
            print(f"Plans file not found: {file_path}")
            return None

        # Read the CSV file
        df = pd.read_csv(file_path)

        # Initialize plans dictionary
        plans = {}

        # Get goal columns (all columns except the first one, which is 'PLANS')
        goal_columns = df.columns[1:].tolist()

        # Iterate through each row in the DataFrame
        for index, row in df.iterrows():
            plan_id = row['PLANS']

            # Create a dictionary for the plan's goals
            plan_goals = {}
            for goal in goal_columns:
                plan_goals[goal] = int(row[goal])

            # Add the plan to the plans dictionary
            plans[plan_id] = {
                "id": plan_id,
                "goals": plan_goals
            }

        return plans

    except Exception as e:
        print(f"Error loading plans: {e}")
        return None




def load_contributions(file_path):
    """
    Load contributions from a CSV file into a structured dictionary.

    The function reads a CSV file where the first column is 'DomainVariable' and
    the remaining columns are goals (G1, G2, etc.) with numeric contribution values.

    Args:
        file_path (str): Path to the CSV file containing contribution values

    Returns:
        dict: A dictionary of domain variables with their goal contributions,
              or None if the file doesn't exist

        Example:
            Input CSV:
            DomainVariable,G1,G5,G7,G8,G9,G10,G11,G12,G13,G14
            TotalCost,10,100,30,80,100,40,0,30,10,15
            TotalEffort,0,0,1,0,0,0,2,1,2,4
            TimeSpent,1,1,1,1,1,0,2,1,2,4

            Output:
            {
            "TotalCost": {
                "G1": 10, "G5": 100, "G7": 30, "G8": 80, "G9": 100,
                "G10": 40, "G11": 0, "G12": 30, "G13": 10, "G14": 15
            },
            "TotalEffort": {
                "G1": 0, "G5": 0, "G7": 1, "G8": 0, "G9": 0,
                "G10": 0, "G11": 2, "G12": 1, "G13": 2, "G14": 4
            },
            "TimeSpent": {
                "G1": 1, "G5": 1, "G7": 1, "G8": 1, "G9": 1,
                "G10": 0, "G11": 2, "G12": 1, "G13": 2, "G14": 4
            }
            }
    """
    try:
        # Check if file exists
        if not os.path.isfile(file_path):
            print(f"Contributions file not found: {file_path}")
            return None

        # Read the CSV file
        df = pd.read_csv(file_path)

        # Initialize contributions dictionary
        contributions = {}

        # Get goal columns (all columns except the first one, which is 'DomainVariable')
        goal_columns = df.columns[1:].tolist()

        # Iterate through each row in the DataFrame
        for index, row in df.iterrows():
            domain_var = row['DomainVariable']

            # Create a dictionary for the domain variable's goal contributions
            var_contributions = {}
            for goal in goal_columns:
                var_contributions[goal] = float(row[goal])

            # Add the domain variable to the contributions dictionary
            contributions[domain_var] = var_contributions

        return contributions

    except Exception as e:
        print(f"Error loading contributions: {e}")
        return None

def calculate_plan_impact(plan, contributions):
    """
    Calculate the impact of a plan on domain variables based on contribution values.

    For each domain variable, the impact is calculated as the sum of contributions
    of goals that are active (value = 1) in the plan.

    Args:
        plan (dict): A plan dictionary with id and goals
        contributions (dict): A dictionary of domain variables with their goal contributions

    Returns:
        dict: A dictionary of domain variables with their calculated impact values

    Example:
        Input Plan:
        {
          "id": "Plan0",
          "goals": {
            "G1": 1, "G5": 1, "G7": 0, "G8": 1, "G9": 0,
            "G10": 0, "G11": 1, "G12": 0, "G13": 1, "G14": 0
          }
        }

        Input Contributions:
        {
          "TotalCost": {
            "G1": 10, "G5": 100, "G7": 30, "G8": 80, "G9": 100,
            "G10": 40, "G11": 0, "G12": 30, "G13": 10, "G14": 15
          },
          ...
        }

        Output:
        [
          {"domain_variable": "TotalCost", "value": 200},
          {"domain_variable": "TotalEffort", "value": 4},
          {"domain_variable": "TimeSpent", "value": 7}
        ]
    """
    # Initialize result
    impact = []

    # For each domain variable in the contributions
    for domain_var, contrib_values in contributions.items():
        # Initialize the total impact value
        total_value = 0

        # For each goal in the contribution values
        for goal, contrib_value in contrib_values.items():
            # Check if the goal exists in the plan and is active (value = 1)
            if goal in plan["goals"] and plan["goals"][goal] == 1:
                # Add the contribution to the total
                total_value += contrib_value

        # Add the domain variable and its calculated value to the result
        impact.append({
            "domain_variable": domain_var,
            "value": total_value
        })

    return impact


def set_quality_goals_for_scenario(quality_goals_def, constraint_options, perturbed=False):
    """
    Set quality goals for a specific scenario based on quality goal definitions and constraint options.
    Optionally applies perturbations to the constraint values.

    Args:
        quality_goals_def (list): List of quality goal definitions
        constraint_options (list): List of constraint options with values and perturbations
        perturbed (bool): Whether to apply perturbations to the constraint values

    Returns:
        list: Updated quality goals with appropriate constraint values

    Example:
        Input quality_goals_def:
        [
          {
            "id": "QG0",
            "domain_variable": "TotalCost",
            "relation_type": "max",
            "column_name": "cost_constraint"
          },
          ...
        ]

        Input constraint_options:
        [
          {"domain_variable": "cost_constraint", "value": 270, "perturbation": {"value": -10}},
          {"domain_variable": "effort_constraint", "value": 6, "perturbation": {"value": 2}},
          ...
        ]

        Output (perturbed=False):
        [
          {
            "id": "QG0",
            "domain_variable": "TotalCost",
            "relation_type": "max",
            "constraint": 270
          },
          ...
        ]

        Output (perturbed=True):
        [
          {
            "id": "QG0",
            "domain_variable": "TotalCost",
            "relation_type": "max",
            "constraint": 260  # 270 + (-10)
          },
          ...
        ]
    """
    # Create a mapping from column_name to constraint value and perturbation
    constraint_map = {}
    for option in constraint_options:
        domain_var = option["domain_variable"]
        constraint_map[domain_var] = {
            "value": option["value"],
            "perturbation": option["perturbation"]["value"] if "perturbation" in option else 0
        }

    # Create a copy of quality goals to avoid modifying the original
    updated_quality_goals = []

    # Update each quality goal with the appropriate constraint value
    for qg in quality_goals_def:
        # Get the column name that this quality goal refers to
        column_name = qg["column_name"]

        # Find the corresponding constraint option
        if column_name in constraint_map:
            # Get base value
            base_value = constraint_map[column_name]["value"]

            # Apply perturbation if required
            if perturbed:
                perturbation_value = constraint_map[column_name]["perturbation"]
                constraint_value = base_value + perturbation_value
            else:
                constraint_value = base_value

            # Create updated quality goal
            updated_qg = {
                "id": qg["id"],
                "domain_variable": qg["domain_variable"],
                "relation_type": qg["relation_type"],
                "constraint": constraint_value
            }

            updated_quality_goals.append(updated_qg)
        else:
            # If no matching constraint found, keep the original QG definition
            # but add a warning message
            print(f"Warning: No constraint option found for column '{column_name}' in quality goal '{qg['id']}'")
            updated_quality_goals.append(qg.copy())

    return updated_quality_goals



def check_plan_validity(plan_impact, quality_goals):
    """
    Check if a plan is valid according to the specified quality goals.

    Args:
        plan_impact (list): List of domain variables with their calculated values
        quality_goals (list): List of quality goals with constraints

    Returns:
        bool: True if the plan is valid (all quality goals are satisfied), False otherwise

    Example:
        Input plan_impact:
        [
          {"domain_variable": "TotalCost", "value": 200},
          {"domain_variable": "TotalEffort", "value": 4},
          {"domain_variable": "TimeSpent", "value": 7}
        ]

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
          },
          {
            "id": "QG2",
            "domain_variable": "TimeSpent",
            "relation_type": "max",
            "constraint": 9
          }
        ]

        Output:
        True (because 200 <= 270, 4 <= 6, and 7 <= 9)
    """
    # Create a map of domain variables to their impact values for easy lookup
    impact_map = {item["domain_variable"]: item["value"] for item in plan_impact}

    # Check each quality goal
    for qg in quality_goals:
        domain_var = qg["domain_variable"]
        relation_type = qg["relation_type"]
        constraint = qg["constraint"]

        # Skip if the domain variable is not in the impact map
        if domain_var not in impact_map:
            print(f"Warning: Domain variable '{domain_var}' from quality goal '{qg['id']}' not found in plan impact")
            continue

        # Get the actual value from the impact
        actual_value = impact_map[domain_var]

        # Check if the quality goal is satisfied based on the relation type
        if relation_type == "max":
            # For "max", the actual value must be less than or equal to the constraint
            if actual_value > constraint:
                return False
        # Add more relation types here if needed (min, equal, etc.)
        else:
            print(f"Warning: Unsupported relation type '{relation_type}' in quality goal '{qg['id']}'")

    # If we've made it here, all quality goals are satisfied
    return True


def filter_valid_plans(plans, plan_impacts, quality_goals):
    """
    Filter plans that satisfy all quality goals.

    Args:
        plans (dict): Dictionary of plans
        plan_impacts (dict): Dictionary of plan impacts, keyed by plan ID
        quality_goals (list): List of quality goals with constraints

    Returns:
        dict: Dictionary containing only the valid plans

    Example:
        Input plans:
        {
          "Plan0": {"id": "Plan0", "goals": {...}},
          "Plan1": {"id": "Plan1", "goals": {...}},
          ...
        }

        Input plan_impacts:
        {
          "Plan0": [
            {"domain_variable": "TotalCost", "value": 200},
            {"domain_variable": "TotalEffort", "value": 4},
            {"domain_variable": "TimeSpent", "value": 7}
          ],
          "Plan1": [
            {"domain_variable": "TotalCost", "value": 300},
            {"domain_variable": "TotalEffort", "value": 8},
            {"domain_variable": "TimeSpent", "value": 10}
          ],
          ...
        }

        Input quality_goals:
        [
          {"id": "QG0", "domain_variable": "TotalCost", "relation_type": "max", "constraint": 270},
          {"id": "QG1", "domain_variable": "TotalEffort", "relation_type": "max", "constraint": 6},
          {"id": "QG2", "domain_variable": "TimeSpent", "relation_type": "max", "constraint": 9}
        ]

        Output:
        {
          "Plan0": {"id": "Plan0", "goals": {...}}  # Only Plan0 is valid
        }
    """
    valid_plans = {}

    for plan_id, plan in plans.items():
        # Skip if we don't have impact data for this plan
        if plan_id not in plan_impacts:
            print(f"Warning: No impact data found for plan '{plan_id}'")
            continue

        # Get the impact for this plan
        impact = plan_impacts[plan_id]

        # Check if the plan is valid
        if check_plan_validity(impact, quality_goals):
            # Add to the valid plans dictionary
            valid_plans[plan_id] = plan

    return valid_plans
