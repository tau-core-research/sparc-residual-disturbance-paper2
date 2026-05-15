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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_slim_publication_files_exist():
    required = [
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "CITATION.cff",
        ROOT / "DATA_NOTICE.md",
        ROOT / "requirements.txt",
        ROOT / "paper2_submission_source/main.tex",
        ROOT / "paper2_submission_source/references.bib",
        ROOT / "paper2_submission_source/main.pdf",
        ROOT / "paper2_submission_source/figures/paper2_projection_rms_distribution.pdf",
        ROOT / "paper2_submission_source/figures/paper2_baseline_auc_comparison.pdf",
        ROOT / "paper2_submission_source/figures/paper2_error_audit.pdf",
        ROOT / "paper2_submission_source/figures/paper2_confusion_matrix.pdf",
        ROOT / "paper2_submission_source/figures/paper2_projection_roc.pdf",
        ROOT / "paper2_submission_source/figures/paper2_distance_stress.pdf",
        ROOT / "paper2_submission_source/figures/paper2_auc_stability_distributions.pdf",
        ROOT / "figures/README.md",
        STUDY / "README.md",
        STUDY / "make_paper2_submission_source_v01.py",
        PACKET / "README.md",
        PACKET / "packet_manifest.json",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_retained_final_packet_inputs_and_outputs_exist():
    required = [
        PACKET / "residual_feature_table.csv",
        PACKET / "paper2_external_proxy_summary_v03.csv",
        PACKET / "paper2_b_class_policy.csv",
        PACKET / "multivariable_no_velocity_stress_metrics_v01.csv",
        PACKET / "paper2_calibration_uncertainty.csv",
        PACKET / "residual_inference_projection_rms_error_audit.csv",
        PACKET / "residual_inference_loogo_predictions.csv",
        PACKET / "paper2_observability_stress.csv",
        PACKET / "distance_resolution_environment_join_v01.csv",
        PACKET / "p09_observability_decomposition_join_v01.csv",
        PACKET / "paper2_figure_typography_audit_v01.md",
        PACKET / "paper2_figure_typography_audit_v01.csv",
        PACKET / "paper2_submission_source_gate_v01.csv",
        PACKET / "paper2_submission_readiness_v02.md",
        PACKET / "paper2_submission_readiness_v02.csv",
        PACKET / "paper2_ac_sample_appendix_v01.csv",
        PACKET / "paper2_baseline_auc_ci_v01.csv",
        PACKET / "paper2_external_proxy_gate_table_v01.csv",
        PACKET / "paper2_b_class_sensitivity_v01.csv",
        PACKET / "paper2_observability_covariate_appendix_v01.csv",
        PACKET / "paper2_outlier_failure_case_appendix_v01.csv",
        PACKET / "paper2_stability_effect_size_v01.csv",
        PACKET / "paper2_final_metric_table.csv",
        PACKET / "paper2_readiness_table.csv",
        PACKET / "paper2_claim_boundary.csv",
        PACKET / "paper2_external_validation_status_board_v02.md",
        PACKET / "paper2_external_validation_status_board_v02.csv",
        PACKET / "paper2_claim_boundary_v02.csv",
        PACKET / "paper2_readiness_table_v02.csv",
        PACKET / "paper2_next_step_decision_v02.csv",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_derived_paper1_inputs_exist_without_raw_sparc_files():
    required = [
        PAPER1_INPUTS / "taucore_specificity_point_map.csv",
        PAPER1_INPUTS / "baseline_score_by_galaxy.csv",
        PAPER1_INPUTS / "scale_matched_pairs.csv",
        PAPER1_INPUTS / "scale_matched_stress.csv",
        PAPER1_INPUTS / "external_evidence_table.csv",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_submission_source_contains_final_claim_boundaries():
    tex = (ROOT / "paper2_submission_source/main.tex").read_text(encoding="utf-8")
    bib = (ROOT / "paper2_submission_source/references.bib").read_text(encoding="utf-8")

    assert "\\bibliography{references}" in tex
    assert "not a Tau Core validation claim" in tex
    assert "Forbidden claims: Tau Core validation" in tex
    assert "The projection-family score is treated operationally" in tex
    assert "The strongest remaining weakness is external validation" in tex
    assert "it is not yet externally established" in tex
    assert "\\section{Conclusion}" in tex
    assert "The next decisive test is a held-out external source-family replication" in tex
    assert "Stability and effect-size appendix" in tex
    assert "CamB is the most important failure case" in tex
    assert "Working submission candidate" not in tex

    assert "Lelli2016SPARC" in bib
    assert "Trachternach2008THINGS" in bib
    assert "Reynolds2020HIAsymmetries" in bib
    assert "Yu2022ALFALFA" in bib


def test_final_metrics_are_reproducible_and_guardrailed():
    metrics = {row["Metric"]: row for row in read_csv(PACKET / "paper2_final_metric_table.csv")}
    assert metrics["Projection_RMS_LOOGO"]["Value"] == "0.771008403"
    assert metrics["Projection_RMS_shuffle_null_p"]["Value"] == "0.002000000"
    assert metrics["Newtonian_Baryonic_RMS_LOOGO_AUC"]["Value"] == "0.506302521"

    gates = {row["GateID"]: row for row in read_csv(PACKET / "paper2_submission_source_gate_v01.csv")}
    assert gates["P2SRC01"]["Status"] == "latex_source_generated"
    assert gates["P2SRC02"]["Status"] == "bibliography_generated"
    assert gates["P2SRC03"]["Status"] == "figures_audited_publication_candidate"
    assert gates["P2SRC04"]["Status"] == "pdf_compiled_with_tectonic"
    assert {row["BlocksSubmission"] for row in gates.values()} == {"no"}
    assert {row["CanClaimTauValidation"] for row in gates.values()} == {"no"}


def test_appendix_tables_capture_outlier_and_stability_checks():
    outliers = {row["GalaxyName"]: row for row in read_csv(PACKET / "paper2_outlier_failure_case_appendix_v01.csv")}
    assert outliers["CamB"]["Projection_RMS"] == "0.963585384"
    assert outliers["CamB"]["NPoints"] == "9"
    assert outliers["CamB"]["ErrorFamily"] == "false_positive_A_as_C"

    stability = {row["Metric"]: row for row in read_csv(PACKET / "paper2_stability_effect_size_v01.csv")}
    assert stability["mann_whitney_u_c_higher"]["Value"] == "367.000000000"
    assert stability["cliffs_delta_c_higher"]["Value"] == "0.542016807"
    assert stability["auc_without_CamB"]["Value"] == "0.819196429"

    figures = read_csv(PACKET / "paper2_figure_typography_audit_v01.csv")
    assert len(figures) == 7
    assert {row["VectorExport"] for row in figures} == {"pdf"}


def test_repo_is_slim_and_raw_data_free():
    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    assert len(tracked) <= 70
    assert not any(path.startswith("data/raw/") for path in tracked)
    assert not any(path.startswith("data/sparc/Rotmod_LTG/") for path in tracked)
    assert not any("tau_core_signal_candidate" in path for path in tracked)
    assert not any("things_route2_primary_input" in path for path in tracked)
    assert not any("yu2022_alfalfa_profile_asymmetry_catalog" in path for path in tracked)


def test_public_package_text_is_english_only():
    public_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [
            ROOT / "README.md",
            ROOT / "DATA_NOTICE.md",
            ROOT / "paper2_submission_source/main.tex",
            ROOT / "paper2_submission_source/references.bib",
            PACKET / "README.md",
            PACKET / "paper2_submission_readiness_v02.md",
            PACKET / "packet_manifest.json",
        ]
    )
    assert "_hu." not in public_text
    assert "laikusan" not in public_text.lower()
