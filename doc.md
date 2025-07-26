# Detailed Description of the Q2S (Quality to Satisfaction) Project

## Essential Summary of Q2S Theory

The Quality to Satisfaction (Q2S) matrix is a tool designed to evaluate and compare different plans based on their ability to satisfy quality objectives. For each plan-objective combination, the Q2S matrix calculates a "satisfaction distance" that represents how well the plan satisfies the objective.

Values in the Q2S matrix represent:
- **Positive values**: satisfaction with margin (higher is better)
- **Zero**: exact satisfaction
- **Negative values**: constraint violation

The basic formula for calculating the satisfaction distance for "max" type constraints is:
```
d_{i,j} = (MaxValue[j] - ActualValue[i,j]) / MaxValue[j]
```

This matrix is used to:
1. **Filter invalid plans** (those with negative values)
2. **Rank valid plans** to select the most promising one

For plan selection, a strategy based on the Hurwicz criterion is used:
```
Score = α * AvgSat + (1-α) * MinSat
```
where:
- `AvgSat` is the average satisfaction distance for all objectives
- `MinSat` is the minimum satisfaction distance (worst case)
- `α` is a parameter that balances optimism and pessimism (typically 0.3, 0.5, or 0.7)

## Introduction to the Meeting Scheduler Case Study

The Meeting Scheduler case study represents a common but complex problem in organizational settings: efficiently planning meetings while considering various constraints. In this context, a meeting must be organized among several participants, considering their availability, preferences, and organizational resources.

The system aims to support the following activities:
- Characterizing the meeting (purpose, participants, duration)
- Collecting participants' timetables (manually or automatically)
- Finding suitable rooms (institutional, convention center, or local)
- Choosing an optimal schedule
- Organizing additional services like coffee breaks
- Notifying participants (via email or phone)

Each of these activities has implications for quality aspects such as cost, time, and effort required to organize the meeting. The Q2S approach helps in selecting the best implementation plan that balances these quality objectives.

### Summary of the Case Study (Meeting Scheduler)

The case study is a meeting planning system with different functional objectives:
- G0: Meeting Scheduled
- G1: Meeting Characterized
- G2: Timetables Collected
- G3: Suitable Room Found
- G4: Schedule Chosen
- G5: Coffee Break Organized
- G6: Manually Collected Timetables
- G7: Automatically Collected Timetables
- G8: Institution Used
- G9: Convention Centre Used
- G10: Local Room Used
- G11: Manually Scheduled
- G12: Automatically Scheduled
- G13: Participants Emailed
- G14: Participants Called

And three quality objectives:
- QG0: Cost ≤ threshold
- QG1: Effort ≤ threshold
- QG2: Time ≤ threshold

Plans are combinations of these functional objectives, and each plan has different impacts on cost, time, and effort.

## Type of Experiment

The experiment evaluates the effectiveness of different plan selection strategies in the presence of perturbations. The experimental procedure follows these sequential steps:

1. **Scenario Definition**: Each scenario is defined by:
   - **Alpha value (α)**: Parameter balancing optimism/pessimism (0.3, 0.5, or 0.7)
   - **Initial constraint configuration**: Base values for all quality goal constraints
   - **Perturbation values**: Specific changes to be applied to each constraint

