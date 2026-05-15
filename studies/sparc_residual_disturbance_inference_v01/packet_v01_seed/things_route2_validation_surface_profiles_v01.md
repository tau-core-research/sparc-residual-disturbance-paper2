# THINGS Route 2 Validation Surface Profiles v0.1

This packet derives native-unit radial surface-brightness profiles for the staged solver-validation galaxies using frozen THINGS/de Blok geometry. It does not convert these profiles into mass surface density, does not run a velocity solver, and does not compute any missing-galaxy score.

## Summary

- `NGC2403` `THINGS_HI_MOM0`: 76 bins, max radius 37.750000 kpc, unit `JY/B*M/S`.
- `NGC2403` `SINGS_IRAC1_3P6UM`: 62 bins, max radius 30.750000 kpc, unit `MJy/sr`.
- `NGC3198` `THINGS_HI_MOM0`: 100 bins, max radius 49.750000 kpc, unit `JY/B*M/S`.
- `NGC3198` `SINGS_IRAC1_3P6UM`: 100 bins, max radius 49.750000 kpc, unit `MJy/sr`.
- `NGC5055` `THINGS_HI_MOM0`: 100 bins, max radius 49.750000 kpc, unit `JY/B*M/S`.
- `NGC5055` `SINGS_IRAC1_3P6UM`: 100 bins, max radius 49.750000 kpc, unit `MJy/sr`.

## Gate

- `R2VALPROF01`: native_unit_surface_profiles_derived_for_three_validation_galaxies / validate=not_until_native_profiles_are_converted_to_surface_density / score=no.
- `R2VALPROF02`: velocity_solver_not_run / validate=no / score=no.

No velocity component arrays are derived here.
No `W_tau_eff` endpoint is opened here.

Guardrail: `route2_validation_surface_profiles_no_velocity_solver_no_scores`
