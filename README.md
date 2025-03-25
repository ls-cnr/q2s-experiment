# Q2S (Quality to Satisfaction) Project

This project implements an experimental framework to evaluate the effectiveness of the Quality to Satisfaction (Q2S) matrix for plan selection in the presence of perturbations.

## Description

The Q2S matrix is a tool designed to evaluate and compare different plans based on their ability to satisfy quality objectives. For each plan-objective combination, the Q2S matrix calculates a "satisfaction distance" that represents how well the plan meets the objective.

Values in the Q2S matrix represent:
- **Positive values**: satisfaction with margin (higher is better)
- **Zero**: exact satisfaction
- **Negative values**: constraint violation

The basic formula for calculating the satisfaction distance for "max" type constraints is:
```
d_{i,j} = (MaxValue[j] - ActualValue[i,j]) / MaxValue[j]
```

The project compares different plan selection strategies:

1. **Q2S**: Combines AvgSat and MinSat according to the α parameter
2. **AvgSat**: Selects the plan with the best average distance
3. **MinSat**: Selects the plan with the best minimum distance
4. **Random**: Randomly selects a valid plan (baseline)

For plan selection, a strategy based on the Hurwicz criterion is used:
```
Score = α * AvgSat + (1-α) * MinSat
```
where:
- `AvgSat` is the average satisfaction distance for all objectives
- `MinSat` is the minimum satisfaction distance (worst case)
- `α` is a parameter that balances optimism and pessimism (typically 0.3, 0.5, or 0.7)

## Case Study (Meeting Scheduler)

The case study is a meeting planning system with different functional objectives and three quality objectives:
- QG0: Cost ≤ threshold
- QG1: Effort ≤ threshold
- QG2: Time ≤ threshold

The experiment evaluates the effectiveness of different plan selection strategies in the presence of perturbations. The experiment consists of generating scenarios with different parameter combinations, selecting plans with different strategies, applying perturbations, and measuring:
- **Success rate**: percentage of plans that remain valid after perturbation
- **Average margins**: average distance from constraints after perturbation

## Project Structure

- `data/`: Contains input and output CSV files
- `scripts/`: Contains Python scripts for the experiment
  - `scenario_generator.py`: Generates experimental scenarios
  - `scenario_processor.py`: Processes scenarios and applies strategies
  - `results_analyzer.py`: Analyzes results and generates reports
  - `q2s_utils.py`: Common utility functions for Q2S calculations
  - `test_q2s_utils.py`: Unit tests for Q2S utility functions
  - `test_exp1_scenario_processor.py`: Unit tests for scenario processor functions

## Prerequisites

- Python 3.7 or higher
- Required packages: numpy, pandas, matplotlib

## Environment Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Generate scenarios:
   ```
   python scripts/scenario_generator.py
   ```

2. Process scenarios:
   ```
   python scripts/scenario_processor.py
   ```

3. Analyze results:
   ```
   python scripts/results_analyzer.py
   ```

4. Run tests:
   ```
   python -m unittest discover scripts
   ```
