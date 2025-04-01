#!/usr/bin/env python3
"""
Q2S Experiment Analyzer
This script analyzes the results of a Q2S experiment and generates visualizations and reports.
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

def print_dataset_statistics(df):
    """
    Print general statistics about the dataset.

    Args:
        df (DataFrame): Pandas DataFrame with experiment results
    """
    print("\n===== DATASET STATISTICS =====")
    print(f"Total scenarios: {len(df)}")

    # Get constraint columns (those ending with "_constraint")
    constraint_cols = [col for col in df.columns if col.endswith("_constraint")]

    # Get perturbation columns (those ending with "_perturbation")
    perturbation_cols = [col for col in df.columns if col.endswith("_perturbation")]

    # Statistics on constraints
    print("\nConstraints statistics:")
    for col in constraint_cols:
        print(f"  {col}: min={df[col].min()}, max={df[col].max()}, avg={df[col].mean():.1f}")

    # Statistics on perturbations
    print("\nPerturbation levels distribution:")
    for col in perturbation_cols:
        pert_counts = df[col].value_counts()
        print(f"  {col}:")
        for level, count in pert_counts.items():
            print(f"    {level}: {count} scenarios ({count/len(df)*100:.1f}%)")

    # Statistics on valid plans
    print(f"\nValid plans: min={df['num_valid_plans'].min()}, max={df['num_valid_plans'].max()}, avg={df['num_valid_plans'].mean():.1f}")
    no_valid_plans = len(df[df['num_valid_plans'] == 0])
    print(f"Scenarios with no valid plans: {no_valid_plans} ({no_valid_plans/len(df)*100:.1f}%)")

    # Statistics on alpha
    alpha_counts = df['alpha'].value_counts()
    print("\nAlpha values distribution:")
    for alpha, count in alpha_counts.items():
        print(f"  {alpha}: {count} scenarios ({count/len(df)*100:.1f}%)")

def compare_strategies(df):
    """
    Compare the performance of the four selection strategies.

    Args:
        df (DataFrame): Pandas DataFrame with experiment results

    Returns:
        DataFrame: DataFrame with summary statistics for each strategy
    """
    print("\n===== STRATEGY COMPARISON =====")

    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()
    print(f"Analyzing {len(valid_df)} scenarios with at least one valid plan")

    # Calculate average success rates and margins for each strategy
    strategies = ['Score', 'Avg', 'Min', 'Rnd']
    success_rates = {}
    margins = {}

    for strategy in strategies:
        success_rates[strategy] = valid_df[f'{strategy}Plan_success'].mean() * 100  # In percentage
        margins[strategy] = valid_df[f'{strategy}Plan_margins'].mean()

    # Print results sorted by success rate
    print("\nSuccess rates (percentage of plans that remain valid after perturbation):")
    for strategy, rate in sorted(success_rates.items(), key=lambda x: x[1], reverse=True):
        print(f"  {strategy}: {rate:.2f}%")

    print("\nAverage margins (distance from constraints after perturbation):")
    for strategy, margin in sorted(margins.items(), key=lambda x: x[1], reverse=True):
        print(f"  {strategy}: {margin:.4f}")

    # Create a dataframe with the results for more detailed analysis
    result_df = pd.DataFrame({
        'Strategy': strategies,
        'Success Rate (%)': [success_rates[s] for s in strategies],
        'Average Margin': [margins[s] for s in strategies]
    })

    return result_df

def analyze_by_perturbation_level(df):
    """
    Analyze how different strategies perform with different perturbation levels.

    Args:
        df (DataFrame): Pandas DataFrame with experiment results

    Returns:
        dict: Dictionary with results by perturbation level
    """
    print("\n===== ANALYSIS BY PERTURBATION LEVEL =====")

    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Get perturbation columns
    perturbation_cols = [col for col in df.columns if col.endswith("_perturbation")]

    # Create a dictionary to store results
    results = {}

    # For each perturbation type
    for pert_col in perturbation_cols:
        domain_var = pert_col.replace("_perturbation", "")
        print(f"\n{pert_col}:")
        results[pert_col] = {}

        # For each perturbation level
        for level in valid_df[pert_col].unique():
            level_df = valid_df[valid_df[pert_col] == level]

            if len(level_df) == 0:
                continue

            results[pert_col][level] = {}
            print(f"  {level} ({len(level_df)} scenarios):")

            # Calculate success rates for each strategy
            strategies = ['Score', 'Avg', 'Min', 'Rnd']
            for strategy in strategies:
                success_rate = level_df[f'{strategy}Plan_success'].mean() * 100  # In percentage
                margin = level_df[f'{strategy}Plan_margins'].mean()
                results[pert_col][level][strategy] = (success_rate, margin)

                print(f"    {strategy}: Success = {success_rate:.2f}%, Margin = {margin:.4f}")

    return results

def analyze_by_alpha(df):
    """
    Analyze how the alpha parameter affects Q2S performance.

    Args:
        df (DataFrame): Pandas DataFrame with experiment results
    """
    print("\n===== ANALYSIS BY ALPHA VALUE =====")

    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Group by alpha and calculate statistics
    alpha_groups = valid_df.groupby('alpha')

    for alpha, group in alpha_groups:
        print(f"\nAlpha = {alpha} ({len(group)} scenarios):")

        # Calculate Q2S success rates
        score_success = group['ScorePlan_success'].mean() * 100
        score_margin = group['ScorePlan_margins'].mean()

        # Compare with other strategies
        avg_success = group['AvgPlan_success'].mean() * 100
        min_success = group['MinPlan_success'].mean() * 100
        rnd_success = group['RndPlan_success'].mean() * 100

        print(f"  Score Strategy Success Rate: {score_success:.2f}%")
        print(f"  Score Strategy Average Margin: {score_margin:.4f}")
        print(f"  Comparison:")
        print(f"    Score vs Avg: {score_success - avg_success:+.2f}%")
        print(f"    Score vs Min: {score_success - min_success:+.2f}%")
        print(f"    Score vs Rnd: {score_success - rnd_success:+.2f}%")

def create_visualizations(df, output_dir):
    """
    Create visualizations to analyze the data.

    Args:
        df (DataFrame): Pandas DataFrame with experiment results
        output_dir (str): Directory where to save the visualizations
    """
    print("\n===== CREATING VISUALIZATIONS =====")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # 1. General comparison of strategies (success rate and average margin)
    plt.figure(figsize=(12, 5))

    # Success rate
    plt.subplot(1, 2, 1)
    strategies = ['Score', 'Avg', 'Min', 'Rnd']
    labels = ['Score', 'Avg', 'Min', 'Random']
    success_rates = [valid_df[f'{s}Plan_success'].mean() * 100 for s in strategies]

    bars = plt.bar(labels, success_rates, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
    plt.title('Success Rate by Strategy')
    plt.ylabel('Success Rate (%)')
    plt.ylim(0, 100)

    # Add labels to bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{height:.1f}%', ha='center', va='bottom')

    # Average margin
    plt.subplot(1, 2, 2)
    margins = [valid_df[f'{s}Plan_margins'].mean() for s in strategies]

    bars = plt.bar(labels, margins, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
    plt.title('Average Margin by Strategy')
    plt.ylabel('Average Margin')

    # Add labels to bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                 f'{height:.3f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'strategy_comparison.png'), dpi=300)
    print(f"Saved strategy_comparison.png")

    # 2. Analysis by perturbation level (success rate)
    perturbation_cols = [col for col in df.columns if col.endswith("_perturbation")]

    for pert_col in perturbation_cols:
        domain_var = pert_col.replace("_perturbation", "")
        plt.figure(figsize=(12, 6))

        # Get all unique perturbation levels
        all_levels = sorted(valid_df[pert_col].unique())

        # Create a data matrix for the chart
        pert_levels = []
        strategy_data = {s: [] for s in strategies}

        for level in all_levels:
            level_df = valid_df[valid_df[pert_col] == level]
            if len(level_df) == 0:
                continue

            pert_levels.append(level)
            for s in strategies:
                strategy_data[s].append(level_df[f'{s}Plan_success'].mean() * 100)

        # Create the bar chart
        bar_width = 0.2
        index = np.arange(len(pert_levels))

        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
        for i, (strategy, color) in enumerate(zip(strategies, colors)):
            bars = plt.bar(index + i*bar_width, strategy_data[strategy], bar_width,
                    label=labels[i], color=color)

            # Add labels to bars
            for bar in bars:
                height = bar.get_height()
                if height > 5:  # Only for significant values
                    plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                            f'{height:.0f}%', ha='center', va='bottom', fontsize=8)

        plt.xlabel('Perturbation Level')
        plt.ylabel('Success Rate (%)')
        plt.title(f'Success Rate by {domain_var} Perturbation Level')
        plt.xticks(index + bar_width * 1.5, pert_levels)
        plt.legend()
        plt.ylim(0, 105)  # Extra space for labels

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'success_by_{domain_var}_perturbation.png'), dpi=300)
        print(f"Saved success_by_{domain_var}_perturbation.png")

    # 3. Analysis by alpha (only for Score strategy)
    plt.figure(figsize=(10, 6))

    alpha_values = sorted(valid_df['alpha'].unique())
    score_success_by_alpha = [valid_df[valid_df['alpha'] == a]['ScorePlan_success'].mean() * 100 for a in alpha_values]

    plt.plot(alpha_values, score_success_by_alpha, 'o-', linewidth=2, markersize=8, color='#3498db')

    # Add labels to points
    for i, alpha in enumerate(alpha_values):
        plt.text(alpha, score_success_by_alpha[i] + 1, f'{score_success_by_alpha[i]:.1f}%',
                 ha='center', va='bottom')

    plt.xlabel('Alpha Value')
    plt.ylabel('Score Strategy Success Rate (%)')
    plt.title('Impact of Alpha on Score Strategy Performance')
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'score_by_alpha.png'), dpi=300)
    print(f"Saved score_by_alpha.png")

    # 4. Correlation between number of valid plans and success rate
    plt.figure(figsize=(10, 6))

    plt.scatter(valid_df['num_valid_plans'], valid_df['ScorePlan_success'] * 100,
                alpha=0.6, color='#3498db', label='Score')
    plt.scatter(valid_df['num_valid_plans'], valid_df['RndPlan_success'] * 100,
                alpha=0.6, color='#f39c12', label='Random')

    # Add trend lines
    z1 = np.polyfit(valid_df['num_valid_plans'], valid_df['ScorePlan_success'] * 100, 1)
    p1 = np.poly1d(z1)
    plt.plot(sorted(valid_df['num_valid_plans'].unique()),
             p1(sorted(valid_df['num_valid_plans'].unique())),
             '--', color='#3498db')

    z2 = np.polyfit(valid_df['num_valid_plans'], valid_df['RndPlan_success'] * 100, 1)
    p2 = np.poly1d(z2)
    plt.plot(sorted(valid_df['num_valid_plans'].unique()),
             p2(sorted(valid_df['num_valid_plans'].unique())),
             '--', color='#f39c12')

    plt.xlabel('Number of Valid Plans')
    plt.ylabel('Success Rate (%)')
    plt.title('Success Rate vs Number of Valid Plans')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'success_vs_valid_plans.png'), dpi=300)
    print(f"Saved success_vs_valid_plans.png")

    plt.close('all')
    print(f"All visualizations saved to {output_dir}")

def generate_summary_report(df, output_file):
    """
    Generate a summary report in Markdown format.

    Args:
        df (DataFrame): Pandas DataFrame with experiment results
        output_file (str): Path where to save the summary report

    Returns:
        DataFrame: DataFrame with summary statistics for each strategy
    """
    print("\n===== GENERATING SUMMARY REPORT =====")

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Calculate essential statistics
    strategies = ['Score', 'Avg', 'Min', 'Rnd']
    success_rates = {s: valid_df[f'{s}Plan_success'].mean() * 100 for s in strategies}
    margins = {s: valid_df[f'{s}Plan_margins'].mean() for s in strategies}

    # Sort strategies from best to worst
    sorted_by_success = sorted(success_rates.items(), key=lambda x: x[1], reverse=True)
    best_strategy = sorted_by_success[0][0]

    # Generate report content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# Q2S Experiment Summary Report
Generated on: {timestamp}

## Overview
- Total scenarios analyzed: {len(df)}
- Scenarios with valid plans: {len(valid_df)} ({len(valid_df)/len(df)*100:.1f}%)
- Average number of valid plans per scenario: {valid_df['num_valid_plans'].mean():.1f}

## Strategy Performance Comparison

### Success Rates (percentage of plans that remain valid after perturbation)
| Strategy | Success Rate (%) |
|----------|-----------------|
"""

    for strategy, rate in sorted_by_success:
        report += f"| {strategy} | {rate:.2f}% |\n"

    report += f"""
### Average Margins (distance from constraints after perturbation)
| Strategy | Average Margin |
|----------|---------------|
"""

    for strategy, margin in sorted(margins.items(), key=lambda x: x[1], reverse=True):
        report += f"| {strategy} | {margin:.4f} |\n"

    report += f"""
## Key Findings
- The best performing strategy is **{best_strategy}** with a success rate of {sorted_by_success[0][1]:.2f}%
- Compared to Random strategy baseline, {best_strategy} performs {success_rates[best_strategy] - success_rates['Rnd']:.2f}% better
"""

    # Add analysis by alpha if Score is the best
    if best_strategy == 'Score':
        alpha_groups = valid_df.groupby('alpha')
        best_alpha = 0
        best_alpha_success = 0

        report += "\n### Performance of Score Strategy by Alpha Value\n"
        report += "| Alpha | Success Rate (%) | Margin |\n"
        report += "|-------|-----------------|--------|\n"

        for alpha, group in alpha_groups:
            score_success = group['ScorePlan_success'].mean() * 100
            score_margin = group['ScorePlan_margins'].mean()

            if score_success > best_alpha_success:
                best_alpha = alpha
                best_alpha_success = score_success

            report += f"| {alpha} | {score_success:.2f}% | {score_margin:.4f} |\n"

        report += f"\nThe optimal alpha value appears to be **{best_alpha}** with a success rate of {best_alpha_success:.2f}%\n"

    # Add analysis for negative perturbations
    report += "\n## Performance Under Negative Perturbations\n"

    # Get perturbation columns
    perturbation_cols = [col for col in df.columns if col.endswith("_perturbation")]

    for pert_col in perturbation_cols:
        domain_var = pert_col.replace("_perturbation", "")

        # Find negative perturbation values (those less than 0)
        neg_perts = []
        for val in valid_df[pert_col].unique():
            try:
                if float(val) < 0:
                    neg_perts.append(val)
            except ValueError:
                # Skip values that can't be converted to float
                continue

        if neg_perts:
            neg_df = valid_df[valid_df[pert_col].isin(neg_perts)]

            if len(neg_df) > 0:
                report += f"\n### {domain_var} Negative Perturbations\n"
                report += "| Strategy | Success Rate (%) | Margin |\n"
                report += "|----------|-----------------|--------|\n"

                for strategy in strategies:
                    success_rate = neg_df[f'{strategy}Plan_success'].mean() * 100
                    margin = neg_df[f'{strategy}Plan_margins'].mean()
                    report += f"| {strategy} | {success_rate:.2f}% | {margin:.4f} |\n"

    # Conclusions
    report += f"""
## Conclusion
Based on the experiment results, the {best_strategy} strategy demonstrates the highest resilience to perturbations,
with a success rate of {sorted_by_success[0][1]:.2f}%. This indicates that {best_strategy}'s approach to plan selection
provides better robustness against uncertainties in the execution environment.
"""

    # Write report to file
    with open(output_file, 'w') as f:
        f.write(report)

    print(f"Summary report generated and saved to {output_file}")

    # Also generate a CSV version of the main statistics
    csv_file = output_file.replace('.md', '.csv')

    result_df = pd.DataFrame({
        'Strategy': strategies,
        'Success Rate (%)': [success_rates[s] for s in strategies],
        'Average Margin': [margins[s] for s in strategies]
    })

    result_df.to_csv(csv_file, index=False)
    print(f"Summary statistics saved to {csv_file}")

    return result_df

