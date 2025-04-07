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
import math

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

    # Calculate average success rates, margins and margin variance for each strategy
    strategies = ['Score', 'Avg', 'Min', 'Rnd']
    success_rates = {}
    margins = {}
    margin_variances = {}  # New dictionary for margin variances

    for strategy in strategies:
        # Calculate success rate (percentage of successful plans)
        success_rates[strategy] = valid_df[f'{strategy}Plan_success'].mean() * 100

        # Calculate average margin
        # First, we need to replace margins of unsuccessful plans (which are 0) with NaN
        # to calculate the correct statistics only for successful plans
        successful_margins = valid_df.loc[valid_df[f'{strategy}Plan_success'] == 1, f'{strategy}Plan_margins']

        # Calculate mean and variance if there are any successful plans
        if len(successful_margins) > 0:
            margins[strategy] = successful_margins.mean()
            margin_variances[strategy] = successful_margins.var()  # Calculate variance
        else:
            margins[strategy] = 0
            margin_variances[strategy] = 0

    # Print results sorted by success rate
    print("\nSuccess rates (percentage of plans that remain valid after perturbation):")
    for strategy, rate in sorted(success_rates.items(), key=lambda x: x[1], reverse=True):
        print(f"  {strategy}: {rate:.2f}%")

    print("\nAverage margins (distance from constraints after perturbation):")
    for strategy, margin in sorted(margins.items(), key=lambda x: x[1], reverse=True):
        print(f"  {strategy}: {margin:.4f}")

    print("\nMargin variances (variability of margins):")
    for strategy, variance in sorted(margin_variances.items(), key=lambda x: x[1]):
        print(f"  {strategy}: {variance:.6f}")

    # Create a dataframe with the results for more detailed analysis
    result_df = pd.DataFrame({
        'Strategy': strategies,
        'Success Rate (%)': [success_rates[s] for s in strategies],
        'Average Margin': [margins[s] for s in strategies],
        'Margin Variance': [margin_variances[s] for s in strategies]
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

def analyze_by_perturbation_level_with_alfas(df):
    """
    Analyze how the Score strategy with different alpha values performs under various perturbation levels.

    Args:
        df (DataFrame): Pandas DataFrame with experiment results

    Returns:
        dict: Dictionary with results by perturbation level and alpha
    """
    print("\n===== ANALYSIS BY PERTURBATION LEVEL WITH ALPHA BREAKDOWN =====")

    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Get perturbation columns
    perturbation_cols = [col for col in df.columns if col.endswith("_perturbation")]

    # Get alpha values
    alpha_values = sorted(valid_df['alpha'].unique())

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

            # Calculate success rates for Avg, Min, and Rnd strategies
            other_strategies = ['Avg', 'Min', 'Rnd']
            for strategy in other_strategies:
                success_rate = level_df[f'{strategy}Plan_success'].mean() * 100  # In percentage
                margin = level_df[f'{strategy}Plan_margins'].mean()
                results[pert_col][level][strategy] = (success_rate, margin)

                print(f"    {strategy}: Success = {success_rate:.2f}%, Margin = {margin:.4f}")

            # Calculate success rates for Score strategy with different alpha values
            print("    Score strategy by alpha:")
            for alpha in alpha_values:
                alpha_level_df = level_df[level_df['alpha'] == alpha]

                if len(alpha_level_df) == 0:
                    continue

                success_rate = alpha_level_df['ScorePlan_success'].mean() * 100
                margin = alpha_level_df['ScorePlan_margins'].mean()
                results[pert_col][level][f'Score (α={alpha})'] = (success_rate, margin)

                print(f"      α={alpha}: Success = {success_rate:.2f}%, Margin = {margin:.4f}")

    return results

def create_perturbation_alpha_charts(df, output_dir, domain_var_display_names):
    """
    Create charts showing Score strategy performance by alpha for each perturbation level.

    Args:
        df (DataFrame): Pandas DataFrame with experiment results
        output_dir (str): Directory where to save visualizations
    """
    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Get alpha values
    alpha_values = sorted(valid_df['alpha'].unique())

    # Get perturbation columns
    perturbation_cols = [col for col in df.columns if col.endswith("_perturbation")]

    # For each perturbation type
    for pert_col in perturbation_cols:
        domain_var = pert_col.replace("_perturbation", "")
        display_name = domain_var_display_names.get(domain_var, domain_var)

        # Get unique perturbation levels for this type
        pert_levels = sorted(valid_df[pert_col].unique())

        # Create a figure with a grid of charts, one for each alpha value
        plt.figure(figsize=(max(len(alpha_values) * 5, 10), 8))

        # Define colors for different strategies
        colors = {
            'Score': '#3498db',
            'Avg': '#2ecc71',
            'Min': '#e74c3c',
            'Rnd': '#f39c12'
        }

        # Initialize data structures for the chart
        data_by_alpha = {}
        for alpha in alpha_values:
            data_by_alpha[alpha] = {
                'levels': [],
                'score_success': [],
                'avg_success': [],
                'min_success': [],
                'rnd_success': []
            }

        # Collect data for each perturbation level
        for level in pert_levels:
            level_df = valid_df[valid_df[pert_col] == level]
            if len(level_df) == 0:
                continue

            # Calculate success rates for each alpha value
            for alpha in alpha_values:
                alpha_level_df = level_df[level_df['alpha'] == alpha]
                if len(alpha_level_df) == 0:
                    continue

                data_by_alpha[alpha]['levels'].append(level)
                data_by_alpha[alpha]['score_success'].append(alpha_level_df['ScorePlan_success'].mean() * 100)
                data_by_alpha[alpha]['avg_success'].append(alpha_level_df['AvgPlan_success'].mean() * 100)
                data_by_alpha[alpha]['min_success'].append(alpha_level_df['MinPlan_success'].mean() * 100)
                data_by_alpha[alpha]['rnd_success'].append(alpha_level_df['RndPlan_success'].mean() * 100)

        # Create subplots for each alpha
        num_alphas = len(alpha_values)
        fig, axes = plt.subplots(1, num_alphas, figsize=(num_alphas * 6, 6), sharey=True)
        if num_alphas == 1:
            axes = [axes]  # Ensure axes is a list even with one subplot

        # Plot data for each alpha
        for i, alpha in enumerate(alpha_values):
            ax = axes[i]
            data = data_by_alpha[alpha]

            # Skip if no data for this alpha
            if not data['levels']:
                continue

            # Set up bar positions
            x = np.arange(len(data['levels']))
            width = 0.2

            # Plot bars for each strategy
            ax.bar(x - width*1.5, data['score_success'], width, label='Score', color=colors['Score'])
            ax.bar(x - width/2, data['avg_success'], width, label='Avg', color=colors['Avg'])
            ax.bar(x + width/2, data['min_success'], width, label='Min', color=colors['Min'])
            ax.bar(x + width*1.5, data['rnd_success'], width, label='Rnd', color=colors['Rnd'])

            # Set labels and title
            ax.set_xlabel('Perturbation Level')
            if i == 0:
                ax.set_ylabel('Success Rate (%)')
            ax.set_title(f'α = {alpha}')
            ax.set_xticks(x)
            ax.set_xticklabels(data['levels'], rotation=45 if len(data['levels']) > 3 else 0)
            ax.set_ylim(0, 100)
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            # Add legend only for the first subplot
            if i == 0:
                ax.legend()

        fig.suptitle(f'Success Rate by {display_name} Perturbation Level and Alpha', fontsize=16)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'success_by_{domain_var}_perturbation_alpha.png'), dpi=300)
        plt.close()
        print(f"Saved success_by_{domain_var}_perturbation_alpha.png")

