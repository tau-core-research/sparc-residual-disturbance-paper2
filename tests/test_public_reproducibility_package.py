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
        PACKET / "paper2_final_metric_table.csv",
        PACKET / "paper2_readiness_table.csv",
        PACKET / "paper2_figure_plan.csv",
        PACKET / "paper2_claim_boundary.csv",
        PACKET / "paper2_related_work.md",
        PACKET / "paper2_validation_controls.md",
        PACKET / "paper2_calibration_policy.md",
        PACKET / "residual_feature_table.csv",
        PACKET / "residual_disturbance_score_v01.csv",
        PACKET / "residual_inference_loogo_metric_summary.csv",
        PACKET / "residual_inference_projection_rms_error_audit.csv",
        PACKET / "residual_inference_projection_rms_error_summary.csv",
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


def test_public_package_is_english_only():
    public_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [
            ROOT / "README.md",
            ROOT / "DATA_NOTICE.md",
            PACKET / "paper2_manuscript_skeleton.md",
            PACKET / "packet_manifest.json",
        ]
    )
    assert "_hu." not in public_text
    assert "laikusan" not in public_text.lower()
