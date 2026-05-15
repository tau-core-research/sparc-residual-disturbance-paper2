# THINGS Table 3 Expanded Control Readout v0.1

This packet evaluates the expanded THINGS Table 3 control readout after scoring all Table 3 galaxies with available local SPARC rotmods. It remains a non-circular-motion control and does not open a velocity endpoint.

## Main Readout

- Joined rows: 13
- Pearson Ar vs W_tau_eff score: -0.310471908
- Spearman Ar vs W_tau_eff score: -0.310866869
- AUC high-vs-low Ar: 0.345238095
- Pearson Ar/Vmax vs W_tau_eff score: 0.321831406
- AUC high-vs-low Ar/Vmax: 0.702380952
- Decision: does_not_absorb_WHISP_direction

## Interpretation

The expanded THINGS control still does not reproduce the WHISP-positive direction. In this overlap, larger published non-circular amplitudes do not imply larger `W_tau_eff` scores. This weakens a simple non-circular-amplitude-only explanation, while remaining below the N>=15 validation threshold.

## Generated Files

- `things_table3_expanded_control_readout_join_v01.csv`
- `things_table3_expanded_control_readout_metrics_v01.csv`
- `things_table3_expanded_control_readout_decision_v01.csv`

## Guardrail

`things_table3_expanded_control_readout_no_velocity_endpoint`
