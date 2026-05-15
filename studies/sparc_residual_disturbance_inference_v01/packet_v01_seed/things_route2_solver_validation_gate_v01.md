# THINGS Route 2 Solver Validation Gate v0.1

This gate defines the validation path for the route 2 component-derivation solver before any missing THINGS galaxy is scored.

## Validation Targets

Frozen validation targets: DDO154, NGC2366, NGC2403, NGC2976, NGC3198, NGC5055, NGC7331.

These galaxies already have SPARC-compatible component curves in the local reference workflow and THINGS non-circular-motion context. They are therefore suitable for validating the reconstruction solver against known component curves without using the missing-galaxy endpoint.

## Pass Standard

At least three validation galaxies must have source products staged outside git, blind component profiles derived under the frozen route 2 policy, and median absolute fractional component error <= 0.15 against existing SPARC component curves.

## Current Decision

- `R2VALG01`: validation_targets_defined_from_existing_THINGS_SPARC_overlap; score=no.
- `R2VALG02`: validation_raw_inputs_not_yet_staged; score=no.
- `R2VALG03`: solver_not_yet_accuracy_validated; score=no.

No missing-galaxy score may be computed from route 2 until this validation gate passes.
No solver or tolerance may be selected using `W_tau_eff` direction.

Guardrail: `route2_solver_validation_before_missing_galaxy_scores`
