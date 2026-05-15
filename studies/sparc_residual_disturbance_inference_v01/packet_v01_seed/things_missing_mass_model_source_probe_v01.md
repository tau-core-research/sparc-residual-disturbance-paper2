# THINGS Missing Mass-Model Source Probe v0.1

This probe records the source-level status for the five unresolved THINGS Table 3 galaxies: NGC925, NGC3031, NGC3621, NGC3627, and NGC4736.

## Result

The public SPARC LTG rotmod archive and SPARC machine-readable mass-model table do not resolve the missing five. The THINGS data page provides HI FITS products for the missing galaxies, but those products are not direct `W_tau_eff` inputs because the score requires baryonic velocity components or a frozen mass-model reconstruction rule.

## Current Gate

THINGS can move from N=13 to N>=15 only after at least two missing galaxies receive public per-radius baryonic mass-model columns (`Vobs`, `Vgas`, `Vdisk`, `Vbul`) or a committed equivalent reconstruction rule.

## Source Probe Table

- `SPARC_ROTMod_LTG`: no_missing_five_found (no).
- `SPARC_TABLE2_MRT`: no_missing_five_found (no).
- `THINGS_DATA_PRODUCTS`: hi_fits_products_exist_for_missing_five (not_directly).
- `DEBLOK2008_ARXIV_SOURCE`: tex_has_global_fit_tables_and_figures_not_machine_rotmod_columns (not_directly).

## Decisions

- `TMSP01`: SPARC_public_rotmod_does_not_resolve_missing_five.
- `TMSP02`: THINGS_HI_products_are_available_but_not_score_ready.

## Guardrail

`source_probe_no_raw_data_redistribution_no_synthetic_mass_models`
