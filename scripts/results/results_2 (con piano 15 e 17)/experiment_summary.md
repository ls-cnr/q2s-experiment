# Q2S Experiment Summary Report
Generated on: 2025-03-26 12:04:25

## Overview
- Total scenarios analyzed: 5184
- Scenarios with valid plans: 5184 (100.0%)
- Average number of valid plans per scenario: 16.3

## Strategy Performance Comparison

### Success Rates (percentage of plans that remain valid after perturbation)
| Strategy | Success Rate (%) |
|----------|-----------------|
| Q2S | 91.67% |
| Avg | 91.67% |
| Min | 91.67% |
| Random | 81.50% |

### Average Margins (distance from constraints after perturbation)
| Strategy | Average Margin |
|----------|---------------|
| Q2S | 0.6327 |
| Avg | 0.6327 |
| Min | 0.6327 |
| Random | 0.4506 |

## Key Findings
- The best performing strategy is **Q2S** with a success rate of 91.67%
- Compared to Random strategy baseline, Q2S performs 10.16% better

### Performance of Q2S by Alpha Value
| Alpha | Success Rate (%) | Margin |
|-------|-----------------|--------|
| 0.3 | 91.67% | 0.6327 |
| 0.5 | 91.67% | 0.6327 |
| 0.7 | 91.67% | 0.6327 |

The optimal alpha value appears to be **0.3** with a success rate of 91.67%

## Performance Under Negative Perturbations

### perturbation_level_cost
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 91.67% | 0.6045 |
| Avg | 91.67% | 0.6045 |
| Min | 91.67% | 0.6045 |
| Random | 81.14% | 0.4229 |

### perturbation_level_effort
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 91.67% | 0.5984 |
| Avg | 91.67% | 0.5984 |
| Min | 91.67% | 0.5984 |
| Random | 81.44% | 0.4169 |

### perturbation_level_time
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 83.33% | 0.5738 |
| Avg | 83.33% | 0.5738 |
| Min | 83.33% | 0.5738 |
| Random | 63.56% | 0.3921 |

## Conclusion
Based on the experiment results, the Q2S strategy demonstrates the highest resilience to perturbations,
with a success rate of 91.67%. This indicates that Q2S's approach to plan selection
provides better robustness against uncertainties in the execution environment.
