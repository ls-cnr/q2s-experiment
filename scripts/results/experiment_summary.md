# Q2S Experiment Summary Report
Generated on: 2025-03-28 09:24:34

## Overview
- Total scenarios analyzed: 4500
- Scenarios with valid plans: 4500 (100.0%)
- Average number of valid plans per scenario: 18.0

## Strategy Performance Comparison

### Success Rates (percentage of plans that remain valid after perturbation)
| Strategy | Success Rate (%) |
|----------|-----------------|
| Avg | 80.00% |
| Q2S | 76.89% |
| Min | 73.33% |
| Random | 62.69% |

### Average Margins (distance from constraints after perturbation)
| Strategy | Average Margin |
|----------|---------------|
| Avg | 0.4769 |
| Q2S | 0.4590 |
| Min | 0.4420 |
| Random | 0.3378 |

## Key Findings
- The best performing strategy is **Avg** with a success rate of 80.00%
- Compared to Random strategy baseline, Avg performs 17.31% better

## Performance Under Negative Perturbations

### perturbation_level_cost
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 76.89% | 0.4518 |
| Avg | 80.00% | 0.4697 |
| Min | 73.33% | 0.4347 |
| Random | 62.92% | 0.3308 |

### perturbation_level_effort
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 80.00% | 0.4313 |
| Avg | 80.00% | 0.4492 |
| Min | 80.00% | 0.4142 |
| Random | 65.26% | 0.3095 |

### perturbation_level_time
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 96.11% | 0.4393 |
| Avg | 100.00% | 0.4572 |
| Min | 91.67% | 0.4222 |
| Random | 68.18% | 0.3175 |

## Conclusion
Based on the experiment results, the Avg strategy demonstrates the highest resilience to perturbations,
with a success rate of 80.00%. This indicates that Avg's approach to plan selection
provides better robustness against uncertainties in the execution environment.