def analyze_score_by_alpha_vs_others(df):
    """
    Analyze how the Score strategy with different alpha values compares to other strategies.

    Args:
        df (DataFrame): Pandas DataFrame with experiment results
    """
    print("\n===== ANALYSIS OF SCORE STRATEGY BY ALPHA VS OTHER STRATEGIES =====")

    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Get all alpha values
    alpha_values = sorted(valid_df['alpha'].unique())

    # Create a comparison table
    print("\nSuccess rates by alpha value vs other strategies:")
    print(f"{'Alpha':<10} | {'Score':<10} | {'Avg':<10} | {'Min':<10} | {'Rnd':<10}")
    print("-" * 60)

    # Store data for visualization
    alpha_labels = []
    score_success_by_alpha = []
    avg_success = []
    min_success = []
    rnd_success = []

    # Calculate success rates for each alpha
    for alpha in alpha_values:
        alpha_df = valid_df[valid_df['alpha'] == alpha]

        if len(alpha_df) == 0:
            continue

        alpha_labels.append(f"Score (α={alpha})")

        # Calculate success rates
        score_success = alpha_df['ScorePlan_success'].mean() * 100
        avg_success_rate = alpha_df['AvgPlan_success'].mean() * 100
        min_success_rate = alpha_df['MinPlan_success'].mean() * 100
        rnd_success_rate = alpha_df['RndPlan_success'].mean() * 100

        # Store for visualization
        score_success_by_alpha.append(score_success)
        avg_success.append(avg_success_rate)
        min_success.append(min_success_rate)
        rnd_success.append(rnd_success_rate)

        # Print comparison table
        print(f"{alpha:<10.1f} | {score_success:<10.2f}% | {avg_success_rate:<10.2f}% | {min_success_rate:<10.2f}% | {rnd_success_rate:<10.2f}%")

    return {
        'alpha_labels': alpha_labels,
        'score_success_by_alpha': score_success_by_alpha,
        'avg_success': avg_success,
        'min_success': min_success,
        'rnd_success': rnd_success
    }

