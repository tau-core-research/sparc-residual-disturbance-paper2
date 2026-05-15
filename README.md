# SPARC Residual-Disturbance Paper 2

This repository is the public reproducibility package for the Paper 2 working packet:

**Residual-shape inference of structural disturbance in SPARC rotation curves: a diagnostic audit**

The package preserves the relative paths cited by the Paper 2 packet. The main packet is:

```text
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed
```

## Main Files

```text
LICENSE
CITATION.cff
DATA_NOTICE.md
requirements.txt
tests/
figures/
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/paper2_manuscript_skeleton.md
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/paper2_manuscript_draft_v03.md
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/paper2_submission_readiness_v01.md
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/paper2_final_metric_table.csv
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/paper2_results_summary_v03.csv
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/paper2_external_proxy_summary_v03.csv
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/paper2_readiness_table.csv
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/paper2_figure_plan.csv
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/paper2_claim_boundary.csv
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/residual_feature_table.csv
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/residual_inference_loogo_metric_summary.csv
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/residual_inference_projection_rms_error_audit.csv
```

## Included Derived Inputs

The Paper 2 scripts require a small set of derived Paper 1 inputs. They are included at their original relative paths:

```text
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/taucore_specificity_point_map.csv
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/baseline_score_by_galaxy.csv
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/scale_matched_pairs.csv
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/scale_matched_stress.csv
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/external_evidence_table.csv
```

These are derived reproducibility artifacts, not raw SPARC rotmod files.

## Reproduce The Packet

Create an environment with Python 3.10 or newer, then install the minimal test dependency:

```bash
python -m pip install -r requirements.txt
```

Regenerate the public Paper 2 packet:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_packet_v01_seed.py
python studies/sparc_residual_disturbance_inference_v01/make_loogo_validation_v01.py
python studies/sparc_residual_disturbance_inference_v01/make_classifier_gate_v01.py
python studies/sparc_residual_disturbance_inference_v01/make_error_audit_v01.py
python studies/sparc_residual_disturbance_inference_v01/make_paper2_seed_packet.py
python studies/sparc_residual_disturbance_inference_v01/make_paper2_validation_controls.py
python studies/sparc_residual_disturbance_inference_v01/make_paper2_calibration_policy.py
python studies/sparc_residual_disturbance_inference_v01/make_paper2_manuscript_packet.py
python studies/sparc_residual_disturbance_inference_v01/make_paper2_figures_and_draft.py
python studies/sparc_residual_disturbance_inference_v01/make_paper2_status_board_v02.py
python studies/sparc_residual_disturbance_inference_v01/make_paper2_manuscript_v02.py
python studies/sparc_residual_disturbance_inference_v01/make_paper2_manuscript_v03.py
python studies/sparc_residual_disturbance_inference_v01/make_paper2_submission_readiness_v01.py
python -m pytest -q
```

The commands regenerate the same packet paths listed above.

## Optional Effective S_tau Pilot

The repository includes derived `S_tau_eff` pilot tables. They can be regenerated only if the raw SPARC rotmod files are available locally:

```bash
SPARC_ROTMOD_DIR=/path/to/Rotmod_LTG \
  python studies/sparc_residual_disturbance_inference_v01/make_s_tau_eff_pilot.py
```

This optional pilot back-solves an empirical `S_tau_eff(R)` from `Vobs` and `Vbar`. It is a diagnostic map, not a predictive model, because it uses the observed velocity target.

The first leakage-controlled source-side rule can then be regenerated with:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_predictive_s_tau_rule.py
```

That rule uses only `EvidenceType` and `Confidence`; it explicitly forbids `Vobs`, `Vbar`, residuals, `Projection_RMS`, `S_tau_eff`, and the A/C class label as rule inputs.

The no-refit velocity readout against the old `S_tau=1` baseline is:

```bash
python studies/sparc_residual_disturbance_inference_v01/evaluate_predictive_s_tau_velocity.py
```

This readout is intentionally allowed to use the derived velocity-level table only after the source-side rule is frozen.

The first frozen radial/source-side rule is:

```bash
python studies/sparc_residual_disturbance_inference_v01/evaluate_radial_s_tau_rule.py
```

It adds only `RadiusFraction` and `aN/a0` to the source metadata. It is still a heuristic readout, not a fitted physical law.

The THINGS source-side ring-level `S_tau(R)` velocity readout is:

```bash
python studies/sparc_residual_disturbance_inference_v01/evaluate_things_source_s_tau_velocity.py
```

