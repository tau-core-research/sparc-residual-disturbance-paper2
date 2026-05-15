# Proxy Direction vs W_tau_eff Readout v0.1

This readout evaluates the frozen P01 direction against the already-defined `W_tau_eff` candidate score. It does not evaluate velocity residuals, does not fit coefficients, and does not define `S_tau_full`.

## Frozen P01 Direction

- `regular_kinematics` and `low_asymmetry`: low burden
- `mixed`: medium burden
- `disturbed_hi`, `tidal`, `interaction`, and `warp`: high burden
- `other` and `no_data`: unscored for the primary directional metric

## Main Readout

- Joined galaxies: 45
- Scored low/medium/high galaxies: 45 (low=17;medium=0;high=28)
- Median W_tau_eff candidate score, low burden: 0.304545455
- Median W_tau_eff candidate score, medium burden: not_applicable_no_medium_cases
- Median W_tau_eff candidate score, high burden: 0.579545455
- AUC high-vs-low score: 0.774159664
- Pearson ordinal burden vs score: 0.457880425

## Interpretation

A positive directional readout supports using residual-blind external evidence as a broad `W_env_obs` prior. A weak, null, or reversed readout would mean that the residual-inferred candidate is not captured by this coarse source-side proxy and must not be promoted to a velocity formula.

## Generated Files

- `proxy_direction_w_tau_eff_join_v01.csv`
- `proxy_direction_w_tau_eff_metric_summary_v01.csv`
