# Yu 2022 ALFALFA Af/Ac Directional Readout v0.1

This packet evaluates whether global ALFALFA HI profile asymmetry from Yu et al. (2022) points in the expected direction against the committed expanded `W_tau_eff` score. It does not fit coefficients and does not validate a Tau Core field model.

## Frozen Direction

The predeclared directional expectation is that larger global HI profile asymmetry (`Af`/`Ac`) should be associated with larger residual-inferred `W_tau_eff` score.

## Main Readout

- Readout rows: 22 (low=12;medium=4;high=6)
- Spearman(LogMaxAfAc, W_tau_eff score): 0.013023835
- Pearson(LogMaxAfAc, W_tau_eff score): 0.010298371
- AUC high-vs-low profile asymmetry: 0.472222222
- Median score low/medium/high: 0.397727273 / 0.615909091 / 0.388636363
- Directional signal status: not_supported

## Interpretation

This is a source-side external hint, not a validation. `Af` and `Ac` are global unresolved HI profile asymmetry measures, whereas `W_tau_eff` is a residual-shape score derived from rotation-curve structure. A positive but weak readout would support continued external validation work; it would not establish a physical Tau Core map.

## Generated Files

- `yu2022_alfalfa_af_ac_w_tau_eff_join_v01.csv`
- `yu2022_alfalfa_af_ac_w_tau_eff_metrics_v01.csv`
- `yu2022_alfalfa_af_ac_w_tau_eff_decision_v01.csv`

## Guardrail

`yu2022_alfalfa_af_ac_directional_readout_no_fit_no_claim`
