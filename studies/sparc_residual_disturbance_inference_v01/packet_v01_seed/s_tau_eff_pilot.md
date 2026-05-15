# Effective S_tau Pilot

This pilot back-solves an empirical `S_tau_eff(R)` from local SPARC rotmod inputs using the fixed velocity-level projection prescription.

```text
S_tau_eff(R) = (Vobs/Vbar - 1) / [alpha ln(1 + 1/(aN/a0))]
```

The raw SPARC rotmod files are not redistributed here. The committed tables are derived diagnostics only.

## Summary

- Point rows: 926
- A median galaxy-level clipped S_tau: 1.093121010
- C median galaxy-level clipped S_tau: 0.888249933
- A median RMS deviation from S_tau=1: 0.290985908
- C median RMS deviation from S_tau=1: 0.444985099

## Interpretation

`S_tau=1` is the old TPG/projection baseline. Values near one indicate that the fixed logarithmic multiplier is close to the observed velocity level. Large deviations identify galaxies or radial zones where a local structural term would have to carry substantial information.

This is not a predictive model yet. It is a diagnostic map derived from `Vobs`, so it cannot be used as independent validation. The next gate is to freeze a source-side or kinematic rule that predicts `S_tau` without using the target residual.

## Generated Files

- `s_tau_eff_point_pilot.csv`
- `s_tau_eff_galaxy_summary.csv`
