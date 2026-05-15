# THINGS Missing Rotmod Acquisition Audit v0.1

This packet audits whether the remaining THINGS Table 3 galaxies can be added to the expanded `W_tau_eff` control readout. It does not create synthetic mass models and does not score galaxies without compatible baryonic components.

## Current State

- THINGS Table 3 rows: 18
- Currently resolved with `W_tau_eff`: 13
- Missing local SPARC-like rotmod inputs: 5
- Missing galaxies: NGC925, NGC3031, NGC3621, NGC3627, NGC4736

## Finding

THINGS can only be pushed from N=13 to N>=15 if at least two of the missing galaxies receive public, compatible mass-model columns (`Vobs`, `Vgas`, `Vdisk`, `Vbul` or an explicitly frozen equivalent). Published rotation curves alone are insufficient for the current `W_tau_eff` score, because the score depends on the baryonic baseline.

## Next Action

download_or_transcribe_public_tables_only; score_after_conversion_rule_is_committed.

## Generated Files

- `things_missing_rotmod_acquisition_audit_v01.csv`
- `things_missing_rotmod_acquisition_plan_v01.csv`

## Guardrail

`things_missing_rotmod_acquisition_audit_no_synthetic_mass_model`
