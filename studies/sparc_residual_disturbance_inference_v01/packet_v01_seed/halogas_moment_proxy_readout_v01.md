# HALOGAS Moment Proxy Readout v0.1

This readout tests whether derived HALOGAS moment-map proxy features align with `W_tau_eff`. It is a small-overlap external control and does not open a velocity endpoint.

## Metrics

- Joined galaxies: 5 (A;C)
- Pearson: 0.216413317
- AUC high-vs-low stress: 0.500000000

## Decision

`weak_or_null_halogas_moment_proxy_control`

Pearson=0.216413317; AUC=0.500000000; N=5.

## Generated Files

- `halogas_moment_proxy_metrics_v01.csv`
- `halogas_moment_proxy_decision_v01.csv`

## Guardrail

`halogas_moment_proxy_small_overlap_no_velocity_endpoint`
