#!/usr/bin/env python3
"""
Q2S Data Visualization Pipeline
This script creates histogram visualizations from Q2S single perturbation analysis tables.
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from q2s_utils import load_json_config

def get_strategy_colors():
    """
    Define color scheme for different strategies.

    Returns:
        dict: Strategy colors mapping
    """
    return {
        'Min': '#e74c3c',           # Red
        'Score_03': '#1f77b4',      # Dark blue
        'Score_05': '#4292c6',      # Medium blue
        'Score_07': '#6baed6',      # Light blue
        'Avg': '#2ecc71',           # Green
        'Rnd': '#f39c12'            # Orange
    }

def create_perturbation_mapping(config):
    """
    Create mapping from perturbation values to descriptive labels based on configuration.

    Args:
        config (dict): Configuration dictionary

    Returns:
        dict: Dictionary mapping perturbation values to labels
    """
    perturbation_mapping = {}

    # Try to find perturbation data in scenario_generator section
    if "scenario_generator" in config and "constraint_options" in config["scenario_generator"]:
        for constraint_option in config["scenario_generator"]["constraint_options"]:
            if "perturbation" in constraint_option:
                domain_var = constraint_option["domain_variable"]
                constraint_base = domain_var.replace("_constraint", "")

                # Create value to label mapping for this constraint
                value_to_label = {}
                for pert in constraint_option["perturbation"]:
                    if "value" in pert and "level" in pert:
                        value = pert["value"]
                        level = pert["level"]

                        # Map level names to display labels
                        if level == "no":
                            label = "zero"
                        elif level == "low_neg":
                            label = "negative"
                        elif level == "high_neg":
                            label = "very negative"
                        elif level == "catastrofic":
                            label = "catastrophic"
                        else:
                            label = level  # fallback to original level name

                        value_to_label[value] = label

                perturbation_mapping[constraint_base] = value_to_label

    print(f"Created perturbation mapping: {perturbation_mapping}")
    return perturbation_mapping

def create_default_perturbation_mapping(perturbation_values):
    """
    Create a default mapping when config mapping is not available.

    Args:
        perturbation_values (list): List of numerical perturbation values

    Returns:
        dict: Dictionary mapping values to labels
    """
    sorted_values = sorted(perturbation_values)
    mapping = {}

    for value in sorted_values:
        if value == 0:
            mapping[value] = "zero"
        elif value > 0:
            mapping[value] = "positive"
        else:
            # Negative values - assign labels based on magnitude
            if len(sorted_values) <= 2:
                mapping[value] = "negative"
            elif len(sorted_values) == 3:
                if value == min(sorted_values):
                    mapping[value] = "very negative"
                else:
                    mapping[value] = "negative"
            else:
                # 4 or more values
                sorted_neg = [v for v in sorted_values if v < 0]
                if len(sorted_neg) >= 3:
                    if value == min(sorted_neg):
                        mapping[value] = "catastrophic"
                    elif value == max(sorted_neg):
                        mapping[value] = "negative"
                    else:
                        mapping[value] = "very negative"
                else:
                    if value == min(sorted_neg):
                        mapping[value] = "very negative"
                    else:
                        mapping[value] = "negative"

    return mapping

def create_single_perturbation_histogram(csv_file, config, output_dir):
    """
    Create histogram for a single perturbation CSV file.

    Args:
        csv_file (str): Path to CSV file
        config (dict): Configuration dictionary
        output_dir (str): Output directory for plots
    """
    try:
        # Read CSV data
        df = pd.read_csv(csv_file)

        if len(df) == 0:
            print(f"No data in {csv_file}")
            return

        # Extract constraint name from filename
        filename = os.path.basename(csv_file)
        constraint_match = filename.replace('_SINGLE_PERTURBATIONS.csv', '')
        constraint_name = constraint_match.replace('_CONSTRAINT', '').replace('_', ' ').title()

        # Get perturbation mapping
        perturbation_mapping_by_constraint = create_perturbation_mapping(config)
        constraint_base = constraint_match.replace('_CONSTRAINT', '').lower()

        if constraint_base in perturbation_mapping_by_constraint:
            perturbation_mapping = perturbation_mapping_by_constraint[constraint_base]
        else:
            # Create default mapping
            perturbation_values = df['Perturbation'].unique()
            perturbation_mapping = create_default_perturbation_mapping(perturbation_values)

        # Prepare data for plotting
        perturbation_levels = sorted(df['Perturbation'].unique())

        # Create labels for x-axis
        x_labels = [perturbation_mapping.get(level, str(level)) for level in perturbation_levels]
        x_positions = np.arange(len(perturbation_levels))

        # Identify success rate columns for strategies
        success_columns = [col for col in df.columns if col.endswith('_Success_Rate')]

        # Define strategy order and get colors
        colors = get_strategy_colors()

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))

        # Calculate bar width
        bar_width = 0.8 / len(success_columns)

        # Plot bars for each strategy
        for i, col in enumerate(success_columns):
            strategy_name = col.replace('_Success_Rate', '')
            strategy_data = df.set_index('Perturbation')[col].reindex(perturbation_levels)

            # Calculate bar positions
            bar_positions = x_positions + (i - len(success_columns)/2 + 0.5) * bar_width

            # Create bars
            bars = ax.bar(bar_positions, strategy_data, bar_width,
                         label=strategy_name,
                         color=colors.get(strategy_name, '#7f7f7f'),
                         alpha=0.8)

        # Customize the plot
        ax.set_xlabel('Perturbation Level', fontsize=14)
        ax.set_ylabel('Success Rate (%)', fontsize=14)
        ax.set_title(f'Analysis of Perturbation for {constraint_name}', fontsize=16, fontweight='bold')

        # Set x-axis
        ax.set_xticks(x_positions)
        ax.set_xticklabels(x_labels, fontsize=12)

        # Set y-axis
        ax.set_ylim(0, 110)
        ax.tick_params(axis='y', labelsize=12)

        # Add legend in upper left
        ax.legend(loc='upper left', fontsize=12)

        # Add grid for better readability
        ax.grid(axis='y', linestyle='--', alpha=0.3)

        # Tight layout
        plt.tight_layout()

        # Save plot
        safe_constraint = constraint_name.replace(' ', '_').lower()
        output_filename = f"{safe_constraint}_perturbation_analysis.png"
        filepath = os.path.join(output_dir, output_filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Created histogram: {output_filename}")

    except Exception as e:
        print(f"Error creating histogram for {csv_file}: {e}")

def process_single_perturbation_tables(tables_dir, config):
    """
    Process all single perturbation CSV files and create histograms.

    Args:
        tables_dir (str): Path to tables directory
        config (dict): Configuration dictionary
    """
    if not os.path.exists(tables_dir):
        print(f"Error: Tables directory {tables_dir} does not exist")
        return

    # Find all single perturbation CSV files
    csv_files = [f for f in os.listdir(tables_dir)
                 if f.endswith('_SINGLE_PERTURBATIONS.csv')]

    if not csv_files:
        print(f"No single perturbation CSV files found in {tables_dir}")
        return

    print(f"Found {len(csv_files)} single perturbation files to process")

    # Create plots subdirectory
    plots_dir = os.path.join(tables_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    # Process each CSV file
    for csv_file in sorted(csv_files):
        print(f"Processing: {csv_file}")
        csv_path = os.path.join(tables_dir, csv_file)
        create_single_perturbation_histogram(csv_path, config, plots_dir)

    print(f"\nAll histograms saved to: {plots_dir}")

def main():
    """Main function to handle command line arguments and run the visualization generation."""
    if len(sys.argv) != 2:
        print("Usage: python pipeline3_data_visualization.py <config_file>")
        print("Example: python pipeline3_data_visualization.py data/meeting_scheduler.json")
        sys.exit(1)

    config_file = sys.argv[1]

    print(f"Starting Q2S data visualization pipeline")
    print(f"Configuration file: {config_file}")

    # Load configuration
    config = load_json_config(config_file)
    if config is None:
        print("Failed to load configuration. Exiting.")
        return

    # Get tables directory from configuration
    output_dir = config["simulation_settings"]["output_directory"]
    tables_dir = os.path.join(output_dir, "tables")

    print(f"Tables directory: {tables_dir}")

    # Set matplotlib style
    plt.style.use('default')

    # Process single perturbation tables
    process_single_perturbation_tables(tables_dir, config)

    print("Data visualization pipeline completed!")

if __name__ == "__main__":
    main()
