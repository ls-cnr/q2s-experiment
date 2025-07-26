# Configuration Guide

This document explains how to create and customize JSON configuration files for the Q2S experimental pipeline.

## Overview

Configuration files define the parameters for experimental scenarios, including:
- Input data file paths
- Quality goals and constraints
- Scenario generation parameters
- Output settings

## Configuration File Structure

A configuration file is a JSON document with four main sections:

```json
{
  "file_paths": { ... },
  "quality_goals": [ ... ],
  "scenario_generator": { ... },
  "simulation_settings": { ... }
}
```

## Section Descriptions

### 1. File Paths

Specifies the location of input CSV files containing plans and contributions data.

```json
"file_paths": {
  "plans": "data/exp1_ms_plans.csv",
  "contributions": "data/exp1_ms_contributions.csv"
}
```

**Fields:**
- `plans`: Path to CSV file defining plan compositions (which goals each plan includes)
- `contributions`: Path to CSV file defining how goals contribute to domain variables

### 2. Quality Goals

Defines the quality objectives that plans must satisfy.

```json
"quality_goals": [
  {
    "id": "QG0",
    "domain_variable": "TotalCost",
    "relation_type": "max",
    "column_name": "cost_constraint"
  },
  {
    "id": "QG1",
    "domain_variable": "TotalEffort",
    "relation_type": "max",
    "column_name": "effort_constraint"
  }
]
```

**Fields:**
- `id`: Unique identifier for the quality goal
- `domain_variable`: Name of the domain variable from the contributions file
- `relation_type`: Constraint type (currently only "max" is supported)
- `column_name`: Name used for this constraint in generated scenario files

### 3. Scenario Generator

Defines the parameters for generating experimental scenarios.

```json
"scenario_generator": {
  "alpha_options": [0.3, 0.5, 0.7],
  "constraint_options": [
    {
      "domain_variable": "cost_constraint",
      "values": [270, 210, 190],
      "perturbation": [
        { "level": "no", "value": 0, "score": 0 },
        { "level": "low_neg", "value": -10, "score": 1 },
        { "level": "high_neg", "value": -75, "score": 2 },
        { "level": "catastrofic", "value": -100, "score": 3 }
      ]
    }
  ]
}
```

**Fields:**
- `alpha_options`: Array of α values for the Q2S strategy (balances optimism/pessimism)
- `constraint_options`: Array of constraint configurations, one per quality goal

**Constraint Options Fields:**
- `domain_variable`: Must match a `column_name` from quality_goals
- `values`: Array of baseline constraint values to test
- `perturbation`: Array of perturbation levels with:
  - `level`: Descriptive name for the perturbation level
  - `value`: Numeric change applied to the constraint
  - `score`: Severity score (0=no change, higher=more severe)

### 4. Simulation Settings

Specifies output configuration.

```json
"simulation_settings": {
  "output_directory": "meeting_scheduler_results",
  "scenarios_filename": "scenarios.csv"
}
```

**Fields:**
- `output_directory`: Directory where all output files will be saved
- `scenarios_filename`: Name of the main scenarios file (usually "scenarios.csv")

## Complete Examples

### Meeting Scheduler Configuration