This optional gate uses the copied THINGS overlap readout in `path_b_source_only_stau_readout_joined_points.csv`. It reports both frozen bounded mappings, does not refit any coefficient, and does not select a mapping by outcome.

The post-outcome failure audit for that gate is:

```bash
python studies/sparc_residual_disturbance_inference_v01/audit_things_source_s_tau_failure.py
```

This audit compares the source-side mappings to the empirical `S_tau_eff` diagnostic only to explain the failure mode. It is not a new rule and must not be used as model selection.

The first conservative contextual `S_tau(R)` candidate is:

```bash
python studies/sparc_residual_disturbance_inference_v01/evaluate_contextual_s_tau_rule.py
```

This post-audit candidate stays close to `S_tau=1` and uses only radius fraction, acceleration regime, and the THINGS stress proxy. It is hypothesis-generating until tested on a held-out source family.

The integrated signed-residual drift diagnostic is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_integrated_tau_drift_v01.py
```

This diagnostic asks whether the fixed TPG/projection baseline departs through cumulative radial drift rather than pointwise random scatter. It is not an `S_tau` rule; it motivates a possible history-dependent `S_tau` gate.

The causal inner-history `S_tau` readout is:

```bash
python studies/sparc_residual_disturbance_inference_v01/evaluate_history_s_tau_rule.py
```

This readout sets each point's `S_tau` from the signed residual history of inner points in the same galaxy. It is not an external prediction, but it tests whether an integrated radial state can improve outer-point residuals.

The Tau Core signal-candidate framing is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_tau_core_signal_candidate_v01.py
```

This packet treats the TPG residual as a possible carrier of a higher-order Tau Core signal, while explicitly keeping ordinary observational, baryonic, and non-circular-motion systematics as live alternatives.

In the current framing, TPG is not outside Tau Core: it is treated as an effective baseline that already carries local Tau Core weights. The residual is the candidate carrier for the missing environment- and observer-dependent weights.

The closing `W_tau_eff` field seed is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_w_tau_eff_field_seed_v01.py
```

This closes the residual-weight branch by defining a map-ready galaxy-level seed. It is not a Tau Core field map; sky coordinates, distances, environment proxies, and systematics controls must be joined before mapping.

The final branch-closure audit is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_w_tau_eff_branch_closure_audit_v01.py
```

This audit records the supported claims, non-established claims, failure modes, and mandatory next gates before any map can be interpreted.

The next model gate for the residual signal-candidate branch is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_tau_core_weight_model_gate_v01.py
```

This gate freezes the target interpretation before any new endpoint readout: TPG carries local Tau Core weights, while the remaining integrated state `W_env_obs(R)` must be predicted from predeclared history, geometry, environment, or observer-state proxies.

The source-side proxy inventory for `W_env_obs(R)` is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_source_side_history_proxy_inventory_v01.py
```

This inventory lists residual-free proxy families and systematics controls. It does not evaluate a velocity endpoint or select a rule.

The first frozen `W_env_obs` proxy design is:

```bash
python studies/sparc_residual_disturbance_inference_v01/freeze_w_env_obs_proxy_design_v01.py
```

This design freezes P01 as the broad prior, P07 as the source-family holdout, P03/P04 as small sanity checks, and P09 as a mandatory systematics control. It blocks velocity endpoint readouts until a formula is frozen.

The frozen P01 direction readout against `W_tau_eff` is:

```bash
python studies/sparc_residual_disturbance_inference_v01/evaluate_proxy_direction_vs_w_tau_eff_v01.py
```

This readout checks whether the residual-blind P01 burden direction aligns with the existing `W_tau_eff` candidate score. It still does not evaluate a velocity endpoint or fit coefficients.

The P07 WHISP source-family holdout is:

```bash
python studies/sparc_residual_disturbance_inference_v01/evaluate_p07_whisp_holdout_v01.py
```

This readout checks whether published WHISP HI lopsidedness/asymmetry aligns with `W_tau_eff` in the overlap. It is a small source-family sanity check, not a final validation.

The WHISP observer-distance external-validation sanity check is:

```bash
python studies/sparc_residual_disturbance_inference_v01/evaluate_observer_distance_whisp_external_validation_v01.py
```

This readout tests whether the observer-distance hypothesis direction reproduces inside the WHISP overlap after WHISP/systematics controls. It does not open a velocity endpoint and it is not class-balanced.

The external validation status board is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_external_validation_status_board_v01.py
```

This board summarizes the WHISP, THINGS, LITTLE THINGS, and HALOGAS source-family status. It freezes the current decision as mixed support for the broad `W_tau_eff` direction, but not for the observer-distance interpretation.

The expanded non-WHISP external validation target plan is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_expanded_external_validation_targets_v01.py
```

