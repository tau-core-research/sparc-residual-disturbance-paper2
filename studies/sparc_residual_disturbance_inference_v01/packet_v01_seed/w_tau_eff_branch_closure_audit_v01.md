# W_tau_eff Branch Closure Audit v0.1

This audit closes the residual-weight branch before any field-map construction. It records what has been established, what remains explicitly unproven, and which controls are mandatory before a map can be interpreted.

## Branch Status

Closed for definition and seed generation. Not closed for Tau Core attribution or field mapping.

## Stable Working Decomposition

- `TPG`: effective baseline carrying local Tau Core weights.
- `W_tau_eff`: residual-inferred candidate for missing environment- and observer-dependent Tau Core weights.
- `W_tau_eff` is a map-ready seed, not the Tau Core field itself.

## What Is Established

- The residual branch has a reproducible galaxy-level `W_tau_eff` seed for 45 galaxies.
- TPG residuals show signed, cumulative, and history-dependent structure.
- A causal inner-history readout improves over `S_tau=1`, but is not an external prediction.

## What Is Not Established

- No Tau Core field map has been built.
- No residual structure has been uniquely attributed to Tau Core.
- Observability, inclination, beam smearing, baryonic modelling, and non-circular motion alternatives remain open.

## Closure Decision

The branch may proceed to map preparation only after this audit. The next branch must begin with coordinate, distance, systematics, and environment joins, not with interpretive sky maps.

## Generated Files

- `w_tau_eff_branch_claim_boundary_v01.csv`
- `w_tau_eff_branch_failure_modes_v01.csv`
- `w_tau_eff_branch_next_gate_v01.csv`