```json
{
  "file_paths": {
    "plans": "data/exp1_ms_plans.csv",
    "contributions": "data/exp1_ms_contributions.csv"
  },
  "quality_goals": [
    {
      "id": "QG0",
      "domain_variable": "TotalCost",
      "relation_type": "max",
      "column_name": "cost_constraint"
    },
    {
      "id": "QG1",
      "domain_variable": "TotalEffort",
      "relation_type": "max",
      "column_name": "effort_constraint"
    },
    {
      "id": "QG2",
      "domain_variable": "TimeSpent",
      "relation_type": "max",
      "column_name": "time_constraint"
    }
  ],
  "scenario_generator": {
    "alpha_options": [0.3, 0.5, 0.7],
    "constraint_options": [
      {
        "domain_variable": "cost_constraint",
        "values": [270, 210, 190],
        "perturbation": [
          { "level": "no", "value": 0, "score": 0 },
          { "level": "low_neg", "value": -10, "score": 1 },
          { "level": "high_neg", "value": -75, "score": 2 },
          { "level": "catastrofic", "value": -100, "score": 3 }
        ]
      },
      {
        "domain_variable": "effort_constraint",
        "values": [6, 4],
        "perturbation": [
          { "level": "no", "value": 0, "score": 0 },
          { "level": "low_neg", "value": -2, "score": 1 },
          { "level": "high_neg", "value": -4, "score": 2 },
          { "level": "catastrofic", "value": -6, "score": 3 }
        ]
      },
      {
        "domain_variable": "time_constraint",
        "values": [9, 7],
        "perturbation": [
          { "level": "no", "value": 0, "score": 0 },
          { "level": "low_neg", "value": -2, "score": 1 },
          { "level": "high_neg", "value": -5, "score": 2 },
          { "level": "catastrofic", "value": -10, "score": 3 }
        ]
      }
    ]
  },
  "simulation_settings": {
    "output_directory": "meeting_scheduler_results",
    "scenarios_filename": "scenarios.csv"
  }
}
```

### Cleaning Robot Configuration

```json
{
  "file_paths": {
    "plans": "data/exp1_cr_plans.csv",
    "contributions": "data/exp1_cr_contributions.csv"
  },
  "quality_goals": [
    {
      "id": "QG0",
      "domain_variable": "Consumption",
      "relation_type": "max",
      "column_name": "consume_constraint"
    },
    {
      "id": "QG1",
      "domain_variable": "Imprecision",
      "relation_type": "max",
      "column_name": "imprecision_constraint"
    },
    {
      "id": "QG2",
      "domain_variable": "Noise",
      "relation_type": "max",
      "column_name": "noise_constraint"
    },
    {
      "id": "QG3",
      "domain_variable": "Time",
      "relation_type": "max",
      "column_name": "time_constraint"
    }
  ],
  "scenario_generator": {
    "alpha_options": [0.3, 0.5, 0.7],
    "constraint_options": [
      {
        "domain_variable": "consume_constraint",
        "values": [4900, 4000, 3000],
        "perturbation": [
          { "level": "no", "value": 0, "score": 0 },
          { "level": "low_neg", "value": -500, "score": 1 },
          { "level": "high_neg", "value": -1000, "score": 2 },
          { "level": "catastrofic", "value": -2000, "score": 3 }
        ]
      },
      {
        "domain_variable": "imprecision_constraint",
        "values": [70, 65],
        "perturbation": [
          { "level": "no", "value": 0, "score": 0 },
          { "level": "low_neg", "value": -5, "score": 1 },
          { "level": "high_neg", "value": -10, "score": 2 },
          { "level": "catastrofic", "value": -20, "score": 3 }
        ]
      },
      {
        "domain_variable": "noise_constraint",
        "values": [30, 20],
        "perturbation": [
          { "level": "no", "value": 0, "score": 0 },
          { "level": "low_neg", "value": -5, "score": 1 },
          { "level": "high_neg", "value": -10, "score": 2 },
          { "level": "catastrofic", "value": -20, "score": 3 }
        ]
      },
      {
        "domain_variable": "time_constraint",
        "values": [200, 150],
        "perturbation": [
          { "level": "no", "value": 0, "score": 0 },
          { "level": "low_neg", "value": -50, "score": 1 },
          { "level": "high_neg", "value": -70, "score": 2 },
          { "level": "catastrofic", "value": -100, "score": 3 }
        ]
      }
    ]
  },
  "simulation_settings": {
    "output_directory": "cleaning_robot_results",
    "scenarios_filename": "scenarios.csv"
  }
}
```

## Creating a New Configuration

Follow these steps to create a configuration for a new case study:

### Step 1: Prepare Input Data Files

Create two CSV files:

**plans.csv** - Define which goals each plan includes:
```csv
PLANS,G1,G2,G3,G4,G5
Plan0,1,1,0,1,0
Plan1,1,0,1,1,0
Plan2,0,1,1,0,1
...
```

