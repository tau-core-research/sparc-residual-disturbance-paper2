# P07 WHISP Source-Family Holdout v0.1

This readout evaluates the frozen P07 WHISP lopsidedness/asymmetry source family against `W_tau_eff`. It does not evaluate velocity residuals, does not fit coefficients, and does not define `S_tau_full`.

## Frozen WHISP Burden

`WHISP_BurdenScore_v01` is the mean of available published HI asymmetry amplitudes (`A1`, `A2`, `A3`) across inner/outer/radial windows plus `EpsilonKin`. Higher burden is expected to align with higher `W_tau_eff` candidate score.

## Main Readout

- Joined galaxies: 10
- Pearson WHISP burden vs W_tau_eff candidate score: 0.441950994
- Pearson WHISP burden vs abs W_tau_eff: 0.530958640
- Median W_tau_eff score, low WHISP burden: 0.231818182
- Median W_tau_eff score, high WHISP burden: 0.531818182
- AUC high-vs-low WHISP burden: 0.760000000

## Interpretation

A positive holdout readout supports the idea that a source-side HI asymmetry family carries part of the same `W_env_obs` direction as the broad P01 prior. Because the overlap is small and class-balanced controls are limited, this is a source-family sanity check rather than a final validation.

## Generated Files

- `p07_whisp_w_tau_eff_holdout_join_v01.csv`
- `p07_whisp_w_tau_eff_holdout_metric_summary_v01.csv`
