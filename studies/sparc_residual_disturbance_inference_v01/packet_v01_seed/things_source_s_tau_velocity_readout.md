# THINGS Source-Side S_tau(R) Velocity Readout

This gate evaluates the copied THINGS ring-level source-side `S_tau(R)` readout against the old `S_tau=1` velocity baseline. It reports both bounded mappings from the source packet and does not select one by outcome.

## Scope

- Joined points: 245
- THINGS-overlap galaxies: 7 (DDO154, NGC2366, NGC2403, NGC2976, NGC3198, NGC5055, NGC7331)
- Input signal: kinematic stress proxy from source-side THINGS ring metadata.
- Forbidden use: no coefficient refit, no target-residual training, no model selection between mappings.

## Main Metrics

- All-galaxy median delta RMS percentile-minus-S1: 0.136344406
- All-galaxy fraction improved, percentile mapping: 0.285714286
- All-galaxy median delta RMS log-minus-S1: 0.207599642
- All-galaxy fraction improved, log mapping: 0.000000000
- A median delta RMS, percentile/log: 0.145138879 / 0.237130558
- C median delta RMS, percentile/log: 0.014173140 / 0.022111705

Negative delta means the source-side `S_tau(R)` mapping improves over `S_tau=1`; positive delta means it worsens.

## Interpretation

This is a small-overlap, source-only kinematic sanity check. It is useful if it indicates whether ring-level stress is a better direction than a single galaxy-level source score, but it is not external validation and not a Tau Core proof. A mixed or negative result means that the next `S_tau` gate needs a better held-out mapping rather than outcome-selected tuning.

## Generated Files

- `things_source_s_tau_velocity_point_readout.csv`
- `things_source_s_tau_velocity_galaxy_summary.csv`
- `things_source_s_tau_velocity_metric_summary.csv`
