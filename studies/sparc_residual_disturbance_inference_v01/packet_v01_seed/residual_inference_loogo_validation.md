# Residual-Disturbance LOOGO Validation v0.1

This packet runs a first leave-one-galaxy-out sanity check for residual-based disturbance inference.

## Method

For each held-out galaxy, the threshold is trained only on the other galaxies as the midpoint between the A and C training medians. The held-out galaxy is then classified as C if its predictor is above that threshold.

## Results

### Projection_RMS

- Accuracy: 0.755555556
- AUC: 0.771008403
- Precision C: 0.869565217
- Recall C: 0.714285714
- False positive A-as-C: 3
- False negative C-as-A: 8

### Projection_LowAccelerationMean

- Accuracy: 0.755555556
- AUC: 0.762605042
- Precision C: 0.869565217
- Recall C: 0.714285714
- False positive A-as-C: 3
- False negative C-as-A: 8

### ResidualDisturbanceScore_v01

- Accuracy: 0.577777778
- AUC: 0.663865546
- Precision C: 0.695652174
- Recall C: 0.571428571
- False positive A-as-C: 7
- False negative C-as-A: 12

## Interpretation

The strongest first held-out sanity check is `Projection_RMS` with AUC `0.771008403`. This supports the idea that residual amplitude carries disturbance information, but it is still not a paper-grade classifier.

## Next Gate

Freeze a second-stage classifier design before adding features: either a simple one-feature baseline kept as primary, or a strictly predeclared multifeature model with nested validation.

## Generated Files

- `residual_inference_loogo_predictions.csv`
- `residual_inference_loogo_metric_summary.csv`
