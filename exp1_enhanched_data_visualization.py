#!/usr/bin/env python3
"""
Enhanced Data Visualization Generator with Error Bar Plots
This script creates error bar plot visualizations for Q2S experiment results
using pre-calculated variance statistics.
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import re

def get_strategy_colors():
    """
    Define color scheme for different strategies.

    Returns:
        dict: Strategy colors mapping
    """
    return {
        'Min': '#e74c3c',           # Red
        'Score': '#3498db',         # Blue (for aggregated)
        'Score_03': '#1f77b4',      # Dark blue
        'Score_05': '#4292c6',      # Medium blue
        'Score_07': '#6baed6',      # Light blue
        'Avg': '#2ecc71',           # Green
        'Rnd': '#f39c12'            # Orange
    }

def extract_info_from_filename(filename):
    """
    Extract constraint name and table type from enhanced CSV filename.

    Args:
        filename (str): Enhanced CSV filename

    Returns:
        tuple: (constraint_name, alpha_type, perturbation_type)
    """
    # Remove .csv and _WITH_VARIANCE suffix
    base_name = filename.replace('.csv', '').replace('_WITH_VARIANCE', '')

    # Extract constraint name - handle the pattern: COST_CONSTRAINT_CONSTRAINT_...
    # This removes the redundant _CONSTRAINT part
    if '_CONSTRAINT_CONSTRAINT_' in base_name:
        # Pattern: COST_CONSTRAINT_CONSTRAINT_LIMITED_...
        # Extract: COST_CONSTRAINT -> cost_constraint
        constraint_match = re.match(r'^([^_]+_CONSTRAINT)_CONSTRAINT_', base_name)
        if constraint_match:
            constraint_raw = constraint_match.group(1)
            # Convert to nice display format
            constraint_name = constraint_raw.replace('_CONSTRAINT', '').replace('_', ' ').title()
        else:
            constraint_name = "Unknown"
    else:
        # Fallback pattern
        constraint_match = re.match(r'^([^_]+_[^_]+)_', base_name)
        if constraint_match:
            constraint_raw = constraint_match.group(1)
            constraint_name = constraint_raw.replace('_', ' ').title()
        else:
            constraint_name = "Unknown"

    # Determine alpha type
    if 'BREAKDOWN_ALPHA' in base_name:
        alpha_type = "Breakdown"
    else:
        alpha_type = "Aggregated"

    # Determine perturbation type
    if 'LIMITED_PERTURBATIONS' in base_name:
        perturbation_type = "Limited"
    else:
        perturbation_type = "Aggregated"

    return constraint_name, alpha_type, perturbation_type

def create_error_bar_plot(csv_file, output_dir):
    """
    Create error bar plot visualization from enhanced CSV data.

    Args:
        csv_file (str): Path to enhanced CSV file
        output_dir (str): Output directory
    """
    try:
        # Read the enhanced CSV data
        df = pd.read_csv(csv_file)

        if len(df) == 0:
            print(f"No data in {csv_file}")
            return

        # Extract information from filename
        filename = os.path.basename(csv_file)
        constraint_name, alpha_type, perturbation_type = extract_info_from_filename(filename)

        # Get unique perturbation levels
        perturbation_levels = sorted(df['Perturbation'].unique())

        # Create subplots for each perturbation level
        n_levels = len(perturbation_levels)
        n_cols = min(3, n_levels)
        n_rows = (n_levels + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(7*n_cols, 6*n_rows), squeeze=False)

        # Flatten axes for easier indexing
        axes_flat = axes.flatten()

        colors = get_strategy_colors()

        for i, level in enumerate(perturbation_levels):
            ax = axes_flat[i]
            level_data = df[df['Perturbation'] == level]

            if len(level_data) == 0:
                continue

            # Get strategies for this perturbation level
            strategies = level_data['Strategy'].unique()

            # Prepare data for plotting
            x_positions = np.arange(len(strategies))
            means = []
            stds = []
            strategy_colors = []

            for strategy in strategies:
                strategy_data = level_data[level_data['Strategy'] == strategy].iloc[0]
                means.append(strategy_data['Success_Rate_Mean'])
                stds.append(strategy_data['Success_Rate_Std'])
                strategy_colors.append(colors.get(strategy, '#7f7f7f'))

            # Create error bar plot
            bars = ax.bar(x_positions, means, yerr=stds,
                         capsize=5,
                         color=strategy_colors, alpha=0.8,
                         error_kw={'elinewidth': 2, 'alpha': 0.8})

            # Customize the subplot
            ax.set_title(f'Perturbation: {level}', fontsize=13, fontweight='bold')
            ax.set_ylabel('Success Rate (%)', fontsize=12)
            ax.set_xlabel('Strategy', fontsize=12)
            ax.set_xticks(x_positions)
            ax.set_xticklabels(strategies, rotation=45, fontsize=11)
            ax.tick_params(axis='y', labelsize=11)

            # Set y-axis limits with some padding
            max_val = max([m + s for m, s in zip(means, stds)]) if means else 100
            ax.set_ylim(0, min(110, max_val * 1.1))

            # Add grid for better readability
            ax.grid(axis='y', linestyle='--', alpha=0.3)

            # Add mean value labels on bars
            for j, (bar, mean, std) in enumerate(zip(bars, means, stds)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + std + 1,
                       f'{mean:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Hide unused subplots
        for i in range(n_levels, len(axes_flat)):
            axes_flat[i].set_visible(False)

        # Create title
        title = f'{constraint_name}, {alpha_type} Alpha, {perturbation_type} Perturbations - Error Bar Plot'
        fig.suptitle(title, fontsize=15, fontweight='bold')

        plt.tight_layout()

        # Save plot
        safe_constraint = constraint_name.replace(' ', '_').lower()
        output_filename = f"{safe_constraint}_{alpha_type}_{perturbation_type}_ERRORBAR.png"
        filepath = os.path.join(output_dir, output_filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)  # Explicitly close the figure to free memory

        print(f"Created error bar plot: {output_filename}")

    except Exception as e:
        print(f"Error creating error bar plot for {csv_file}: {e}")

def create_comparison_plot(csv_file, output_dir):
    """
    Create comparison plot showing all perturbation levels in one chart.

    Args:
        csv_file (str): Path to enhanced CSV file
        output_dir (str): Output directory
    """
    try:
        # Read the enhanced CSV data
        df = pd.read_csv(csv_file)

        if len(df) == 0:
            print(f"No data in {csv_file}")
            return

        # Extract information from filename
        filename = os.path.basename(csv_file)
        constraint_name, alpha_type, perturbation_type = extract_info_from_filename(filename)

        # Get unique perturbation levels and strategies
        perturbation_levels = sorted(df['Perturbation'].unique())
        strategies = df['Strategy'].unique()

        # Create the plot
        fig, ax = plt.subplots(figsize=(max(12, len(perturbation_levels) * 2), 8))

        colors = get_strategy_colors()

        # Calculate bar positions
        x = np.arange(len(perturbation_levels))
        width = 0.8 / len(strategies)

        # Plot each strategy
        for i, strategy in enumerate(strategies):
            strategy_means = []
            strategy_stds = []

            for level in perturbation_levels:
                level_strategy_data = df[(df['Perturbation'] == level) & (df['Strategy'] == strategy)]
                if len(level_strategy_data) > 0:
                    row = level_strategy_data.iloc[0]
                    strategy_means.append(row['Success_Rate_Mean'])
                    strategy_stds.append(row['Success_Rate_Std'])
                else:
                    strategy_means.append(0)
                    strategy_stds.append(0)

            # Create bars with error bars
            bars = ax.bar(x + i * width - (len(strategies)-1) * width/2,
                         strategy_means, width,
                         yerr=strategy_stds,
                         capsize=4,
                         label=strategy,
                         color=colors.get(strategy, '#7f7f7f'),
                         alpha=0.8,
                         error_kw={'elinewidth': 1.5, 'alpha': 0.8})

        # Customize the plot
        ax.set_xlabel('Perturbation Level', fontsize=14)
        ax.set_ylabel('Success Rate (%)', fontsize=14)
        ax.set_title(f'{constraint_name}, {alpha_type} Alpha, {perturbation_type} Perturbations - Comparison',
                    fontsize=15, fontweight='bold')

        # Set x-axis
        ax.set_xticks(x)
        ax.set_xticklabels(perturbation_levels, fontsize=12)

        # Set y-axis
        ax.tick_params(axis='y', labelsize=12)
        ax.set_ylim(0, 110)

        # Add legend and grid
        ax.legend(loc='upper left', fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.3)

        plt.tight_layout()

        # Save plot
        safe_constraint = constraint_name.replace(' ', '_').lower()
        output_filename = f"{safe_constraint}_{alpha_type}_{perturbation_type}_COMPARISON.png"
        filepath = os.path.join(output_dir, output_filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)  # Explicitly close the figure to free memory

        print(f"Created comparison plot: {output_filename}")

    except Exception as e:
        print(f"Error creating comparison plot for {csv_file}: {e}")

def process_enhanced_tables(tables_enhanced_dir):
    """
    Process all enhanced CSV files and create error bar visualizations.

    Args:
        tables_enhanced_dir (str): Path to enhanced tables directory
    """
    if not os.path.exists(tables_enhanced_dir):
        print(f"Error: Enhanced tables directory {tables_enhanced_dir} does not exist")
        return

    # Find all enhanced CSV files
    csv_files = [f for f in os.listdir(tables_enhanced_dir)
                 if f.endswith('_WITH_VARIANCE.csv')]

    if not csv_files:
        print(f"No enhanced CSV files found in {tables_enhanced_dir}")
        return

    print(f"Found {len(csv_files)} enhanced CSV files to process")

    # Create output directories
    errorbar_dir = os.path.join(tables_enhanced_dir, "errorbar_plots")
    comparison_dir = os.path.join(tables_enhanced_dir, "comparison_plots")
    os.makedirs(errorbar_dir, exist_ok=True)
    os.makedirs(comparison_dir, exist_ok=True)

    # Process each CSV file
    for csv_file in sorted(csv_files):
        print(f"\nProcessing: {csv_file}")

        csv_path = os.path.join(tables_enhanced_dir, csv_file)

        # Create error bar plot (separate subplots for each perturbation)
        create_error_bar_plot(csv_path, errorbar_dir)

        # Create comparison plot (all perturbations in one chart)
        create_comparison_plot(csv_path, comparison_dir)

    print(f"\nAll visualizations saved to:")
    print(f"Error bar plots: {errorbar_dir}")
    print(f"Comparison plots: {comparison_dir}")

def main():
    """Main function to handle command line arguments and run the enhanced visualization generation."""
    if len(sys.argv) != 2:
        print("Usage: python exp1_enhanched_data_visualization.py <tables_enhanced_directory>")
        print("Example: python exp1_enhanched_data_visualization.py meeting_scheduler_results/tables_enhanced")
        sys.exit(1)

    tables_enhanced_dir = sys.argv[1]

    print(f"Starting enhanced data visualization generation")
    print(f"Enhanced tables directory: {tables_enhanced_dir}")

    # Set style for better-looking plots
    plt.style.use('default')

    process_enhanced_tables(tables_enhanced_dir)

    print("Enhanced visualization generation completed!")

if __name__ == "__main__":
    main()
