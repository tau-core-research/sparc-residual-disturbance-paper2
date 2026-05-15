# Tau Core Weight Model Gate v0.1

This gate continues the residual signal-candidate branch without jumping to field mapping. It freezes the next model interpretation to test: TPG carries local Tau Core weights, while the remaining residual structure is a candidate for missing environment- and observer-dependent weights.

## Working Equation

The branch should treat the current TPG prescription as the local-weight baseline:

`V_TPG(R)=Vbar(R)*(1+alpha*ln(1+a0/aN))`.

The missing term is not a new pointwise constant. The evidence favors an integrated state:

`S_tau_full(R)=1+g(W_env_obs(R))`

where `W_env_obs(R)` must be predicted from a predeclared history, geometry, environment, or observer-state proxy before any endpoint velocity readout.

## Why This Gate Exists

- The residual is structured, signed, cumulative, and history-dependent.
- The history readout improves the TPG baseline, especially in C systems.
- The history readout is not external prediction, so the next model must replace inner residual history with source-side or geometry-side predictors.

## Claim Boundary

This gate does not prove Tau Core, does not build a field map, and does not fit a new formula. It freezes the next model target and the tests required to make it paper-grade.

## Generated Files

- `tau_core_weight_model_gate_v01.csv`
- `tau_core_weight_model_evidence_matrix_v01.csv`
- `tau_core_weight_model_next_tests_v01.csv`
