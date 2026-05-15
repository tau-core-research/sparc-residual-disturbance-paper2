# Predictive S_tau Velocity Readout

This readout compares the frozen source-side `S_tau` rule with the old `S_tau=1` projection baseline on velocity-level log residuals. No coefficients are refit.

## Main Metrics

- All-galaxy median delta RMS source-minus-S1: -0.003098856
- All-galaxy fraction improved: 0.511111111
- A median delta RMS: -0.003098856
- C median delta RMS: 0.007165785

Negative delta means the frozen source-side rule improves over `S_tau=1`; positive delta means it worsens.

## Interpretation

This is the first direct no-refit test of whether the source-side `S_tau` rule improves the TPG/projection baseline. A weak or mixed result should be treated as evidence that the simple galaxy-level evidence mapping is not yet sufficient; the next viable rule likely needs radial or kinematic source information.

## Generated Files

- `predictive_s_tau_velocity_point_readout.csv`
- `predictive_s_tau_velocity_galaxy_summary.csv`
- `predictive_s_tau_velocity_metric_summary.csv`
