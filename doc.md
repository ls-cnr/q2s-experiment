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
3. **Guide the objective relaxation process** when no plan satisfies all constraints

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

The experiment evaluates the effectiveness of different plan selection strategies in the presence of perturbations. The strategies compared are:

1. **Q2S**: Combines AvgSat and MinSat according to the α parameter
2. **AvgSat**: Selects the plan with the best average distance
3. **MinSat**: Selects the plan with the best minimum distance
4. **Random**: Randomly selects a valid plan (baseline)

The experiment consists of generating scenarios with different parameter combinations, selecting plans with different strategies, applying perturbations, and measuring:
- **Success rate**: percentage of plans that remain valid after perturbation
- **Average margins**: average distance from constraints after perturbation

## Function of the 3 Scripts

1. **Scenario Generator** (`scenario_generator.py`):
   - Generates all possible combinations of scenario parameters
   - Saves these combinations to a CSV file (`all_scenarios.csv`)

2. **Scenario Processor** (`scenario_processor.py`):
   - Loads plans, contributions, and quality objectives from CSV files
   - For each scenario in the file:
     - Calculates the impacts of each plan
     - Filters valid plans
     - Calculates the Q2S matrix
     - Applies different selection strategies
     - Applies perturbations to selected plans
     - Checks if they remain valid
     - Records the results
   - Saves all results to a CSV file (`all_scenarios_results.csv`)

3. **Results Analyzer** (`results_analyzer.py`):
   - Loads results from the CSV file
   - Calculates summary statistics
   - Generates visualizations
   - Produces a synthetic report (`experiment_summary.csv`)

## Input and Output Data Formats

### Input:

1. **exp1_plans.csv**:
   - Defines the composition of plans in terms of functional goals
   - Format: 0/1 matrix where rows are plans and columns are goals

   ```
   PLANS,G1,G5,G7,G8,G9,G10,G11,G12,G13,G14
   Plan0,1,1,0,1,0,0,1,0,1,0
   Plan1,1,1,0,1,0,0,1,0,0,1
   ...
   ```

2. **exp1_contributions.csv**:
   - Defines how each goal contributes to domain variables
   - Format: rows = domain variables, columns = goals

   ```
   DomainVariable,G1,G5,G7,G8,G9,G10,G11,G12,G13,G14
   TotalCost,,100,,80,200,,,,,
   TotalEffort,,,1,,,,2,1,2,4
   TimeSpent,1,1,1,1,1,,2,1,2,4
   ```

3. **exp1_quality_goals.csv**:
   - Defines quality goals and their constraints
   - Format: list of goals with associated domain variable and constraint

   ```
   Quality Goals,Domain Variable,QG constraints
   QG0,TotalCost,200
   QG1,TotalEffort,3
   QG2,TimeSpent,6
   ```

4. **all_scenarios.csv**:
   - Generated by the first script
   - Contains all scenarios to be processed

   ```
   id,event_size,organizers,time,budget,alpha,perturbation_level_org,perturbation_level_time,perturbation_level_cost
   1,small,1,2,100,0.3,pos,no,low_neg
   ...
   ```

### Output:

1. **all_scenarios_results.csv**:
   - Generated by the second script
   - Contains results for each scenario

   ```
   id,event_size,organizers,time,budget,perturbation_level_org,perturbation_level_time,perturbation_level_cost,alpha,Q2S_success,Q2S_margins,Avg_success,Avg_margins,Min_success,Min_margins,Random_success,Random_margins,num_valid_plans
   ```

2. **experiment_summary.csv**:
   - Generated by the third script
   - Contains summary statistics of the experiment

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
- "pos": Improvement (compared to planned values)
- "no": No change
- "low_neg": Slight deterioration
- "high_neg": Significant deterioration

Specific values for perturbation:
```python
PERTURBATION_VALUE = {
    "org": {
        "pos": -1,        # 1 more organizer
        "no": 0,          # No change
        "low_neg": 1,     # 1 fewer organizer
        "high_neg": 2     # 2 fewer organizers
    },
    "time": {
        "pos": -24,       # 1 day less (hours)
        "no": 0,          # No change
        "low_neg": 24,    # 1 extra day (hours)
        "high_neg": 48    # 2 extra days (hours)
    },
    "cost": {
        "pos": -50,       # 50 euros less
        "no": 0,          # No change
        "low_neg": 50,    # 50 euros more
        "high_neg": 100   # 100 euros more
    }
}
```

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

3. **Loading quality goals**:
   ```python
   def load_quality_goals(file_path="data/exp1_quality_goals.csv"):
       quality_goals = {}
       df = pd.read_csv(file_path)
       for _, row in df.iterrows():
           qg_id = row['Quality Goals']
           domain_var = row['Domain Variable']
           constraint = float(row['QG constraints'])
           quality_goals[qg_id] = {
               "name": qg_id,
               "domain_variable": domain_var,
               "max_value": constraint,
               "type": "max"
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

This document contains all the essential information to continue the project in another chat or session, preserving the decisions made and the implemented structure.
