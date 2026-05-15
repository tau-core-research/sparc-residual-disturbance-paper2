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
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/paper2_final_metric_table.csv
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

## Scope

This repository is a reproducibility package for Paper 2 only. It is a diagnostic residual-shape inference packet. It is not a Tau Core theory repository, not a gravity proof, and not a replacement for external evidence labels.

Raw SPARC inputs, private notes, large local downloads, and broader Tau Core development materials are intentionally excluded.
