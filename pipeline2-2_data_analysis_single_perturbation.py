#!/usr/bin/env python3
"""
Pipeline Step 2.2: Data Analysis Single Perturbation
This script processes the pre_processed_scenarios.csv file and creates filtered tables
for each quality goal, containing scenarios where only one quality goal is varied.

For each quality goal, it:
1. Filters rows where only that quality goal can have any perturbation value (including 0)
   while all other quality goals have perturbation = 0
2. Creates a filtered table: <quality_goal>_single_perturbation.csv
3. Creates a summary table: summary_<quality_goal>_single_perturbation.csv

This includes both the baseline case (perturbation = 0) and all perturbation levels
for the target quality goal, allowing comparison against the baseline.

The summary table contains aggregated statistics for each perturbation level:
- Success Rate: percentage of successful scenarios
- Average Margin: mean of margin values
- Variance Margin: variance of margin values

For all strategies: Min, Score_03, Score_05, Score_07, Avg, Rnd
"""

import argparse
import json
import pandas as pd
import os
from pathlib import Path


def load_config(config_file):
    """Load configuration from JSON file."""
    with open(config_file, 'r') as f:
        return json.load(f)


def get_perturbation_columns(config):
    """Extract perturbation column names from quality goals."""
    quality_goals = config.get('quality_goals', [])
    perturbation_columns = []

    for qg in quality_goals:
        domain_variable = qg.get('column_name', qg.get('domain_variable'))
        if domain_variable:
            perturbation_columns.append(f"{domain_variable}_perturbation")

    return perturbation_columns


def extract_quality_goal_name(domain_variable):
    """Extract the quality goal name from domain variable.

    Examples:
    - cost_constraint -> cost
    - effort_constraint -> effort
    - time_constraint -> time
    """
    if domain_variable.endswith('_constraint'):
        return domain_variable[:-11]  # Remove '_constraint'
    return domain_variable


def filter_single_perturbation(df, target_column, all_perturbation_columns):
    """Filter dataframe to keep only rows with single perturbation or baseline.

    This includes:
    - Rows where only the target quality goal is perturbed (any value including 0)
    - All other quality goals must have perturbation = 0

    Args:
        df: Input dataframe
        target_column: The perturbation column for the target quality goal
        all_perturbation_columns: List of all perturbation columns

    Returns:
        Filtered dataframe
    """
    # Start with all rows (target column can be any value)
    condition = pd.Series([True] * len(df), index=df.index)

    # Add conditions for other columns = 0
    for col in all_perturbation_columns:
        if col != target_column:
            condition = condition & (df[col] == 0)

    return df[condition].copy()


def calculate_strategy_stats(group_df, strategy_prefix):
    """Calculate success rate, average margin, and variance margin for a strategy."""
    success_col = f"{strategy_prefix}_success"
    margins_col = f"{strategy_prefix}_margins"

    if success_col not in group_df.columns or margins_col not in group_df.columns:
        return 0.0, 0.0, 0.0

    # Success rate (percentage)
    success_rate = (group_df[success_col].sum() / len(group_df)) * 100

    # Average margin
    avg_margin = group_df[margins_col].mean()

    # Variance margin
    var_margin = group_df[margins_col].var()

    return success_rate, avg_margin, var_margin


