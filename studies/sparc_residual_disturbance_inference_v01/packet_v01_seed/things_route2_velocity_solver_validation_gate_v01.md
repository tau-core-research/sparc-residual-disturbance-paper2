# THINGS Route 2 Velocity-Solver Validation Gate v0.1

This gate checks whether the derived SINGS IRAC1 surface-density proxy is already close enough to the SPARC `SBdisk` reference profiles to justify running the velocity solver. It does not run the velocity solver and does not compute any missing-galaxy score.

## Surface-Profile Check

- `NGC2403`: N=64, median fractional error=0.794116205, within-50% fraction=0.281250000, status=fail_surface_profile_mismatch.
- `NGC3198`: N=39, median fractional error=0.676691670, within-50% fraction=0.205128205, status=fail_surface_profile_mismatch.
- `NGC5055`: N=23, median fractional error=1.247986973, within-50% fraction=0.000000000, status=fail_surface_profile_mismatch.

## Gate

- `R2VELVAL01`: surface_profile_reference_check_failed / solver=no / score=no.
- `R2VELVAL02`: missing_galaxy_route2_scores_blocked / solver=no / score=no.

Interpretation: the current route 2 photometry is not yet a validated route to SPARC-compatible stellar component curves. The next defensible step is a frozen background-subtraction and photometry policy, then rerun this reference check before any velocity-solver validation.

No velocity component arrays are derived here.
No `W_tau_eff` endpoint is opened here.

Guardrail: `route2_velocity_solver_validation_blocked_by_surface_profile_mismatch`
