# Q2S Experiment Summary Report
Generated on: 2025-03-26 11:57:43

## Overview
- Total scenarios analyzed: 5184
- Scenarios with valid plans: 5184 (100.0%)
- Average number of valid plans per scenario: 15.3

## Strategy Performance Comparison

### Success Rates (percentage of plans that remain valid after perturbation)
| Strategy | Success Rate (%) |
|----------|-----------------|
| Q2S | 91.67% |
| Avg | 91.67% |
| Min | 91.67% |
| Random | 80.62% |

### Average Margins (distance from constraints after perturbation)
| Strategy | Average Margin |
|----------|---------------|
| Q2S | 0.5716 |
| Avg | 0.5716 |
| Min | 0.5605 |
| Random | 0.4386 |

## Key Findings
- The best performing strategy is **Q2S** with a success rate of 91.67%
- Compared to Random strategy baseline, Q2S performs 11.04% better

### Performance of Q2S by Alpha Value
| Alpha | Success Rate (%) | Margin |
|-------|-----------------|--------|
| 0.3 | 91.67% | 0.5716 |
| 0.5 | 91.67% | 0.5716 |
| 0.7 | 91.67% | 0.5716 |

The optimal alpha value appears to be **0.3** with a success rate of 91.67%

## Performance Under Negative Perturbations

### perturbation_level_cost
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 91.67% | 0.5434 |
| Avg | 91.67% | 0.5434 |
| Min | 91.67% | 0.5323 |
| Random | 80.15% | 0.4109 |

### perturbation_level_effort
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 91.67% | 0.5374 |
| Avg | 91.67% | 0.5374 |
| Min | 91.67% | 0.5263 |
| Random | 80.71% | 0.4042 |

### perturbation_level_time
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 83.33% | 0.5128 |
| Avg | 83.33% | 0.5128 |
| Min | 83.33% | 0.5017 |
| Random | 61.89% | 0.3798 |

## Conclusion
Based on the experiment results, the Q2S strategy demonstrates the highest resilience to perturbations,
with a success rate of 91.67%. This indicates that Q2S's approach to plan selection
provides better robustness against uncertainties in the execution environment.