def analyze_results(config_file):
    """
    Main function to analyze experiment results.

    Args:
        config_file (str): Path to the configuration file

    Returns:
        DataFrame: DataFrame with summary statistics for each strategy
    """
    print(f"Starting analysis with configuration from {config_file}")

    # Load configuration
    config = load_json_config(config_file)
    if config is None:
        print("Failed to load configuration. Exiting.")
        return None

    # Get input and output paths from configuration
    output_dir = config["simulation_settings"]["output_directory"]
    scenarios_file = os.path.join(output_dir, config["simulation_settings"]["scenarios_filename"])
    results_file = os.path.join(output_dir, config["simulation_settings"]["results_filename"])

    print(f"Input file: {scenarios_file}")
    print(f"Output directory: {output_dir}")
    print(f"Results file: {results_file}")

    # Load the data
    df = load_results(scenarios_file)
    if df is None or len(df) == 0:
        print("No data to analyze. Exiting.")
        return None

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Run the analyses
    print_dataset_statistics(df)
    result_df = compare_strategies(df)

    # More detailed analyses
    analyze_by_perturbation_level(df)
    analyze_by_alpha(df)

    # Create visualizations
    viz_dir = os.path.join(output_dir, "visualizations")
    create_visualizations(df, viz_dir)

    # Generate summary report
    generate_summary_report(df, results_file)

    print(f"\nAnalysis complete. Results saved to {output_dir}")

    return result_df

def main():
    """Main function to handle command line arguments and run the analysis."""
    if len(sys.argv) != 2:
        print("Usage: python exp1_analyzer.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    start_time = datetime.now()
    print(f"Starting Q2S analysis with configuration from {config_file}")

    result_df = analyze_results(config_file)

    if result_df is not None:
        print("Analysis completed successfully.")
    else:
        print("Analysis failed.")
        sys.exit(1)

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    print(f"Analysis completed in {elapsed_time}")

if __name__ == "__main__":
    main()
