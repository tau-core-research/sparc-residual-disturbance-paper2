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
