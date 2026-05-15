# WHISP Holwerda 2011 Morphology Readout v0.1

This packet ingests the Holwerda et al. (2011) WHISP HI morphology catalogue from VizieR `J/MNRAS/416/2415` and evaluates the source-family direction against the resolved `W_tau_eff` score table. It does not refit `W_tau_eff`, does not use velocity residuals as predictors, and does not define a Tau Core field model.

## Main Readout

- Joined galaxies: 25 (original_seed=17;expanded=8)
- Minimum N gate: met
- Pearson AsymmetryA vs W_tau_eff score: 0.161199465
- Spearman AsymmetryA vs W_tau_eff score: 0.235045205
- AUC high-vs-low AsymmetryA: 0.644230769
- Median W_tau_eff score low/high AsymmetryA: 0.554545455 / 0.690909091
- Directional status: positive_source_family_replication

## Interpretation

The Holwerda WHISP morphology catalogue clears the N>=15 source-family gate and gives a positive directional readout. This is a stronger WHISP-family replication than the earlier 14-row van Eymeren readout, but it is not a fully independent external-family validation because both catalogues are WHISP-derived.

## Generated Files

- `whisp_holwerda2011_download_manifest_v01.csv`
- `whisp_holwerda2011_morphology_catalog_v01.csv`
- `whisp_holwerda2011_w_tau_eff_join_v01.csv`
- `whisp_holwerda2011_w_tau_eff_metrics_v01.csv`
- `whisp_holwerda2011_w_tau_eff_decision_v01.csv`

## Guardrail

`whisp_holwerda2011_morphology_readout_no_velocity_endpoint_no_refit`
