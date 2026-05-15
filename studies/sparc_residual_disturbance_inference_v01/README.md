# SPARC Residual-Disturbance Inference v0.1

This study explores the reverse diagnostic question:

```text
residual pattern -> disturbance/coherence class
```

It is intentionally separate from Paper 1. Paper 1 tests whether external,
residual-blind labels predict residual scatter. This packet asks whether
residual structure itself can be used as a diagnostic fingerprint for
disturbance or non-equilibrium candidates.

## Guardrail

This is a prediction/diagnostic pilot, not a Tau Core proof and not an
external-label validation replacement. Any classifier trained on the Paper 1
labels must be treated as exploratory unless it is tested on held-out galaxies
or an independent source family.

## Regeneration

The current packet is regenerated incrementally. The late-stage W_env_obs
control gate is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_w_env_obs_systematics_competition_v01.py
python studies/sparc_residual_disturbance_inference_v01/evaluate_p05_things_non_circular_control_v01.py
python studies/sparc_residual_disturbance_inference_v01/evaluate_p09_observability_decomposition_v01.py
python studies/sparc_residual_disturbance_inference_v01/evaluate_distance_resolution_environment_join_v01.py
python studies/sparc_residual_disturbance_inference_v01/evaluate_multivariable_no_velocity_stress_v01.py
python studies/sparc_residual_disturbance_inference_v01/make_observer_distance_hypothesis_gate_v01.py
python studies/sparc_residual_disturbance_inference_v01/evaluate_observer_distance_whisp_external_validation_v01.py
python studies/sparc_residual_disturbance_inference_v01/make_external_validation_status_board_v01.py
python studies/sparc_residual_disturbance_inference_v01/make_expanded_external_validation_targets_v01.py
python studies/sparc_residual_disturbance_inference_v01/make_external_source_acquisition_plan_v01.py
python studies/sparc_residual_disturbance_inference_v01/download_external_validation_sources_v01.py
python studies/sparc_residual_disturbance_inference_v01/download_halogas_candidate_moments_v01.py
python studies/sparc_residual_disturbance_inference_v01/make_source_alias_crossmatch_v01.py
python studies/sparc_residual_disturbance_inference_v01/derive_halogas_moment_features_v01.py
python studies/sparc_residual_disturbance_inference_v01/evaluate_halogas_moment_proxy_v01.py
python studies/sparc_residual_disturbance_inference_v01/make_w_env_obs_systematics_competition_v01.py
```

This creates the systematics competition matrix and sanitized control summaries.
It preserves the key guardrail: positive proxy-direction readouts do not open a
velocity endpoint or a Tau Core attribution claim before non-circular-motion and
observability controls compete.
