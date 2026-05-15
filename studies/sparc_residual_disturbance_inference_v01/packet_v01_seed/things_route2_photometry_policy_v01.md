# THINGS Route 2 Photometry Policy Audit v0.1

This audit freezes a simple, source-only background policy for SINGS IRAC1 profiles: subtract the median native MJy/sr value in the outer 20 percent of the extracted radial profile and floor at zero. The policy does not use SPARC `SBdisk`, velocity residuals, `W_tau_eff`, or missing-galaxy score direction.

## Frozen Backgrounds

- `NGC2403`: background=0.00294824317 MJy/sr.
- `NGC3198`: background=0.00776277203 MJy/sr.
- `NGC5055`: background=0.00107257813 MJy/sr.

## Reference Check

- `NGC2403`: N=64, median fractional error=0.781244659, within-50% fraction=0.312500000, status=fail_background_only_photometry_policy.
- `NGC3198`: N=39, median fractional error=0.761423989, within-50% fraction=0.179487179, status=fail_background_only_photometry_policy.
- `NGC5055`: N=23, median fractional error=1.247624967, within-50% fraction=0.000000000, status=fail_background_only_photometry_policy.

## Gate

- `R2PHOTG01`: background_only_photometry_policy_failed_reference_check / solver=no / score=no.
- `R2PHOTG02`: route2_missing_galaxy_expansion_remains_blocked / solver=no / score=no.

Conclusion: simple source-only background subtraction does not validate route 2 stellar photometry against SPARC `SBdisk`. The route2 velocity-solver path remains blocked unless published mass-model columns are recovered or a more complete, pre-registered photometry/decomposition pipeline is introduced and validated.

No velocity component arrays are derived here.
No `W_tau_eff` endpoint is opened here.

Guardrail: `route2_photometry_policy_background_only_does_not_validate_solver`
