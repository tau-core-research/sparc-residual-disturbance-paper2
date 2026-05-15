# LVHIS Alias-Resolved Reynolds 2020 Crossmatch v0.1

This packet resolves LVHIS survey IDs through the public ATNF LVHIS database and re-crossmatches the Reynolds et al. (2020) resolved H I asymmetry catalogue to the frozen `W_tau_eff` seed. It is a join-key and external-proxy audit only.

## Metrics

- LVHIS alias rows: 82
- Alias-resolved `W_tau_eff` overlap: 6 (HALOGAS;LVHIS)
- New LVHIS alias matches: 2 (NGC0055;NGC1705)
- Pearson Amap vs W_tau_eff: -0.233039744
- Pearson Avel vs W_tau_eff: 0.375346400
- AUC C higher Amap: 0.388888889
- AUC C higher Avel: 0.777777778
- Minimum N gate: not_met

## Decision

`alias_resolution_improves_overlap_but_below_minimum_n`

Alias-resolved overlap=6; new LVHIS alias matches=2; frozen minimum N=15.

The alias step increases the overlap, but not enough for a directional non-WHISP validation claim. The velocity-field asymmetry readout is recorded as a small-sample hint only; it is not a Tau Core claim and does not open a velocity endpoint.

## Generated Files

- `lvhis_database_download_manifest_v01.csv`
- `lvhis_alias_resolution_v01.csv`
- `reynolds2020_lvh_alias_resolved_w_tau_eff_crossmatch_v01.csv`
- `reynolds2020_lvh_alias_resolved_metrics_v01.csv`
- `reynolds2020_lvh_alias_resolved_decision_v01.csv`

## Guardrail

`lvhis_alias_resolved_reynolds2020_no_velocity_endpoint`
