# Contextual S_tau Rule v0.1

This gate freezes a conservative contextual THINGS `S_tau(R)` candidate after the source-side failure audit. It is a post-audit candidate, not validation. The rule stays close to `S_tau=1` and uses only radius fraction, acceleration regime, and the THINGS stress proxy.

## Rule Summary

- Start at `S_tau=1.00`.
- Apply small additive context terms for low acceleration, radius zone, and stress level.
- Bound the result to `[0.88, 1.12]`.
- Forbidden inputs: `Vobs`, `Vbar`, residuals, empirical `S_tau_eff`, A/C class, and outcome-selected mapping choice.

## Velocity Readout

- All-galaxy median delta RMS contextual-minus-S1: 0.002491356
- All-galaxy fraction improved: 0.428571429
- A median delta RMS: -0.004336262
- C median delta RMS: 0.009241461

Negative delta means the contextual rule improves over `S_tau=1`; positive delta means it worsens.

## Interpretation

This rule tests whether a small, context-aware local term is safer than a direct stress-to-suppression mapping. Because the rule was motivated after inspecting a failure mode, any positive result remains hypothesis-generating until a held-out source-family gate is run.

## Generated Files

- `contextual_s_tau_rule_v01.csv`
- `contextual_s_tau_velocity_point_readout.csv`
- `contextual_s_tau_velocity_galaxy_summary.csv`
- `contextual_s_tau_velocity_metric_summary.csv`
