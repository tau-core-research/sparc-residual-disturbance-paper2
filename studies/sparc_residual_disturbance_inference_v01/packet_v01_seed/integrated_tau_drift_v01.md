# Integrated Tau Drift v0.1

This diagnostic tests whether the fixed TPG/projection baseline departs from the observed rotation curves through cumulative radial drift rather than pointwise random scatter. It uses signed log residuals from the already fixed `S_tau=1` prescription.

## Definitions

- `SignedLogResidual_TPG = ln(Vobs / V_TPG)`.
- `CumulativeMeanSignedResidual(R)` is the running mean of signed residuals from the inner radius to `R`.
- `MaxAbsCumulativeMeanResidual` measures the strongest integrated drift amplitude.
- `SignImbalance` measures whether residuals have a persistent sign rather than alternating randomly.
- `FirstBreakRadiusFraction_abs0p15` is the first radius fraction where the absolute cumulative mean exceeds 0.15.

## Main Results

- Galaxies: 45
- Median max cumulative drift, all: 0.271772121
- Median max cumulative drift, A: 0.214401710
- Median max cumulative drift, C: 0.394781377
- AUC(C higher) for max cumulative drift: 0.670168067
- AUC(C higher) for sign imbalance: 0.685924370
- AUC(C higher) for same-sign run fraction: 0.710084034

## Interpretation

This is not an `S_tau` rule and not a validation claim. It asks whether TPG departures have memory-like radial structure. If cumulative drift and sign persistence separate disturbed systems better than raw pointwise scatter, the next model should treat `S_tau` as an integrated or history-dependent quantity rather than as an independent local constant.

## Generated Files

- `integrated_tau_drift_point_trace_v01.csv`
- `integrated_tau_drift_galaxy_summary_v01.csv`
- `integrated_tau_drift_metric_summary_v01.csv`
