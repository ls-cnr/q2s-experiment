# Q2S Experiment Summary Report
Generated on: 2025-03-26 12:10:13

## Overview
- Total scenarios analyzed: 10125
- Scenarios with valid plans: 10125 (100.0%)
- Average number of valid plans per scenario: 16.3

## Strategy Performance Comparison

### Success Rates (percentage of plans that remain valid after perturbation)
| Strategy | Success Rate (%) |
|----------|-----------------|
| Q2S | 80.00% |
| Avg | 80.00% |
| Min | 80.00% |
| Random | 66.43% |

### Average Margins (distance from constraints after perturbation)
| Strategy | Average Margin |
|----------|---------------|
| Q2S | 0.5524 |
| Avg | 0.5524 |
| Min | 0.5524 |
| Random | 0.3704 |

## Key Findings
- The best performing strategy is **Q2S** with a success rate of 80.00%
- Compared to Random strategy baseline, Q2S performs 13.57% better

### Performance of Q2S by Alpha Value
| Alpha | Success Rate (%) | Margin |
|-------|-----------------|--------|
| 0.3 | 80.00% | 0.5524 |
| 0.5 | 80.00% | 0.5524 |
| 0.7 | 80.00% | 0.5524 |

The optimal alpha value appears to be **0.3** with a success rate of 80.00%

## Performance Under Negative Perturbations

### perturbation_level_cost
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 80.00% | 0.5418 |
| Avg | 80.00% | 0.5418 |
| Min | 80.00% | 0.5418 |
| Random | 67.52% | 0.3604 |

### perturbation_level_effort
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 80.00% | 0.5421 |
| Avg | 80.00% | 0.5421 |
| Min | 80.00% | 0.5421 |
| Random | 67.30% | 0.3594 |

### perturbation_level_time
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 83.33% | 0.5323 |
| Avg | 83.33% | 0.5323 |
| Min | 83.33% | 0.5323 |
| Random | 61.14% | 0.3498 |

## Conclusion
Based on the experiment results, the Q2S strategy demonstrates the highest resilience to perturbations,
with a success rate of 80.00%. This indicates that Q2S's approach to plan selection
provides better robustness against uncertainties in the execution environment.
