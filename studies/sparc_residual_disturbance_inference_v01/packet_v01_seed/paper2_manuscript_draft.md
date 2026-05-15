# Residual-shape inference of structural disturbance in SPARC rotation curves: a diagnostic audit

## Abstract

We test whether fixed rotation-curve residual-shape features can recover externally reviewed structural-disturbance labels in the SPARC sample. The analysis reverses the direction of the Paper 1 residual-blind audit: the A/C labels are targets here, while residuals are predictors. The primary frozen diagnostic is `Projection_RMS`, evaluated with leave-one-galaxy-out thresholding, a shuffled-label null, bootstrap uncertainty, baseline-family comparisons, and distance-matched stress checks. `Projection_RMS` reaches a LOOGO AUC of 0.771 with accuracy 0.756; a shuffled-label null gives empirical p=0.002, and the bootstrap 95% AUC interval is [0.601, 0.909]. MOND-like and RAR-like residual scores also separate A/C systems, while a Newtonian baryonic RMS control is near chance. The result is therefore best read as a residual-shape diagnostic association in the low-acceleration residual family, not as a Tau Core validation result, not as a unique projection-model selection result, and not as a replacement for external evidence labels.

## 1. Introduction

Rotation-curve residuals are often treated as model failures or nuisance structure. In disturbed galaxies, however, residual morphology can also encode non-equilibrium dynamics, non-circular motion, beam-smearing sensitivity, asymmetric drift corrections, or geometry-dependent observational systematics. This paper asks a deliberately narrower question: can fixed residual-shape features recover externally reviewed A/C disturbance class better than chance?

The study is a diagnostic audit. It does not attempt to prove a gravitational model. It uses the external labels inherited from the Paper 1 evidence packet as targets and tests whether a small set of residual features can recover those targets under simple, reviewable validation rules.

## 2. Data and Label Scope

The working sample contains 45 SPARC galaxies with Paper 1 A/C labels: 17 externally regular A systems and 28 externally disturbed C systems. B-class systems are intentionally excluded from primary training and primary A/C validation because they are uncertain by construction. They are retained only as an uncertainty band and as a possible prioritization set for future external review.

The residual-feature table is generated from the fixed point map in `taucore_specificity_point_map.csv`. Required derived Paper 1 inputs are included in this repository only where needed to preserve reproducibility paths.

## 3. Residual Features

The primary diagnostic is `Projection_RMS`, the galaxy-level RMS of the fixed projection residual. Additional exploratory features include radial residual structure, low-acceleration residual burden, and residual differences between the projection, MOND-simple, and empirical RAR-like baselines. The composite score is not promoted as the primary result because it does not improve the leave-one-galaxy-out baseline.

## 4. Validation Design

The primary classifier is intentionally simple: for each held-out galaxy, the A/C threshold is recomputed from the remaining galaxies as the midpoint between the A and C medians, and the held-out galaxy is classified by whether its score lies above or below that threshold. This leave-one-galaxy-out design avoids fitting the threshold on the held-out galaxy while keeping the rule transparent.

A shuffled-label null preserves class counts and tests whether the observed AUC is typical under random A/C assignment. Bootstrap resampling provides sample-size uncertainty, but it is not treated as independent external validation.

## 5. Results

The primary `Projection_RMS` diagnostic reaches LOOGO AUC=0.771008403 with accuracy=0.755555556. The shuffled-label empirical p-value is 0.002000000, with null 95th-percentile AUC reported as null_p95_auc=0.634453782. The bootstrap 95% AUC interval is [0.600802469, 0.909100262].

![Projection RMS distribution](../../../figures/paper2_projection_rms_distribution.svg)

## 6. Baseline-Family Comparison

MOND-simple RMS reaches AUC=0.720588235, and empirical RAR-like RMS reaches AUC=0.731092437. The Newtonian baryonic RMS control reaches AUC=0.506302521. This pattern argues against a generic residual-amplitude artifact and supports the narrower claim that A/C separation appears mainly in low-acceleration residual-family scores. It does not establish projection-formula uniqueness.

![Baseline AUC comparison](../../../figures/paper2_baseline_auc_comparison.svg)

## 7. Error Audit

The Projection RMS threshold yields 34 correct classifications, 3 false-positive A-as-C systems, and 8 false-negative C-as-A systems. The false negatives are especially important: several externally disturbed systems do not express that disturbance as a large smooth rotation-curve residual burden. This is a useful diagnostic failure mode, not a reason to relabel the galaxies from residuals alone.

![Projection RMS error audit](../../../figures/paper2_error_audit.svg)

## 8. Observability Stress

Distance matching does not erase the signal, but it does not solve the selection-function problem. The greedy distance-matched C-higher fraction is 0.647058824 (n_pairs=17), and the strict distance-caliper median C-A difference is 0.119490421 (n_pairs=13). The correct interpretation is that observability remains a major caveat.

![Distance stress](../../../figures/paper2_distance_stress.svg)

## 9. B-Class Policy

Using the frozen Projection RMS A/C threshold, 13 of 28 B-class galaxies score C-like (A_like=15; threshold=0.166489797). This split is descriptive only. B galaxies are not used as primary training labels because that would turn uncertainty into pseudo-ground-truth.

## 10. Limitations

The sample is small. The labels are externally reviewed but not immune to source selection or observability bias. Nearby galaxies can reveal structural disturbance more easily than distant galaxies, and beam smearing, inclination, non-circular motion, pressure support, and asymmetric drift corrections can all affect residual morphology. The analysis also lacks independent external validation in a second survey family. HALOGAS H07 is treated only as a weak, non-specific external-family control.

## 11. Claim Boundary

Allowed claim: fixed residual-shape features recover externally reviewed A/C disturbance class better than chance in the current SPARC packet, with important observability caveats.

Forbidden claims: Tau Core validation, projection-model uniqueness, replacement of external evidence labels by residual-only labels, or independent external validation.

## 12. Phase II

The primary diagnostic gate is ready_with_caveats; observability is caveated_not_solved; external validation is not_yet_available. The next paper-grade step is a held-out external validation sample with a frozen evidence rule and a predeclared residual-feature map.
