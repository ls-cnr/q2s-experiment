#!/usr/bin/env python3
"""
Q2S Data Organizer
This script processes Q2S experiment results and creates organized data views
for analysis, including both aggregated and alpha-breakdown tables.
"""

import sys
import os
import pandas as pd
from datetime import datetime
from q2s_utils import load_json_config

def load_results(file_path):
    """
    Load results from a CSV file.

    Args:
        file_path (str): Path to the CSV results file

    Returns:
        DataFrame: Pandas DataFrame with the results, or None if loading failed
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} experiment results from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading results: {e}")
        return None

def identify_constraints_from_config(config, df):
    """
    Identify constraint types from the configuration file and map to actual columns.

    Args:
        config (dict): Configuration dictionary
        df (DataFrame): Input dataframe to check actual column names

    Returns:
        dict: Dictionary mapping constraint base names to their perturbation column names
    """
    constraints_map = {}

    if "quality_goals" in config:
        # Get all perturbation columns from data
        perturbation_cols = [col for col in df.columns if col.endswith("_perturbation")]

        for qg in config["quality_goals"]:
            domain_var = qg["domain_variable"]
            # Remove _constraint suffix to get base name
            constraint_base = domain_var.replace("_constraint", "")

            # Try to find matching perturbation column
            # First try exact match with _perturbation
            exact_match = f"{constraint_base}_perturbation"
            if exact_match in perturbation_cols:
                constraints_map[constraint_base] = exact_match
                continue

            # Try with _constraint_perturbation pattern
            constraint_match = f"{constraint_base}_constraint_perturbation"
            if constraint_match in perturbation_cols:
                constraints_map[constraint_base] = constraint_match
                continue

            # Try to find partial match (case insensitive)
            for col in perturbation_cols:
                if constraint_base.lower() in col.lower():
                    constraints_map[constraint_base] = col
                    break

    if constraints_map:
        print(f"Identified constraints from config: {list(constraints_map.keys())}")
        print(f"Mapped to perturbation columns: {list(constraints_map.values())}")
    else:
        print("No constraints could be mapped from config to actual data columns")

    return constraints_map

def identify_constraints_from_data(df):
    """
    Identify constraint types from the dataframe columns as fallback.

    Args:
        df (DataFrame): Input dataframe

    Returns:
        dict: Dictionary mapping constraint base names to their perturbation column names
    """
    perturbation_cols = [col for col in df.columns if col.endswith("_perturbation")]
    constraints_map = {}

    for col in perturbation_cols:
        # Remove _perturbation suffix to get constraint name
        constraint_name = col.replace("_perturbation", "")
        constraints_map[constraint_name] = col

    print(f"Identified constraints from data: {list(constraints_map.keys())}")
    print(f"Perturbation columns: {list(constraints_map.values())}")
    return constraints_map

def generate_aggregated_table(df, constraint_name, perturbation_col, output_dir):
    """
    Generate aggregated alpha table for a specific constraint.

    Args:
        df (DataFrame): Input dataframe
        constraint_name (str): Name of the constraint (e.g., 'cost', 'effort')
        perturbation_col (str): Actual perturbation column name in the data
        output_dir (str): Output directory for tables
    """
    if perturbation_col not in df.columns:
        print(f"Warning: {perturbation_col} not found in data")
        return

    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Get unique perturbation levels
    perturbation_levels = sorted(valid_df[perturbation_col].unique())

    # Initialize results table
    results = []

    for level in perturbation_levels:
        level_df = valid_df[valid_df[perturbation_col] == level]

        if len(level_df) == 0:
            continue

        row = {'Perturbation': level}

        # Calculate metrics for each strategy in desired order: Min, Score, Avg, Rnd
        strategies = ['Min', 'Score', 'Avg', 'Rnd']
        for strategy in strategies:
            success_col = f'{strategy}Plan_success'
            margin_col = f'{strategy}Plan_margins'

            if success_col in level_df.columns and margin_col in level_df.columns:
                success_rate = level_df[success_col].mean() * 100
                margin = level_df[margin_col].mean()

                row[f'{strategy}_Success_Rate'] = round(success_rate, 2)
                row[f'{strategy}_Margin'] = round(margin, 4)

        results.append(row)

    # Create DataFrame and save
    result_df = pd.DataFrame(results)
    filename = f"{constraint_name.upper()}_CONSTRAINT_PERTURBATIONS_WITH_AGGREGATED_ALPHA.csv"
    filepath = os.path.join(output_dir, filename)
    result_df.to_csv(filepath, index=False)
    print(f"Saved {filename}")

def generate_breakdown_table(df, constraint_name, perturbation_col, output_dir):
    """
    Generate alpha breakdown table for a specific constraint.

    Args:
        df (DataFrame): Input dataframe
        constraint_name (str): Name of the constraint (e.g., 'cost', 'effort')
        perturbation_col (str): Actual perturbation column name in the data
        output_dir (str): Output directory for tables
    """
    if perturbation_col not in df.columns:
        print(f"Warning: {perturbation_col} not found in data")
        return

    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Get unique perturbation levels and alpha values
    perturbation_levels = sorted(valid_df[perturbation_col].unique())
    alpha_values = sorted(valid_df['alpha'].unique())

    # Initialize results table
    results = []

    for level in perturbation_levels:
        level_df = valid_df[valid_df[perturbation_col] == level]

        if len(level_df) == 0:
            continue

        row = {'Perturbation': level}

        # Add Min strategy first
        if 'MinPlan_success' in level_df.columns and 'MinPlan_margins' in level_df.columns:
            success_rate = level_df['MinPlan_success'].mean() * 100
            margin = level_df['MinPlan_margins'].mean()
            row['Min_Success_Rate'] = round(success_rate, 2)
            row['Min_Margin'] = round(margin, 4)

        # Add Score strategy breakdown by alpha
        for alpha in alpha_values:
            alpha_level_df = level_df[level_df['alpha'] == alpha]

            if len(alpha_level_df) > 0:
                success_rate = alpha_level_df['ScorePlan_success'].mean() * 100
                margin = alpha_level_df['ScorePlan_margins'].mean()

                alpha_str = str(alpha).replace('.', '')
                row[f'Score_{alpha_str}_Success_Rate'] = round(success_rate, 2)
                row[f'Score_{alpha_str}_Margin'] = round(margin, 4)

        # Add Avg and Rnd strategies at the end
        end_strategies = ['Avg', 'Rnd']
        for strategy in end_strategies:
            success_col = f'{strategy}Plan_success'
            margin_col = f'{strategy}Plan_margins'

            if success_col in level_df.columns and margin_col in level_df.columns:
                success_rate = level_df[success_col].mean() * 100
                margin = level_df[margin_col].mean()

                row[f'{strategy}_Success_Rate'] = round(success_rate, 2)
                row[f'{strategy}_Margin'] = round(margin, 4)

        results.append(row)

    # Create DataFrame and save
    result_df = pd.DataFrame(results)
    filename = f"{constraint_name.upper()}_CONSTRAINT_PERTURBATIONS_WITH_BREAKDOWN_ALPHA.csv"
    filepath = os.path.join(output_dir, filename)
    result_df.to_csv(filepath, index=False)
    print(f"Saved {filename}")

def generate_limited_aggregated_table(df, constraint_name, perturbation_col, constraints_map, output_dir):
    """
    Generate limited aggregated alpha table (isolated perturbations only).

    Args:
        df (DataFrame): Input dataframe
        constraint_name (str): Name of the target constraint
        perturbation_col (str): Actual perturbation column name for this constraint
        constraints_map (dict): Dictionary mapping constraint names to perturbation columns
        output_dir (str): Output directory for tables
    """
    if perturbation_col not in df.columns:
        print(f"Warning: {perturbation_col} not found in data")
        return

    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Filter for isolated perturbations: target constraint can vary, others must be 0
    other_constraints = [c for c in constraints_map.keys() if c != constraint_name]

    # Build filter condition
    filter_condition = pd.Series([True] * len(valid_df), index=valid_df.index)

    for other_constraint in other_constraints:
        other_perturbation_col = constraints_map[other_constraint]
        if other_perturbation_col in valid_df.columns:
            filter_condition &= (valid_df[other_perturbation_col] == 0)

    # Apply filter
    isolated_df = valid_df[filter_condition].copy()

    if len(isolated_df) == 0:
        print(f"Warning: No isolated perturbation scenarios found for {constraint_name}")
        return

    print(f"Found {len(isolated_df)} isolated perturbation scenarios for {constraint_name}")

    # Get unique perturbation levels
    perturbation_levels = sorted(isolated_df[perturbation_col].unique())

    # Initialize results table
    results = []

    for level in perturbation_levels:
        level_df = isolated_df[isolated_df[perturbation_col] == level]

        if len(level_df) == 0:
            continue

        row = {'Perturbation': level}

        # Calculate metrics for each strategy in desired order: Min, Score, Avg, Rnd
        strategies = ['Min', 'Score', 'Avg', 'Rnd']
        for strategy in strategies:
            success_col = f'{strategy}Plan_success'
            margin_col = f'{strategy}Plan_margins'

            if success_col in level_df.columns and margin_col in level_df.columns:
                success_rate = level_df[success_col].mean() * 100
                margin = level_df[margin_col].mean()

                row[f'{strategy}_Success_Rate'] = round(success_rate, 2)
                row[f'{strategy}_Margin'] = round(margin, 4)

        results.append(row)

    # Create DataFrame and save
    result_df = pd.DataFrame(results)
    filename = f"{constraint_name.upper()}_CONSTRAINT_LIMITED_PERTURBATIONS_WITH_AGGREGATED_ALPHA.csv"
    filepath = os.path.join(output_dir, filename)
    result_df.to_csv(filepath, index=False)
    print(f"Saved {filename}")

def generate_limited_breakdown_table(df, constraint_name, perturbation_col, constraints_map, output_dir):
    """
    Generate limited alpha breakdown table (isolated perturbations only).

    Args:
        df (DataFrame): Input dataframe
        constraint_name (str): Name of the target constraint
        perturbation_col (str): Actual perturbation column name for this constraint
        constraints_map (dict): Dictionary mapping constraint names to perturbation columns
        output_dir (str): Output directory for tables
    """
    if perturbation_col not in df.columns:
        print(f"Warning: {perturbation_col} not found in data")
        return

    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Filter for isolated perturbations: target constraint can vary, others must be 0
    other_constraints = [c for c in constraints_map.keys() if c != constraint_name]

    # Build filter condition
    filter_condition = pd.Series([True] * len(valid_df), index=valid_df.index)

    for other_constraint in other_constraints:
        other_perturbation_col = constraints_map[other_constraint]
        if other_perturbation_col in valid_df.columns:
            filter_condition &= (valid_df[other_perturbation_col] == 0)

    # Apply filter
    isolated_df = valid_df[filter_condition].copy()

    if len(isolated_df) == 0:
        print(f"Warning: No isolated perturbation scenarios found for {constraint_name}")
        return

    print(f"Found {len(isolated_df)} isolated perturbation scenarios for {constraint_name}")

    # Get unique perturbation levels and alpha values
    perturbation_levels = sorted(isolated_df[perturbation_col].unique())
    alpha_values = sorted(isolated_df['alpha'].unique())

    # Initialize results table
    results = []

    for level in perturbation_levels:
        level_df = isolated_df[isolated_df[perturbation_col] == level]

        if len(level_df) == 0:
            continue

        row = {'Perturbation': level}

        # Add Min strategy first
        if 'MinPlan_success' in level_df.columns and 'MinPlan_margins' in level_df.columns:
            success_rate = level_df['MinPlan_success'].mean() * 100
            margin = level_df['MinPlan_margins'].mean()
            row['Min_Success_Rate'] = round(success_rate, 2)
            row['Min_Margin'] = round(margin, 4)

        # Add Score strategy breakdown by alpha
        for alpha in alpha_values:
            alpha_level_df = level_df[level_df['alpha'] == alpha]

            if len(alpha_level_df) > 0:
                success_rate = alpha_level_df['ScorePlan_success'].mean() * 100
                margin = alpha_level_df['ScorePlan_margins'].mean()

                alpha_str = str(alpha).replace('.', '')
                row[f'Score_{alpha_str}_Success_Rate'] = round(success_rate, 2)
                row[f'Score_{alpha_str}_Margin'] = round(margin, 4)

        # Add Avg and Rnd strategies at the end
        end_strategies = ['Avg', 'Rnd']
        for strategy in end_strategies:
            success_col = f'{strategy}Plan_success'
            margin_col = f'{strategy}Plan_margins'

            if success_col in level_df.columns and margin_col in level_df.columns:
                success_rate = level_df[success_col].mean() * 100
                margin = level_df[margin_col].mean()

                row[f'{strategy}_Success_Rate'] = round(success_rate, 2)
                row[f'{strategy}_Margin'] = round(margin, 4)

        results.append(row)

    # Create DataFrame and save
    result_df = pd.DataFrame(results)
    filename = f"{constraint_name.upper()}_CONSTRAINT_LIMITED_PERTURBATIONS_WITH_BREAKDOWN_ALPHA.csv"
    filepath = os.path.join(output_dir, filename)
    result_df.to_csv(filepath, index=False)
    print(f"Saved {filename}")

def organize_data(config_file):
    """
    Main function to organize experiment data into structured tables.

    Args:
        config_file (str): Path to the configuration file
    """
    print(f"Starting data organization with configuration from {config_file}")

    # Load configuration
    config = load_json_config(config_file)
    if config is None:
        print("Failed to load configuration. Exiting.")
        return

    # Get input and output paths from configuration
    output_dir = config["simulation_settings"]["output_directory"]
    scenarios_file = os.path.join(output_dir, config["simulation_settings"]["scenarios_filename"])

    print(f"Input file: {scenarios_file}")
    print(f"Output directory: {output_dir}")

    # Load the data
    df = load_results(scenarios_file)
    if df is None or len(df) == 0:
        print("No data to organize. Exiting.")
        return

    # Identify constraints and map to actual column names
    try:
        constraints_map = identify_constraints_from_config(config, df)
        if not constraints_map:
            print("Config mapping failed, falling back to data column analysis")
            constraints_map = identify_constraints_from_data(df)
    except Exception as e:
        print(f"Failed to identify constraints from config: {e}")
        constraints_map = identify_constraints_from_data(df)

    if not constraints_map:
        print("No constraints identified. Exiting.")
        return

    # Create tables subdirectory
    tables_dir = os.path.join(output_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)

    print(f"\n===== GENERATING TABLES FOR {len(constraints_map)} CONSTRAINTS =====")

    # Generate all table types for each constraint
    for constraint_name, perturbation_col in constraints_map.items():
        print(f"\nProcessing constraint: {constraint_name} (column: {perturbation_col})")

        # Generate all 4 table types
        generate_aggregated_table(df, constraint_name, perturbation_col, tables_dir)
        generate_breakdown_table(df, constraint_name, perturbation_col, tables_dir)
        generate_limited_aggregated_table(df, constraint_name, perturbation_col, constraints_map, tables_dir)
        generate_limited_breakdown_table(df, constraint_name, perturbation_col, constraints_map, tables_dir)

    print(f"\n===== DATA ORGANIZATION COMPLETE =====")
    print(f"All tables saved to: {tables_dir}")

def main():
    """Main function to handle command line arguments and run the data organization."""
    if len(sys.argv) != 2:
        print("Usage: python exp1_data_organizer.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    start_time = datetime.now()
    print(f"Starting Q2S data organization with configuration from {config_file}")

    organize_data(config_file)

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    print(f"Data organization completed in {elapsed_time}")

if __name__ == "__main__":
    main()
