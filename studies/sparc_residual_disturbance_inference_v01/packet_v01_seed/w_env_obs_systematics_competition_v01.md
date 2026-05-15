# W_env_obs Systematics Competition v0.1

This gate asks whether the current source-side `W_tau_eff` direction can survive obvious competing explanations. It is a control matrix, not a new positive endpoint.

## Positive Direction Still Present

- P01 broad external-evidence direction: `AUC=0.774159664`.
- P07 WHISP source-family holdout: `AUC=0.760000000;Pearson=0.441950994`.

These are useful candidate signals, but they do not attribute the residual-inferred weight to Tau Core.

## Main Open Competitors

- P05 non-circular motion control: `does_not_absorb_direction_in_small_overlap`.
- P06 pressure-support control: control-only until overlap expands.
- P08 HALOGAS linewidth stress: retain as a weak or negative control.
- P09 inclination/observability: `blocks_attribution_until_galaxy_level_join`.

## Decision

The branch is positive as a proxy-direction result and still blocked as a physical attribution result. The next allowed gate is `P05_non_circular_overlap_control_before_S_tau_formula`. The velocity endpoint remains closed.

## Generated Files

- `w_env_obs_systematics_competition_matrix_v01.csv`
- `w_env_obs_systematics_competition_coverage_v01.csv`
- `w_env_obs_systematics_competition_readiness_v01.csv`
- `systematics_control_things_harmonic_summary_v01.csv`
- `systematics_control_littlethings_pressure_summary_v01.csv`
- `systematics_control_halogas_linewidth_summary_v01.csv`
- `systematics_control_inclination_summary_v01.csv`

## Guardrail

`systematics_competition_no_attribution_no_velocity_endpoint`
