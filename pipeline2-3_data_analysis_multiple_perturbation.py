#!/usr/bin/env python3
"""
Pipeline Step 2.3: Data Analysis Multiple Perturbation
This script processes the pre_processed_scenarios.csv file and creates:

1. scenarios_perturbation_severity.csv: A table with aggregated perturbation severity scores
2. summary_multiple_perturbation.csv: Summary statistics aggregated by perturbation_score

The perturbation_score is calculated by summing individual perturbation scores
for each quality goal, based on the value-to-score mapping in the configuration.

Both output files are saved in the 'tables' subdirectory.

The summary table contains averaged statistics for each perturbation score level:
- Success Rate: average success rate across scenarios with the same perturbation_score
- Average Margin: average margin values across scenarios with the same perturbation_score

For all strategies: Min, Score_03, Score_05, Score_07, Avg, Rnd
"""

import argparse
import json
import pandas as pd
import os


def load_config(config_file):
    """Load configuration from JSON file."""
    with open(config_file, 'r') as f:
        return json.load(f)


def create_perturbation_mappings(config):
    """Create value-to-score mappings for each quality goal."""
    mappings = {}

    scenario_gen = config.get('scenario_generator', {})
    constraint_options = scenario_gen.get('constraint_options', [])

    for constraint_opt in constraint_options:
        domain_variable = constraint_opt['domain_variable']
        perturbations = constraint_opt['perturbation']

        # Create value -> score mapping
        value_to_score = {}
        for p in perturbations:
            value_to_score[p['value']] = p['score']

        mappings[domain_variable] = value_to_score

    return mappings


def calculate_perturbation_score(row, perturbation_mappings):
    """Calculate the total perturbation score for a row."""
    total_score = 0

    for domain_variable, mapping in perturbation_mappings.items():
        perturbation_col = f"{domain_variable}_perturbation"

        if perturbation_col in row:
            perturbation_value = row[perturbation_col]
            if perturbation_value in mapping:
                total_score += mapping[perturbation_value]
            else:
                print(f"Warning: Perturbation value {perturbation_value} not found in mapping for {domain_variable}")

    return total_score


def process_perturbation_severity(preprocessed_df, config):
    """Process the dataframe to add perturbation_score and remove individual perturbation columns."""

    # Create perturbation mappings
    perturbation_mappings = create_perturbation_mappings(config)

    print("Created perturbation mappings:")
    for domain_var, mapping in perturbation_mappings.items():
        print(f"  {domain_var}: {mapping}")

    # Make a copy of the dataframe
    result_df = preprocessed_df.copy()

    # Calculate perturbation_score for each row
    result_df['perturbation_score'] = result_df.apply(
        lambda row: calculate_perturbation_score(row, perturbation_mappings),
        axis=1
    )

    # Identify perturbation columns to remove
    perturbation_cols_to_remove = []
    for domain_variable in perturbation_mappings.keys():
        perturbation_col = f"{domain_variable}_perturbation"
        if perturbation_col in result_df.columns:
            perturbation_cols_to_remove.append(perturbation_col)

    # Remove individual perturbation columns
    result_df = result_df.drop(columns=perturbation_cols_to_remove)

    print(f"Removed columns: {perturbation_cols_to_remove}")
    print(f"Added column: perturbation_score")

    # Reorder columns to match desired format
    # ID,cost_constraint,effort_constraint,time_constraint,perturbation_score,num_valid_plans,...
    desired_order = ['ID']

    # Add constraint columns
    for domain_variable in perturbation_mappings.keys():
        if domain_variable in result_df.columns:
            desired_order.append(domain_variable)

    # Add perturbation_score and num_valid_plans
    desired_order.extend(['perturbation_score', 'num_valid_plans'])

    # Add remaining columns (strategy results)
    remaining_cols = [col for col in result_df.columns if col not in desired_order]
    desired_order.extend(remaining_cols)

    # Reorder columns
    result_df = result_df[desired_order]

    return result_df


def create_summary_multiple_perturbation(severity_df, output_dir):
    """Create summary table aggregated by perturbation_score."""

    # Create tables subdirectory
    tables_dir = os.path.join(output_dir, 'tables')
    os.makedirs(tables_dir, exist_ok=True)

    # Group by perturbation_score
    grouped = severity_df.groupby('perturbation_score')

    summary_rows = []

    # Define strategies and their column prefixes
    strategies = [
        ('Min', 'MinPlan'),
        ('Score_03', 'Score0_3Plan'),
        ('Score_05', 'Score0_5Plan'),
        ('Score_07', 'Score0_7Plan'),
        ('Avg', 'AvgPlan'),
        ('Rnd', 'RndPlan')
    ]

    for perturbation_score, group_df in grouped:
        row = {'perturbation_score': perturbation_score}

        # Calculate average success rate and average margin for each strategy
        for strategy_name, column_prefix in strategies:
            success_col = f"{column_prefix}_success"
            margins_col = f"{column_prefix}_margins"

            if success_col in group_df.columns and margins_col in group_df.columns:
                # Success rate (mean of success values, already 0/1, so mean gives the rate)
                success_rate = group_df[success_col].mean() * 100  # Convert to percentage

                # Average margin (mean of margin values)
                avg_margin = group_df[margins_col].mean()

                row[f'{strategy_name}_Success_Rate'] = success_rate
                row[f'{strategy_name}_Average_Margin'] = avg_margin
            else:
                row[f'{strategy_name}_Success_Rate'] = 0.0
                row[f'{strategy_name}_Average_Margin'] = 0.0

        summary_rows.append(row)

    # Create summary dataframe
    summary_df = pd.DataFrame(summary_rows)

    # Sort by perturbation_score
    summary_df = summary_df.sort_values('perturbation_score')

    # Round numerical values for readability
    numeric_cols = [col for col in summary_df.columns if col != 'perturbation_score']
    summary_df[numeric_cols] = summary_df[numeric_cols].round(6)

    # Save summary table
    summary_file = os.path.join(tables_dir, 'summary_multiple_perturbation.csv')
    summary_df.to_csv(summary_file, index=False)

    print(f"Created summary_multiple_perturbation.csv with {len(summary_df)} perturbation levels")

    return summary_file, len(summary_df)


def main():
    parser = argparse.ArgumentParser(
        description="Process perturbation severity by aggregating individual perturbation scores"
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
    print(f"Input columns: {list(preprocessed_df.columns)}")

    # Process perturbation severity
    print("\nProcessing perturbation severity...")
    severity_df = process_perturbation_severity(preprocessed_df, config)

    # Create tables subdirectory
    tables_dir = os.path.join(output_dir, 'tables')
    os.makedirs(tables_dir, exist_ok=True)

    # Save result in tables subdirectory
    output_file = os.path.join(tables_dir, 'scenarios_perturbation_severity.csv')
    severity_df.to_csv(output_file, index=False)

    print(f"\nPerturbation severity data saved to: {output_file}")
    print(f"Generated {len(severity_df)} scenarios")
    print(f"Output columns: {list(severity_df.columns)}")

    # Show perturbation score distribution
    print(f"\nPerturbation score distribution:")
    score_counts = severity_df['perturbation_score'].value_counts().sort_index()
    for score, count in score_counts.items():
        print(f"  Score {score}: {count} scenarios")

    # Create summary table
    print("\nCreating summary table...")
    summary_file, summary_rows = create_summary_multiple_perturbation(severity_df, output_dir)

    print(f"Summary table saved to: {summary_file}")
    print(f"Summary contains {summary_rows} perturbation score levels")


if __name__ == "__main__":
    main()
