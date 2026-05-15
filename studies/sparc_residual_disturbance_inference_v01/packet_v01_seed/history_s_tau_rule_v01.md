# History-Dependent S_tau Rule v0.1

This readout tests a causal integrated `S_tau` candidate. For each radial point, the current `S_tau` is set from the mean signed TPG residual of the inner points only. The current point residual, future points, empirical `S_tau_eff`, and A/C label are forbidden inputs.

## Rule

`S_tau_history(R_i) = clip(1 + 0.50 * mean_{j<i} signed_residual_TPG(R_j), 0.50, 1.50)`.

The first point in each galaxy uses `S_tau=1` because it has no inner history.

## Velocity Readout

- All-galaxy median delta RMS history-minus-S1: -0.016862038
- All-galaxy fraction improved: 0.933333333
- A median delta RMS: -0.008566997
- C median delta RMS: -0.042417618

Negative delta means the history rule improves over `S_tau=1`; positive delta means it worsens.

## Interpretation

This is not an external prediction, because it learns from inner observed residuals of the same galaxy. Its role is narrower: test whether an integrated radial state can carry useful information for outer points. A positive result would motivate a source-side proxy for the history state; a null result would weaken the integrated `S_tau` path.

## Generated Files

- `history_s_tau_rule_v01.csv`
- `history_s_tau_velocity_point_readout.csv`
- `history_s_tau_velocity_galaxy_summary.csv`
- `history_s_tau_velocity_metric_summary.csv`
