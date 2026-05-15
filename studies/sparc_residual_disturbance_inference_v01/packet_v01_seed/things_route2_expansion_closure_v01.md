# THINGS Route 2 Expansion Closure v0.1

Route 2 is closed as not score-ready. The closure is methodological, not a negative Tau claim: the staged source products and validation audits remain useful, but they do not justify scoring the missing THINGS galaxies.

## Evidence

- `R2CLOSE01`: useful_but_not_score_ready - THINGS MOM0/MOM1 and SINGS IRAC1 products are staged outside git with checksum manifests.
- `R2CLOSE02`: useful_negative_control - Validation galaxies produced native and surface-density proxy profiles, but this does not validate velocity components.
- `R2CLOSE03`: failed - Derived IRAC profiles do not reproduce SPARC SBdisk at the frozen threshold.
- `R2CLOSE04`: failed - Outer-annulus background subtraction does not unblock SPARC SBdisk agreement.
- `R2CLOSE05`: failed - Official SPARC and de Blok machine/source checks do not expose score-ready per-radius columns for the missing five.

## Decisions

- `R2CLOSED01`: closed_not_score_ready; forbidden=score_missing_THINGS_galaxies_from_route2_outputs.
- `R2CLOSED02`: not_reached; forbidden=claim_THINGS_N15_or_paper_grade_external_validation_from_route2.

## Claim Boundary

- `R2CLAIM01`: forbidden - replace with: Route2 produced a reproducible negative audit and remains not score-ready.
- `R2CLAIM02`: forbidden - replace with: Velocity-solver validation was blocked before solver execution by failed stellar surface-profile checks.
- `R2CLAIM03`: forbidden - replace with: THINGS remains below the frozen N>=15 external-validation gate.
- `R2CLAIM04`: forbidden - replace with: Route2 only shows that this reconstruction path is not validated for missing THINGS mass-model recovery.

## Reopening Condition

Route 2 may be reopened only if citable, machine-readable per-radius mass-model columns are obtained for at least two missing THINGS galaxies, or if a complete photometry/decomposition plus velocity-solver pipeline is pre-registered and validates against existing SPARC component curves before missing-galaxy scoring.

No route2 `W_tau_eff` score is computed here.
No synthetic mass-model columns are created here.

Guardrail: `route2_expansion_closed_not_score_ready_no_synthetic_mass_models`
