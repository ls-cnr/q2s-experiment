# Q2S Experiment Summary Report
Generated on: 2025-03-26 12:01:36

## Overview
- Total scenarios analyzed: 5184
- Scenarios with valid plans: 5184 (100.0%)
- Average number of valid plans per scenario: 14.3

## Strategy Performance Comparison

### Success Rates (percentage of plans that remain valid after perturbation)
| Strategy | Success Rate (%) |
|----------|-----------------|
| Q2S | 91.67% |
| Avg | 91.67% |
| Min | 91.67% |
| Random | 79.97% |

### Average Margins (distance from constraints after perturbation)
| Strategy | Average Margin |
|----------|---------------|
| Avg | 0.5627 |
| Q2S | 0.5625 |
| Min | 0.5594 |
| Random | 0.4294 |

## Key Findings
- The best performing strategy is **Q2S** with a success rate of 91.67%
- Compared to Random strategy baseline, Q2S performs 11.70% better

### Performance of Q2S by Alpha Value
| Alpha | Success Rate (%) | Margin |
|-------|-----------------|--------|
| 0.3 | 91.67% | 0.5625 |
| 0.5 | 91.67% | 0.5625 |
| 0.7 | 91.67% | 0.5625 |

The optimal alpha value appears to be **0.3** with a success rate of 91.67%

## Performance Under Negative Perturbations

### perturbation_level_cost
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 91.67% | 0.5343 |
| Avg | 91.67% | 0.5345 |
| Min | 91.67% | 0.5312 |
| Random | 79.50% | 0.4011 |

### perturbation_level_effort
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 91.67% | 0.5282 |
| Avg | 91.67% | 0.5285 |
| Min | 91.67% | 0.5252 |
| Random | 80.05% | 0.3956 |

### perturbation_level_time
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 83.33% | 0.5036 |
| Avg | 83.33% | 0.5039 |
| Min | 83.33% | 0.5006 |
| Random | 60.63% | 0.3709 |

## Conclusion
Based on the experiment results, the Q2S strategy demonstrates the highest resilience to perturbations,
with a success rate of 91.67%. This indicates that Q2S's approach to plan selection
provides better robustness against uncertainties in the execution environment.
