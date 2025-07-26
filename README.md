# Evaluating the Q2S (Quality to Satisfaction)

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

## The Experiment

The experimental validation of the Q2S approach evaluates which plan selection strategy produces plans that remain valid even after unexpected changes in the environment.

### Experimental Procedure

The experimental procedure follows these sequential steps:

1. **Scenario Definition**: Each scenario is defined by:
   - **Alpha value (α)**: Parameter balancing optimism/pessimism (0.3, 0.5, or 0.7)
   - **Initial constraint configuration**: Base values for all quality goal constraints
   - **Perturbation values**: Specific changes to be applied to each constraint

2. **Plan Selection**: For each scenario, all 5 strategies select their preferred plan:
   - Q2S strategy (with the scenario's α value)
   - AvgSat strategy
   - MinSat strategy
   - Random strategy

3. **Perturbation Application**: The predefined perturbations are applied to the selected plans, potentially making previously valid plans invalid

4. **Performance Evaluation**: For each strategy, the system measures:
   - **Success**: Whether the selected plan remains valid after perturbation
   - **Margin**: The distance from constraint boundaries after perturbation

This procedure allows for direct comparison of strategy robustness across thousands of scenarios with varying conditions and perturbation levels.

### Variables

**Independent variables** include:
- Perturbation type (which constraint changes) and intensity (low, medium, high)
- Plan selection strategy:
  - **Q2S approach**: Combines average satisfaction distance and minimum satisfaction distance with α parameter
  - **Maximum average distance (AvgSat)**: Selects the plan with the highest average distance to constraint boundaries
  - **Minimum distance (MinSat)**: Selects the plan with the lowest margin to constraint boundaries
  - **Random plan selection**: Randomly selects any plan that satisfies all constraints (baseline)

**Dependent variables** measured:
- Success rate: percentage of scenarios without constraint violations after perturbation
- Constraint margin: normalized distance to violation

We evaluate the Q2S approach using two case studies, each defined by a JSON configuration file (see [CONFIGURATION.md](CONFIGURATION.md) for configuration details):

### Case Study 1: Meeting Scheduler

The Meeting Scheduler case study involves planning meetings with different parameters:
- Participants: 5-50
- Available organizers: 1-5
- Time constraints: 1-14 days
- Budget constraints: $100-$1000

Three quality objectives are defined:
- QG0: Cost ≤ threshold
- QG1: Effort ≤ threshold
- QG2: Time ≤ threshold

**Key Findings**:

The experimental results from scenarios with the Meeting Scheduler showed:

- **Success rates** (percentage of plans that remain valid after perturbation):
  - Avg: 22.33%
  - Score: 21.00%
  - Min: 19.40%
  - Rnd: 16.38%

- **Average margins** (distance from constraints after perturbation):
  - Avg: 0.3145
  - Score: 0.3067
  - Min: 0.2812
  - Rnd: 0.2586

- **Score strategy by alpha**:
  - α=0.3: Success Rate = 20.40%, Margin = 0.0611
  - α=0.5: Success Rate = 20.40%, Margin = 0.0621
  - α=0.7: Success Rate = 22.20%, Margin = 0.0700

### Case Study 2: Cleaning Robot

The Cleaning Robot case study involves a robot with different constraints:
- Power consumption
- Cleaning precision
- Noise levels
- Time to complete tasks

Four quality objectives are defined:
- QG0: Consumption ≤ threshold
- QG1: Imprecision ≤ threshold
- QG2: Noise ≤ threshold
- QG3: Time ≤ threshold

**Key Findings**:

The experimental results from scenarios with the Cleaning Robot showed:

- **Success rates** (percentage of plans that remain valid after perturbation):
  - Score: 25.49%
  - Avg: 23.17%
  - Min: 23.10%
  - Rnd: 18.60%

- **Average margins** (distance from constraints after perturbation):
  - Avg: 0.2967
  - Score: 0.2624
  - Min: 0.2381
  - Rnd: 0.2544

- **Score strategy by alpha**:
  - α=0.3: Success Rate = 24.30%, Margin = 0.0589
  - α=0.5: Success Rate = 26.16%, Margin = 0.0670
  - α=0.7: Success Rate = 26.00%, Margin = 0.0747

## Project Structure

The current project structure is as follows:

```
.
├── README.md
├── requirements.txt
├── doc.md
├── pipeline.py                                    # Main pipeline orchestrator
├── pipeline1_scenario_generator.py               # Step 1: Generate scenarios
├── pipeline2-1_data_analysis_pre_process.py      # Step 2.1: Pre-process data
├── pipeline2-2_data_analysis_single_perturbation.py  # Step 2.2: Single perturbation analysis
├── pipeline2-3_data_analysis_multiple_perturbation.py # Step 2.3: Multiple perturbation analysis
├── pipeline3_data_visualization.py               # Step 3: Create visualizations
├── data/
│   ├── meeting_scheduler.json                     # Meeting scheduler configuration
│   ├── cleaning_robot.json                       # Cleaning robot configuration
│   ├── exp1_ms_plans.csv                         # Meeting scheduler plans
│   ├── exp1_ms_contributions.csv                 # Meeting scheduler contributions
│   ├── exp1_cr_plans.csv                         # Cleaning robot plans
│   └── exp1_cr_contributions.csv                 # Cleaning robot contributions
├── meeting_scheduler_results/
│   ├── scenarios.csv                              # Generated scenarios
│   ├── pre_processed_scenarios.csv               # Pre-processed data
│   ├── tables/                                    # Analysis tables
│   │   ├── scenarios_*_single_perturbation.csv   # Single perturbation data
│   │   ├── summary_*_single_perturbation.csv     # Single perturbation summaries
│   │   ├── scenarios_perturbation_severity.csv   # Multiple perturbation data
│   │   └── summary_multiple_perturbation.csv     # Multiple perturbation summary
│   └── plots/                                     # Generated visualizations
│       ├── histo_single_*_perturbation_*.png     # Single perturbation plots
│       └── histo_multi_perturbation_*.png        # Multiple perturbation plots
├── cleaning_robot_results/
│   ├── scenarios.csv
│   ├── pre_processed_scenarios.csv
│   ├── tables/
│   └── plots/
├── q2s_matrix.py                                  # Q2S matrix implementation
├── q2s_utils.py                                   # Utility functions
├── exp1_scenario.py                              # Core scenario processing
└── exp1_log.py                                   # Logging utilities
```

## Pipeline Overview

The analysis pipeline consists of 5 sequential steps:

1. **Pipeline 1 - Scenario Generation**: Generates all possible scenario combinations based on configuration parameters
2. **Pipeline 2.1 - Data Pre-processing**: Groups scenarios by alpha values for analysis
3. **Pipeline 2.2 - Single Perturbation Analysis**: Analyzes scenarios where only one quality goal is perturbed
4. **Pipeline 2.3 - Multiple Perturbation Analysis**: Analyzes scenarios with combined perturbations across multiple quality goals
5. **Pipeline 3 - Data Visualization**: Creates histogram plots comparing strategy performance

Each step produces intermediate files that are used by subsequent steps, allowing for modular execution and debugging.

## Prerequisites

The following libraries are required:
- numpy
- pandas
- matplotlib

## Environment Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Complete Pipeline Execution

To run the complete analysis pipeline, use the main pipeline script with a JSON configuration file. See [CONFIGURATION.md](CONFIGURATION.md) for details on creating configuration files.

```bash
python pipeline.py <configuration_file>
```

Examples:
```bash
python pipeline.py data/meeting_scheduler.json
python pipeline.py data/cleaning_robot.json
```

### Individual Pipeline Steps

You can also run individual pipeline steps:

```bash
# Step 1: Generate scenarios
python pipeline1_scenario_generator.py data/meeting_scheduler.json

# Step 2.1: Pre-process data
python pipeline2-1_data_analysis_pre_process.py data/meeting_scheduler.json

# Step 2.2: Single perturbation analysis
python pipeline2-2_data_analysis_single_perturbation.py data/meeting_scheduler.json

# Step 2.3: Multiple perturbation analysis
python pipeline2-3_data_analysis_multiple_perturbation.py data/meeting_scheduler.json

# Step 3: Create visualizations
python pipeline3_data_visualization.py data/meeting_scheduler.json
```

### Skipping Pipeline Steps

You can skip specific steps if you want to rerun only parts of the pipeline:

```bash
# Skip scenario generation (step 1) and pre-processing (step 2.1)
python pipeline.py data/meeting_scheduler.json --skip-step 1 --skip-step 2
```

## Configuration Files

The pipeline uses JSON configuration files to define experiments. See [CONFIGURATION.md](CONFIGURATION.md) for detailed documentation on creating and customizing configuration files.

## Output Files

The pipeline generates several types of output files:

### Data Files
- `scenarios.csv`: Raw generated scenarios
- `pre_processed_scenarios.csv`: Scenarios grouped by alpha values
- `tables/scenarios_*_single_perturbation.csv`: Filtered data for single perturbations
- `tables/summary_*_single_perturbation.csv`: Statistical summaries for single perturbations
- `tables/scenarios_perturbation_severity.csv`: Data with combined perturbation scores
- `tables/summary_multiple_perturbation.csv`: Statistical summary for multiple perturbations

### Visualization Files
- `plots/histo_single_*_perturbation_success.png`: Success rate comparisons for single perturbations
- `plots/histo_single_*_perturbation_margin.png`: Margin comparisons for single perturbations
- `plots/histo_multi_perturbation_success.png`: Success rate comparison for multiple perturbations
- `plots/histo_multi_perturbation_margin.png`: Margin comparison for multiple perturbations

## Testing

Run the test suite to verify the implementation:

```bash
python test_q2s_matrix.py
python test_q2s_utils.py
python test_scenario.py
```

## Contributing

When adding new case studies or modifications:

1. Create appropriate `plans.csv` and `contributions.csv` files in the `data/` directory
2. Create a corresponding JSON configuration file (see [CONFIGURATION.md](CONFIGURATION.md) for guidance)
3. Test the configuration with the pipeline
4. Update documentation as needed

For detailed information about the project implementation and design decisions, see [doc.md](doc.md).
