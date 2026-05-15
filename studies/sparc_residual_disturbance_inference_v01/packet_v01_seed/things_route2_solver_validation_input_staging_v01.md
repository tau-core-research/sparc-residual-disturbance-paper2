# THINGS Route 2 Solver Validation Input Staging v0.1

This packet stages the raw source products needed for the first solver-validation pass. Raw files remain outside git; the public packet stores source URLs, sizes, and SHA256 checksums only.

- Staged files: 6
- Total staged bytes: 80786880
- Validation galaxies: `NGC2403`, `NGC3198`, `NGC5055`.
- Required products per galaxy: THINGS NA MOM0 and SINGS IRAC1 3.6 micron image.
- No missing-galaxy score is computed here.
- No `W_tau_eff` endpoint is opened here.

## Gate

- `R2VALSTAGE01`: validation_raw_inputs_staged_for_three_overlap_galaxies / validate=yes / score=no.
- `R2VALSTAGE02`: validation_raw_inputs_not_git_tracked / validate=yes / score=no.

## Guardrail

`route2_solver_validation_inputs_staged_raw_ignored_no_scores`
