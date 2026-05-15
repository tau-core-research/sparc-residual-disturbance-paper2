# Paper 2 Manuscript Skeleton

Working title: Residual-shape inference of structural disturbance in SPARC rotation curves: a diagnostic audit

## Abstract Skeleton

We test whether fixed rotation-curve residual-shape features can recover externally reviewed A/C disturbance labels in the SPARC sample. The primary predeclared diagnostic is `Projection_RMS`, evaluated with leave-one-galaxy-out thresholding, shuffled-label null tests, bootstrap uncertainty, baseline-family comparisons, and distance-matched stress checks. The current result is a diagnostic association, not a Tau Core validation claim and not a unique projection-model selection result.

## Main Result

- `Projection_RMS` LOOGO AUC: 0.771008403 (accuracy=0.755555556)
- Bootstrap 95% AUC interval: [0.600802469, 0.909100262]
- Shuffled-label empirical p: 0.002000000 (null_p95_auc=0.634453782)

## Baseline-Family Result

- MOND RMS LOOGO AUC: 0.720588235
- RAR RMS LOOGO AUC: 0.731092437
- Newtonian baryonic RMS LOOGO AUC: 0.506302521

Interpretation: the separation is strongest in low-acceleration residual-family scores and is not established as projection-formula uniqueness.

## Observability and B-Class Policy

- Distance-matched C-higher fraction: 0.647058824 (n_pairs=17)
- Strict distance-caliper median difference: 0.119490421 (n_pairs=13)
- B-class threshold split: 13 C-like (A_like=15; threshold=0.166489797)

B galaxies are not used as primary training or validation truth. They may be used only as an uncertainty band or as a prioritized list for future external review.

## Proposed Manuscript Sections

1. Introduction: residual-shape diagnostics and non-circular disturbance context.
2. Data and labels: SPARC A/C labels inherited from the frozen Paper 1 evidence packet.
3. Residual features: fixed score-table features and predeclared `Projection_RMS` baseline.
4. Validation design: LOOGO thresholding, shuffled-label null, bootstrap uncertainty.
5. Results: primary diagnostic, baseline families, Newtonian scope control.
6. Error audit: false-positive and false-negative systems without residual relabeling.
7. Observability stress: distance-matched controls and unresolved selection-function caveat.
8. B-class uncertainty band and candidate prioritization.
9. Discussion: diagnostic value, limitations, and Phase II external validation.

## Readiness Summary

- Primary diagnostic: ready_with_caveats -- report_as_residual_shape_diagnostic_not_physical_proof
- Baseline specificity: ready_as_non_unique_low_acceleration_family_result -- state_that_projection_is_not_unique_and_newtonian_is_scope_control
- Observability: caveated_not_solved -- keep_as_major_limitation_and_phase_ii_requirement
- B-class use: policy_frozen -- use_only_as_uncertainty_band_or_candidate_prioritization
- External validation: not_yet_available -- present_as_future_work_not_as_current_evidence

## Claim Boundary

Allowed: fixed residual-shape features recover externally reviewed A/C disturbance class better than chance in the current SPARC packet, with important observability caveats.

Forbidden: Tau Core validation, projection-model uniqueness, replacement of external labels by residual-only labels, or claim of independent external validation.

## Next Gate

Generate publication-grade figures and a first full manuscript draft from this skeleton.
