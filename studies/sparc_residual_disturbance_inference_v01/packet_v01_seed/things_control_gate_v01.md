# THINGS Control Gate v0.1

This packet rechecks THINGS after the expanded `W_tau_eff` score resolver. It does not fit coefficients, does not open a velocity endpoint, and does not make a Tau Core attribution.

## Resolver Audit

- THINGS Table 3 rows: 18
- Rows with resolved `W_tau_eff`: 8
- New rows from expanded resolver only: 0

## Competition Readout

- WHISP Holwerda AUC/Spearman: 0.644230769 / 0.235045205
- WHISP van Eymeren AUC/Spearman: 0.714285714 / 0.362637363
- THINGS Table 3 AUC/Pearson: 0.187500000 / -0.087767676
- THINGS P05 AUC/Pearson: 0.333333333 / 0.217454567

## Decision

`THINGS_controls_do_not_absorb_WHISP_direction`

In the currently available exact-name overlap, THINGS non-circular controls do not reproduce the WHISP-positive direction. This weakens the simplest explanation that the WHISP/`W_tau_eff` association is only a non-circular-motion amplitude effect. Because the THINGS overlap is small, the correct next step is still non-WHISP resolved-HI replication rather than Tau Core attribution.

## Generated Files

- `things_expanded_score_resolver_audit_v01.csv`
- `things_vs_whisp_control_matrix_v01.csv`
- `things_control_gate_decision_v01.csv`

## Guardrail

`things_control_gate_no_velocity_endpoint_no_tau_attribution`
