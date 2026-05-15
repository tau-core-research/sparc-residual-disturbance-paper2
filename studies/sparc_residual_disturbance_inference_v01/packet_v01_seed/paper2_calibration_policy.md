# Paper 2 Calibration and Policy Gate

This packet adds calibration uncertainty, B-class policy, and Newtonian baseline scope for the residual-disturbance inference branch.

## Calibration Uncertainty

- Predictor: `Projection_RMS`
- Observed AUC: 0.771008403
- Bootstrap 95% CI: [0.600802469, 0.909100262]
- Median-midpoint threshold: 0.166489797
- In-sample threshold accuracy: 0.755555556

## B-Class Policy

- B galaxies remain excluded from primary training and primary A/C AUC.
- B galaxies scored C-like under the A/C threshold: 13/28
- B may be used only as an uncertainty band and candidate-prioritization set.

## Newtonian Scope

- Projection score-table LOOGO AUC: 0.771008403
- Newtonian baryonic LOOGO AUC: 0.506302521
- Newtonian accuracy: 0.511111111

## Interpretation

The Paper 2 primary diagnostic remains a low-acceleration residual-family signal rather than a generic Newtonian baryonic residual classifier. The B-class policy prevents uncertain labels from becoming pseudo-ground-truth, and the bootstrap interval makes the sample-size uncertainty explicit.

## Guardrail

This gate is not a Tau Core validation result. It still does not authorize projection-model uniqueness or replacing external evidence labels with residual-only labels.

## Generated Files

- `paper2_calibration_uncertainty.csv`
- `paper2_b_class_policy.csv`
- `paper2_newtonian_scope.csv`
