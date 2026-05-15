import csv
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "studies/sparc_residual_disturbance_inference_v01"
PACKET = STUDY / "packet_v01_seed"
PAPER1_INPUTS = (
    ROOT
    / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced"
)


def test_publication_repo_checklist_files_exist():
    required = [
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "CITATION.cff",
        ROOT / "DATA_NOTICE.md",
        ROOT / "requirements.txt",
        ROOT / "figures/README.md",
        ROOT / "tests",
        STUDY / "README.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_minimal_derived_inputs_exist():
    required = [
        PAPER1_INPUTS / "taucore_specificity_point_map.csv",
        PAPER1_INPUTS / "baseline_score_by_galaxy.csv",
        PAPER1_INPUTS / "scale_matched_pairs.csv",
        PAPER1_INPUTS / "scale_matched_stress.csv",
        PAPER1_INPUTS / "external_evidence_table.csv",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_paper2_packet_referenced_paths_exist():
    required = [
        PACKET / "README.md",
        PACKET / "packet_manifest.json",
        PACKET / "paper2_manuscript_skeleton.md",
        PACKET / "paper2_manuscript_draft.md",
        PACKET / "paper2_final_metric_table.csv",
        PACKET / "paper2_readiness_table.csv",
        PACKET / "paper2_figure_plan.csv",
        PACKET / "paper2_claim_boundary.csv",
        PACKET / "paper2_related_work.md",
        PACKET / "paper2_validation_controls.md",
        PACKET / "paper2_calibration_policy.md",
        PACKET / "s_tau_eff_pilot.md",
        PACKET / "s_tau_eff_point_pilot.csv",
        PACKET / "s_tau_eff_galaxy_summary.csv",
        PACKET / "predictive_s_tau_rule_v01.md",
        PACKET / "predictive_s_tau_rule_v01.csv",
        PACKET / "predictive_s_tau_by_galaxy_v01.csv",
        PACKET / "predictive_s_tau_readout_v01.csv",
        PACKET / "predictive_s_tau_velocity_readout.md",
        PACKET / "predictive_s_tau_velocity_point_readout.csv",
        PACKET / "predictive_s_tau_velocity_galaxy_summary.csv",
        PACKET / "predictive_s_tau_velocity_metric_summary.csv",
        PACKET / "radial_s_tau_rule_v01.md",
        PACKET / "radial_s_tau_rule_v01.csv",
        PACKET / "radial_s_tau_velocity_point_readout.csv",
        PACKET / "radial_s_tau_velocity_galaxy_summary.csv",
        PACKET / "radial_s_tau_velocity_metric_summary.csv",
        PACKET / "path_b_source_only_stau_readout.md",
        PACKET / "path_b_source_only_stau_readout_joined_points.csv",
        PACKET / "things_source_s_tau_velocity_readout.md",
        PACKET / "things_source_s_tau_velocity_point_readout.csv",
        PACKET / "things_source_s_tau_velocity_galaxy_summary.csv",
        PACKET / "things_source_s_tau_velocity_metric_summary.csv",
        PACKET / "things_source_s_tau_failure_audit.md",
        PACKET / "things_source_s_tau_failure_point_audit.csv",
        PACKET / "things_source_s_tau_failure_galaxy_audit.csv",
        PACKET / "things_source_s_tau_failure_metric_summary.csv",
        PACKET / "contextual_s_tau_rule_v01.md",
        PACKET / "contextual_s_tau_rule_v01.csv",
        PACKET / "contextual_s_tau_velocity_point_readout.csv",
        PACKET / "contextual_s_tau_velocity_galaxy_summary.csv",
        PACKET / "contextual_s_tau_velocity_metric_summary.csv",
        PACKET / "integrated_tau_drift_v01.md",
        PACKET / "integrated_tau_drift_point_trace_v01.csv",
        PACKET / "integrated_tau_drift_galaxy_summary_v01.csv",
        PACKET / "integrated_tau_drift_metric_summary_v01.csv",
        PACKET / "history_s_tau_rule_v01.md",
        PACKET / "history_s_tau_rule_v01.csv",
        PACKET / "history_s_tau_velocity_point_readout.csv",
        PACKET / "history_s_tau_velocity_galaxy_summary.csv",
        PACKET / "history_s_tau_velocity_metric_summary.csv",
        PACKET / "tau_core_signal_candidate_v01.md",
        PACKET / "tau_core_signal_candidate_galaxy_summary_v01.csv",
        PACKET / "tau_core_signal_candidate_relation_summary_v01.csv",
        PACKET / "w_tau_eff_field_seed_v01.md",
        PACKET / "w_tau_eff_field_seed_v01.csv",
        PACKET / "w_tau_eff_field_seed_summary_v01.csv",
        PACKET / "w_tau_eff_branch_closure_audit_v01.md",
        PACKET / "w_tau_eff_branch_claim_boundary_v01.csv",
        PACKET / "w_tau_eff_branch_failure_modes_v01.csv",
        PACKET / "w_tau_eff_branch_next_gate_v01.csv",
        PACKET / "tau_core_weight_model_gate_v01.md",
        PACKET / "tau_core_weight_model_gate_v01.csv",
        PACKET / "tau_core_weight_model_evidence_matrix_v01.csv",
        PACKET / "tau_core_weight_model_next_tests_v01.csv",
        PACKET / "source_side_history_proxy_inventory_v01.md",
        PACKET / "source_side_history_proxy_inventory_v01.csv",
        PACKET / "source_side_history_proxy_readiness_v01.csv",
        PACKET / "w_env_obs_proxy_design_v01.md",
        PACKET / "w_env_obs_proxy_design_v01.csv",
        PACKET / "w_env_obs_proxy_rule_freeze_v01.csv",
        PACKET / "w_env_obs_proxy_endpoint_plan_v01.csv",
        PACKET / "proxy_direction_w_tau_eff_readout_v01.md",
        PACKET / "proxy_direction_w_tau_eff_join_v01.csv",
        PACKET / "proxy_direction_w_tau_eff_metric_summary_v01.csv",
        PACKET / "whisp_vaneymeren2011_overlap.csv",
        PACKET / "p07_whisp_w_tau_eff_holdout_v01.md",
        PACKET / "p07_whisp_w_tau_eff_holdout_join_v01.csv",
        PACKET / "p07_whisp_w_tau_eff_holdout_metric_summary_v01.csv",
        PACKET / "w_env_obs_systematics_competition_v01.md",
        PACKET / "w_env_obs_systematics_competition_matrix_v01.csv",
        PACKET / "w_env_obs_systematics_competition_coverage_v01.csv",
        PACKET / "w_env_obs_systematics_competition_readiness_v01.csv",
        PACKET / "systematics_control_things_harmonic_summary_v01.csv",
        PACKET / "systematics_control_littlethings_pressure_summary_v01.csv",
        PACKET / "systematics_control_halogas_linewidth_summary_v01.csv",
        PACKET / "systematics_control_inclination_summary_v01.csv",
        PACKET / "p05_things_non_circular_w_tau_eff_control_v01.md",
        PACKET / "p05_things_non_circular_w_tau_eff_control_join_v01.csv",
        PACKET / "p05_things_non_circular_w_tau_eff_control_metrics_v01.csv",
        PACKET / "p05_things_non_circular_w_tau_eff_control_decision_v01.csv",
        PACKET / "p09_observability_decomposition_v01.md",
        PACKET / "p09_observability_decomposition_join_v01.csv",
        PACKET / "p09_observability_decomposition_metrics_v01.csv",
        PACKET / "p09_observability_decomposition_decision_v01.csv",
        PACKET / "distance_resolution_environment_join_v01.md",
        PACKET / "distance_resolution_environment_join_v01.csv",
        PACKET / "distance_resolution_environment_metrics_v01.csv",
        PACKET / "distance_resolution_environment_decision_v01.csv",
        PACKET / "multivariable_no_velocity_stress_v01.md",
        PACKET / "multivariable_no_velocity_stress_join_v01.csv",
        PACKET / "multivariable_no_velocity_stress_metrics_v01.csv",
        PACKET / "multivariable_no_velocity_stress_decision_v01.csv",
        PACKET / "observer_distance_hypothesis_gate_v01.md",
        PACKET / "observer_distance_hypothesis_claim_boundary_v01.csv",
        PACKET / "observer_distance_hypothesis_validation_plan_v01.csv",
        PACKET / "observer_distance_hypothesis_readiness_v01.csv",
        PACKET / "observer_distance_whisp_external_validation_v01.md",
        PACKET / "observer_distance_whisp_external_validation_join_v01.csv",
        PACKET / "observer_distance_whisp_external_validation_metrics_v01.csv",
        PACKET / "observer_distance_whisp_external_validation_decision_v01.csv",
        PACKET / "external_validation_status_board_v01.md",
        PACKET / "external_validation_status_board_v01.csv",
        PACKET / "external_validation_status_decision_v01.csv",
        PACKET / "residual_feature_table.csv",
        PACKET / "residual_disturbance_score_v01.csv",
        PACKET / "residual_inference_loogo_metric_summary.csv",
        PACKET / "residual_inference_projection_rms_error_audit.csv",
        PACKET / "residual_inference_projection_rms_error_summary.csv",
        ROOT / "figures/paper2_projection_rms_distribution.svg",
        ROOT / "figures/paper2_baseline_auc_comparison.svg",
        ROOT / "figures/paper2_error_audit.svg",
        ROOT / "figures/paper2_distance_stress.svg",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_final_metrics_and_claim_boundaries_are_guardrailed():
    with (PACKET / "paper2_final_metric_table.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["Projection_RMS_LOOGO"]["Value"] == "0.771008403"
    assert metrics["Projection_RMS_shuffle_null_p"]["Value"] == "0.002000000"
    assert metrics["Newtonian_Baryonic_RMS_LOOGO_AUC"]["Value"] == "0.506302521"
    assert "diagnostic_class_recovery_not_tau_core_validation" in {
        row["Guardrail"] for row in metrics.values()
    }

    manuscript = (PACKET / "paper2_manuscript_skeleton.md").read_text(encoding="utf-8")
    assert "not a Tau Core validation claim" in manuscript
    assert "Forbidden: Tau Core validation" in manuscript
    assert "replacement of external labels by residual-only labels" in manuscript

    draft = (PACKET / "paper2_manuscript_draft.md").read_text(encoding="utf-8")
    assert "## 12. Phase II" in draft
    assert "not as a Tau Core validation result" in draft
    assert "does not establish projection-formula uniqueness" in draft


def test_regeneration_scripts_exist_in_expected_order():
    required = [
        STUDY / "make_packet_v01_seed.py",
        STUDY / "make_loogo_validation_v01.py",
        STUDY / "make_classifier_gate_v01.py",
        STUDY / "make_error_audit_v01.py",
        STUDY / "make_paper2_seed_packet.py",
        STUDY / "make_paper2_validation_controls.py",
        STUDY / "make_paper2_calibration_policy.py",
        STUDY / "make_paper2_manuscript_packet.py",
        STUDY / "make_paper2_figures_and_draft.py",
        STUDY / "make_s_tau_eff_pilot.py",
        STUDY / "make_predictive_s_tau_rule.py",
        STUDY / "evaluate_predictive_s_tau_velocity.py",
        STUDY / "evaluate_radial_s_tau_rule.py",
        STUDY / "evaluate_things_source_s_tau_velocity.py",
        STUDY / "audit_things_source_s_tau_failure.py",
        STUDY / "evaluate_contextual_s_tau_rule.py",
        STUDY / "make_integrated_tau_drift_v01.py",
        STUDY / "evaluate_history_s_tau_rule.py",
        STUDY / "make_tau_core_signal_candidate_v01.py",
        STUDY / "make_w_tau_eff_field_seed_v01.py",
        STUDY / "make_w_tau_eff_branch_closure_audit_v01.py",
        STUDY / "make_tau_core_weight_model_gate_v01.py",
        STUDY / "make_source_side_history_proxy_inventory_v01.py",
        STUDY / "freeze_w_env_obs_proxy_design_v01.py",
        STUDY / "evaluate_proxy_direction_vs_w_tau_eff_v01.py",
        STUDY / "evaluate_p07_whisp_holdout_v01.py",
        STUDY / "make_w_env_obs_systematics_competition_v01.py",
        STUDY / "evaluate_p05_things_non_circular_control_v01.py",
        STUDY / "evaluate_p09_observability_decomposition_v01.py",
        STUDY / "evaluate_distance_resolution_environment_join_v01.py",
        STUDY / "evaluate_multivariable_no_velocity_stress_v01.py",
        STUDY / "make_observer_distance_hypothesis_gate_v01.py",
        STUDY / "evaluate_observer_distance_whisp_external_validation_v01.py",
        STUDY / "make_external_validation_status_board_v01.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_raw_sparc_inputs_are_not_tracked():
    if not (ROOT / ".git").exists():
        return
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    tracked_paths = set(result.stdout.splitlines())
    forbidden = [
        "data/external/SPARC_Table1.txt",
        "data/raw/sparc_zenodo_16284118/Rotmod_LTG.zip",
    ]
    assert not any(path in tracked_paths for path in forbidden)
    assert not any(path.startswith("data/sparc/Rotmod_LTG/") for path in tracked_paths)


def test_effective_s_tau_pilot_is_diagnostic_and_not_predictive():
    with (PACKET / "s_tau_eff_galaxy_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    a_values = [
        float(row["Median_S_tau_eff_clipped"])
        for row in rows
        if row["Class"] == "A"
    ]
    c_values = [
        float(row["Median_S_tau_eff_clipped"])
        for row in rows
        if row["Class"] == "C"
    ]
    assert round(sorted(a_values)[len(a_values) // 2], 9) == 1.093121010
    assert round((sorted(c_values)[13] + sorted(c_values)[14]) / 2, 9) == 0.888249933
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "derived_from_vobs_not_heldout_prediction"
    }

    text = (PACKET / "s_tau_eff_pilot.md").read_text(encoding="utf-8")
    assert "`S_tau=1` is the old TPG/projection baseline" in text
    assert "not a predictive model yet" in text
    assert "without using the target residual" in text


def test_predictive_s_tau_rule_is_frozen_without_target_leakage():
    with (PACKET / "predictive_s_tau_rule_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rules = list(csv.DictReader(handle))
    assert len(rules) == 9
    assert {row["AllowedInputs"] for row in rules} == {"EvidenceType;Confidence"}
    assert {row["ForbiddenInputs"] for row in rules} == {
        "Vobs;Vbar;Projection_RMS;residuals;S_tau_eff;Class"
    }
    assert {row["InterpretationGuardrail"] for row in rules} == {
        "frozen_source_side_rule_not_fit_to_s_tau_eff"
    }

    with (PACKET / "predictive_s_tau_readout_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    assert {row["ReadoutUse"] for row in rows} == {
        "post_freeze_diagnostic_only_not_rule_training"
    }

    predicted = [float(row["Predicted_S_tau_source_v01"]) for row in rows]
    readout = [float(row["Median_S_tau_eff_clipped_ReadoutOnly"]) for row in rows]
    mae_rule = sum(abs(a - b) for a, b in zip(predicted, readout)) / len(rows)
    mae_baseline = sum(abs(1.0 - value) for value in readout) / len(rows)
    assert round(mae_rule, 9) == 0.337389701
    assert round(mae_baseline, 9) == 0.358271634

    text = (PACKET / "predictive_s_tau_rule_v01.md").read_text(encoding="utf-8")
    assert "Forbidden inputs: `Vobs`, `Vbar`, residuals" in text
    assert "Pearson(predicted source S_tau, empirical S_tau_eff): 0.171323258" in text
    assert "not a fitted improvement over TPG" in text


def test_predictive_s_tau_velocity_readout_is_no_refit_and_mixed():
    with (PACKET / "predictive_s_tau_velocity_metric_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Subset"]: row for row in csv.DictReader(handle)}
    assert set(rows) == {"all", "A", "C"}
    assert rows["all"]["MedianDeltaRMS_SourceMinusS1"] == "-0.003098856"
    assert rows["all"]["FractionGalaxiesImproved"] == "0.511111111"
    assert rows["A"]["MedianDeltaRMS_SourceMinusS1"] == "-0.003098856"
    assert rows["C"]["MedianDeltaRMS_SourceMinusS1"] == "0.007165785"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "velocity_residual_readout_not_refit"
    }

    with (PACKET / "predictive_s_tau_velocity_galaxy_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        galaxies = list(csv.DictReader(handle))
    assert len(galaxies) == 45
    assert {row["InterpretationGuardrail"] for row in galaxies} == {
        "source_rule_vs_s_tau1_no_refit"
    }

    text = (PACKET / "predictive_s_tau_velocity_readout.md").read_text(
        encoding="utf-8"
    )
    assert "No coefficients are refit" in text
    assert "weak or mixed result" in text
    assert "radial or kinematic source information" in text


def test_radial_s_tau_rule_is_frozen_and_still_caveated_for_c_systems():
    with (PACKET / "radial_s_tau_rule_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rules = list(csv.DictReader(handle))
    assert len(rules) == 5
    assert {row["AllowedInputs"] for row in rules} == {
        "EvidenceType;Confidence;RadiusFraction;aN_over_a0"
    }
    assert {row["ForbiddenInputs"] for row in rules} == {
        "Vobs;Vbar;Projection_RMS;residuals;S_tau_eff;Class"
    }

    with (PACKET / "radial_s_tau_velocity_metric_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Subset"]: row for row in csv.DictReader(handle)}
    assert rows["all"]["MedianDeltaRMS_RadialMinusS1"] == "-0.010837261"
    assert rows["all"]["FractionGalaxiesImproved"] == "0.555555556"
    assert rows["A"]["MedianDeltaRMS_RadialMinusS1"] == "-0.010837261"
    assert rows["C"]["MedianDeltaRMS_RadialMinusS1"] == "0.006546441"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "radial_velocity_residual_readout_not_refit"
    }

    text = (PACKET / "radial_s_tau_rule_v01.md").read_text(encoding="utf-8")
    assert "does not use `Vobs`, residuals, or `S_tau_eff`" in text
    assert "leakage-controlled radial heuristic" in text


def test_things_source_s_tau_velocity_gate_is_small_overlap_and_no_refit():
    with (PACKET / "path_b_source_only_stau_readout_joined_points.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        source_rows = list(csv.DictReader(handle))
    assert len(source_rows) == 245
    assert {row["ReadoutStatus"] for row in source_rows} == {
        "source_only_bounded_stau_sensitivity_not_model_selection"
    }
    assert {
        row["GalaxyName"] for row in source_rows
    } == {"DDO154", "NGC2366", "NGC2403", "NGC2976", "NGC3198", "NGC5055", "NGC7331"}

    with (PACKET / "things_source_s_tau_velocity_point_readout.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        point_rows = list(csv.DictReader(handle))
    assert len(point_rows) == 245
    assert {row["InterpretationGuardrail"] for row in point_rows} == {
        "things_source_s_tau_velocity_readout_no_refit_not_validation"
    }
    assert max(float(row["JoinRadiusDeltaKpc"]) for row in point_rows) == 0.0

    with (PACKET / "things_source_s_tau_velocity_metric_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Subset"]: row for row in csv.DictReader(handle)}
    assert set(rows) == {"all", "A", "C"}
    assert rows["all"]["NGalaxies"] == "7"
    assert rows["all"]["MedianDeltaRMS_SourcePercentileMinusS1"] == "0.136344406"
    assert rows["all"]["FractionGalaxiesImprovedPercentile"] == "0.285714286"
    assert rows["all"]["MedianDeltaRMS_SourceLogMinusS1"] == "0.207599642"
    assert rows["all"]["FractionGalaxiesImprovedLog"] == "0.000000000"
    assert rows["C"]["MedianDeltaRMS_SourcePercentileMinusS1"] == "0.014173140"
    assert rows["C"]["MedianDeltaRMS_SourceLogMinusS1"] == "0.022111705"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "things_source_s_tau_velocity_readout_no_refit_not_validation"
    }

    text = (PACKET / "things_source_s_tau_velocity_readout.md").read_text(
        encoding="utf-8"
    )
    assert "does not select one by outcome" in text
    assert "not external validation and not a Tau Core proof" in text


def test_things_source_s_tau_failure_audit_explains_direction_without_rule_selection():
    with (PACKET / "things_source_s_tau_failure_point_audit.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        points = list(csv.DictReader(handle))
    assert len(points) == 245
    assert {row["InterpretationGuardrail"] for row in points} == {
        "post_outcome_failure_diagnostic_not_rule_selection"
    }

    with (PACKET / "things_source_s_tau_failure_metric_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Group"]: row for row in csv.DictReader(handle)}
    assert rows["all"]["MedianDeltaAbsError_SourcePercentileMinusS1"] == "0.255945686"
    assert rows["all"]["MedianDeltaAbsError_SourceLogMinusS1"] == "0.528276275"
    assert rows["all"]["FractionPercentileTooLow"] == "0.751020408"
    assert rows["all"]["FractionLogTooLow"] == "0.889795918"
    assert rows["all"]["PearsonStress_EmpiricalS_tau_eff"] == "-0.325117821"
    assert rows["C"]["MedianDeltaAbsError_SourcePercentileMinusS1"] == "-0.127651156"
    assert rows["radius_outer"]["FractionLogTooLow"] == "1.000000000"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "post_outcome_failure_diagnostic_not_rule_selection"
    }

    text = (PACKET / "things_source_s_tau_failure_audit.md").read_text(
        encoding="utf-8"
    )
    assert "must not be used to choose a new rule" in text
    assert "stress magnitude alone is therefore an incomplete proxy" in text


def test_contextual_s_tau_rule_is_conservative_and_hypothesis_generating():
    with (PACKET / "contextual_s_tau_rule_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rules = list(csv.DictReader(handle))
    assert len(rules) == 9
    assert {row["AllowedInputs"] for row in rules} == {
        "RadiusFraction;aN_over_a0;StressDispersionOverRotationScale"
    }
    assert {row["ForbiddenInputs"] for row in rules} == {
        "Vobs;Vbar;residuals;S_tau_eff;Class;outcome_selected_mapping"
    }
    assert {row["InterpretationGuardrail"] for row in rules} == {
        "contextual_s_tau_rule_post_audit_candidate_not_validation"
    }

    with (PACKET / "contextual_s_tau_velocity_point_readout.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        points = list(csv.DictReader(handle))
    assert len(points) == 245
    s_values = [float(row["Predicted_S_tau_contextual_v01"]) for row in points]
    assert min(s_values) >= 0.88
    assert max(s_values) <= 1.12

    with (PACKET / "contextual_s_tau_velocity_metric_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Subset"]: row for row in csv.DictReader(handle)}
    assert rows["all"]["NGalaxies"] == "7"
    assert rows["all"]["MedianDeltaRMS_ContextualMinusS1"] == "0.002491356"
    assert rows["all"]["FractionGalaxiesImproved"] == "0.428571429"
    assert rows["A"]["MedianDeltaRMS_ContextualMinusS1"] == "-0.004336262"
    assert rows["C"]["MedianDeltaRMS_ContextualMinusS1"] == "0.009241461"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "contextual_s_tau_rule_post_audit_candidate_not_validation"
    }

    text = (PACKET / "contextual_s_tau_rule_v01.md").read_text(encoding="utf-8")
    assert "post-audit candidate, not validation" in text
    assert "held-out source-family gate" in text


def test_integrated_tau_drift_supports_history_dependent_diagnostic_gate():
    with (PACKET / "integrated_tau_drift_point_trace_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        points = list(csv.DictReader(handle))
    assert len(points) == 926
    assert {row["InterpretationGuardrail"] for row in points} == {
        "signed_residual_drift_diagnostic_not_predictive_s_tau_rule"
    }

    with (PACKET / "integrated_tau_drift_galaxy_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        galaxies = list(csv.DictReader(handle))
    assert len(galaxies) == 45
    assert {row["InterpretationGuardrail"] for row in galaxies} == {
        "signed_residual_drift_diagnostic_not_predictive_s_tau_rule"
    }

    with (PACKET / "integrated_tau_drift_metric_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {(row["Group"], row["Metric"]): row for row in csv.DictReader(handle)}
    assert rows[("all", "AbsFinalMeanSignedResidual")]["AUC_C_higher"] == "0.783613445"
    assert rows[("all", "MaxAbsCumulativeMeanResidual")]["AUC_C_higher"] == "0.670168067"
    assert rows[("all", "SignImbalance")]["AUC_C_higher"] == "0.685924370"
    assert rows[("all", "MaxSameSignRunFraction")]["AUC_C_higher"] == "0.710084034"
    assert rows[("A", "AbsFinalMeanSignedResidual")]["Median"] == "0.070366381"
    assert rows[("C", "AbsFinalMeanSignedResidual")]["Median"] == "0.173436672"
    assert rows[("A", "MaxSameSignRunFraction")]["Median"] == "0.750000000"
    assert rows[("C", "MaxSameSignRunFraction")]["Median"] == "0.970588235"

    text = (PACKET / "integrated_tau_drift_v01.md").read_text(encoding="utf-8")
    assert "cumulative radial drift rather than pointwise random scatter" in text
    assert "integrated or history-dependent quantity" in text


def test_history_s_tau_rule_uses_inner_residual_history_and_improves_readout():
    with (PACKET / "history_s_tau_rule_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rules = list(csv.DictReader(handle))
    assert len(rules) == 4
    assert {row["AllowedInputs"] for row in rules} == {
        "inner_radius_signed_TPG_residual_history"
    }
    assert {row["ForbiddenInputs"] for row in rules} == {
        "current_point_residual;future_points;S_tau_eff;Class;external_label"
    }
    assert {row["InterpretationGuardrail"] for row in rules} == {
        "causal_inner_residual_history_readout_not_external_prediction"
    }

    with (PACKET / "history_s_tau_velocity_point_readout.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        points = list(csv.DictReader(handle))
    assert len(points) == 926
    s_values = [float(row["Predicted_S_tau_history_v01"]) for row in points]
    assert min(s_values) >= 0.5
    assert max(s_values) <= 1.5
    first_points = [row for row in points if row["PointIndex"] == "1"]
    assert {row["HistoryStatePriorMeanSignedResidual"] for row in first_points} == {
        "0.000000000"
    }

    with (PACKET / "history_s_tau_velocity_metric_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Subset"]: row for row in csv.DictReader(handle)}
    assert rows["all"]["MedianDeltaRMS_HistoryMinusS1"] == "-0.016862038"
    assert rows["all"]["FractionGalaxiesImproved"] == "0.933333333"
    assert rows["A"]["MedianDeltaRMS_HistoryMinusS1"] == "-0.008566997"
    assert rows["A"]["FractionGalaxiesImproved"] == "0.823529412"
    assert rows["C"]["MedianDeltaRMS_HistoryMinusS1"] == "-0.042417618"
    assert rows["C"]["FractionGalaxiesImproved"] == "1.000000000"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "causal_inner_residual_history_readout_not_external_prediction"
    }

    text = (PACKET / "history_s_tau_rule_v01.md").read_text(encoding="utf-8")
    assert "current point residual, future points" in text
    assert "source-side proxy for the history state" in text


def test_tau_core_signal_candidate_is_framed_without_attribution_claim():
    with (PACKET / "tau_core_signal_candidate_galaxy_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        galaxies = list(csv.DictReader(handle))
    assert len(galaxies) == 45
    assert {row["InterpretationGuardrail"] for row in galaxies} == {
        "tau_core_signal_candidate_not_attribution_or_proof"
    }

    with (PACKET / "tau_core_signal_candidate_relation_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Relation"]: row for row in csv.DictReader(handle)}
    assert rows["Projection_RMS__vs__TauCoreSignalCandidateScore_v01"]["Pearson"] == "0.731059386"
    assert rows["Projection_RMS__vs__TauCoreSignalCandidateScore_v01"]["RightAUC_C_higher"] == "0.774159664"
    assert rows["AbsFinalMeanSignedResidual__vs__HistoryImprovement_PositiveIsBetter"]["Pearson"] == "0.954744346"
    assert rows["HistoryImprovement_PositiveIsBetter__vs__TauCoreSignalCandidateScore_v01"]["LeftAUC_C_higher"] == "0.762605042"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "tau_core_signal_candidate_not_attribution_or_proof"
    }

    a_scores = [
        float(row["TauCoreSignalCandidateScore_v01"])
        for row in galaxies
        if row["Class"] == "A"
    ]
    c_scores = [
        float(row["TauCoreSignalCandidateScore_v01"])
        for row in galaxies
        if row["Class"] == "C"
    ]
    assert round(sorted(a_scores)[len(a_scores) // 2], 9) == 0.304545455
    assert round((sorted(c_scores)[13] + sorted(c_scores)[14]) / 2, 9) == 0.579545455

    text = (PACKET / "tau_core_signal_candidate_v01.md").read_text(encoding="utf-8")
    assert "TPG prescription already carries the local Tau Core weights" in text
    assert "It does not identify the residual itself with Tau Core" in text
    assert "environment/observer weights" in text
    assert "Attribution requires external source-side predictors or controls" in text


def test_w_tau_eff_field_seed_closes_branch_without_map_claim():
    with (PACKET / "w_tau_eff_field_seed_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    assert {row["MapReadiness"] for row in rows} == {
        "needs_ra_dec_distance_environment_join"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "w_tau_eff_residual_inferred_seed_not_tau_core_field_map"
    }
    assert {row["CandidateConfidenceTier"] for row in rows} == {
        "high_candidate",
        "medium_candidate",
        "low_or_control_candidate",
    }

    with (PACKET / "w_tau_eff_field_seed_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        summary = {row["Group"]: row for row in csv.DictReader(handle)}
    assert summary["all"]["NGalaxies"] == "45"
    assert summary["all"]["Median_W_tau_eff_candidate_score_v01"] == "0.500000000"
    assert summary["A"]["Median_W_tau_eff_candidate_score_v01"] == "0.304545455"
    assert summary["C"]["Median_W_tau_eff_candidate_score_v01"] == "0.579545455"
    assert summary["all"]["NHighCandidate"] == "12"
    assert summary["A"]["NHighCandidate"] == "2"
    assert summary["C"]["NHighCandidate"] == "10"
    assert {row["InterpretationGuardrail"] for row in summary.values()} == {
        "w_tau_eff_residual_inferred_seed_not_tau_core_field_map"
    }

    text = (PACKET / "w_tau_eff_field_seed_v01.md").read_text(encoding="utf-8")
    assert "TPG`: effective baseline carrying local Tau Core weights" in text
    assert "not claim a Tau Core field map" in text
    assert "RA, Dec, distance, distance uncertainty" in text


def test_w_tau_eff_branch_closure_audit_blocks_premature_mapping_claims():
    with (PACKET / "w_tau_eff_branch_claim_boundary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        claims = {row["ClaimID"]: row for row in csv.DictReader(handle)}
    assert claims["C01"]["Status"] == "supported"
    assert claims["C02"]["Status"] == "supported"
    assert claims["C03"]["Status"] == "supported"
    assert claims["C04"]["Status"] == "not_established"
    assert claims["C05"]["Status"] == "not_established"
    assert "W_tau_eff is the Tau Core field" in claims["C04"]["Claim"]
    assert {row["Guardrail"] for row in claims.values()} == {
        "w_tau_eff_branch_closed_not_map_not_tau_core_proof"
    }

    with (PACKET / "w_tau_eff_branch_failure_modes_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        failures = list(csv.DictReader(handle))
    assert len(failures) == 5
    alternatives = {row["AlternativeExplanation"] for row in failures}
    assert "Non-circular or non-equilibrium gas motions" in alternatives
    assert "Observability and resolution bias" in alternatives
    assert "Inclination and deprojection uncertainty" in alternatives
    assert "Baryonic mass-model mismatch" in alternatives
    assert "Environmental galaxy dynamics rather than observer-weight field" in alternatives

    with (PACKET / "w_tau_eff_branch_next_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert set(gates) == {"G01", "G02", "G03", "G04"}
    assert gates["G01"]["Gate"] == "coordinate_distance_join"
    assert gates["G02"]["Gate"] == "systematics_join"
    assert gates["G03"]["Gate"] == "environment_join"
    assert gates["G04"]["Gate"] == "map_null_tests"
    assert "visual sky maps are treated as evidence without null tests" in gates["G04"]["DoNotProceedIf"]

    text = (PACKET / "w_tau_eff_branch_closure_audit_v01.md").read_text(
        encoding="utf-8"
    )
    assert "Closed for definition and seed generation" in text
    assert "Not closed for Tau Core attribution or field mapping" in text
    assert "not with interpretive sky maps" in text


def test_tau_core_weight_model_gate_freezes_next_model_target():
    with (PACKET / "tau_core_weight_model_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        components = {row["ComponentID"]: row for row in csv.DictReader(handle)}
    assert set(components) == {"M01", "M02", "M03", "M04"}
    assert components["M01"]["Symbol"] == "W_local_TPG(R)"
    assert "local Tau Core weights" in components["M01"]["Definition"]
    assert components["M02"]["Symbol"] == "W_env_obs(R)"
    assert "environment_tuning" in components["M01"]["ForbiddenInputs"]
    assert "current_point_residual" in components["M02"]["ForbiddenInputs"]
    assert {row["Guardrail"] for row in components.values()} == {
        "model_gate_not_fit_not_tau_core_proof"
    }

    with (PACKET / "tau_core_weight_model_evidence_matrix_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        evidence = {row["EvidenceID"]: row for row in csv.DictReader(handle)}
    assert evidence["E01"]["Metric"] == "TauCoreSignalCandidateScore_v01 AUC(C higher)=0.774159664"
    assert "all-galaxy improvement fraction=0.933333333" in evidence["E03"]["Metric"]
    assert evidence["E04"]["Metric"] == "Pearson=0.954744346"

    with (PACKET / "tau_core_weight_model_next_tests_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        tests = {row["TestID"]: row for row in csv.DictReader(handle)}
    assert tests["T01"]["NextTest"] == "source_side_history_proxy"
    assert tests["T02"]["NextTest"] == "systematics_competition"
    assert tests["T03"]["NextTest"] == "map_readiness_join"
    assert tests["T04"]["NextTest"] == "heldout_formula_freeze"
    assert "Predeclared proxy" in tests["T01"]["PassCondition"]

    text = (PACKET / "tau_core_weight_model_gate_v01.md").read_text(
        encoding="utf-8"
    )
    assert "TPG carries local Tau Core weights" in text
    assert "S_tau_full(R)=1+g(W_env_obs(R))" in text
    assert "does not prove Tau Core" in text


def test_source_side_history_proxy_inventory_has_no_endpoint_readout():
    with (PACKET / "source_side_history_proxy_inventory_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["ProxyID"]: row for row in csv.DictReader(handle)}
    assert set(rows) == {"P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09"}
    assert rows["P01"]["ReadinessTier"] == "ready_as_broad_prior"
    assert rows["P07"]["ReadinessTier"] == "ready_for_source_family_holdout"
    assert rows["P03"]["ReadinessTier"] == "ready_for_small_heldout_sanity_check"
    assert rows["P09"]["ReadinessTier"] == "control_required"
    assert rows["P01"]["CoverageGalaxies"] == "73"
    assert rows["P07"]["CoverageGalaxies"] == "14"
    assert "TPG_residual" in rows["P01"]["ForbiddenInputs"]
    assert {row["Guardrail"] for row in rows.values()} == {
        "proxy_inventory_only_no_velocity_endpoint_no_rule_selection"
    }

    with (PACKET / "source_side_history_proxy_readiness_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        readiness = {row["ReadinessTier"]: row for row in csv.DictReader(handle)}
    assert readiness["ready_as_broad_prior"]["ProxyIDs"] == "P01"
    assert readiness["ready_for_source_family_holdout"]["ProxyIDs"] == "P07"
    assert readiness["ready_for_small_heldout_sanity_check"]["ProxyIDs"] == "P03;P04"
    assert readiness["control_required"]["ProxyIDs"] == "P09"

    text = (PACKET / "source_side_history_proxy_inventory_v01.md").read_text(
        encoding="utf-8"
    )
    assert "No velocity endpoint is evaluated here" in text
    assert "Ready broad/holdout proxy IDs: P01, P07" in text
    assert "Do not tune a velocity formula from this inventory" in text


def test_w_env_obs_proxy_design_freezes_roles_and_blocks_velocity_endpoint():
    with (PACKET / "w_env_obs_proxy_design_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        design = {row["DesignID"]: row for row in csv.DictReader(handle)}
    assert design["D01"]["ProxyID"] == "P01"
    assert design["D01"]["Role"] == "primary_broad_prior"
    assert design["D02"]["ProxyID"] == "P07"
    assert design["D02"]["Role"] == "source_family_holdout"
    assert design["D03"]["ProxyID"] == "P03"
    assert design["D04"]["ProxyID"] == "P04"
    assert design["D05"]["ProxyID"] == "P09"
    assert "TPG_residual" in design["D01"]["ForbiddenInputs"]
    assert {row["Guardrail"] for row in design.values()} == {
        "proxy_design_frozen_no_endpoint_readout_no_rule_fitting"
    }

    with (PACKET / "w_env_obs_proxy_rule_freeze_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rules = {row["RuleStep"]: row for row in csv.DictReader(handle)}
    assert rules["R01"]["FrozenChoice"] == "P01_primary"
    assert rules["R02"]["FrozenChoice"] == "direction_only_no_coefficients"
    assert rules["R03"]["FrozenChoice"] == "P07_holdout"
    assert rules["R05"]["FrozenChoice"] == "endpoint_blocked"

    with (PACKET / "w_env_obs_proxy_endpoint_plan_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        endpoints = {row["EndpointGate"]: row for row in csv.DictReader(handle)}
    assert endpoints["E01"]["AllowedAfterThisDesign"] == "yes_next"
    assert endpoints["E02"]["AllowedAfterThisDesign"] == "yes_after_E01"
    assert endpoints["E03"]["AllowedAfterThisDesign"] == "no"
    assert endpoints["E03"]["Endpoint"] == "velocity_readout_with_S_tau_full"

    text = (PACKET / "w_env_obs_proxy_design_v01.md").read_text(encoding="utf-8")
    assert "Primary broad prior: `P01`" in text
    assert "No `S_tau_full` coefficient selection" in text
    assert "No velocity endpoint readout" in text


def test_proxy_direction_vs_w_tau_eff_is_positive_without_velocity_endpoint():
    with (PACKET / "proxy_direction_w_tau_eff_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    assert {row["ReadoutUse"] for row in rows} == {
        "frozen_P01_direction_vs_existing_W_tau_eff_no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "proxy_direction_readout_no_velocity_endpoint_no_coefficient_fit"
    }
    assert {row["P01BurdenTier"] for row in rows} == {"low", "high"}

    with (PACKET / "proxy_direction_w_tau_eff_metric_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "45"
    assert metrics["coverage_scored_low_medium_high"]["SecondaryValue"] == "low=17;medium=0;high=28"
    assert metrics["median_score_low"]["Value"] == "0.304545455"
    assert metrics["median_score_high"]["Value"] == "0.579545455"
    assert metrics["auc_high_vs_low_score"]["Value"] == "0.774159664"
    assert metrics["pearson_ordinal_vs_score"]["Value"] == "0.457880425"
    assert {row["InterpretationGuardrail"] for row in metrics.values()} == {
        "proxy_direction_readout_no_velocity_endpoint_no_coefficient_fit"
    }

    text = (PACKET / "proxy_direction_w_tau_eff_readout_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not evaluate velocity residuals" in text
    assert "AUC high-vs-low score: 0.774159664" in text
    assert "must not be promoted to a velocity formula" in text


def test_p07_whisp_holdout_is_positive_but_small_overlap():
    with (PACKET / "p07_whisp_w_tau_eff_holdout_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 10
    assert {row["ReadoutUse"] for row in rows} == {
        "P07_WHISP_source_family_holdout_no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "p07_source_family_holdout_no_velocity_endpoint_no_coefficient_fit"
    }
    assert {row["WHISP_BurdenSplit"] for row in rows} == {"low", "high"}

    with (PACKET / "p07_whisp_w_tau_eff_holdout_metric_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "10"
    assert metrics["pearson_whisp_burden_vs_w_tau_score"]["Value"] == "0.441950994"
    assert metrics["pearson_whisp_burden_vs_abs_w_tau"]["Value"] == "0.530958640"
    assert metrics["median_score_low_whisp_burden"]["Value"] == "0.231818182"
    assert metrics["median_score_high_whisp_burden"]["Value"] == "0.531818182"
    assert metrics["auc_high_vs_low_whisp_burden"]["Value"] == "0.760000000"

    text = (PACKET / "p07_whisp_w_tau_eff_holdout_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not evaluate velocity residuals" in text
    assert "AUC high-vs-low WHISP burden: 0.760000000" in text
    assert "source-family sanity check rather than a final validation" in text


def test_w_env_obs_systematics_competition_blocks_attribution_until_controls():
    with (PACKET / "w_env_obs_systematics_competition_matrix_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        matrix = {row["ControlID"]: row for row in csv.DictReader(handle)}
    assert set(matrix) == {"S01", "S02", "S03", "S04", "S05", "S06"}
    assert matrix["S01"]["ProxyID"] == "P05"
    assert matrix["S01"]["CurrentReadout"] == (
        "Pearson=0.217454567;AUC=0.333333333;Status=does_not_absorb_direction_in_small_overlap"
    )
    assert matrix["S01"]["Decision"] == "does_not_absorb_direction_in_small_overlap"
    assert matrix["S04"]["ProxyID"] == "P09"
    assert matrix["S04"]["CanCompeteNow"] == "summary_only"
    assert matrix["S04"]["CurrentReadout"] == (
        "ReconstructionRiskAUC=0.750000000;ObserverGeometryAUC=0.389328063;"
        "Status=ordinary_observability_risk_competes_with_signal"
    )
    assert matrix["S04"]["Decision"] == "ordinary_observability_risk_competes_with_signal"
    assert matrix["S05"]["CurrentReadout"] == "AUC=0.774159664"
    assert matrix["S06"]["CurrentReadout"] == "AUC=0.760000000;Pearson=0.441950994"
    assert {row["InterpretationGuardrail"] for row in matrix.values()} == {
        "systematics_competition_no_attribution_no_velocity_endpoint"
    }

    with (PACKET / "w_env_obs_systematics_competition_coverage_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        coverage = {row["Family"]: row for row in csv.DictReader(handle)}
    assert coverage["P01_paper1_external_evidence"]["JoinedWithWTauEff"] == "45"
    assert coverage["P07_WHISP_lopsidedness"]["JoinedWithWTauEff"] == "10"
    assert coverage["P05_THINGS_harmonic_non_circular"]["JoinedWithWTauEff"] == "7"
    assert coverage["P06_LITTLE_THINGS_pressure"]["JoinedWithWTauEff"] == "2"
    assert coverage["P08_HALOGAS_linewidth"]["JoinedWithWTauEff"] == "5"
    assert coverage["P09_inclination_systematics"]["JoinedWithWTauEff"] == "binned_summary"

    with (PACKET / "systematics_control_things_harmonic_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        things = list(csv.DictReader(handle))
    assert len(things) == 7
    assert "MeanAbsResidualProjection" not in things[0]
    assert "MeanAbsResidualMONDSimple" not in things[0]
    assert {row["ControlUse"] for row in things} == {
        "published_harmonic_non_circular_control_only"
    }

    with (PACKET / "systematics_control_halogas_linewidth_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        halogas = list(csv.DictReader(handle))
    assert len(halogas) == 5
    assert "MeanAbsResidualProjection" not in halogas[0]
    assert {row["ControlUse"] for row in halogas} == {
        "external_linewidth_stress_control_only"
    }

    with (PACKET / "w_env_obs_systematics_competition_readiness_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        readiness = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert readiness["D01"]["Status"] == "supported_but_not_attributed"
    assert readiness["D02"]["Status"] == "ordinary_observability_risk_now_primary_blocker"
    assert readiness["D03"]["Status"] == "blocked"
    assert readiness["D04"]["NextAction"] == "distance_resolution_environment_join_before_formula"

    text = (PACKET / "w_env_obs_systematics_competition_v01.md").read_text(
        encoding="utf-8"
    )
    assert "The velocity endpoint remains closed" in text
    assert "not a new positive endpoint" in text


def test_p05_things_non_circular_control_is_small_overlap_and_does_not_absorb_signal():
    with (PACKET / "p05_things_non_circular_w_tau_eff_control_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 7
    assert {row["GalaxyName"] for row in rows} == {
        "DDO154",
        "NGC2366",
        "NGC2403",
        "NGC2976",
        "NGC3198",
        "NGC5055",
        "NGC7331",
    }
    assert {row["ReadoutUse"] for row in rows} == {
        "P05_THINGS_non_circular_control_no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "p05_non_circular_control_no_velocity_endpoint_no_attribution"
    }

    with (PACKET / "p05_things_non_circular_w_tau_eff_control_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "7"
    assert metrics["pearson_p05_burden_vs_w_tau_score"]["Value"] == "0.217454567"
    assert metrics["spearman_p05_burden_vs_w_tau_score"]["Value"] == "0.107142857"
    assert metrics["auc_high_vs_low_p05_burden"]["Value"] == "0.333333333"
    assert metrics["pearson_NonCircularAmplitudeOverVmaxPercent_vs_w_tau_score"]["Value"] == "0.518486407"

    with (PACKET / "p05_things_non_circular_w_tau_eff_control_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["P05D01"]["Status"] == "does_not_absorb_direction_in_small_overlap"
    assert decisions["P05D01"]["NextAction"] == "retain_P05_control_but_proceed_to_P09_observability_join"
    assert decisions["P05D02"]["Status"] == "velocity_endpoint_still_closed"

    text = (PACKET / "p05_things_non_circular_w_tau_eff_control_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not use velocity residuals as predictors" in text
    assert "cannot by itself fit or reject a Tau Core formula" in text


def test_p09_observability_decomposition_keeps_observer_channel_but_flags_reconstruction_risk():
    with (PACKET / "p09_observability_decomposition_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    assert {row["ReadoutUse"] for row in rows} == {
        "P09_observability_decomposition_no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "p09_observability_decomposition_not_bias_erasure_not_attribution"
    }
    assert {row["ResidualBlindCheck"] for row in rows} == {"true"}
    assert {row["Class"] for row in rows} == {"A", "C"}

    with (PACKET / "p09_observability_decomposition_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "45"
    assert metrics["pearson_observer_geometry_vs_w_tau_score"]["Value"] == "-0.225721262"
    assert metrics["auc_high_vs_low_observer_geometry"]["Value"] == "0.389328063"
    assert metrics["pearson_reconstruction_risk_vs_w_tau_score"]["Value"] == "0.289724767"
    assert metrics["spearman_reconstruction_risk_vs_w_tau_score"]["Value"] == "0.333959220"
    assert metrics["auc_high_vs_low_reconstruction_risk"]["Value"] == "0.750000000"
    assert metrics["median_score_by_ReconstructionRiskSplit_high"]["Value"] == "0.659090910"
    assert metrics["median_score_by_ReconstructionRiskSplit_low"]["Value"] == "0.327272727"

    with (PACKET / "p09_observability_decomposition_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["P09D01"]["Status"] == "ordinary_observability_risk_competes_with_signal"
    assert decisions["P09D01"]["NextAction"] == "do_not_open_velocity_endpoint_before_distance_resolution_regression"
    assert decisions["P09D02"]["Status"] == "decompose_observability_do_not_delete_it"

    text = (PACKET / "p09_observability_decomposition_v01.md").read_text(
        encoding="utf-8"
    )
    assert "not as something to erase automatically" in text
    assert "observer geometry should not be dismissed as mere nuisance" in text


def test_distance_resolution_environment_join_keeps_formula_endpoint_closed():
    with (PACKET / "distance_resolution_environment_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    assert {row["ReadoutUse"] for row in rows} == {
        "distance_resolution_environment_join_no_formula_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "distance_resolution_environment_control_no_formula_endpoint"
    }
    assert sum(1 for row in rows if row["EnvironmentCuePresent"] == "true") == 15
    assert {row["Class"] for row in rows} == {"A", "C"}

    with (PACKET / "distance_resolution_environment_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "45"
    assert metrics["environment_cue_coverage"]["Value"] == "15"
    assert metrics["pearson_DistanceMpc_vs_w_tau_score"]["Value"] == "-0.329848302"
    assert metrics["spearman_DistanceMpc_vs_w_tau_score"]["Value"] == "-0.447379969"
    assert metrics["auc_high_vs_low_DistanceSplit"]["Value"] == "0.269762846"
    assert metrics["auc_high_vs_low_AngularRadiusProxySplit"]["Value"] == "0.432806324"
    assert metrics["auc_high_vs_low_ReconstructionRiskSplit"]["Value"] == "0.750000000"
    assert metrics["auc_high_vs_low_EnvMaxThetaSplit"]["Value"] == "0.602040816"

    with (PACKET / "distance_resolution_environment_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["DRE01"]["Status"] == "reconstruction_risk_remains_primary_observability_blocker"
    assert decisions["DRE01"]["NextAction"] == "freeze_multivariable_no_velocity_endpoint_stress_test"
    assert decisions["DRE02"]["Status"] == "velocity_endpoint_still_closed"

    text = (PACKET / "distance_resolution_environment_join_v01.md").read_text(
        encoding="utf-8"
    )
    assert "before any velocity formula is opened" in text
    assert "does not select or validate a Tau Core velocity formula" in text


def test_multivariable_no_velocity_stress_supports_observer_distance_hypothesis_only():
    with (PACKET / "multivariable_no_velocity_stress_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    assert {row["ReadoutUse"] for row in rows} == {
        "observer_distance_tau_candidate_stress_no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "multivariable_stress_no_velocity_endpoint_no_formula_selection"
    }
    assert {row["Class"] for row in rows} == {"A", "C"}

    with (PACKET / "multivariable_no_velocity_stress_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "45"
    assert metrics["pearson_tau_distance_raw_vs_w_tau_score"]["Value"] == "0.404324367"
    assert metrics["auc_nearer_vs_farther_tau_distance_raw"]["Value"] == "0.771739130"
    assert metrics[
        "partial_pearson_tau_distance_after_nuisance_vs_score_after_nuisance"
    ]["Value"] == "0.434416486"
    assert metrics["partial_auc_tau_distance_residual_high_vs_low_score_residual"]["Value"] == "0.662000000"
    assert metrics["nuisance_model_r2_for_w_tau_score"]["Value"] == "0.207747757"

    with (PACKET / "multivariable_no_velocity_stress_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["MV01"]["Status"] == "observer_distance_candidate_survives_nuisance_stress"
    assert decisions["MV01"]["NextAction"] == (
        "freeze_as_hypothesis_not_formula_then_seek_external_environment_distance_validation"
    )
    assert decisions["MV02"]["Status"] == "velocity_endpoint_still_closed"

    text = (PACKET / "multivariable_no_velocity_stress_v01.md").read_text(
        encoding="utf-8"
    )
    assert "without opening a velocity endpoint" in text
    assert "does not establish a Tau Core field" in text


def test_observer_distance_hypothesis_gate_freezes_claim_boundary_and_validation_plan():
    with (PACKET / "observer_distance_hypothesis_claim_boundary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        claims = {row["ClaimID"]: row for row in csv.DictReader(handle)}
    assert set(claims) == {"ODC01", "ODC02", "ODC03", "ODC04"}
    assert claims["ODC01"]["Status"] == "supported_as_in_sample_hypothesis"
    assert claims["ODC01"]["Evidence"] == "raw Pearson=0.404324367; raw AUC=0.771739130"
    assert claims["ODC02"]["Status"] == "supported_as_stress_survival"
    assert claims["ODC02"]["Evidence"] == (
        "partial Pearson=0.434416486; partial AUC=0.662000000; "
        "nuisance-only R2=0.207747757"
    )
    assert claims["ODC03"]["Status"] == "not_established"
    assert claims["ODC04"]["Status"] == "blocked"
    assert "velocity formula" in claims["ODC01"]["ForbiddenWording"]
    assert "formula validation" in claims["ODC04"]["ForbiddenWording"]
    assert {row["InterpretationGuardrail"] for row in claims.values()} == {
        "observer_distance_hypothesis_only_no_formula_no_tau_core_proof"
    }

    with (PACKET / "observer_distance_hypothesis_validation_plan_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        validation = {row["ValidationID"]: row for row in csv.DictReader(handle)}
    assert set(validation) == {"ODV01", "ODV02", "ODV03", "ODV04"}
    assert validation["ODV01"]["Target"] == "WHISP overlap"
    assert validation["ODV02"]["EndpointPermission"] == "no_velocity_endpoint"
    assert validation["ODV04"]["EndpointPermission"] == "blocked_until_external_validation"

    with (PACKET / "observer_distance_hypothesis_readiness_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        readiness = {row["ReadinessID"]: row for row in csv.DictReader(handle)}
    assert readiness["ODR01"]["Status"] == "yes_with_guardrails"
    assert readiness["ODR02"]["Status"] == "no"
    assert readiness["ODR03"]["NextAction"] == "observer_distance_external_validation_readout"

    text = (PACKET / "observer_distance_hypothesis_gate_v01.md").read_text(
        encoding="utf-8"
    )
    assert "hypothesis-level result only" in text
    assert "does not claim a Tau Core field detection" in text
    assert "At least one external source-family validation" in text


def test_observer_distance_whisp_external_validation_is_guardrailed():
    with (PACKET / "observer_distance_whisp_external_validation_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 10
    assert {row["Class"] for row in rows} == {"C"}
    assert {row["ReadoutUse"] for row in rows} == {
        "WHISP_observer_distance_external_validation_no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "whisp_external_validation_no_velocity_endpoint_no_formula_selection"
    }

    with (PACKET / "observer_distance_whisp_external_validation_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "10"
    assert metrics["class_coverage"]["Value"] == "C"
    assert metrics["pearson_tau_distance_raw_vs_w_tau_score"]["Value"] == "0.167726020"
    assert metrics["auc_nearer_vs_farther_tau_distance_raw"]["Value"] == "0.560000000"
    assert (
        metrics["partial_pearson_tau_distance_after_whisp_controls"]["Value"]
        == "-0.224079320"
    )
    assert metrics["partial_auc_tau_distance_after_whisp_controls"]["Value"] == "0.360000000"

    with (PACKET / "observer_distance_whisp_external_validation_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["ODW01"]["Status"] == (
        "direction_not_reproduced_in_small_whisp_overlap"
    )
    assert decisions["ODW01"]["NextAction"] == (
        "do_not_promote_observer_distance_hypothesis_before_other_external_checks"
    )
    assert decisions["ODW02"]["Status"] == "velocity_endpoint_still_closed"

    text = (PACKET / "observer_distance_whisp_external_validation_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not open a velocity endpoint" in text
    assert "not class-balanced" in text
    assert "cannot validate a Tau Core field or velocity formula" in text


def test_external_validation_status_board_closes_observer_distance_endpoint():
    with (PACKET / "external_validation_status_board_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["FamilyID"]: row for row in csv.DictReader(handle)}
    assert set(rows) == {"P07", "ODW", "P05", "P06", "P08"}
    assert rows["P07"]["Status"] == "positive_small_source_family_sanity_check"
    assert rows["P07"]["PrimaryMetric"] == "AUC=0.760000000;Pearson=0.441950994"
    assert rows["ODW"]["Status"] == "direction_not_reproduced_in_small_whisp_overlap"
    assert rows["ODW"]["PrimaryMetric"] == (
        "rawPearson=0.167726020;partialPearson=-0.224079320;partialAUC=0.360000000"
    )
    assert rows["P05"]["Status"] == "does_not_absorb_direction_in_small_overlap"
    assert rows["P06"]["Status"] == "too_small_for_directional_validation"
    assert rows["P08"]["Status"] == "weak_small_overlap_control_only"
    assert {row["EndpointPermission"] for row in rows.values()} == {
        "no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "external_validation_status_no_velocity_endpoint_no_tau_core_claim"
    }

    with (PACKET / "external_validation_status_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["EVS01"]["Status"] == (
        "mixed_external_validation_supporting_w_tau_direction_not_observer_distance"
    )
    assert decisions["EVS01"]["NextAction"] == (
        "prioritize_non_whisp_THINGS_LITTLE_THINGS_HALOGAS_expansion_before_formula"
    )
    assert decisions["EVS02"]["Status"] == "closed"

    text = (PACKET / "external_validation_status_board_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not open a velocity endpoint" in text
    assert "does not claim a Tau Core field detection" in text
    assert "not for the observer-distance interpretation" in text


def test_public_package_is_english_only():
    public_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [
            ROOT / "README.md",
            ROOT / "DATA_NOTICE.md",
            PACKET / "paper2_manuscript_skeleton.md",
            PACKET / "paper2_manuscript_draft.md",
            PACKET / "packet_manifest.json",
        ]
    )
    assert "_hu." not in public_text
    assert "laikusan" not in public_text.lower()
