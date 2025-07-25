#!/usr/bin/env python3
"""
Q2S Data Analysis Pipeline
This script processes Q2S experiment results and creates single perturbation analysis tables
with breakdown by alpha values and margin variance calculations, plus multiple perturbation scenarios.
"""

import sys
import os
import pandas as pd
import numpy as np
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

def create_perturbation_score_mapping(config):
    """
    Create mapping from perturbation values to scores based on configuration.

    Args:
        config (dict): Configuration dictionary

    Returns:
        dict: Dictionary mapping perturbation values to scores
    """
    perturbation_mapping = {}

    # Try to find perturbation data in scenario_generator section first
    if "scenario_generator" in config and "constraint_options" in config["scenario_generator"]:
        for constraint_option in config["scenario_generator"]["constraint_options"]:
            if "perturbation" in constraint_option:
                # Create mapping for this constraint
                constraint_mapping = {}
                for pert in constraint_option["perturbation"]:
                    if "value" in pert and "score" in pert:
                        constraint_mapping[pert["value"]] = pert["score"]

                domain_var = constraint_option["domain_variable"]
                constraint_base = domain_var.replace("_constraint", "")
                perturbation_mapping[constraint_base] = constraint_mapping

    # Fallback: try quality_goals section
    elif "quality_goals" in config:
        for qg in config["quality_goals"]:
            if "perturbation" in qg:
                # Create mapping for this constraint
                constraint_mapping = {}
                for pert in qg["perturbation"]:
                    if "value" in pert and "score" in pert:
                        constraint_mapping[pert["value"]] = pert["score"]

                domain_var = qg["domain_variable"]
                constraint_base = domain_var.replace("_constraint", "")
                perturbation_mapping[constraint_base] = constraint_mapping

    print(f"Created perturbation score mapping: {perturbation_mapping}")
    return perturbation_mapping

def generate_multiple_perturbation_scenarios(df, config, constraints_map, output_dir):
    """
    Generate scenarios table with multiple perturbation score.

    Args:
        df (DataFrame): Input dataframe
        config (dict): Configuration dictionary
        constraints_map (dict): Dictionary mapping constraint names to perturbation columns
        output_dir (str): Output directory for tables
    """
    print("Generating multiple perturbation scenarios table...")

    # Create perturbation score mapping
    perturbation_mapping = create_perturbation_score_mapping(config)

    if not perturbation_mapping:
        print("Warning: No perturbation score mapping found in configuration")
        return

    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Calculate perturbation score for each scenario
    perturbation_scores = []

    for idx, row in valid_df.iterrows():
        total_score = 0

        for constraint_name, perturbation_col in constraints_map.items():
            if constraint_name in perturbation_mapping and perturbation_col in valid_df.columns:
                perturbation_value = row[perturbation_col]
                constraint_mapping = perturbation_mapping[constraint_name]

                if perturbation_value in constraint_mapping:
                    score = constraint_mapping[perturbation_value]
                    total_score += score
                else:
                    print(f"Warning: Perturbation value {perturbation_value} not found in mapping for {constraint_name}")

        perturbation_scores.append(total_score)

    # Add perturbation_score column
    valid_df = valid_df.copy()
    valid_df['perturbation_score'] = perturbation_scores

    # Select columns for the output table
    # Base columns (without perturbation columns)
    base_columns = ['ID', 'alpha']

    # Constraint columns (the base constraints, not perturbations)
    constraint_columns = []
    for constraint_name in constraints_map.keys():
        constraint_col = f"{constraint_name}_constraint"
        if constraint_col in valid_df.columns:
            constraint_columns.append(constraint_col)
        elif constraint_name in valid_df.columns:
            constraint_columns.append(constraint_name)

    # Perturbation score column
    perturbation_columns = ['perturbation_score']

    # Result columns (num_valid_plans and strategy results)
    result_columns = ['num_valid_plans']
    strategy_columns = []

    for strategy in ['Score', 'Avg', 'Min', 'Rnd']:
        plan_id_col = f'{strategy}Plan_ID'
        plan_success_col = f'{strategy}Plan_success'
        plan_margins_col = f'{strategy}Plan_margins'

        if all(col in valid_df.columns for col in [plan_id_col, plan_success_col, plan_margins_col]):
            strategy_columns.extend([plan_id_col, plan_success_col, plan_margins_col])

    # Combine all columns
    output_columns = base_columns + constraint_columns + perturbation_columns + result_columns + strategy_columns

    # Filter dataframe to include only existing columns
    existing_columns = [col for col in output_columns if col in valid_df.columns]
    result_df = valid_df[existing_columns].copy()

    # Sort by perturbation_score for better readability
    result_df = result_df.sort_values(['perturbation_score', 'alpha', 'ID']).reset_index(drop=True)

    # Save the table
    filename = "Scenarios_multiple_perturbation.csv"
    filepath = os.path.join(output_dir, filename)
    result_df.to_csv(filepath, index=False)

    print(f"Saved {filename}")
    print(f"Generated {len(result_df)} scenarios with perturbation scores ranging from {result_df['perturbation_score'].min()} to {result_df['perturbation_score'].max()}")

    # Print perturbation score distribution
    score_distribution = result_df['perturbation_score'].value_counts().sort_index()
    print("Perturbation score distribution:")
    for score, count in score_distribution.items():
        print(f"  Score {score}: {count} scenarios ({count/len(result_df)*100:.1f}%)")

