#!/usr/bin/env python3
"""Build Paper 2 manuscript skeleton and final summary tables."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from make_packet_v01_seed import PACKET


FINAL_METRICS_CSV = PACKET / "paper2_final_metric_table.csv"
READINESS_CSV = PACKET / "paper2_readiness_table.csv"
FIGURE_PLAN_CSV = PACKET / "paper2_figure_plan.csv"
SKELETON = PACKET / "paper2_manuscript_skeleton.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_final_metrics() -> list[dict[str, str]]:
    loogo = {
        row["Predictor"]: row
        for row in read_csv(PACKET / "residual_inference_loogo_metric_summary.csv")
    }
    baseline = {
        row["Predictor"]: row
        for row in read_csv(PACKET / "paper2_baseline_family_loogo.csv")
    }
    calibration = read_csv(PACKET / "paper2_calibration_uncertainty.csv")[0]
    null = read_csv(PACKET / "paper2_shuffled_label_null.csv")[0]
    newtonian = {
        row["Predictor"]: row
        for row in read_csv(PACKET / "paper2_newtonian_scope.csv")
    }
    b_policy = read_csv(PACKET / "paper2_b_class_policy.csv")[0]
    stress = {
        row["StressTest"]: row
        for row in read_csv(PACKET / "paper2_observability_stress.csv")
    }

    rows = [
        {
            "TableID": "T1_primary_projection_rms",
            "Metric": "Projection_RMS_LOOGO",
            "Value": loogo["Projection_RMS"]["AUC_C_higher"],
            "SecondaryValue": f"accuracy={loogo['Projection_RMS']['Accuracy']}",
            "UseInManuscript": "primary_result",
            "Guardrail": "diagnostic_class_recovery_not_tau_core_validation",
        },
        {
            "TableID": "T1_primary_projection_rms",
            "Metric": "Projection_RMS_bootstrap_auc_ci95",
            "Value": calibration["AUC_CI95Low"],
            "SecondaryValue": calibration["AUC_CI95High"],
            "UseInManuscript": "sample_size_uncertainty",
            "Guardrail": "bootstrap_uncertainty_not_external_validation",
        },
        {
            "TableID": "T1_primary_projection_rms",
            "Metric": "Projection_RMS_shuffle_null_p",
            "Value": null["EmpiricalP_AUC_ge_observed"],
            "SecondaryValue": f"null_p95_auc={null['NullP95AUC']}",
            "UseInManuscript": "random_label_null",
            "Guardrail": "shuffle_null_not_independent_validation",
        },
        {
            "TableID": "T2_baseline_family",
            "Metric": "MOND_RMS_LOOGO_AUC",
            "Value": baseline["MOND_RMS"]["AUC_C_higher"],
            "SecondaryValue": f"accuracy={baseline['MOND_RMS']['Accuracy']}",
            "UseInManuscript": "baseline_family_comparison",
            "Guardrail": "not_projection_uniqueness",
        },
        {
            "TableID": "T2_baseline_family",
            "Metric": "RAR_RMS_LOOGO_AUC",
            "Value": baseline["RAR_RMS"]["AUC_C_higher"],
            "SecondaryValue": f"accuracy={baseline['RAR_RMS']['Accuracy']}",
            "UseInManuscript": "baseline_family_comparison",
            "Guardrail": "not_projection_uniqueness",
        },
        {
            "TableID": "T2_baseline_family",
            "Metric": "Newtonian_Baryonic_RMS_LOOGO_AUC",
            "Value": newtonian["Newtonian_Baryonic_RMS"]["AUC_C_higher"],
            "SecondaryValue": f"accuracy={newtonian['Newtonian_Baryonic_RMS']['Accuracy']}",
            "UseInManuscript": "scope_control",
            "Guardrail": "not_low_acceleration_specificity_proof",
        },
        {
            "TableID": "T3_observability_stress",
            "Metric": "distance_matched_greedy_fraction_c_higher",
            "Value": stress["sparc_distance_greedy_unique_matched_pairs"]["FractionPairs_C_higher"],
            "SecondaryValue": f"n_pairs={stress['sparc_distance_greedy_unique_matched_pairs']['NPairs']}",
            "UseInManuscript": "observability_caveat",
            "Guardrail": "distance_matching_not_full_selection_function",
        },
        {
            "TableID": "T3_observability_stress",
            "Metric": "distance_strict_caliper_median_diff",
            "Value": stress["sparc_distance_mpc_matched_pairs_caliper"]["MedianPairedDiff_C_minus_A"],
            "SecondaryValue": f"n_pairs={stress['sparc_distance_mpc_matched_pairs_caliper']['NPairs']}",
            "UseInManuscript": "observability_caveat",
            "Guardrail": "strict_caliper_small_n",
        },
        {
            "TableID": "T4_b_policy",
            "Metric": "B_class_projection_threshold_split",
            "Value": b_policy["BPredictedC_like"],
            "SecondaryValue": f"A_like={b_policy['BPredictedA_like']}; threshold={b_policy['ProjectionRMSThreshold']}",
            "UseInManuscript": "descriptive_uncertainty_band",
            "Guardrail": "do_not_train_on_b_as_truth",
        },
    ]
    return rows


def build_readiness_rows() -> list[dict[str, str]]:
    return [
        {
            "Gate": "Primary diagnostic",
            "Status": "ready_with_caveats",
            "Evidence": "Projection_RMS_LOOGO_AUC_0.771_accuracy_0.756_shuffle_p_0.002_bootstrap_ci_0.601_0.909",
            "ManuscriptAction": "report_as_residual_shape_diagnostic_not_physical_proof",
        },
        {
            "Gate": "Baseline specificity",
            "Status": "ready_as_non_unique_low_acceleration_family_result",
            "Evidence": "MOND_RMS_AUC_0.721_RAR_RMS_AUC_0.731_Newtonian_AUC_0.506",
            "ManuscriptAction": "state_that_projection_is_not_unique_and_newtonian_is_scope_control",
        },
        {
            "Gate": "Observability",
            "Status": "caveated_not_solved",
            "Evidence": "distance_matched_fraction_C_higher_0.647_strict_caliper_N13_effect_0.119",
            "ManuscriptAction": "keep_as_major_limitation_and_phase_ii_requirement",
        },
        {
            "Gate": "B-class use",
            "Status": "policy_frozen",
            "Evidence": "13_of_28_B_score_C_like_under_projection_threshold",
            "ManuscriptAction": "use_only_as_uncertainty_band_or_candidate_prioritization",
        },
        {
            "Gate": "External validation",
            "Status": "not_yet_available",
            "Evidence": "HALOGAS_H07_closed_as_weak_non_specific_control",
            "ManuscriptAction": "present_as_future_work_not_as_current_evidence",
        },
    ]


def build_figure_plan_rows() -> list[dict[str, str]]:
    return [
        {
            "FigureID": "F1",
            "Content": "Projection_RMS distributions for A and C classes with threshold",
            "SourceFiles": "residual_feature_table.csv;paper2_calibration_uncertainty.csv",
            "Purpose": "show_primary_class_separation",
            "RequiredBeforeSubmission": "yes",
        },
        {
            "FigureID": "F2",
            "Content": "AUC comparison across Projection, MOND, RAR, and Newtonian residual families",
            "SourceFiles": "paper2_baseline_family_loogo.csv;paper2_newtonian_scope.csv",
            "Purpose": "show_low_acceleration_family_not_projection_uniqueness",
            "RequiredBeforeSubmission": "yes",
        },
        {
            "FigureID": "F3",
            "Content": "Confusion/error audit with false-positive A-as-C and false-negative C-as-A galaxies",
            "SourceFiles": "residual_inference_projection_rms_error_audit.csv;residual_inference_projection_rms_error_summary.csv",
            "Purpose": "make_failure_modes_reviewable",
            "RequiredBeforeSubmission": "yes",
        },
        {
            "FigureID": "F4",
            "Content": "Distance-matched stress summary",
            "SourceFiles": "paper2_observability_stress.csv",
            "Purpose": "show_observability_caveat_transparently",
            "RequiredBeforeSubmission": "optional_if_table_is_clear",
        },
    ]


def write_skeleton(
    final_metrics: list[dict[str, str]],
    readiness: list[dict[str, str]],
) -> None:
    metric = {row["Metric"]: row for row in final_metrics}
    readiness_by_gate = {row["Gate"]: row for row in readiness}
    lines = [
        "# Paper 2 Manuscript Skeleton",
        "",
        "Working title: Residual-shape inference of structural disturbance in SPARC rotation curves: a diagnostic audit",
        "",
        "## Abstract Skeleton",
        "",
        "We test whether fixed rotation-curve residual-shape features can recover externally reviewed A/C disturbance labels in the SPARC sample. The primary predeclared diagnostic is `Projection_RMS`, evaluated with leave-one-galaxy-out thresholding, shuffled-label null tests, bootstrap uncertainty, baseline-family comparisons, and distance-matched stress checks. The current result is a diagnostic association, not a Tau Core validation claim and not a unique projection-model selection result.",
        "",
        "## Main Result",
        "",
        f"- `Projection_RMS` LOOGO AUC: {metric['Projection_RMS_LOOGO']['Value']} ({metric['Projection_RMS_LOOGO']['SecondaryValue']})",
        f"- Bootstrap 95% AUC interval: [{metric['Projection_RMS_bootstrap_auc_ci95']['Value']}, {metric['Projection_RMS_bootstrap_auc_ci95']['SecondaryValue']}]",
        f"- Shuffled-label empirical p: {metric['Projection_RMS_shuffle_null_p']['Value']} ({metric['Projection_RMS_shuffle_null_p']['SecondaryValue']})",
        "",
        "## Baseline-Family Result",
        "",
        f"- MOND RMS LOOGO AUC: {metric['MOND_RMS_LOOGO_AUC']['Value']}",
        f"- RAR RMS LOOGO AUC: {metric['RAR_RMS_LOOGO_AUC']['Value']}",
        f"- Newtonian baryonic RMS LOOGO AUC: {metric['Newtonian_Baryonic_RMS_LOOGO_AUC']['Value']}",
        "",
        "Interpretation: the separation is strongest in low-acceleration residual-family scores and is not established as projection-formula uniqueness.",
        "",
        "## Observability and B-Class Policy",
        "",
        f"- Distance-matched C-higher fraction: {metric['distance_matched_greedy_fraction_c_higher']['Value']} ({metric['distance_matched_greedy_fraction_c_higher']['SecondaryValue']})",
        f"- Strict distance-caliper median difference: {metric['distance_strict_caliper_median_diff']['Value']} ({metric['distance_strict_caliper_median_diff']['SecondaryValue']})",
        f"- B-class threshold split: {metric['B_class_projection_threshold_split']['Value']} C-like ({metric['B_class_projection_threshold_split']['SecondaryValue']})",
        "",
        "B galaxies are not used as primary training or validation truth. They may be used only as an uncertainty band or as a prioritized list for future external review.",
        "",
        "## Proposed Manuscript Sections",
        "",
        "1. Introduction: residual-shape diagnostics and non-circular disturbance context.",
        "2. Data and labels: SPARC A/C labels inherited from the frozen Paper 1 evidence packet.",
        "3. Residual features: fixed score-table features and predeclared `Projection_RMS` baseline.",
        "4. Validation design: LOOGO thresholding, shuffled-label null, bootstrap uncertainty.",
        "5. Results: primary diagnostic, baseline families, Newtonian scope control.",
        "6. Error audit: false-positive and false-negative systems without residual relabeling.",
        "7. Observability stress: distance-matched controls and unresolved selection-function caveat.",
        "8. B-class uncertainty band and candidate prioritization.",
        "9. Discussion: diagnostic value, limitations, and Phase II external validation.",
        "",
        "## Readiness Summary",
        "",
    ]
    for gate, row in readiness_by_gate.items():
        lines.append(f"- {gate}: {row['Status']} -- {row['ManuscriptAction']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Allowed: fixed residual-shape features recover externally reviewed A/C disturbance class better than chance in the current SPARC packet, with important observability caveats.",
            "",
            "Forbidden: Tau Core validation, projection-model uniqueness, replacement of external labels by residual-only labels, or claim of independent external validation.",
            "",
            "## Next Gate",
            "",
            "Generate publication-grade figures and a first full manuscript draft from this skeleton.",
        ]
    )
    SKELETON.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_outline() -> None:
    outline = PACKET / "paper2_cautious_outline.md"
    text = outline.read_text(encoding="utf-8")
    text = text.replace(
        "## Paper-Grade Missing Pieces\n\n"
        "- Add shuffled-label null distribution for the LOOGO primary baseline.\n"
        "- Add distance/radius/mass observability stress tests for the classifier score.\n"
        "- Add baseline-family comparison table for Projection, MOND-simple, RAR, and Newtonian features.\n"
        "- Freeze whether B-class galaxies are excluded, held out, or used only as an uncertainty set.\n"
        "- Report calibration and uncertainty, not only AUC/accuracy.",
        "## Paper-Grade Status\n\n"
        "- Shuffled-label null distribution is available for the LOOGO primary baseline.\n"
        "- First distance-matched observability stress tests are available, but selection-function control remains incomplete.\n"
        "- Baseline-family comparison is available for Projection, MOND-simple, RAR, and Newtonian features.\n"
        "- B-class policy is frozen: exclude from primary A/C training and validation; use only as an uncertainty band.\n"
        "- Calibration uncertainty is available through bootstrap AUC intervals.",
    )
    outline.write_text(text, encoding="utf-8")


def update_readme() -> None:
    readme = PACKET / "README.md"
    text = readme.read_text(encoding="utf-8")
    replacement = (
        "paper-grade claim remains bounded by shuffled-label null tests,\n"
        "observability stress tests, baseline-family comparisons, calibration\n"
        "uncertainty, and the frozen B-class policy.\n\n"
        "The current next gate is a publication-grade figure set and a first full\n"
        "Paper 2 manuscript draft from `paper2_manuscript_skeleton.md`.\n"
    )
    old = (
        "paper-grade claim remains blocked until shuffled-label null tests,\n"
        "observability stress tests, and baseline-family comparisons are added.\n"
    )
    if old in text:
        text = text.replace(old, replacement)
    readme.write_text(text, encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "paper2_final_metric_table.csv",
            "paper2_readiness_table.csv",
            "paper2_figure_plan.csv",
            "paper2_manuscript_skeleton.md",
        }
    )
    manifest["files"] = sorted(files)
    manifest["paper2_manuscript_packet_status"] = (
        "skeleton_final_tables_and_figure_plan_ready"
    )
    manifest["paper2_next_gate"] = "publication_grade_figures_and_full_draft"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    final_metrics = build_final_metrics()
    readiness = build_readiness_rows()
    figure_plan = build_figure_plan_rows()
    write_csv(
        FINAL_METRICS_CSV,
        final_metrics,
        ["TableID", "Metric", "Value", "SecondaryValue", "UseInManuscript", "Guardrail"],
    )
    write_csv(
        READINESS_CSV,
        readiness,
        ["Gate", "Status", "Evidence", "ManuscriptAction"],
    )
    write_csv(
        FIGURE_PLAN_CSV,
        figure_plan,
        ["FigureID", "Content", "SourceFiles", "Purpose", "RequiredBeforeSubmission"],
    )
    write_skeleton(final_metrics, readiness)
    update_outline()
    update_readme()
    update_manifest()
    print(SKELETON)
    print("paper2_manuscript_packet=4")


if __name__ == "__main__":
    main()
