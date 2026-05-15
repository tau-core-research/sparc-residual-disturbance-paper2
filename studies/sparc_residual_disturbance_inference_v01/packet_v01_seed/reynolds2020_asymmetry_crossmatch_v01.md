# Reynolds 2020 Asymmetry Crossmatch v0.1

This packet parses the VizieR machine-readable tables for Reynolds et al. (2020), `J/MNRAS/493/5089`, and exact-name crossmatches the resolved H I asymmetry parameters to the current `W_tau_eff` seed. It is an external-proxy crossmatch only and does not open a velocity endpoint.

## Metrics

- Catalog rows: 142
- Exact `W_tau_eff` overlap: 4 (HALOGAS)
- Pearson Amap vs W_tau_eff: 0.514475616
- Pearson Avel vs W_tau_eff: 0.063521995
- Minimum N gate: not_met

## Decision

`catalog_ingested_but_exact_overlap_below_minimum_n`

VizieR rows=142; exact W_tau_eff overlap=4; frozen minimum N=15.

The exact-name overlap is currently HALOGAS-only. LVHIS uses survey IDs rather than common galaxy names, so LVHIS alias resolution is the next step before treating this as a non-WHISP validation family.

## Generated Files

- `reynolds2020_vizier_download_manifest_v01.csv`
- `reynolds2020_asymmetry_catalog_v01.csv`
- `reynolds2020_asymmetry_w_tau_eff_crossmatch_v01.csv`
- `reynolds2020_asymmetry_crossmatch_metrics_v01.csv`
- `reynolds2020_asymmetry_crossmatch_decision_v01.csv`

## Guardrail

`reynolds2020_asymmetry_crossmatch_no_velocity_endpoint`
