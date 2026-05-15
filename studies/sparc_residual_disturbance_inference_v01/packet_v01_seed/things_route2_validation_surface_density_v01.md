# THINGS Route 2 Validation Surface-Density Conversion v0.1

This packet converts the native validation profiles into frozen surface-density proxies. It uses AIPS CLEAN beam values parsed from THINGS MOM0 HISTORY cards and a fixed AB 3.6 micron luminosity conversion for SINGS IRAC1. It does not run a velocity solver and does not compute missing-galaxy scores.

## Beam Audit

- `NGC2403`: beam parsed=yes, BMAJ=8.750880 arcsec, BMIN=7.648560 arcsec.
- `NGC3198`: beam parsed=yes, BMAJ=11.431080 arcsec, BMIN=9.362520 arcsec.
- `NGC5055`: beam parsed=yes, BMAJ=10.058040 arcsec, BMIN=8.663760 arcsec.

## Conversion Summary

- `NGC2403` `THINGS_HI_MOM0`: 44 bins, median 3.01182108.
- `NGC2403` `SINGS_IRAC1_3P6UM`: 62 bins, median 4.12681543.
- `NGC3198` `THINGS_HI_MOM0`: 42 bins, median 13.6095955.
- `NGC3198` `SINGS_IRAC1_3P6UM`: 100 bins, median 10.8822436.
- `NGC5055` `THINGS_HI_MOM0`: 100 bins, median 2.42937205.
- `NGC5055` `SINGS_IRAC1_3P6UM`: 100 bins, median 12.286463.

## Gate

- `R2VALDENS01`: surface_density_proxy_profiles_converted_for_three_validation_galaxies / validate=not_until_velocity_solver_maps_surface_density_to_components / score=no.
- `R2VALDENS02`: velocity_solver_not_run / validate=no / score=no.

No velocity component arrays are derived here.
No `W_tau_eff` endpoint is opened here.

Guardrail: `route2_validation_surface_density_conversion_no_velocity_solver_no_scores`
