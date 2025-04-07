# Q2S Experiment Summary Report
Generated on: 2025-03-25 16:22:32

## Overview
- Total scenarios analyzed: 12288
- Scenarios with valid plans: 8640 (70.3%)
- Average number of valid plans per scenario: 9.2

## Strategy Performance Comparison

### Success Rates (percentage of plans that remain valid after perturbation)
| Strategy | Success Rate (%) |
|----------|-----------------|
| Q2S | 42.50% |
| Avg | 42.50% |
| Min | 42.50% |
| Random | 38.14% |

### Average Margins (distance from constraints after perturbation)
| Strategy | Average Margin |
|----------|---------------|
| Q2S | -0.0373 |
| Avg | -0.0373 |
| Min | -0.0516 |
| Random | -0.1511 |

## Key Findings
- The best performing strategy is **Q2S** with a success rate of 42.50%
- Compared to Random strategy baseline, Q2S performs 4.36% better

### Performance of Q2S by Alpha Value
| Alpha | Success Rate (%) | Margin |
|-------|-----------------|--------|
| 0.3 | 42.50% | -0.0373 |
| 0.5 | 42.50% | -0.0373 |
| 0.7 | 42.50% | -0.0373 |

The optimal alpha value appears to be **0.3** with a success rate of 42.50%

## Performance Under Negative Perturbations

### perturbation_level_cost
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 40.00% | -0.0795 |
| Avg | 40.00% | -0.0795 |
| Min | 40.00% | -0.0939 |
| Random | 33.91% | -0.1934 |

### perturbation_level_effort
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 37.50% | -0.0649 |
| Avg | 37.50% | -0.0649 |
| Min | 37.50% | -0.0813 |
| Random | 31.03% | -0.1855 |

### perturbation_level_time
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 0.00% | -1.0003 |
| Avg | 0.00% | -1.0003 |
| Min | 0.00% | -1.0146 |
| Random | 0.00% | -1.1138 |

## Conclusion
Based on the experiment results, the Q2S strategy demonstrates the highest resilience to perturbations,
with a success rate of 42.50%. This indicates that Q2S's approach to plan selection
provides better robustness against uncertainties in the execution environment.