def create_summary_table(filtered_df, perturbation_col, qg_name, tables_dir):
    """Create summary statistics table for a quality goal."""

    # Group by perturbation value
    grouped = filtered_df.groupby(perturbation_col)

    summary_rows = []

    for perturbation_value, group_df in grouped:
        row = {'Perturbation': perturbation_value}

        # Define strategies and their column prefixes
        strategies = [
            ('Min', 'MinPlan'),
            ('Score_03', 'Score0_3Plan'),
            ('Score_05', 'Score0_5Plan'),
            ('Score_07', 'Score0_7Plan'),
            ('Avg', 'AvgPlan'),
            ('Rnd', 'RndPlan')
        ]

        # Calculate stats for each strategy
        for strategy_name, column_prefix in strategies:
            success_rate, avg_margin, var_margin = calculate_strategy_stats(group_df, column_prefix)

            row[f'{strategy_name}_Success_Rate'] = success_rate
            row[f'{strategy_name}_Average_Margin'] = avg_margin
            row[f'{strategy_name}_Variance_Margin'] = var_margin

        summary_rows.append(row)

    # Create summary dataframe
    summary_df = pd.DataFrame(summary_rows)

    # Sort by perturbation value
    summary_df = summary_df.sort_values('Perturbation')

    # Round numerical values for readability
    numeric_cols = [col for col in summary_df.columns if col != 'Perturbation']
    summary_df[numeric_cols] = summary_df[numeric_cols].round(6)

    # Save summary table
    summary_file = os.path.join(tables_dir, f"summary_{qg_name}_single_perturbation.csv")
    summary_df.to_csv(summary_file, index=False)

    print(f"Created summary_{qg_name}_single_perturbation.csv with {len(summary_df)} perturbation levels")

    return summary_file, len(summary_df)


def create_single_perturbation_tables(preprocessed_df, config, output_dir):
    """Create filtered tables for each quality goal."""

    # Get all perturbation columns
    perturbation_columns = get_perturbation_columns(config)

    # Create tables subdirectory
    tables_dir = os.path.join(output_dir, 'tables')
    os.makedirs(tables_dir, exist_ok=True)

    # Get quality goals
    quality_goals = config.get('quality_goals', [])

    results = {}

    for qg in quality_goals:
        domain_variable = qg.get('column_name', qg.get('domain_variable'))
        if not domain_variable:
            continue

        # Get the perturbation column name
        perturbation_col = f"{domain_variable}_perturbation"

        if perturbation_col not in preprocessed_df.columns:
            print(f"Warning: Column {perturbation_col} not found in data")
            continue

        # Filter for single perturbation
        filtered_df = filter_single_perturbation(
            preprocessed_df,
            perturbation_col,
            perturbation_columns
        )

        # Get quality goal name for filename
        qg_name = extract_quality_goal_name(domain_variable)

        # Save filtered table
        output_file = os.path.join(tables_dir, f"scenarios_{qg_name}_single_perturbation.csv")
        filtered_df.to_csv(output_file, index=False)

        # Create summary table
        summary_file, summary_rows = create_summary_table(
            filtered_df, perturbation_col, qg_name, tables_dir
        )

        results[qg_name] = {
            'file': output_file,
            'rows': len(filtered_df),
            'perturbation_column': perturbation_col,
            'summary_file': summary_file,
            'summary_rows': summary_rows
        }

        print(f"Created {qg_name}_single_perturbation.csv with {len(filtered_df)} rows")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Create single perturbation tables for each quality goal"
    )
    parser.add_argument(
        'config_file',
        help='Path to the configuration JSON file'
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config_file)

    # Get file paths
    output_dir = config['simulation_settings']['output_directory']
    preprocessed_file = os.path.join(output_dir, 'pre_processed_scenarios.csv')

    # Check if preprocessed file exists
    if not os.path.exists(preprocessed_file):
        raise FileNotFoundError(f"Pre-processed scenarios file not found: {preprocessed_file}")

    # Load preprocessed data
    print(f"Loading pre-processed scenarios from: {preprocessed_file}")
    preprocessed_df = pd.read_csv(preprocessed_file)

    print(f"Loaded {len(preprocessed_df)} pre-processed scenarios")
    print(f"Columns: {list(preprocessed_df.columns)}")

    # Create single perturbation tables
    print("\nCreating single perturbation tables...")
    results = create_single_perturbation_tables(preprocessed_df, config, output_dir)

    # Summary
    print(f"\nSummary:")
    print(f"Created {len(results)} single perturbation tables in: {os.path.join(output_dir, 'tables')}")

    for qg_name, info in results.items():
        print(f"- {qg_name}: {info['rows']} rows (column: {info['perturbation_column']})")
        print(f"  Summary: {info['summary_rows']} perturbation levels")


if __name__ == "__main__":
    main()
