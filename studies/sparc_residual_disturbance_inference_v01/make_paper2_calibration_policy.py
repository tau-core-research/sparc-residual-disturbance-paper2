#!/usr/bin/env python3
"""Add Paper 2 calibration, B-class policy, and Newtonian baseline scope."""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path

from make_packet_v01_seed import PACKET


ROOT = Path(__file__).resolve().parents[2]
PAPER1_PACKET = ROOT / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced"
FEATURES_CSV = PACKET / "residual_feature_table.csv"
BASELINE_BY_GALAXY = PAPER1_PACKET / "baseline_score_by_galaxy.csv"

CALIBRATION_CSV = PACKET / "paper2_calibration_uncertainty.csv"
B_POLICY_CSV = PACKET / "paper2_b_class_policy.csv"
NEWTONIAN_CSV = PACKET / "paper2_newtonian_scope.csv"
REPORT = PACKET / "paper2_calibration_policy.md"

PRIMARY = "Projection_RMS"
RANDOM_SEED = 20260516
N_BOOTSTRAPS = 2000


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    if n % 2:
        return ordered[n // 2]
    return (ordered[n // 2 - 1] + ordered[n // 2]) / 2


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[int(position)]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def auc(labels: list[int], scores: list[float]) -> float:
    positives = [score for label, score in zip(labels, scores) if label == 1]
    negatives = [score for label, score in zip(labels, scores) if label == 0]
    wins = 0.0
    total = 0
    for pos in positives:
        for neg in negatives:
            total += 1
            if pos > neg:
                wins += 1
            elif pos == neg:
                wins += 0.5
    return wins / total if total else math.nan


def fmt(value: float) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.9f}"


def ac_feature_rows() -> list[dict[str, str]]:
    return [row for row in read_csv(FEATURES_CSV) if row["Class"] in {"A", "C"}]


def primary_threshold(rows: list[dict[str, str]]) -> float:
    a_values = [float(row[PRIMARY]) for row in rows if row["Class"] == "A"]
    c_values = [float(row[PRIMARY]) for row in rows if row["Class"] == "C"]
    return (median(a_values) + median(c_values)) / 2


def build_calibration_rows() -> list[dict[str, str]]:
    rows = ac_feature_rows()
    labels = [1 if row["Class"] == "C" else 0 for row in rows]
    scores = [float(row[PRIMARY]) for row in rows]
    observed_auc = auc(labels, scores)
    threshold = primary_threshold(rows)
    predictions = ["C" if score > threshold else "A" for score in scores]
    accuracy = sum(pred == row["Class"] for pred, row in zip(predictions, rows)) / len(rows)
    rng = random.Random(RANDOM_SEED)
    boot_aucs: list[float] = []
    for _ in range(N_BOOTSTRAPS):
        sample = [rows[rng.randrange(len(rows))] for _ in rows]
        sample_labels = [1 if row["Class"] == "C" else 0 for row in sample]
        if len(set(sample_labels)) < 2:
            continue
        sample_scores = [float(row[PRIMARY]) for row in sample]
        boot_aucs.append(auc(sample_labels, sample_scores))
    return [
        {
            "CalibrationID": "projection_rms_auc_bootstrap",
            "Predictor": PRIMARY,
            "NGalaxies": str(len(rows)),
            "ObservedAUC": fmt(observed_auc),
            "BootstrapN": str(N_BOOTSTRAPS),
            "RandomSeed": str(RANDOM_SEED),
            "AUC_CI95Low": fmt(percentile(boot_aucs, 0.025)),
            "AUC_CI95High": fmt(percentile(boot_aucs, 0.975)),
            "Threshold": fmt(threshold),
            "ThresholdAccuracyInSample": fmt(accuracy),
            "InterpretationGuardrail": "bootstrap_uncertainty_not_external_validation",
        }
    ]


def baseline_rows_by_score(score: str) -> list[dict[str, str]]:
    return [row for row in read_csv(BASELINE_BY_GALAXY) if row["Score"] == score]


def build_b_policy_rows() -> list[dict[str, str]]:
    rows = baseline_rows_by_score("projection_fixed")
    ac = [row for row in rows if row["Class"] in {"A", "C"}]
    b_rows = [row for row in rows if row["Class"] == "B"]
    threshold = (median([float(row["RmsLog"]) for row in ac if row["Class"] == "A"]) + median([float(row["RmsLog"]) for row in ac if row["Class"] == "C"])) / 2
    b_c_like = sum(float(row["RmsLog"]) > threshold for row in b_rows)
    return [
        {
            "PolicyID": "B_primary_policy",
            "Decision": "exclude_B_from_primary_training_and_primary_AUC",
            "Reason": "B_labels_are_intentionally_uncertain_not_clean_targets",
            "NB": str(len(b_rows)),
            "ThresholdSource": "A_C_projection_fixed_median_midpoint",
            "ProjectionRMSThreshold": fmt(threshold),
            "BPredictedC_like": str(b_c_like),
            "BPredictedA_like": str(len(b_rows) - b_c_like),
            "AllowedUse": "descriptive_uncertainty_band_and_candidate_prioritization_only",
            "ForbiddenUse": "do_not_train_primary_classifier_on_B_as_intermediate_truth",
        }
    ]


def loogo_metric_for_score(score: str, predictor_label: str) -> dict[str, str]:
    rows = [row for row in baseline_rows_by_score(score) if row["Class"] in {"A", "C"}]
    predictions: list[dict[str, str]] = []
    for heldout in rows:
        training = [row for row in rows if row["GalaxyName"] != heldout["GalaxyName"]]
        threshold = (
            median([float(row["RmsLog"]) for row in training if row["Class"] == "A"])
            + median([float(row["RmsLog"]) for row in training if row["Class"] == "C"])
        ) / 2
        predicted = "C" if float(heldout["RmsLog"]) > threshold else "A"
        predictions.append(
            {
                "TrueClass": heldout["Class"],
                "PredictedClass": predicted,
                "Score": heldout["RmsLog"],
            }
        )
    labels = [1 if row["TrueClass"] == "C" else 0 for row in predictions]
    scores = [float(row["Score"]) for row in predictions]
    predicted_c = sum(row["PredictedClass"] == "C" for row in predictions)
    true_c = sum(row["TrueClass"] == "C" for row in predictions)
    tp = sum(row["TrueClass"] == "C" and row["PredictedClass"] == "C" for row in predictions)
    fp = sum(row["TrueClass"] == "A" and row["PredictedClass"] == "C" for row in predictions)
    fn = sum(row["TrueClass"] == "C" and row["PredictedClass"] == "A" for row in predictions)
    correct = sum(row["TrueClass"] == row["PredictedClass"] for row in predictions)
    return {
        "Predictor": predictor_label,
        "SourceScore": score,
        "Validation": "leave_one_galaxy_out_median_midpoint_threshold",
        "NGalaxies": str(len(rows)),
        "Accuracy": fmt(correct / len(rows)),
        "AUC_C_higher": fmt(auc(labels, scores)),
        "PredictedC": str(predicted_c),
        "TrueC": str(true_c),
        "FalsePositiveAasC": str(fp),
        "FalseNegativeCasA": str(fn),
        "PrecisionC": fmt(tp / predicted_c if predicted_c else math.nan),
        "RecallC": fmt(tp / true_c if true_c else math.nan),
        "InterpretationGuardrail": "newtonian_scope_control_not_low_acceleration_specificity_proof",
    }


def build_newtonian_rows() -> list[dict[str, str]]:
    return [
        loogo_metric_for_score("projection_fixed", "Projection_RMS_from_paper1_score_table"),
        loogo_metric_for_score("newtonian_baryonic", "Newtonian_Baryonic_RMS"),
    ]


def write_report(
    calibration: list[dict[str, str]],
    b_policy: list[dict[str, str]],
    newtonian: list[dict[str, str]],
) -> None:
    cal = calibration[0]
    b = b_policy[0]
    newton = next(row for row in newtonian if row["Predictor"] == "Newtonian_Baryonic_RMS")
    projection = next(row for row in newtonian if row["Predictor"] == "Projection_RMS_from_paper1_score_table")
    lines = [
        "# Paper 2 Calibration and Policy Gate",
        "",
        "This packet adds calibration uncertainty, B-class policy, and Newtonian baseline scope for the residual-disturbance inference branch.",
        "",
        "## Calibration Uncertainty",
        "",
        f"- Predictor: `{cal['Predictor']}`",
        f"- Observed AUC: {cal['ObservedAUC']}",
        f"- Bootstrap 95% CI: [{cal['AUC_CI95Low']}, {cal['AUC_CI95High']}]",
        f"- Median-midpoint threshold: {cal['Threshold']}",
        f"- In-sample threshold accuracy: {cal['ThresholdAccuracyInSample']}",
        "",
        "## B-Class Policy",
        "",
        "- B galaxies remain excluded from primary training and primary A/C AUC.",
        f"- B galaxies scored C-like under the A/C threshold: {b['BPredictedC_like']}/{b['NB']}",
        "- B may be used only as an uncertainty band and candidate-prioritization set.",
        "",
        "## Newtonian Scope",
        "",
        f"- Projection score-table LOOGO AUC: {projection['AUC_C_higher']}",
        f"- Newtonian baryonic LOOGO AUC: {newton['AUC_C_higher']}",
        f"- Newtonian accuracy: {newton['Accuracy']}",
        "",
        "## Interpretation",
        "",
        "The Paper 2 primary diagnostic remains a low-acceleration residual-family signal rather than a generic Newtonian baryonic residual classifier. The B-class policy prevents uncertain labels from becoming pseudo-ground-truth, and the bootstrap interval makes the sample-size uncertainty explicit.",
        "",
        "## Guardrail",
        "",
        "This gate is not a Tau Core validation result. It still does not authorize projection-model uniqueness or replacing external evidence labels with residual-only labels.",
        "",
        "## Generated Files",
        "",
        "- `paper2_calibration_uncertainty.csv`",
        "- `paper2_b_class_policy.csv`",
        "- `paper2_newtonian_scope.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_claim_boundary(calibration: list[dict[str, str]], newtonian: list[dict[str, str]]) -> None:
    path = PACKET / "paper2_claim_boundary.csv"
    rows = read_csv(path)
    newton = next(row for row in newtonian if row["Predictor"] == "Newtonian_Baryonic_RMS")
    for row in rows:
        if row["ClaimID"] == "P2_C01_primary_diagnostic":
            if "_bootstrap_ci_" not in row["CurrentEvidence"]:
                row["CurrentEvidence"] += f"_bootstrap_ci_{calibration[0]['AUC_CI95Low']}_{calibration[0]['AUC_CI95High']}"
            row["RequiredUpgrade"] = "manuscript_tables_and_final_observability_language"
            row["Status"] = "paper_grade_candidate_with_caveats"
        if row["ClaimID"] == "P2_C02_model_specificity":
            if "_newtonian_auc_" not in row["CurrentEvidence"]:
                row["CurrentEvidence"] += f"_newtonian_auc_{newton['AUC_C_higher']}"
            row["RequiredUpgrade"] = "state_as_low_acceleration_family_not_projection_uniqueness"
            row["Status"] = "baseline_scope_defined_not_specific"
        if row["ClaimID"] == "P2_C03_classifier_use":
            if not row["CurrentEvidence"].endswith("_b_policy_frozen"):
                row["CurrentEvidence"] += "_b_policy_frozen"
            row["RequiredUpgrade"] = "use_b_only_for_uncertainty_band"
            row["Status"] = "diagnostic_prioritization_only"
    write_csv(
        path,
        rows,
        [
            "ClaimID",
            "AllowedClaim",
            "CurrentEvidence",
            "RequiredUpgrade",
            "ForbiddenClaim",
            "Status",
        ],
    )


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "paper2_calibration_policy.md",
            "paper2_calibration_uncertainty.csv",
            "paper2_b_class_policy.csv",
            "paper2_newtonian_scope.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["paper2_calibration_policy_status"] = (
        "calibration_b_policy_newtonian_scope_frozen"
    )
    manifest["paper2_next_gate"] = "paper2_manuscript_skeleton_and_final_tables"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    calibration = build_calibration_rows()
    b_policy = build_b_policy_rows()
    newtonian = build_newtonian_rows()
    write_csv(
        CALIBRATION_CSV,
        calibration,
        [
            "CalibrationID",
            "Predictor",
            "NGalaxies",
            "ObservedAUC",
            "BootstrapN",
            "RandomSeed",
            "AUC_CI95Low",
            "AUC_CI95High",
            "Threshold",
            "ThresholdAccuracyInSample",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        B_POLICY_CSV,
        b_policy,
        [
            "PolicyID",
            "Decision",
            "Reason",
            "NB",
            "ThresholdSource",
            "ProjectionRMSThreshold",
            "BPredictedC_like",
            "BPredictedA_like",
            "AllowedUse",
            "ForbiddenUse",
        ],
    )
    write_csv(
        NEWTONIAN_CSV,
        newtonian,
        [
            "Predictor",
            "SourceScore",
            "Validation",
            "NGalaxies",
            "Accuracy",
            "AUC_C_higher",
            "PredictedC",
            "TrueC",
            "FalsePositiveAasC",
            "FalseNegativeCasA",
            "PrecisionC",
            "RecallC",
            "InterpretationGuardrail",
        ],
    )
    write_report(calibration, b_policy, newtonian)
    update_claim_boundary(calibration, newtonian)
    update_manifest()
    print(REPORT)
    print("paper2_calibration_policy=3")


if __name__ == "__main__":
    main()
