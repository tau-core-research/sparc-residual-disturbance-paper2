# Path B Source-Only S_tau Readout

This packet applies the two source-only bounded `S_tau(R)` candidates to the already frozen C06 nearest-ring residual join.
It is a labeled sensitivity readout, not model selection and not a choice between mappings.

## Coverage

- Joined points: 245
- Joined galaxies: 7
- Join rule: reuse C06 `THINGS_RingIndex` and attach source-only calibration rows
- Expected sign: negative, because higher `S_tau` means higher coherence and should correspond to lower residual burden

## Readout

### S_tau_source_percentile

- Pearson(S_tau_source_percentile, AbsResidualProjection): -0.204529065
- Pearson(S_tau_source_percentile, AbsResidualMONDSimple): -0.232749223
- Pearson(S_tau_source_percentile, AbsResidualRAR): -0.238784448

### S_tau_source_log

- Pearson(S_tau_source_log, AbsResidualProjection): -0.194428704
- Pearson(S_tau_source_log, AbsResidualMONDSimple): -0.224346065
- Pearson(S_tau_source_log, AbsResidualRAR): -0.229953574

## Interpretation

Both bounded source-only mappings are reported as a sensitivity pair. A negative coefficient has the expected physical direction, but this packet does not make the signal Tau-Core-specific because MOND/RAR comparator residuals remain visible.

## Guardrail

Do not select the percentile or log mapping by whichever looks better here. A future endpoint must predeclare one primary bounded mapping or move to a held-out source family before claiming model specificity.

## Generated Files

- `path_b_source_only_stau_readout_joined_points.csv`
- `path_b_source_only_stau_readout_metric_summary.csv`
