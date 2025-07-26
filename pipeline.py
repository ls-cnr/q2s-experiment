#!/usr/bin/env python3
"""
Complete Data Analysis Pipeline
This script runs the complete data analysis pipeline in sequence:

1. pipeline1_scenario_generator.py - Generate scenario data
2. pipeline2-1_data_analysis_pre_process.py - Pre-process scenarios
3. pipeline2-2_data_analysis_single_perturbation.py - Single perturbation analysis
4. pipeline2-3_data_analysis_multiple_perturbation.py - Multiple perturbation analysis
5. pipeline3_data_visualization.py - Create visualization plots

All scripts use the same configuration file for execution.
"""

import argparse
import subprocess
import sys
import os
import time
from pathlib import Path


def run_script(script_name, config_file, step_number, total_steps):
    """
    Run a pipeline script and handle errors.

    Args:
        script_name (str): Name of the script to run
        config_file (str): Path to configuration file
        step_number (int): Current step number
        total_steps (int): Total number of steps

    Returns:
        bool: True if successful, False if failed
    """
    print(f"\n{'='*60}")
    print(f"STEP {step_number}/{total_steps}: {script_name}")
    print(f"{'='*60}")

    # Check if script exists
    if not os.path.exists(script_name):
        print(f"ERROR: Script {script_name} not found!")
        return False

    # Run the script
    start_time = time.time()
    try:
        print(f"Running: python {script_name} {config_file}")
        result = subprocess.run(
            [sys.executable, script_name, config_file],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )

        end_time = time.time()
        duration = end_time - start_time

        # Print output
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        # Check if successful
        if result.returncode == 0:
            print(f"✅ STEP {step_number} COMPLETED SUCCESSFULLY (Duration: {duration:.1f}s)")
            return True
        else:
            print(f"❌ STEP {step_number} FAILED (Return code: {result.returncode})")
            return False

    except subprocess.TimeoutExpired:
        print(f"❌ STEP {step_number} FAILED: Timeout after 1 hour")
        return False
    except Exception as e:
        print(f"❌ STEP {step_number} FAILED: {str(e)}")
        return False


def validate_config_file(config_file):
    """
    Validate that the configuration file exists and is readable.

    Args:
        config_file (str): Path to configuration file

    Returns:
        bool: True if valid, False otherwise
    """
    if not os.path.exists(config_file):
        print(f"ERROR: Configuration file not found: {config_file}")
        return False

    try:
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"✅ Configuration file validated: {config_file}")
        return True
    except Exception as e:
        print(f"ERROR: Invalid configuration file {config_file}: {str(e)}")
        return False


def print_pipeline_summary(successful_steps, failed_steps, total_duration):
    """Print a summary of the pipeline execution."""
    print(f"\n{'='*60}")
    print("PIPELINE EXECUTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
    print(f"Successful steps: {len(successful_steps)}")
    print(f"Failed steps: {len(failed_steps)}")

    if successful_steps:
        print(f"\n✅ SUCCESSFUL STEPS:")
        for step in successful_steps:
            print(f"   - {step}")

    if failed_steps:
        print(f"\n❌ FAILED STEPS:")
        for step in failed_steps:
            print(f"   - {step}")

    if not failed_steps:
        print(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"All analysis and visualization files have been generated.")
    else:
        print(f"\n⚠️  PIPELINE COMPLETED WITH ERRORS!")
        print(f"Check the failed steps and fix any issues before proceeding.")


def main():
    parser = argparse.ArgumentParser(
        description="Run the complete data analysis pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Pipeline Steps:
1. Generate scenario data
2. Pre-process scenarios (group by alpha)
3. Single perturbation analysis
4. Multiple perturbation analysis
5. Create visualization plots

All steps use the same configuration file.

Example:
    python pipeline.py meeting_scheduler.json
        """
    )
    parser.add_argument(
        'config_file',
        help='Path to the configuration JSON file'
    )
    parser.add_argument(
        '--skip-step',
        action='append',
        type=int,
        help='Skip specific step numbers (can be used multiple times)'
    )

    args = parser.parse_args()

    # Validate configuration file
    if not validate_config_file(args.config_file):
        sys.exit(1)

    # Define pipeline steps
    pipeline_steps = [
        ("pipeline1_scenario_generator.py", "Generate scenario data"),
        ("pipeline2-1_data_analysis_pre_process.py", "Pre-process scenarios"),
        ("pipeline2-2_data_analysis_single_perturbation.py", "Single perturbation analysis"),
        ("pipeline2-3_data_analysis_multiple_perturbation.py", "Multiple perturbation analysis"),
        ("pipeline3_data_visualization.py", "Create visualization plots")
    ]

    # Handle skip steps
    skip_steps = set(args.skip_step or [])
    if skip_steps:
        print(f"Skipping steps: {sorted(skip_steps)}")

    # Start pipeline execution
    print(f"🚀 STARTING DATA ANALYSIS PIPELINE")
    print(f"Configuration file: {args.config_file}")
    print(f"Total steps: {len(pipeline_steps)}")

    start_time = time.time()
    successful_steps = []
    failed_steps = []

    # Execute each step
    for i, (script_name, description) in enumerate(pipeline_steps, 1):
        if i in skip_steps:
            print(f"\n⏭️  STEP {i}/{len(pipeline_steps)}: {script_name} (SKIPPED)")
            continue

        success = run_script(script_name, args.config_file, i, len(pipeline_steps))

        if success:
            successful_steps.append(f"Step {i}: {description}")
        else:
            failed_steps.append(f"Step {i}: {description}")

            # Ask user if they want to continue after failure
            print(f"\n⚠️  Step {i} failed. Do you want to continue with the remaining steps?")
            user_input = input("Continue? (y/N): ").strip().lower()
            if user_input not in ['y', 'yes']:
                print("Pipeline execution stopped by user.")
                break

    # Calculate total duration
    end_time = time.time()
    total_duration = end_time - start_time

    # Print summary
    print_pipeline_summary(successful_steps, failed_steps, total_duration)

    # Exit with appropriate code
    if failed_steps:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
