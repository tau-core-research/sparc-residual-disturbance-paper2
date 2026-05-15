# THINGS Table 3 Expanded W_tau_eff Scores v0.1

This packet expands THINGS Table 3 control coverage by scoring every published Table 3 galaxy that has a local SPARC rotmod and at least eight valid radial points. Existing original or Yu-expanded scores are retained without refit.

## Summary

- THINGS Table 3 rows: 18
- Resolved W_tau_eff rows: 13
- Newly scored from rotmod: 5
- Excluded without local rotmod: 5
- Coverage decision: expanded_but_still_below_N15

## Boundary

This is a control expansion only. It does not refit `W_tau_eff`, does not use THINGS metrics to tune the score, and does not open a velocity endpoint.

## Generated Files

- `things_table3_expanded_w_tau_eff_point_trace_v01.csv`
- `things_table3_expanded_w_tau_eff_scores_v01.csv`
- `things_table3_expanded_w_tau_eff_summary_v01.csv`
- `things_table3_expanded_w_tau_eff_decision_v01.csv`

## Guardrail

`things_table3_expanded_w_tau_eff_no_endpoint_refit`
