# Paper 2 Cautious Outline

Working title:

`Residual-shape inference of structural disturbance in SPARC rotation curves: a diagnostic audit`

## Central Question

Can residual-shape features from fixed rotation-curve baseline scores recover externally assigned A/C disturbance class better than chance?

## Primary Claim Candidate

A simple residual-amplitude feature, `Projection_RMS`, recovers A/C class in a leave-one-galaxy-out sanity check with AUC 0.771 and accuracy 0.756. This is a diagnostic result, not a physical proof or model-selection result.

## Required Framing

- Paper 1 direction: external labels -> residual scatter.
- Paper 2 direction: residual shape -> external disturbance class.
- The labels are targets here, not residual-blind evidence.
- Projection/MOND/RAR/Newton residual families must remain side-by-side.
- B-class galaxies stay outside the primary A/C classifier unless a separate uncertainty analysis is frozen.

## Proposed Sections

1. Introduction: residuals as diagnostic fingerprints, not theory confirmation.
2. Related work: HI lopsidedness, harmonic decomposition, non-circular motions, rotation-curve diversity.
3. Data: Paper 1 residual point map and frozen A/C evidence labels.
4. Features: residual amplitude, radial structure, low-acceleration burden, comparator differences.
5. Validation: leave-one-galaxy-out threshold classifier and shuffled-label null.
6. Results: Projection_RMS primary baseline; composite score demoted.
7. Error audit: false-positive A-as-C and false-negative C-as-A families.
8. Controls: distance/radius/mass/observability sensitivity and baseline-family comparison.
9. Limitations: small sample, label subjectivity, residual target leakage risk, no Tau-specific claim.
10. Discussion: how residual-shape inference can prioritize future external A/C review.

## Paper-Grade Status

- Shuffled-label null distribution is available for the LOOGO primary baseline.
- First distance-matched observability stress tests are available, but selection-function control remains incomplete.
- Baseline-family comparison is available for Projection, MOND-simple, RAR, and Newtonian features.
- B-class policy is frozen: exclude from primary A/C training and validation; use only as an uncertainty band.
- Calibration uncertainty is available through bootstrap AUC intervals.

## HALOGAS H07 Role

HALOGAS H07 should be mentioned only as an external-family weak control: a simple LR cube linewidth-stress proxy did not produce a strong or Tau-specific residual association. It should not be used as Paper 2 primary evidence.