def generate_single_perturbations_table(df, constraint_name, perturbation_col, constraints_map, output_dir):
    """
    Generate single perturbations table with alpha breakdown and margin variance.

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
            margin_avg = level_df['MinPlan_margins'].mean()
            margin_var = level_df['MinPlan_margins'].var()

            row['Min_Success_Rate'] = round(success_rate, 2)
            row['Min_Average_Margin'] = round(margin_avg, 4)
            row['Min_Variance_Margin'] = round(margin_var, 6)

        # Add Score strategy breakdown by alpha
        for alpha in alpha_values:
            alpha_level_df = level_df[level_df['alpha'] == alpha]

            if len(alpha_level_df) > 0:
                success_rate = alpha_level_df['ScorePlan_success'].mean() * 100
                margin_avg = alpha_level_df['ScorePlan_margins'].mean()
                margin_var = alpha_level_df['ScorePlan_margins'].var()

                alpha_str = str(alpha).replace('.', '')
                row[f'Score_{alpha_str}_Success_Rate'] = round(success_rate, 2)
                row[f'Score_{alpha_str}_Average_Margin'] = round(margin_avg, 4)
                row[f'Score_{alpha_str}_Variance_Margin'] = round(margin_var, 6)

        # Add Avg and Rnd strategies at the end
        end_strategies = ['Avg', 'Rnd']
        for strategy in end_strategies:
            success_col = f'{strategy}Plan_success'
            margin_col = f'{strategy}Plan_margins'

            if success_col in level_df.columns and margin_col in level_df.columns:
                success_rate = level_df[success_col].mean() * 100
                margin_avg = level_df[margin_col].mean()
                margin_var = level_df[margin_col].var()

                row[f'{strategy}_Success_Rate'] = round(success_rate, 2)
                row[f'{strategy}_Average_Margin'] = round(margin_avg, 4)
                row[f'{strategy}_Variance_Margin'] = round(margin_var, 6)

        results.append(row)

    # Create DataFrame and save
    result_df = pd.DataFrame(results)

    # Reorder columns to match the requested format
    base_columns = ['Perturbation']

    # Min columns
    min_columns = [col for col in result_df.columns if col.startswith('Min_')]

    # Score columns (sorted by alpha)
    score_columns = []
    for alpha in alpha_values:
        alpha_str = str(alpha).replace('.', '')
        score_cols = [col for col in result_df.columns if col.startswith(f'Score_{alpha_str}_')]
        score_columns.extend(score_cols)

    # Avg and Rnd columns
    avg_columns = [col for col in result_df.columns if col.startswith('Avg_')]
    rnd_columns = [col for col in result_df.columns if col.startswith('Rnd_')]

    # Combine all columns in the desired order
    ordered_columns = base_columns + min_columns + score_columns + avg_columns + rnd_columns

    # Reorder dataframe
    result_df = result_df[ordered_columns]

    # Save with simplified filename
    filename = f"{constraint_name.upper()}_SINGLE_PERTURBATIONS.csv"
    filepath = os.path.join(output_dir, filename)
    result_df.to_csv(filepath, index=False)
    print(f"Saved {filename}")

def organize_data(config_file):
    """
    Main function to organize experiment data into single perturbation tables.

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

    print(f"\n===== GENERATING SINGLE PERTURBATION TABLES FOR {len(constraints_map)} CONSTRAINTS =====")

    # Generate single perturbation table for each constraint
    for constraint_name, perturbation_col in constraints_map.items():
        print(f"\nProcessing constraint: {constraint_name} (column: {perturbation_col})")
        generate_single_perturbations_table(df, constraint_name, perturbation_col, constraints_map, tables_dir)

    print(f"\n===== GENERATING MULTIPLE PERTURBATION SCENARIOS TABLE =====")

    # Generate multiple perturbation scenarios table
    generate_multiple_perturbation_scenarios(df, config, constraints_map, tables_dir)

    print(f"\n===== DATA ORGANIZATION COMPLETE =====")
    print(f"All tables saved to: {tables_dir}")

def main():
    """Main function to handle command line arguments and run the data organization."""
    if len(sys.argv) != 2:
        print("Usage: python pipeline2_data_analysis.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    start_time = datetime.now()
    print(f"Starting Q2S analysis pipeline with configuration from {config_file}")

    organize_data(config_file)

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    print(f"Analysis pipeline completed in {elapsed_time}")

if __name__ == "__main__":
    main()
