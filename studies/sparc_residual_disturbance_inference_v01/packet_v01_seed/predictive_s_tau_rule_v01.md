# Predictive S_tau Rule v0.1

This gate freezes a source-side `S_tau` rule before looking at the `S_tau_eff` readout. The rule uses only external evidence metadata: `EvidenceType` and `Confidence`.

## Frozen Rule

- regular or low-asymmetry evidence maps near `S_tau > 1`
- disturbed HI, warp, interaction, and tidal evidence map below `S_tau = 1`
- mixed, other, and no-data evidence remain close to neutral
- confidence applies only a small directional adjustment

Forbidden inputs: `Vobs`, `Vbar`, residuals, `Projection_RMS`, `S_tau_eff`, and the A/C class label.

## Post-Freeze Readout

- Galaxies with `S_tau_eff` readout: 45
- Pearson(predicted source S_tau, empirical S_tau_eff): 0.171323258
- MAE source rule: 0.337389701
- MAE constant S_tau=1 baseline: 0.358271634
- RMSE source rule: 0.455173290
- RMSE constant S_tau=1 baseline: 0.459345537
- Median predicted S_tau for A: 1.050000000
- Median predicted S_tau for C: 0.825000000

## Interpretation

This is the first leakage-controlled `S_tau` predictor. It is still not a physical derivation, and it is not a fitted improvement over TPG. Its role is to define a simple predeclared source-side mapping that can be stress-tested against the empirical `S_tau_eff` diagnostic and later replaced by kinematic or radial source rules.

## Next Gate

Evaluate whether the source-side rule improves velocity residuals relative to `S_tau=1` without refitting any coefficients.

## Generated Files

- `predictive_s_tau_rule_v01.csv`
- `predictive_s_tau_by_galaxy_v01.csv`
- `predictive_s_tau_readout_v01.csv`
