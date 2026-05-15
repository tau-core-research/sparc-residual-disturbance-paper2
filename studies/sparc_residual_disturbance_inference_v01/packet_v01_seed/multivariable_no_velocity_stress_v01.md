# Multivariable No-Velocity Stress Test v0.1

This gate tests the observer-distance Tau candidate without opening a velocity endpoint. The candidate channel is `TauDistanceCandidate_NearerHigher_z`, a nearer-higher transform of log distance. It is stressed against angular size, sampling, velocity-error, inclination-error, distance-fractional-error, and physical-radius nuisance controls.

## Readout

- Joined galaxies: 45
- Raw tau-distance Pearson vs W_tau_eff score: 0.404324367
- Raw nearer-vs-farther AUC: 0.771739130
- Partial tau-distance Pearson after nuisance controls: 0.434416486
- Partial tau-distance residual AUC: 0.662000000
- Nuisance-only score model R2: 0.207747757

## Decision

`observer_distance_candidate_survives_nuisance_stress`

Raw tau-distance Pearson=0.404324367; partial Pearson=0.434416486; partial AUC=0.662000000.

This is hypothesis support or weakening only. It does not establish a Tau Core field, and it does not select a velocity formula.

## Generated Files

- `multivariable_no_velocity_stress_join_v01.csv`
- `multivariable_no_velocity_stress_metrics_v01.csv`
- `multivariable_no_velocity_stress_decision_v01.csv`

## Guardrail

`multivariable_stress_no_velocity_endpoint_no_formula_selection`
