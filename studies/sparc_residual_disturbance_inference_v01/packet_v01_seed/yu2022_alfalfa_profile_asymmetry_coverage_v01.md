# Yu 2022 ALFALFA Profile-Asymmetry Coverage v0.1

This packet ingests the Yu et al. (2022) ALFALFA integrated H I profile-asymmetry catalogue from VizieR and checks coverage against the current `W_tau_eff` seed and the locally available SPARC rotmod inventory. It is a coverage audit only.

## Result

- Yu et al. catalogue rows: 29958
- Current `W_tau_eff` seed overlap: 7
- Local SPARC rotmod overlap: 26
- New seed-expansion candidates: 19
- Potential N>=15 gate after expansion: met

## Decision

`promising_for_predeclared_seed_expansion`

Current seed overlap=7; local SPARC rotmod overlap=26; potential expansion gate=met.

Yu et al. (2022) is a stronger next external family than Reynolds for this repo because UGC/AGC naming gives a larger SPARC rotmod overlap. The next allowed step is to freeze the expansion rule before computing any expanded residual score.

## Generated Files

- `yu2022_alfalfa_download_manifest_v01.csv`
- `yu2022_alfalfa_profile_asymmetry_catalog_v01.csv`
- `yu2022_alfalfa_profile_asymmetry_coverage_v01.csv`
- `yu2022_alfalfa_profile_asymmetry_coverage_summary_v01.csv`
- `yu2022_alfalfa_profile_asymmetry_coverage_decision_v01.csv`

## Guardrail

`yu2022_alfalfa_coverage_no_directional_readout`
