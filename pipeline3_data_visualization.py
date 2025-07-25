#!/usr/bin/env python3
"""
Table Visualization Generator
This script creates comparative histogram visualizations for Q2S experiment results tables.
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import re

def extract_title_components(filename):
    """
    Extract title components from CSV filename.

    Args:
        filename (str): CSV filename

    Returns:
        tuple: (variable_name, alpha_type, perturbation_type)
    """
    # Remove .csv extension
    base_name = filename.replace('.csv', '')

    # Extract variable name (everything before _CONSTRAINT)
    variable_match = re.match(r'^([^_]+_[^_]+)_', base_name)
    if variable_match:
        variable_raw = variable_match.group(1)
        # Convert COST_CONSTRAINT to Cost
        variable_name = variable_raw.replace('_CONSTRAINT', '').replace('_', ' ').title()
    else:
        variable_name = "Unknown"

    # Determine alpha type
    if 'BREAKDOWN_ALPHA' in base_name:
        alpha_type = "Breakdown alfa"
    else:
        alpha_type = "Aggregated alfa"

    # Determine perturbation type
    if 'LIMITED_PERTURBATIONS' in base_name:
        perturbation_type = "Limited perturbations"
    else:
        perturbation_type = "Aggregated perturbations"

    return variable_name, alpha_type, perturbation_type

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

def create_histogram(csv_file, output_dir):
    """
    Create histogram visualization for a single CSV table.

    Args:
        csv_file (str): Path to CSV file
        output_dir (str): Output directory for images
    """
    try:
        # Read CSV data
        df = pd.read_csv(csv_file)

        if 'Perturbation' not in df.columns:
            print(f"Warning: No 'Perturbation' column found in {csv_file}")
            return

        # Extract title components
        filename = os.path.basename(csv_file)
        variable_name, alpha_type, perturbation_type = extract_title_components(filename)
        title = f"{variable_name}, {alpha_type}, {perturbation_type}"

        # Sort by perturbation values
        df_sorted = df.sort_values('Perturbation')

        # Identify success rate columns
        success_cols = [col for col in df.columns if col.endswith('_Success_Rate')]

        if not success_cols:
            print(f"Warning: No success rate columns found in {csv_file}")
            return

        # Set up the plot
        fig, ax = plt.subplots(figsize=(12, 8))

        # Calculate bar positions
        x = np.arange(len(df_sorted))
        width = 0.8 / len(success_cols)  # Adjust width based on number of strategies

        colors = get_strategy_colors()

        # Create bars for each strategy
        for i, col in enumerate(success_cols):
            # Extract strategy name from column name
            strategy_name = col.replace('_Success_Rate', '')

            # Get color for this strategy
            color = colors.get(strategy_name, colors.get('Score', '#7f7f7f'))  # Default to Score color or gray

            # Create bars
            bars = ax.bar(x + i * width - (len(success_cols)-1) * width/2,
                         df_sorted[col],
                         width,
                         label=strategy_name,
                         color=color,
                         alpha=0.8)

        # Customize the plot
        ax.set_xlabel('Perturbation Level', fontsize=14)
        ax.set_ylabel('Success Rate (%)', fontsize=14)
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Set x-axis labels
        ax.set_xticks(x)
        ax.set_xticklabels(df_sorted['Perturbation'], rotation=45 if len(df_sorted) > 5 else 0, fontsize=12)

        # Set y-axis tick labels font size
        ax.tick_params(axis='y', labelsize=12)

        # Set y-axis limits
        ax.set_ylim(0, min(110, max(df_sorted[success_cols].max().max() * 1.1, 10)))

        # Add legend in upper left corner of the plot
        ax.legend(loc='upper left', fontsize=12)

        # Add grid for better readability
        ax.grid(axis='y', linestyle='--', alpha=0.3)

        # Adjust layout to prevent clipping
        plt.tight_layout()

        # Save the plot
        output_filename = filename.replace('.csv', '.png')
        output_path = os.path.join(output_dir, output_filename)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Created visualization: {output_filename}")

    except Exception as e:
        print(f"Error creating visualization for {csv_file}: {e}")

def process_tables_directory(tables_dir):
    """
    Process all CSV files in the tables directory and create visualizations.

    Args:
        tables_dir (str): Path to tables directory
    """
    if not os.path.exists(tables_dir):
        print(f"Error: Tables directory {tables_dir} does not exist")
        return

    # Find all CSV files
    csv_files = [f for f in os.listdir(tables_dir) if f.endswith('.csv')]

    if not csv_files:
        print(f"No CSV files found in {tables_dir}")
        return

    print(f"Found {len(csv_files)} CSV files to process")

    # Create visualizations for each CSV file
    for csv_file in sorted(csv_files):
        csv_path = os.path.join(tables_dir, csv_file)
        print(f"Processing: {csv_file}")
        create_histogram(csv_path, tables_dir)

    print(f"\nAll visualizations saved to: {tables_dir}")

def main():
    """Main function to handle command line arguments and run the visualization generation."""
    if len(sys.argv) != 2:
        print("Usage: python table_visualization.py <tables_directory>")
        print("Example: python table_visualization.py meeting_scheduler_results/tables")
        sys.exit(1)

    tables_dir = sys.argv[1]

    print(f"Starting table visualization generation for: {tables_dir}")

    process_tables_directory(tables_dir)

    print("Visualization generation completed!")

if __name__ == "__main__":
    main()
