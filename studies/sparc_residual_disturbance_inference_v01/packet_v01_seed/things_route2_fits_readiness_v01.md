# THINGS Route 2 FITS Readiness Audit v0.1

This audit checks whether the staged FITS products for NGC925 and NGC3031 are readable and contain enough metadata to begin component-array derivation. It does not derive `Vgas`, `Vdisk`, `Vbul`, or any `W_tau_eff` score.

## Readiness

- THINGS MOM0/MOM1 products are readable for both primary galaxies.
- SINGS IRAC 3.6 micron products are readable for both primary galaxies.
- WCS-like coordinate headers and image units are present.
- Component arrays are still not derived.

## Remaining Blockers

- Freeze ring geometry and radius grid for extraction.
- Convert MOM0 flux units into HI surface-density profiles.
- Convert IRAC 3.6 micron images into stellar surface-density profiles using the frozen M/L policy.
- Apply a frozen disk-potential or external solver rule to convert surface density profiles into `Vgas`, `Vdisk`, and `Vbul`.
- Define `eVobs` or an uncertainty carry-through rule before scoring.

## Gate

- `R2FITS01`: fits_headers_readable_for_two_primary_galaxies / score=no.
- `R2FITS02`: source_units_identified / score=no.
- `R2FITS03`: component_arrays_not_yet_derived / score=no.

## Guardrail

`fits_readiness_only_no_component_arrays_no_scores`
