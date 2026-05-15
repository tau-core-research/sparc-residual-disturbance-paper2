# Residual-Disturbance Inference Seed Packet v0.1

This packet starts the reverse diagnostic branch: infer disturbance/coherence candidates from residual structure.
The working hypothesis is that residual structure itself can be used as a diagnostic fingerprint, not merely as model error.

## Question

Can galaxy-level residual features act as a diagnostic fingerprint for externally reviewed A/C disturbance class?

## Feature Families

- residual amplitude: mean, median, RMS
- radial structure: outer/inner ratio and radius-residual correlation
- low-acceleration burden: mean residual in `aN/a0<0.1` points
- comparator structure: Projection-minus-MOND and Projection-minus-RAR absolute-residual differences

## Seed Score

`ResidualDisturbanceScore_v01` is the mean rank of six predeclared projection/comparator features. Higher score means more C-like residual structure.

## Seed Result

- In-sample AUC for `ResidualDisturbanceScore_v01`: 0.663865546
- Galaxies: 45 (`A=17`, `C=28`)

## Interpretation

This is useful only as a diagnostic pilot. It does not replace the residual-blind Paper 1 audit, because here the residuals are intentionally used as predictors.

## Next Gate

The next step must freeze a held-out validation design: leave-one-galaxy-out, source-family holdout, or train/test split by evidence source. Do not promote in-sample AUC to a paper-grade claim.

## Generated Files

- `residual_feature_table.csv`
- `residual_disturbance_score_v01.csv`
- `residual_inference_metric_summary.csv`
