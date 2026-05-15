# Residual-Disturbance Classifier Gate v0.1

This packet freezes the second-stage decision boundary after the first leave-one-galaxy-out validation.

## Decision

`Projection_RMS` becomes the primary baseline. It is simple, physically interpretable, and currently stronger than the first multifeature residual-disturbance score.

The current composite score is demoted to exploratory. Adding features is not automatically an improvement.

## Gates

### RDI_G01_primary_baseline

- Priority: 1
- Decision: `freeze_projection_rms_as_primary_baseline`
- Rationale: Projection_RMS has the strongest LOOGO AUC=0.771008403 and accuracy=0.755555556 with simple physical meaning.
- Allowed next action: report_projection_rms_as_primary_residual_diagnostic_baseline
- Blocked action: do_not_replace_with_multifeature_score_unless_nested_validation_beats_baseline
- Status: `primary_baseline_frozen`

### RDI_G02_secondary_baseline

- Priority: 2
- Decision: `keep_low_acceleration_mean_as_secondary_sanity_check`
- Rationale: Projection_LowAccelerationMean has similar LOOGO accuracy=0.755555556 and AUC=0.762605042 but is less general than full Projection_RMS.
- Allowed next action: report_as_supporting_low_acceleration_readout
- Blocked action: do_not_claim_low_acceleration_feature_is_unique_without_comparator_holdout
- Status: `secondary_supporting_baseline`

### RDI_G03_composite_score

- Priority: 3
- Decision: `demote_residual_disturbance_score_v01_to_exploratory`
- Rationale: The first composite score underperforms: LOOGO accuracy=0.577777778 and AUC=0.663865546.
- Allowed next action: redesign_only_under_predeclared_nested_validation
- Blocked action: do_not_use_current_composite_as_primary_classifier
- Status: `demoted_exploratory`

### RDI_G04_next_validation

- Priority: 4
- Decision: `require_nested_or_source_family_validation_before_paper_claim`
- Rationale: LOOGO is a useful first sanity check but still reuses the same Paper 1 label set and source context.
- Allowed next action: freeze_nested_validation_or_external_source_family_holdout
- Blocked action: do_not_present_current_results_as_paper_grade_classifier
- Status: `open_required_upgrade`

## Guardrail

Do not optimize feature sets on the same A/C labels and then report the result as validated. Any richer classifier must beat the `Projection_RMS` baseline under nested validation or an external source-family holdout.

## Generated File

- `residual_inference_classifier_gate_v01.csv`
