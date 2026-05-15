# Tau Core Environment/Observer Weight Candidate v0.1

This packet formalizes the working hypothesis that the TPG prescription already carries the local Tau Core weights captured by the fixed projection baseline, while the remaining TPG residual is a candidate carrier of environment- and observer-dependent Tau Core weights. It does not identify the residual itself with Tau Core. The residual can also contain ordinary observational, baryonic, and non-circular-motion systematics.

## Operational Definition

`TauCoreSignalCandidateScore_v01` is the mean rank of five diagnostics designed to isolate the non-local part left after the TPG local-weight baseline: final signed drift, maximum cumulative drift, sign imbalance, same-sign run fraction, and the improvement obtained by the causal inner-history readout.

## Main Readout

- Galaxies: 45
- Median candidate score, A: 0.304545455
- Median candidate score, C: 0.579545455
- AUC(C higher), candidate score: 0.774159664
- AUC(C higher), projection RMS: 0.771008403
- AUC(C higher), history improvement: 0.762605042
- Pearson(projection RMS, candidate score): 0.731059386
- Pearson(abs final signed drift, history improvement): 0.954744346

## Interpretation

The residual difference is a plausible carrier of missing environment/observer weights because its signed, cumulative, and history-dependent features are structured rather than random. However, the current evidence supports only a Tau Core weight-candidate framing. Attribution requires external source-side predictors or controls that can explain why this residual structure is not merely disturbance, observability, inclination, beam smearing, or baryonic-model error.

## Consequence For The Model

The next useful Tau Core expression should separate local weights already approximated by TPG from environment/observer-dependent weights left in the residual. The current results favor an integrated state variable: a term whose value at radius `R` depends on accumulated inner geometry, environment, viewing geometry, or coherence history.

## Generated Files

- `tau_core_signal_candidate_galaxy_summary_v01.csv`
- `tau_core_signal_candidate_relation_summary_v01.csv`
