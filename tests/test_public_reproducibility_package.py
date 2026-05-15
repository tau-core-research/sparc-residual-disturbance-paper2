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
