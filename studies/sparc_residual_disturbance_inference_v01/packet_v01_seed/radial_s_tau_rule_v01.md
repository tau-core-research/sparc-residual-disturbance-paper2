# Radial S_tau Rule v0.1

This gate evaluates a frozen radial/source-side `S_tau(R)` rule against the old `S_tau=1` projection baseline. The rule uses only source-side evidence metadata plus `RadiusFraction` and `aN/a0`; it does not use `Vobs`, residuals, or `S_tau_eff` to define the rule.

## Main Metrics

- All-galaxy median delta RMS radial-minus-S1: -0.010837261
- All-galaxy fraction improved: 0.555555556
- A median delta RMS: -0.010837261
- C median delta RMS: 0.006546441

Negative delta means the radial rule improves over `S_tau=1`; positive delta means it worsens.

## Interpretation

This is a leakage-controlled radial heuristic, not a fitted physical law. It tests whether adding a predeclared radial/acceleration dependence helps more than a single galaxy-level `S_tau` value.

## Generated Files

- `radial_s_tau_rule_v01.csv`
- `radial_s_tau_velocity_point_readout.csv`
- `radial_s_tau_velocity_galaxy_summary.csv`
- `radial_s_tau_velocity_metric_summary.csv`