def create_score_alpha_comparison_chart(data, output_dir):
    """
    Create a chart comparing Score strategy with different alpha values to other strategies.

    Args:
        data (dict): Data returned by analyze_score_by_alpha_vs_others
        output_dir (str): Directory where to save the visualization
    """
    plt.figure(figsize=(12, 7))

    # Collect all data
    labels = data['alpha_labels'] + ['Avg', 'Min', 'Random']

    # Use the average of each strategy across all alpha scenarios
    avg_of_avg = sum(data['avg_success']) / len(data['avg_success'])
    avg_of_min = sum(data['min_success']) / len(data['min_success'])
    avg_of_rnd = sum(data['rnd_success']) / len(data['rnd_success'])

    success_rates = data['score_success_by_alpha'] + [avg_of_avg, avg_of_min, avg_of_rnd]

    # Define colors: blues for Score with different alphas, then other colors
    alpha_colors = ['#1f77b4', '#4292c6', '#6baed6', '#9ecae1'][:len(data['alpha_labels'])]
    other_colors = ['#2ecc71', '#e74c3c', '#f39c12']
    colors = alpha_colors + other_colors

    # Create the bar chart
    bars = plt.bar(labels, success_rates, color=colors)

    # Add labels to bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{height:.1f}%', ha='center', va='bottom')

    plt.title('Success Rate: Score Strategy by Alpha vs Other Strategies')
    plt.ylabel('Success Rate (%)')
    plt.ylim(0, max(success_rates) * 1.15)  # Add some space for labels
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'score_alpha_vs_others.png'), dpi=300)
    print("Saved score_alpha_vs_others.png")

