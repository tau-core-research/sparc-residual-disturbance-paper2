# Paper 2 Validation Controls

This packet adds the first Paper-1-style reviewer controls to the residual-disturbance inference branch.

## Shuffled-Label Null

- Predictor: `Projection_RMS`
- Observed AUC: 0.771008403
- Null median AUC: 0.497899160
- Null 95th percentile AUC: 0.634453782
- Empirical p(AUC >= observed): 0.002000000

## Baseline-Family Comparison

### Projection_RMS

- LOOGO AUC: 0.771008403
- Accuracy: 0.755555556
- False positive A-as-C: 3
- False negative C-as-A: 8

### MOND_RMS

- LOOGO AUC: 0.720588235
- Accuracy: 0.644444444
- False positive A-as-C: 3
- False negative C-as-A: 13

### RAR_RMS

- LOOGO AUC: 0.731092437
- Accuracy: 0.622222222
- False positive A-as-C: 4
- False negative C-as-A: 13

## Distance-Matched Stress

- `sparc_distance_greedy_unique_matched_pairs`: N=17, median C-A diff=0.082473220, fraction C higher=0.647058824
- `sparc_distance_optimal_ordered_matched_pairs`: N=17, median C-A diff=0.082473220, fraction C higher=0.647058824
- `sparc_distance_mpc_matched_pairs_caliper`: N=13, median C-A diff=0.119490421, fraction C higher=

## Interpretation

`Projection_RMS` is the strongest current residual-family baseline by LOOGO AUC. The shuffled-label null makes the primary AUC difficult to dismiss as random label order, but the distance-matched stress tests show that observability remains a live caveat rather than a solved problem.

## Guardrail

These controls move Paper 2 closer to a publishable diagnostic audit, but they still do not establish Tau Core validation, projection-model uniqueness, or replacement of external evidence labels.

## Generated Files

- `paper2_shuffled_label_null.csv`
- `paper2_baseline_family_loogo.csv`
- `paper2_observability_stress.csv`