**contributions.csv** - Define how goals contribute to domain variables:
```csv
DomainVariable,G1,G2,G3,G4,G5
TotalCost,100,50,75,,200
TotalTime,2,1,3,1,
QualityLevel,,,5,10,15
...
```

### Step 2: Create the Configuration File

1. **Start with the template**:
   ```json
   {
     "file_paths": {
       "plans": "data/your_plans.csv",
       "contributions": "data/your_contributions.csv"
     },
     "quality_goals": [],
     "scenario_generator": {
       "alpha_options": [0.3, 0.5, 0.7],
       "constraint_options": []
     },
     "simulation_settings": {
       "output_directory": "your_case_study_results",
       "scenarios_filename": "scenarios.csv"
     }
   }
   ```

2. **Define quality goals** (one per domain variable from contributions.csv):
   ```json
   "quality_goals": [
     {
       "id": "QG0",
       "domain_variable": "TotalCost",
       "relation_type": "max",
       "column_name": "cost_constraint"
     }
   ]
   ```

3. **Add constraint options** (one per quality goal):
   ```json
   "constraint_options": [
     {
       "domain_variable": "cost_constraint",
       "values": [1000, 800, 600],
       "perturbation": [
         { "level": "no", "value": 0, "score": 0 },
         { "level": "low_neg", "value": -50, "score": 1 },
         { "level": "high_neg", "value": -150, "score": 2 },
         { "level": "catastrofic", "value": -300, "score": 3 }
       ]
     }
   ]
   ```

### Step 3: Test the Configuration

Run the pipeline to verify your configuration works:

```bash
python pipeline.py your_config.json
```

## Best Practices

### Constraint Values
- Use multiple baseline values to test different constraint tightness levels
- Ensure at least some plans satisfy all constraints at baseline values
- Consider realistic ranges for your domain

### Perturbation Design
- Always include a "no perturbation" level (value: 0, score: 0)
- Use negative values for constraint tightening (making constraints harder to satisfy)
- Use positive values for constraint relaxation (making constraints easier to satisfy)
- Design perturbation intensities that are meaningful for your domain

### Naming Conventions
- Use descriptive `column_name` values that clearly identify the constraint
- Keep `level` names consistent across constraints ("no", "low_neg", "high_neg", "catastrofic")
- Use meaningful directory names in `output_directory`

### Testing Strategy
- Start with a small configuration to test the pipeline
- Gradually add more constraint values and perturbation levels
- Monitor the number of scenarios generated (alpha_options × constraint_values × perturbation_combinations)

## Common Issues

### Missing Domain Variables
Ensure all `domain_variable` names in `constraint_options` match `column_name` values in `quality_goals`.

### Invalid File Paths
Verify that the paths in `file_paths` point to existing CSV files with the correct format.

### Too Many Scenarios
The total number of scenarios equals: `len(alpha_options) × (product of len(values) for each constraint) × (product of len(perturbation) for each constraint)`. Large configurations can generate millions of scenarios.

### Perturbation Score Consistency
Ensure perturbation scores increase with severity and that score 0 is always used for "no change".

## Advanced Configuration

### Custom Alpha Values
You can use any alpha values between 0 and 1:
```json
"alpha_options": [0.1, 0.25, 0.5, 0.75, 0.9]
```

### Variable Perturbation Levels
Different constraints can have different numbers of perturbation levels:
```json
{
  "domain_variable": "cost_constraint",
  "values": [1000],
  "perturbation": [
    { "level": "no", "value": 0, "score": 0 },
    { "level": "low_neg", "value": -50, "score": 1 },
    { "level": "medium_neg", "value": -100, "score": 2 },
    { "level": "high_neg", "value": -200, "score": 3 },
    { "level": "catastrofic", "value": -400, "score": 4 }
  ]
}
```

### Multiple Baseline Values
Test different constraint tightness levels:
```json
{
  "domain_variable": "time_constraint",
  "values": [100, 80, 60, 40],
  "perturbation": [...]
}
```

This will test the strategies under different levels of constraint pressure.
