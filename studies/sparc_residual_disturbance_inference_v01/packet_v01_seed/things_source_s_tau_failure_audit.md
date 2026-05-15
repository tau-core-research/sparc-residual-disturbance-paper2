# THINGS Source-Side S_tau Failure Audit

This audit explains the previous THINGS source-side velocity readout after the outcome is known. It compares source-side `S_tau(R)` candidates to the empirical `S_tau_eff(R)` diagnostic only to identify failure modes. It must not be used to choose a new rule without a subsequent freeze-and-test gate.

## Main Diagnostics

- Point rows: 245
- Median delta absolute S_tau error, percentile-minus-S1: 0.255945686
- Fraction points improved, percentile mapping: 0.330612245
- Median delta absolute S_tau error, log-minus-S1: 0.528276275
- Fraction points improved, log mapping: 0.228571429
- Fraction percentile mapping too low relative to empirical S_tau_eff: 0.751020408
- Pearson(stress, empirical S_tau_eff): -0.325117821

## Interpretation

The failure mode is not merely noise. The source-side mappings often push `S_tau` below one where the empirical velocity-level diagnostic prefers values near or above one. In this overlap, stress magnitude alone is therefore an incomplete proxy for the local projection multiplier.

## Next Gate

Freeze a new source-side rule only after declaring its inputs and sign logic. Candidate inputs should distinguish stress type or radial context rather than using stress magnitude alone.

## Generated Files

- `things_source_s_tau_failure_point_audit.csv`
- `things_source_s_tau_failure_galaxy_audit.csv`
- `things_source_s_tau_failure_metric_summary.csv`
