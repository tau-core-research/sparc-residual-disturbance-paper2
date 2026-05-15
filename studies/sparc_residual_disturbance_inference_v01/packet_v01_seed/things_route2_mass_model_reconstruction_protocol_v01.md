# THINGS Route 2 Mass-Model Reconstruction Protocol v0.1

This protocol freezes the second route for completing at least two of the five unresolved THINGS Table 3 galaxies. It is intentionally a protocol only: no new `W_tau_eff` score is computed here.

## Scope

Route 2 is allowed because direct public-table recovery did not expose score-ready per-radius baryonic velocity columns for NGC925, NGC3031, NGC3621, NGC3627, or NGC4736. The goal is to reconstruct or recover compatible mass-model inputs without tuning any choice to the final residual score.

## Required Components

A galaxy becomes score-ready only when the packet contains radius-matched `R`, `Vobs`, `eVobs`, `Vgas`, `Vdisk`, and `Vbul` columns, or a documented zero-bulge policy fixed before scoring.

## Frozen Choices

- Use the published rotation-curve radius grid when available.
- If the gas component is derived from HI surface density, use a single thin-disk rule and a 1.4 helium/metals factor.
- Fix the 3.6 micron stellar mass-to-light policy before scoring.
- Decide bulge handling before scoring from published decomposition or morphology, not from the score direction.
- Require at least eight valid radial points, matching the existing expanded THINGS scoring discipline.

## Forbidden Actions

- Do not digitize final model plots as score-ready data unless a separate uncertainty and double-entry protocol is committed.
- Do not tune gas geometry, M/L, interpolation, bulge inclusion, or radius cuts after viewing `W_tau_eff`.
- Do not claim THINGS N>=15 until at least two missing galaxies pass the complete input gate.
- Do not promote route 2 output to Tau Core validation; it remains a THINGS control expansion.

## Next Step

Build a per-galaxy input inventory for the five missing objects and download or recover only the source products needed for the required components.

## Guardrail

`route2_protocol_frozen_before_any_new_things_score`
