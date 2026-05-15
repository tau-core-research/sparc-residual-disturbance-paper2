# THINGS Route 2 Solver Validation FITS Audit v0.1

This audit checks the FITS headers and units for the staged solver-validation inputs. It does not derive surface-density profiles, component velocity curves, or any missing-galaxy `W_tau_eff` score.

## Readiness

- THINGS MOM0 validation products are readable for NGC2403, NGC3198, and NGC5055.
- SINGS IRAC1 validation products are readable for NGC2403, NGC3198, and NGC5055.
- MOM0 uses `JY/B*M/S`; IRAC1 uses `MJy/sr`.
- Raw files remain outside git.

## Gate

- `R2VALFITS01`: validation_fits_headers_readable_for_three_overlap_galaxies / validate=partial_after_geometry_profile_extraction_script / score=no.
- `R2VALFITS02`: source_units_identified / validate=partial / score=no.
- `R2VALFITS03`: component_arrays_not_yet_derived / validate=no / score=no.

No component arrays are derived here.
No missing-galaxy score is computed here.

## Guardrail

`route2_solver_validation_fits_readiness_no_component_arrays_no_scores`