def create_perturbation_alpha_allin_charts(df, output_dir, domain_var_display_names):
    """
    Create charts showing Score strategy with all alpha values and other strategies
    for each perturbation level, all in the same chart.

    Args:
        df (DataFrame): Pandas DataFrame with experiment results
        output_dir (str): Directory where to save visualizations
    """
    # Filter scenarios with at least one valid plan
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Get alpha values
    alpha_values = sorted(valid_df['alpha'].unique())

    # Get perturbation columns
    perturbation_cols = [col for col in df.columns if col.endswith("_perturbation")]

    # For each perturbation type
    for pert_col in perturbation_cols:
        domain_var = pert_col.replace("_perturbation", "")
        display_name = domain_var_display_names.get(domain_var, domain_var)

        # Get unique perturbation levels for this type
        pert_levels = sorted(valid_df[pert_col].unique())

        # Define colors for different strategies
        colors = {
            'Score_0.3': '#1f77b4',  # Dark blue
            'Score_0.5': '#6baed6',  # Medium blue
            'Score_0.7': '#c6dbef',  # Light blue
            'Avg': '#2ecc71',        # Green
            'Min': '#e74c3c',        # Red
            'Rnd': '#f39c12'         # Orange
        }

        # Data structure to hold the results
        results = {}
        max_success_rate = 0  # Track maximum success rate for y-axis scaling

        # For each perturbation level
        for level in pert_levels:
            level_df = valid_df[valid_df[pert_col] == level]
            if len(level_df) == 0:
                continue

            results[level] = {
                'Score_0.3': 0,
                'Score_0.5': 0,
                'Score_0.7': 0,
                'Avg': level_df['AvgPlan_success'].mean() * 100,
                'Min': level_df['MinPlan_success'].mean() * 100,
                'Rnd': level_df['RndPlan_success'].mean() * 100
            }

            # Update max success rate
            max_success_rate = max(max_success_rate,
                                  results[level]['Avg'],
                                  results[level]['Min'],
                                  results[level]['Rnd'])

            # Get Score success rates for each alpha
            for alpha in alpha_values:
                alpha_level_df = level_df[level_df['alpha'] == alpha]
                if len(alpha_level_df) > 0:
                    score_success = alpha_level_df['ScorePlan_success'].mean() * 100
                    results[level][f'Score_{alpha}'] = score_success
                    # Update max success rate
                    max_success_rate = max(max_success_rate, score_success)

        # Calculate appropriate y-axis maximum (round up to the next multiple of 10)
        y_max = math.ceil(max_success_rate / 10) * 10

        # Create the bar chart with proper spacing
        fig, ax = plt.subplots(figsize=(max(len(pert_levels) * 3, 12), 8))

        # Increase spacing between groups
        x = np.arange(len(pert_levels)) * 1.5  # the label locations with more space
        width = 0.2  # width of the bars - wider bars

        # Define offsets for each strategy
        offsets = [-2.5*width, -1.5*width, -0.5*width, 0.5*width, 1.5*width, 2.5*width]

        # Plot bars for each strategy
        bars = []
        labels = []

        # Strategy categories to plot
        strategies_to_plot = [f'Score_{alpha}' for alpha in alpha_values] + ['Avg', 'Min', 'Rnd']

        # Plot all strategies
        for i, strategy in enumerate(strategies_to_plot):
            strategy_values = [results[level][strategy] if level in results else 0 for level in pert_levels]

            # Get proper label
            if strategy.startswith('Score_'):
                alpha = strategy.split('_')[1]
                label = f'Score (α={alpha})'
            else:
                label = strategy

            # Create bar
            bar = ax.bar(x + offsets[i], strategy_values, width, color=colors[strategy])
            bars.append(bar)
            labels.append(label)

        # Set labels, title and legend
        ax.set_xlabel('Perturbation Level', fontsize=12)
        ax.set_ylabel('Success Rate (%)', fontsize=12)
        ax.set_title(f'Success Rate by {display_name} Perturbation Level', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(pert_levels, fontsize=11)

        # Set y-axis to dynamically calculated maximum
        ax.set_ylim(0, y_max)

        ax.legend(labels=labels, loc='upper right', fontsize=11)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'success_by_{domain_var}_perturbation_all_alphas.png'), dpi=300)
        plt.close()
        print(f"Saved success_by_{domain_var}_perturbation_all_alphas.png")

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

def create_visualizations(df, output_dir,domain_var_display_names):
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
        display_name = domain_var_display_names.get(domain_var, domain_var)

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
        plt.title(f'Success Rate by {display_name} Perturbation Level')
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
    success_rates = {}
    margins = {}
    margin_variances = {}

    for strategy in strategies:
        # Success rates
        success_rates[strategy] = valid_df[f'{strategy}Plan_success'].mean() * 100

        # Calculate margins and variance only for successful plans
        successful_margins = valid_df.loc[valid_df[f'{strategy}Plan_success'] == 1, f'{strategy}Plan_margins']
        if len(successful_margins) > 0:
            margins[strategy] = successful_margins.mean()
            margin_variances[strategy] = successful_margins.var()
        else:
            margins[strategy] = 0
            margin_variances[strategy] = 0

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
| Strategy | Average Margin | Margin Variance |
|----------|---------------|-----------------|
"""

    for strategy, margin in sorted(margins.items(), key=lambda x: x[1], reverse=True):
        variance = margin_variances[strategy]
        report += f"| {strategy} | {margin:.4f} | {variance:.6f} |\n"

    report += f"""
