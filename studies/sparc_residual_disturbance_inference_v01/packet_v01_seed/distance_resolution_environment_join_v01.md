# Distance, Resolution, and Environment Join v0.1

This gate decomposes the P09 observability blocker before any velocity formula is opened. It joins derived SPARC distance controls, rotation-curve sampling/resolution proxies, and residual-blind environment cue fields.

## Readout

- Joined galaxies: 45
- Environment cue coverage: 15
- Reconstruction-risk AUC: 0.750000000
- Distance AUC: 0.269762846
- Angular-radius proxy AUC: 0.432806324
- Environment-theta AUC: 0.602040816

## Decision

`reconstruction_risk_remains_primary_observability_blocker`

Reconstruction-risk AUC=0.750000000; angular-radius AUC=0.432806324; distance AUC=0.269762846; environment-theta AUC=0.602040816.

The result is a covariate gate only. It may motivate a later multivariable stress test, but it does not select or validate a Tau Core velocity formula.

## Generated Files

- `distance_resolution_environment_join_v01.csv`
- `distance_resolution_environment_metrics_v01.csv`
- `distance_resolution_environment_decision_v01.csv`

## Guardrail

`distance_resolution_environment_control_no_formula_endpoint`
