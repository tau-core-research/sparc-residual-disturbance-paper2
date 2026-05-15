# W_tau_eff Field Seed v0.1

This closing packet defines a map-ready residual-inferred effective tau-weight seed. It is the bridge from the residual/history branch to later sky or distance mapping.

## Definition

The working decomposition is:

- `TPG`: effective baseline carrying local Tau Core weights.
- `W_tau_eff`: residual-inferred candidate for the missing environment- and observer-dependent Tau Core weights.

`W_tau_eff_signed_v01` is the final mean signed TPG log residual. `W_tau_eff_candidate_score_v01` is the previously defined rank-composite score using signed drift, cumulative drift, sign persistence, and history-rule improvement.

## Main Summary

- Galaxies: 45
- Median candidate score, all: 0.500000000
- Median candidate score, A: 0.304545455
- Median candidate score, C: 0.579545455
- High-candidate galaxies, all/A/C: 12 / 2 / 10

## Not A Map Yet

This packet intentionally does not claim a Tau Core field map. The public packet does not yet include the sky-position, distance, and environment columns required for mapping. The next stage must join RA, Dec, distance, distance uncertainty, and environment/LSS proxies before testing angular or radial structure.

## Required Next Inputs

- RA and Dec
- distance and distance uncertainty
- inclination/systematics controls
- environment or large-scale-structure proxy
- source-family provenance for held-out validation

## Generated Files

- `w_tau_eff_field_seed_v01.csv`
- `w_tau_eff_field_seed_summary_v01.csv`
