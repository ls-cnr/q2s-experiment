# Q2S Experiment Summary Report
Generated on: 2025-03-26 14:28:19

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
| Random | 68.19% |

### Average Margins (distance from constraints after perturbation)
| Strategy | Average Margin |
|----------|---------------|
| Avg | 0.5046 |
| Q2S | 0.4930 |
| Min | 0.4838 |
| Random | 0.3711 |

## Key Findings
- The best performing strategy is **Q2S** with a success rate of 80.00%
- Compared to Random strategy baseline, Q2S performs 11.81% better

### Performance of Q2S by Alpha Value
| Alpha | Success Rate (%) | Margin |
|-------|-----------------|--------|
| 0.3 | 80.00% | 0.4874 |
| 0.5 | 80.00% | 0.4901 |
| 0.7 | 80.00% | 0.5014 |

The optimal alpha value appears to be **0.3** with a success rate of 80.00%

## Performance Under Negative Perturbations

### perturbation_level_cost
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 80.00% | 0.4922 |
| Avg | 80.00% | 0.5039 |
| Min | 80.00% | 0.4831 |
| Random | 68.23% | 0.3700 |

### perturbation_level_effort
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 80.00% | 0.4827 |
| Avg | 80.00% | 0.4943 |
| Min | 80.00% | 0.4736 |
| Random | 69.52% | 0.3613 |

### perturbation_level_time
| Strategy | Success Rate (%) | Margin |
|----------|-----------------|--------|
| Q2S | 83.33% | 0.4728 |
| Avg | 83.33% | 0.4844 |
| Min | 83.33% | 0.4637 |
| Random | 62.74% | 0.3506 |

## Conclusion
Based on the experiment results, the Q2S strategy demonstrates the highest resilience to perturbations,
with a success rate of 80.00%. This indicates that Q2S's approach to plan selection
provides better robustness against uncertainties in the execution environment.
