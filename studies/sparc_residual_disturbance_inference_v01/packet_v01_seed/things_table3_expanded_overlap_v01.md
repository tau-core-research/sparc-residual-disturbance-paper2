# THINGS Table 3 Expanded Overlap v0.1

This packet curates the published THINGS harmonic-decomposition Table 3 values and joins the exact-name overlap to `W_tau_eff`. It is an external-control readout only and does not open a velocity endpoint.

## Metrics

- Published Table 3 rows: 18
- `W_tau_eff` overlap: 8
- Pearson Ar vs W_tau_eff: -0.087767676
- AUC high-vs-low Ar: 0.187500000
- Minimum N gate: not_met

## Decision

`expanded_overlap_available_but_below_minimum_n`

Overlap N=8; frozen minimum N=12.

## Generated Files

- `things_trachternach2008_table3_v01.csv`
- `things_table3_w_tau_eff_overlap_v01.csv`
- `things_table3_w_tau_eff_metrics_v01.csv`
- `things_table3_expansion_decision_v01.csv`

## Guardrail

`things_table3_published_control_no_velocity_endpoint`