## Key Findings
- The best performing strategy is **{best_strategy}** with a success rate of {sorted_by_success[0][1]:.2f}%
- Compared to Random strategy baseline, {best_strategy} performs {success_rates[best_strategy] - success_rates['Rnd']:.2f}% better
- {best_strategy} has a margin variance of {margin_variances[best_strategy]:.6f}, which indicates {'low' if margin_variances[best_strategy] < 0.001 else 'moderate' if margin_variances[best_strategy] < 0.01 else 'high'} variability in constraint satisfaction
"""

    # Add analysis by alpha if Score is the best
    if best_strategy == 'Score':
        alpha_groups = valid_df.groupby('alpha')
        best_alpha = 0
        best_alpha_success = 0

        report += "\n### Performance of Score Strategy by Alpha Value\n"
        report += "| Alpha | Success Rate (%) | Margin | Margin Variance |\n"
        report += "|-------|-----------------|--------|----------------|\n"

        for alpha, group in alpha_groups:
            score_success = group['ScorePlan_success'].mean() * 100

            # Calculate margin and variance for successful plans only
            successful_margins = group.loc[group['ScorePlan_success'] == 1, 'ScorePlan_margins']
            score_margin = successful_margins.mean() if len(successful_margins) > 0 else 0
            score_variance = successful_margins.var() if len(successful_margins) > 0 else 0

            if score_success > best_alpha_success:
                best_alpha = alpha
                best_alpha_success = score_success

            report += f"| {alpha} | {score_success:.2f}% | {score_margin:.4f} | {score_variance:.6f} |\n"

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
                report += "| Strategy | Success Rate (%) | Margin | Margin Variance |\n"
                report += "|----------|-----------------|--------|----------------|\n"

                for strategy in strategies:
                    success_rate = neg_df[f'{strategy}Plan_success'].mean() * 100

                    # Calculate margin and variance for successful plans only
                    successful_margins = neg_df.loc[neg_df[f'{strategy}Plan_success'] == 1, f'{strategy}Plan_margins']
                    margin = successful_margins.mean() if len(successful_margins) > 0 else 0
                    variance = successful_margins.var() if len(successful_margins) > 0 else 0

                    report += f"| {strategy} | {success_rate:.2f}% | {margin:.4f} | {variance:.6f} |\n"

    # Conclusions
    report += f"""
## Conclusion
Based on the experiment results, the {best_strategy} strategy demonstrates the highest resilience to perturbations,
with a success rate of {sorted_by_success[0][1]:.2f}%. This indicates that {best_strategy}'s approach to plan selection
provides better robustness against uncertainties in the execution environment.

The margin variance analysis shows that {'the most consistent' if best_strategy == sorted(margin_variances.items(), key=lambda x: x[1])[0][0] else 'a relatively consistent'} performance across different scenarios, which is valuable for predictable system behavior.
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
        'Average Margin': [margins[s] for s in strategies],
        'Margin Variance': [margin_variances[s] for s in strategies]
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

    # Create a domain variable to display name mapping
    domain_var_display_names = {}
    for qg in config["quality_goals"]:
        column_name = qg["column_name"]  # Nome della colonna nel CSV (es. "cost_constraint")
        display_name = qg["domain_variable"]  # Nome logico (es. "TotalCost")
        domain_var_display_names[column_name] = display_name

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Run the analyses
    print_dataset_statistics(df)
    result_df = compare_strategies(df)

    # More detailed analyses
    analyze_by_perturbation_level(df)
    alpha_pert_results = analyze_by_perturbation_level_with_alfas(df)
    analyze_by_alpha(df)

    # Analysis of Score strategy by alpha vs other strategies
    alpha_comparison_data = analyze_score_by_alpha_vs_others(df)

   # Create visualizations
    viz_dir = os.path.join(output_dir, "visualizations")
    create_visualizations(df, viz_dir,domain_var_display_names)
    create_perturbation_alpha_charts(df, viz_dir,domain_var_display_names)
    create_perturbation_alpha_allin_charts(df, viz_dir,domain_var_display_names)

    create_score_alpha_comparison_chart(alpha_comparison_data, viz_dir)


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
