# WHISP Expanded W_tau_eff Readout v0.1

This packet re-evaluates the WHISP lopsidedness/asymmetry family after the Yu-expanded `W_tau_eff` score table made four additional WHISP overlaps usable. Original seed scores are retained without refit; expanded scores are used only where the original seed had no score.

## Main Readout

- Joined galaxies: 14 (original_seed=10;expanded=4)
- Pearson WHISP burden vs W_tau_eff score: 0.391218683
- Spearman WHISP burden vs W_tau_eff score: 0.362637363
- AUC high-vs-low WHISP burden: 0.714285714
- Median W_tau_eff score low/high burden: 0.231818182 / 0.531818182
- Radial contrast Pearson/AUC: 0.374287364 / 0.551020408
- Kinematic epsilon Pearson: 0.273373152
- Decision: positive_but_not_paper_grade

## Interpretation

The expanded WHISP overlap remains directionally positive, but the sample is still below the frozen N>=15 external-validation gate. This strengthens the case for a WHISP-style radial/asymmetry branch, while keeping the result below paper-grade validation status.

## Generated Files

- `whisp_expanded_w_tau_eff_readout_join_v01.csv`
- `whisp_expanded_w_tau_eff_readout_metrics_v01.csv`
- `whisp_expanded_w_tau_eff_readout_decision_v01.csv`

## Guardrail

`whisp_expanded_readout_no_velocity_endpoint_no_refit`
