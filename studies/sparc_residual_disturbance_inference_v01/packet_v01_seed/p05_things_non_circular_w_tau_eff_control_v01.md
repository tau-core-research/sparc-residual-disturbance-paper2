# P05 THINGS Non-Circular Control v0.1

This readout joins the sanitized P05 THINGS harmonic non-circular control summary to `W_tau_eff`. It uses only published non-circular or harmonic-control columns and does not use velocity residuals as predictors.

## Readout

- Joined galaxies: 7
- Pearson P05 burden vs W_tau_eff candidate score: 0.217454567
- Spearman P05 burden vs W_tau_eff candidate score: 0.107142857
- Median W_tau_eff score, low P05 burden: 0.484090909
- Median W_tau_eff score, high P05 burden: 0.409090909
- AUC high-vs-low P05 burden: 0.333333333

## Decision

`does_not_absorb_direction_in_small_overlap`

P05 burden Pearson=0.217454567; AUC=0.333333333 on seven THINGS galaxies.

This is a small-overlap control. It can block overinterpretation, but it cannot by itself fit or reject a Tau Core formula.

## Generated Files

- `p05_things_non_circular_w_tau_eff_control_join_v01.csv`
- `p05_things_non_circular_w_tau_eff_control_metrics_v01.csv`
- `p05_things_non_circular_w_tau_eff_control_decision_v01.csv`

## Guardrail

`p05_non_circular_control_no_velocity_endpoint_no_attribution`
