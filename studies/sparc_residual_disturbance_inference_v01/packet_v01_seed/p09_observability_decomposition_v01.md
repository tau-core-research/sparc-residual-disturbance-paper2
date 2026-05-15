# P09 Observability Decomposition v0.1

This gate treats observability as a decomposition problem, not as something to erase automatically. The goal is to separate ordinary reconstruction risk from a possible observer-geometry channel compatible with Tau Core's observer-centered framing.

## Channels

- `ObserverGeometryChannel_v01`: line-of-sight geometry pressure from low- and high-inclination viewing geometry.
- `ReconstructionRiskChannel_v01`: ordinary measurement/deprojection risk from `NPoints`, `MeanErrVobsKms`, and `InclinationErrorDeg`.

## Readout

- Joined galaxies: 45
- Observer geometry Pearson vs W_tau_eff score: -0.225721262
- Observer geometry AUC high-vs-low: 0.389328063
- Reconstruction risk Pearson vs W_tau_eff score: 0.289724767
- Reconstruction risk AUC high-vs-low: 0.750000000

## Decision

`ordinary_observability_risk_competes_with_signal`

Observer-geometry Pearson=-0.225721262; AUC=0.389328063; reconstruction-risk Pearson=0.289724767; AUC=0.750000000.

This does not prove Tau Core attribution. It does say that observer geometry should not be dismissed as mere nuisance before distance, resolution, and environment joins are run.

## Generated Files

- `p09_observability_decomposition_join_v01.csv`
- `p09_observability_decomposition_metrics_v01.csv`
- `p09_observability_decomposition_decision_v01.csv`

## Guardrail

`p09_observability_decomposition_not_bias_erasure_not_attribution`
