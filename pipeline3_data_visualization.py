#!/usr/bin/env python3
"""
Pipeline Step 3: Data Visualization
This script creates histogram plots comparing different strategies across perturbation levels
using the summary tables generated in previous steps.

For each quality goal, it generates:
1. Single perturbation success rate comparison histogram
2. Single perturbation average margin comparison histogram

Additionally, it creates:
3. Multiple perturbation success rate comparison histogram
4. Multiple perturbation average margin comparison histogram

The plots compare 6 strategies: Min (α=0), α=0.3, α=0.5, α=0.7, Avg (α=1), and Rnd
across different perturbation levels with custom labels and pastel color palette.
"""

import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path


def load_config(config_file):
    """Load configuration from JSON file."""
    with open(config_file, 'r') as f:
        return json.load(f)


def extract_quality_goal_name(domain_variable):
    """Extract the quality goal name from domain variable."""
    if domain_variable.endswith('_constraint'):
        return domain_variable[:-11]  # Remove '_constraint'
    return domain_variable


def get_perturbation_label_mapping():
    """Create mapping from perturbation values to descriptive labels."""
    # This mapping assumes common perturbation values
    # Can be extended or made configurable if needed
    return {
        -100: "catastrophic",
        -75: "very negative",
        -10: "negative",
        0: "zero perturbation"
    }