This freezes the next target families, minimum coverage gates, balance requirements, and pass/fail criteria before any additional data expansion.

The external source acquisition plan is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_external_source_acquisition_plan_v01.py
```

This freezes public source URLs, required derived fields, and raw-data redistribution guardrails for the next expansion step.

The structured external source metadata download is:

```bash
python studies/sparc_residual_disturbance_inference_v01/download_external_validation_sources_v01.py
```

This stores raw source pages and API metadata under `data/raw/` and writes only derived manifests into the public packet.

The HALOGAS candidate moment-map download is:

```bash
python studies/sparc_residual_disturbance_inference_v01/download_halogas_candidate_moments_v01.py
```

This downloads only the candidate non-cube FITS products and verifies their MD5 checksums. Large HALOGAS cubes remain excluded from this step.

The source alias crossmatch and HALOGAS moment-feature derivation are:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_source_alias_crossmatch_v01.py
python studies/sparc_residual_disturbance_inference_v01/derive_halogas_moment_features_v01.py
python studies/sparc_residual_disturbance_inference_v01/evaluate_halogas_moment_proxy_v01.py
```

These commands build the exact-name external-source join, derive small HALOGAS moment-map proxy features, and evaluate the proxy as a small external control. They do not use SPARC velocity residuals as predictors and do not open a velocity endpoint.

The THINGS Table 3 expanded overlap check is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_things_table3_expanded_overlap_v01.py
```

This curates the published Trachternach et al. harmonic-decomposition summary values, joins them to `W_tau_eff`, and freezes the current THINGS expansion status.

The Reynolds et al. 2020 resolved H I asymmetry VizieR crossmatch is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_reynolds2020_asymmetry_crossmatch_v01.py
```

This parses `J/MNRAS/493/5089`, joins exact-name overlaps to `W_tau_eff`, and records the remaining LVHIS alias-resolution blocker.

The LVHIS alias-resolved Reynolds et al. 2020 crossmatch is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_lvh_alias_resolved_reynolds2020_crossmatch_v01.py
```

This resolves LVHIS survey IDs through the public ATNF LVHIS database, re-runs the Reynolds et al. crossmatch, and records the remaining minimum-N blocker without redistributing raw survey products.

The Reynolds et al. 2020 coverage-ceiling audit is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_reynolds2020_coverage_ceiling_audit_v01.py
```

This closes the simple-alias expansion route by documenting that the current frozen `W_tau_eff` seed can provide only six Reynolds et al. matches after LVHIS ID resolution.

The Reynolds et al. 2020 seed-expansion freeze is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_reynolds2020_seed_expansion_freeze_v01.py
```

This predeclares the candidate universe for a possible expanded `W_tau_eff` seed. It does not calculate new residual scores and keeps the Reynolds Amap/Avel directional readout closed until a SPARC rotmod availability audit and expanded scoring table are committed.

The SPARC rotmod availability audit for the frozen Reynolds queue is:

```bash
python studies/sparc_residual_disturbance_inference_v01/audit_reynolds2020_sparc_rotmod_availability_v01.py
```

This records derived availability, point counts, and checksums for locally available SPARC rotmod inputs. It does not redistribute raw SPARC data and does not compute an expanded directional readout.

The Yu et al. 2022 ALFALFA profile-asymmetry coverage audit is:

```bash
python studies/sparc_residual_disturbance_inference_v01/audit_yu2022_alfalfa_profile_asymmetry_coverage_v01.py
```

This ingests the VizieR `J/ApJS/261/21` table, uses the AGC-to-UGC convention documented in the catalogue, and checks coverage against the current `W_tau_eff` seed and the local SPARC rotmod inventory. It is coverage-only and does not compute an Af/Ac directional readout.

The Yu et al. 2022 ALFALFA seed-expansion freeze is:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_yu2022_alfalfa_seed_expansion_freeze_v01.py
```

This freezes the ALFALFA expansion queue and primary-quality gate before any expanded score is computed. It keeps the Af/Ac directional readout closed until the expanded scoring script and expanded score table are committed.

## Scope

This repository is a reproducibility package for Paper 2 only. It is a diagnostic residual-shape inference packet. It is not a Tau Core theory repository, not a gravity proof, and not a replacement for external evidence labels.

Raw SPARC inputs, private notes, large local downloads, and broader Tau Core development materials are intentionally excluded.