2. **Plan Selection**: For each scenario, all strategies select their preferred plan:
   - Q2S strategy (with the scenario's α value)
   - AvgSat strategy
   - MinSat strategy
   - Random strategy

3. **Perturbation Application**: The predefined perturbations are applied to the selected plans, potentially making previously valid plans invalid

4. **Performance Evaluation**: For each strategy, the system measures:
   - **Success**: Whether the selected plan remains valid after perturbation
   - **Margin**: The distance from constraint boundaries after perturbation

The strategies compared are:

1. **Q2S**: Combines AvgSat and MinSat according to the α parameter
2. **AvgSat**: Selects the plan with the best average distance
3. **MinSat**: Selects the plan with the best minimum distance
4. **Random**: Randomly selects a valid plan (baseline)

The experiment measures:
- **Success rate**: percentage of plans that remain valid after perturbation
- **Average margins**: average distance from constraints after perturbation

## Pipeline Architecture

The experimental framework consists of 6 main components:

### 1. Main Pipeline Orchestrator (`pipeline.py`)
- **Purpose**: Coordinates the execution of all pipeline steps
- **Input**: Configuration JSON file
- **Function**:
  - Validates configuration file
  - Executes each pipeline step in sequence
  - Handles errors and provides progress tracking
  - Supports selective step execution with `--skip-step` option
- **Usage**: `python pipeline.py <config_file>`

### 2. Scenario Generator (`pipeline1_scenario_generator.py`)
- **Purpose**: Generates all possible combinations of scenario parameters
- **Input**: Configuration file specifying alpha options, constraint values, and perturbation levels
- **Process**:
  - Creates all combinations of alpha values, constraint configurations, and perturbation levels
  - For each combination, generates a unique scenario with ID
  - Calculates Q2S matrix for each scenario
  - Applies different selection strategies
  - Records plan selection results
- **Output**: `scenarios.csv` containing all generated scenarios with strategy results

### 3. Data Pre-processor (`pipeline2-1_data_analysis_pre_process.py`)
- **Purpose**: Groups scenarios that differ only by alpha value
- **Input**: `scenarios.csv`
- **Process**:
  - Groups rows with identical constraints and perturbations but different alpha values
  - Creates separate columns for ScorePlan results for each alpha (Score0_3Plan, Score0_5Plan, Score0_7Plan)
  - Consolidates AvgPlan, MinPlan, and RndPlan results (identical across alphas)
- **Output**: `pre_processed_scenarios.csv`

### 4. Single Perturbation Analyzer (`pipeline2-2_data_analysis_single_perturbation.py`)
- **Purpose**: Analyzes scenarios where only one quality goal is perturbed
- **Input**: `pre_processed_scenarios.csv`
- **Process**:
  - For each quality goal, filters scenarios where only that goal has perturbations
  - Includes baseline cases (perturbation = 0) for comparison
  - Creates summary statistics for each perturbation level
  - Calculates success rates, average margins, and variance margins for all strategies
- **Output**:
  - `tables/scenarios_{quality_goal}_single_perturbation.csv` (filtered data)
  - `tables/summary_{quality_goal}_single_perturbation.csv` (statistical summaries)

### 5. Multiple Perturbation Analyzer (`pipeline2-3_data_analysis_multiple_perturbation.py`)
- **Purpose**: Analyzes scenarios with combined perturbations across multiple quality goals
- **Input**: `pre_processed_scenarios.csv`
- **Process**:
  - Calculates perturbation severity scores by summing individual perturbation scores
  - Groups scenarios by total perturbation severity
  - Creates summary statistics for each severity level
  - Analyzes strategy performance under different levels of combined stress
- **Output**:
  - `tables/scenarios_perturbation_severity.csv` (data with severity scores)
  - `tables/summary_multiple_perturbation.csv` (statistical summary)

### 6. Visualization Generator (`pipeline3_data_visualization.py`)
- **Purpose**: Creates histogram plots comparing strategy performance
- **Input**: All summary CSV files from previous steps
- **Process**:
  - For each quality goal: creates success rate and margin comparison plots for single perturbations
  - For multiple perturbations: creates global severity comparison plots
  - Uses consistent pastel color palette across all visualizations
  - Generates publication-ready plots with proper legends and labels
- **Output**:
  - `plots/histo_single_{quality_goal}_perturbation_success.png`
  - `plots/histo_single_{quality_goal}_perturbation_margin.png`
  - `plots/histo_multi_perturbation_success.png`
  - `plots/histo_multi_perturbation_margin.png`

## Input and Output Data Formats

### Input:

1. **Configuration File** (JSON):
   - Defines file paths, quality goals, scenario parameters, and output settings
   - See CONFIGURATION.md for detailed format specification

   ```json
   {
     "file_paths": {
       "plans": "data/exp1_ms_plans.csv",
       "contributions": "data/exp1_ms_contributions.csv"
     },
     "quality_goals": [...],
     "scenario_generator": {...},
     "simulation_settings": {...}
   }
   ```

2. **Plans File** (`*_plans.csv`):
   - Defines the composition of plans in terms of functional goals
   - Format: 0/1 matrix where rows are plans and columns are goals

   ```
   PLANS,G1,G5,G7,G8,G9,G10,G11,G12,G13,G14
   Plan0,1,1,0,1,0,0,1,0,1,0
   Plan1,1,1,0,1,0,0,1,0,0,1
   ...
   ```

3. **Contributions File** (`*_contributions.csv`):
   - Defines how each goal contributes to domain variables
   - Format: rows = domain variables, columns = goals

   ```
   DomainVariable,G1,G5,G7,G8,G9,G10,G11,G12,G13,G14
   TotalCost,,100,,80,200,,,,,
   TotalEffort,,,1,,,,2,1,2,4
   TimeSpent,1,1,1,1,1,,2,1,2,4
   ```

### Output:

The pipeline generates a structured output directory with the following organization:

```
{output_directory}/
├── scenarios.csv                              # Raw generated scenarios
├── pre_processed_scenarios.csv               # Alpha-grouped scenarios
├── tables/                                    # Analysis tables
│   ├── scenarios_{quality_goal}_single_perturbation.csv
│   ├── summary_{quality_goal}_single_perturbation.csv
│   ├── scenarios_perturbation_severity.csv
│   └── summary_multiple_perturbation.csv
└── plots/                                     # Visualizations
    ├── histo_single_{quality_goal}_perturbation_success.png
    ├── histo_single_{quality_goal}_perturbation_margin.png
    ├── histo_multi_perturbation_success.png
    └── histo_multi_perturbation_margin.png
```

#### Main Data Files:

1. **scenarios.csv**:
   - Generated by pipeline step 1
   - Contains all scenario combinations with strategy selection results

   ```
   ID,alpha,cost_constraint,effort_constraint,time_constraint,cost_constraint_perturbation,effort_constraint_perturbation,time_constraint_perturbation,num_valid_plans,ScorePlan_ID,ScorePlan_success,ScorePlan_margins,AvgPlan_ID,AvgPlan_success,AvgPlan_margins,MinPlan_ID,MinPlan_success,MinPlan_margins,RndPlan_ID,RndPlan_success,RndPlan_margins
   1,0.3,270,6,9,0,0,0,18,Plan8,1,0.4259,Plan17,1,0.4815,Plan6,1,0.358,Plan12,1,0.3025
   ...
   ```

2. **pre_processed_scenarios.csv**:
   - Generated by pipeline step 2.1
   - Alpha-grouped scenarios with separate columns for each alpha's ScorePlan results

3. **Summary Tables** (`tables/summary_*.csv`):
   - Generated by pipeline steps 2.2 and 2.3
   - Statistical summaries with success rates, average margins, and variance margins
   - Used for generating visualizations

## Scenario Parameters

### Event size:
- "small": 5-10 participants
- "medium": 15-25 participants
- "big": 30-50 participants

### Organizers:
- 1, 2, or 3 organizers

### Available time:
- 2, 6, or 14 days

### Budget:
- 100, 200, or 500 euros

### Alpha (α):
- 0.3: More pessimistic strategy (prefers minimum margins)
- 0.5: Balanced strategy
- 0.7: More optimistic strategy (prefers average margins)

### Perturbations:
For each dimension (organizers, time, cost), perturbation levels are:
- "no": No change (score: 0)
- "low_neg": Slight deterioration (score: 1)
- "high_neg": Significant deterioration (score: 2)
- "catastrophic": Severe deterioration (score: 3)

Specific values vary by case study and are defined in the configuration file's perturbation mappings.

## Data Loading Strategy

Data is loaded from external CSV files for maximum flexibility:

1. **Loading plans**:
   ```python
   def load_plans(file_path="data/exp1_plans.csv"):
       plans = {}
       df = pd.read_csv(file_path)
       for _, row in df.iterrows():
           plan_id = row['PLANS']
           goals = []
           for col in df.columns[1:]:
               if row[col] == 1:
                   goals.append(col)
           plans[plan_id] = {"name": plan_id, "goals": goals}
       return plans
   ```

2. **Loading contributions**:
   ```python
   def load_contributions(file_path="data/exp1_contributions.csv"):
       contributions = {}
       df = pd.read_csv(file_path)
       for _, row in df.iterrows():
           domain_var = row['DomainVariable']
           goal_contributions = {}
           for col in df.columns[1:]:
               if pd.notna(row[col]):
                   goal_contributions[col] = float(row[col])
           contributions[domain_var] = goal_contributions
       return contributions
   ```

3. **Loading quality goals from configuration**:
   ```python
   def load_quality_goals_from_config(config):
       quality_goals = {}
       for qg in config['quality_goals']:
           qg_id = qg['id']
           quality_goals[qg_id] = {
               "name": qg_id,
               "domain_variable": qg['domain_variable'],
               "column_name": qg['column_name'],
               "type": qg.get('relation_type', 'max')
           }
       return quality_goals
   ```

## Event Size Adaptation Strategy

To make costs, effort, and time more realistically dependent on event size, we introduce scaling factors applied during impact calculation:

1. **Base factors for event size**:
   - Small: 1x factor (base values)
   - Medium: 2-3x factor
   - Big: 4-6x factor

2. **Specific modifiers for activities**:
   - Convention Centre (G9): scales significantly with size (3x medium, 7x big)
   - Local Room (G10): scales moderately (1.5x medium, 2.5x big)
   - Coffee Break (G5): scales linearly with participants
   - Email (G13): scales minimally (1.2x medium, 1.5x big)
   - Call (G14): scales linearly with participants
   - Manual Scheduling (G11): scales exponentially (2x medium, 5x big)

3. **Implementation**: Instead of directly modifying the CSV file, adapt the `calculate_plan_impact()` function to apply these modifiers based on `event_size`.

This approach maintains the original data files but introduces greater variability in values, making the experiment more realistic.

## Running the Complete Pipeline

To execute the full experimental pipeline:

```bash
# Complete pipeline execution
python pipeline.py data/meeting_scheduler.json
python pipeline.py data/cleaning_robot.json

# Execute specific steps only
python pipeline1_scenario_generator.py data/meeting_scheduler.json
python pipeline2-1_data_analysis_pre_process.py data/meeting_scheduler.json
python pipeline2-2_data_analysis_single_perturbation.py data/meeting_scheduler.json
python pipeline2-3_data_analysis_multiple_perturbation.py data/meeting_scheduler.json
python pipeline3_data_visualization.py data/meeting_scheduler.json

# Skip certain steps
python pipeline.py data/meeting_scheduler.json --skip-step 1 --skip-step 2
```

The pipeline automatically creates the output directory structure and processes all scenarios according to the configuration parameters.