def create_strategy_comparison_plots(summary_df, quality_goal, output_dir):
    """Create comparison plots for a quality goal."""

    # Create plots subdirectory
    plots_dir = os.path.join(output_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)

    # Get perturbation values and create labels
    perturbation_values = sorted(summary_df['Perturbation'].unique())
    label_mapping = get_perturbation_label_mapping()

    # Create custom labels for x-axis
    x_labels = []
    for val in perturbation_values:
        if val in label_mapping:
            x_labels.append(label_mapping[val])
        else:
            x_labels.append(str(val))

    # Define strategies with their data columns and display labels
    strategies = [
        ('Min_Success_Rate', 'Min_Average_Margin', 'Min (α = 0)'),
        ('Score_03_Success_Rate', 'Score_03_Average_Margin', 'α=0.3'),
        ('Score_05_Success_Rate', 'Score_05_Average_Margin', 'α=0.5'),
        ('Score_07_Success_Rate', 'Score_07_Average_Margin', 'α=0.7'),
        ('Avg_Success_Rate', 'Avg_Average_Margin', 'Avg (α=1)'),
        ('Rnd_Success_Rate', 'Rnd_Average_Margin', 'Rnd')
    ]

    # Set up plot parameters with pastel colors
    x_pos = np.arange(len(perturbation_values))
    width = 0.13  # Width of bars
    colors = ['#F1948A', '#F8C471', '#A9DFBF', '#AED6F1', '#D2B4DE', '#D7C3A0']  # Pastel colors

    # Create Success Rate plot
    fig, ax = plt.subplots(figsize=(12, 8))

    for i, (success_col, _, label) in enumerate(strategies):
        if success_col in summary_df.columns:
            values = summary_df.set_index('Perturbation').loc[perturbation_values, success_col].values
            ax.bar(x_pos + i * width, values, width, label=label, color=colors[i])

    ax.set_xlabel(f'{quality_goal.title()} Perturbation', fontsize=12)
    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title(f'Comparison of Strategies by {quality_goal.title()} Perturbation', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos + width * 2.5)  # Center the x-tick labels
    ax.set_xticklabels(x_labels)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Save Success Rate plot
    success_file = os.path.join(plots_dir, f'histo_single_{quality_goal}_perturbation_success.png')
    plt.tight_layout()
    plt.savefig(success_file, dpi=300, bbox_inches='tight')
    plt.close()

    # Create Average Margin plot
    fig, ax = plt.subplots(figsize=(12, 8))

    for i, (_, margin_col, label) in enumerate(strategies):
        if margin_col in summary_df.columns:
            values = summary_df.set_index('Perturbation').loc[perturbation_values, margin_col].values
            ax.bar(x_pos + i * width, values, width, label=label, color=colors[i])

    ax.set_xlabel(f'{quality_goal.title()} Perturbation', fontsize=12)
    ax.set_ylabel('Average Margin', fontsize=12)
    ax.set_title(f'Comparison of Strategies by {quality_goal.title()} Perturbation', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos + width * 2.5)  # Center the x-tick labels
    ax.set_xticklabels(x_labels)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Save Average Margin plot
    margin_file = os.path.join(plots_dir, f'histo_single_{quality_goal}_perturbation_margin.png')
    plt.tight_layout()
    plt.savefig(margin_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Created plots for {quality_goal}:")
    print(f"  - {success_file}")
    print(f"  - {margin_file}")

    return [success_file, margin_file]


def create_multiple_perturbation_plots(summary_df, output_dir):
    """Create comparison plots for multiple perturbation severity."""

    # Create plots subdirectory
    plots_dir = os.path.join(output_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)

    # Get perturbation scores (from highest severity to lowest)
    perturbation_scores = sorted(summary_df['perturbation_score'].unique(), reverse=True)
    x_labels = [str(score) for score in perturbation_scores]

    # Define strategies with their data columns and display labels
    strategies = [
        ('Min_Success_Rate', 'Min_Average_Margin', 'Min (α = 0)'),
        ('Score_03_Success_Rate', 'Score_03_Average_Margin', 'α=0.3'),
        ('Score_05_Success_Rate', 'Score_05_Average_Margin', 'α=0.5'),
        ('Score_07_Success_Rate', 'Score_07_Average_Margin', 'α=0.7'),
        ('Avg_Success_Rate', 'Avg_Average_Margin', 'Avg (α=1)'),
        ('Rnd_Success_Rate', 'Rnd_Average_Margin', 'Rnd')
    ]

    # Set up plot parameters with same pastel colors
    x_pos = np.arange(len(perturbation_scores))
    width = 0.13  # Width of bars
    colors = ['#F1948A', '#F8C471', '#A9DFBF', '#AED6F1', '#D2B4DE', '#D7C3A0']  # Pastel colors

    # Create Success Rate plot
    fig, ax = plt.subplots(figsize=(12, 8))

    for i, (success_col, _, label) in enumerate(strategies):
        if success_col in summary_df.columns:
            values = summary_df.set_index('perturbation_score').loc[perturbation_scores, success_col].values
            ax.bar(x_pos + i * width, values, width, label=label, color=colors[i])

    ax.set_xlabel('Global Perturbation Severity', fontsize=12)
    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title('Comparison of Strategies by Global Perturbation', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos + width * 2.5)  # Center the x-tick labels
    ax.set_xticklabels(x_labels)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Save Success Rate plot
    success_file = os.path.join(plots_dir, 'histo_multi_perturbation_success.png')
    plt.tight_layout()
    plt.savefig(success_file, dpi=300, bbox_inches='tight')
    plt.close()

    # Create Average Margin plot
    fig, ax = plt.subplots(figsize=(12, 8))

    for i, (_, margin_col, label) in enumerate(strategies):
        if margin_col in summary_df.columns:
            values = summary_df.set_index('perturbation_score').loc[perturbation_scores, margin_col].values
            ax.bar(x_pos + i * width, values, width, label=label, color=colors[i])

    ax.set_xlabel('Global Perturbation Severity', fontsize=12)
    ax.set_ylabel('Average Margin', fontsize=12)
    ax.set_title('Comparison of Strategies by Global Perturbation', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos + width * 2.5)  # Center the x-tick labels
    ax.set_xticklabels(x_labels)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Save Average Margin plot
    margin_file = os.path.join(plots_dir, 'histo_multi_perturbation_margin.png')
    plt.tight_layout()
    plt.savefig(margin_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Created multiple perturbation plots:")
    print(f"  - {success_file}")
    print(f"  - {margin_file}")

    return [success_file, margin_file]


def main():
    parser = argparse.ArgumentParser(
        description="Create visualization plots comparing strategies across perturbation levels"
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
    tables_dir = os.path.join(output_dir, 'tables')

    # Get quality goals from config
    quality_goals = config.get('quality_goals', [])

    print(f"Creating visualization plots...")

    created_plots = []

    # Process each quality goal (single perturbation plots)
    if quality_goals:
        print(f"\nCreating single perturbation plots for {len(quality_goals)} quality goals...")

        for qg in quality_goals:
            domain_variable = qg.get('column_name', qg.get('domain_variable'))
            if not domain_variable:
                continue

            # Get quality goal name
            quality_goal = extract_quality_goal_name(domain_variable)

            # Load summary data
            summary_file = os.path.join(tables_dir, f'summary_{quality_goal}_single_perturbation.csv')

            if not os.path.exists(summary_file):
                print(f"Warning: Summary file not found: {summary_file}")
                continue

            print(f"\nProcessing {quality_goal}...")
            summary_df = pd.read_csv(summary_file)

            print(f"Loaded summary data: {len(summary_df)} perturbation levels")
            print(f"Perturbation values: {sorted(summary_df['Perturbation'].unique())}")

            # Create plots
            plot_files = create_strategy_comparison_plots(summary_df, quality_goal, output_dir)
            created_plots.extend(plot_files)

    # Process multiple perturbation plot
    print(f"\nCreating multiple perturbation plots...")
    multiple_summary_file = os.path.join(tables_dir, 'summary_multiple_perturbation.csv')

    if os.path.exists(multiple_summary_file):
        print(f"Loading multiple perturbation summary data...")
        multiple_summary_df = pd.read_csv(multiple_summary_file)

        print(f"Loaded multiple perturbation data: {len(multiple_summary_df)} severity levels")
        print(f"Perturbation scores: {sorted(multiple_summary_df['perturbation_score'].unique())}")

        # Create multiple perturbation plots
        plot_files = create_multiple_perturbation_plots(multiple_summary_df, output_dir)
        created_plots.extend(plot_files)
    else:
        print(f"Warning: Multiple perturbation summary file not found: {multiple_summary_file}")

    # Summary
    print(f"\n" + "="*50)
    print(f"Visualization complete!")
    print(f"Created {len(created_plots)} plots in: {os.path.join(output_dir, 'plots')}")

    for plot_file in created_plots:
        print(f"  - {os.path.basename(plot_file)}")


if __name__ == "__main__":
    main()
