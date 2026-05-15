#!/usr/bin/env python3
"""Run leave-one-galaxy-out validation for residual disturbance inference."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "studies/sparc_residual_disturbance_inference_v01/packet_v01_seed"
FEATURES_CSV = PACKET / "residual_feature_table.csv"
PREDICTIONS_CSV = PACKET / "residual_inference_loogo_predictions.csv"
METRICS_CSV = PACKET / "residual_inference_loogo_metric_summary.csv"
REPORT = PACKET / "residual_inference_loogo_validation.md"

PREDICTORS = ["Projection_RMS", "Projection_LowAccelerationMean", "ResidualDisturbanceScore_v01"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    if n % 2:
        return ordered[n // 2]
    return (ordered[n // 2 - 1] + ordered[n // 2]) / 2


def fmt(value: float) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.9f}"


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


def add_seed_score(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    scored = [dict(row) for row in rows]
    rank_features = [
        "Projection_RMS",
        "Projection_OuterInnerRatio",
        "Projection_RadiusPearson",
        "Projection_LowAccelerationMean",
        "ProjectionMinusMOND_Mean",
        "ProjectionMinusRAR_Mean",
    ]
    for feature in rank_features:
        sorted_rows = sorted(scored, key=lambda row: float(row[feature]))
        denom = len(sorted_rows) - 1
        ranks = {row["GalaxyName"]: index / denom for index, row in enumerate(sorted_rows)}
        for row in scored:
            row[f"Rank_{feature}"] = ranks[row["GalaxyName"]]
    for row in scored:
        row["ResidualDisturbanceScore_v01"] = sum(
            row[f"Rank_{feature}"] for feature in rank_features
        ) / len(rank_features)
    return scored


def threshold_from_training(training: list[dict[str, str]], predictor: str) -> float:
    a_values = [float(row[predictor]) for row in training if row["Class"] == "A"]
    c_values = [float(row[predictor]) for row in training if row["Class"] == "C"]
    return (median(a_values) + median(c_values)) / 2


def build_predictions() -> list[dict[str, str]]:
    rows = add_seed_score(read_csv(FEATURES_CSV))
    predictions: list[dict[str, str]] = []
    for heldout in rows:
        training = [row for row in rows if row["GalaxyName"] != heldout["GalaxyName"]]
        for predictor in PREDICTORS:
            threshold = threshold_from_training(training, predictor)
            score = float(heldout[predictor])
            predicted = "C" if score > threshold else "A"
            predictions.append(
                {
                    "GalaxyName": heldout["GalaxyName"],
                    "TrueClass": heldout["Class"],
                    "Predictor": predictor,
                    "Score": fmt(score),
                    "LOOGOThreshold": fmt(threshold),
                    "PredictedClass": predicted,
                    "Correct": str(predicted == heldout["Class"]).lower(),
                    "ValidationStatus": "leave_one_galaxy_out_threshold_no_refit_on_heldout",
                }
            )
    return predictions


def build_metrics(predictions: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for predictor in PREDICTORS:
        values = [row for row in predictions if row["Predictor"] == predictor]
        labels = [1 if row["TrueClass"] == "C" else 0 for row in values]
        scores = [float(row["Score"]) for row in values]
        correct = sum(row["Correct"] == "true" for row in values)
        predicted_c = sum(row["PredictedClass"] == "C" for row in values)
        true_c = sum(row["TrueClass"] == "C" for row in values)
        tp = sum(row["TrueClass"] == "C" and row["PredictedClass"] == "C" for row in values)
        fp = sum(row["TrueClass"] == "A" and row["PredictedClass"] == "C" for row in values)
        fn = sum(row["TrueClass"] == "C" and row["PredictedClass"] == "A" for row in values)
        precision = tp / predicted_c if predicted_c else math.nan
        recall = tp / true_c if true_c else math.nan
        rows.append(
            {
                "Predictor": predictor,
                "Validation": "leave_one_galaxy_out_median_midpoint_threshold",
                "NGalaxies": str(len(values)),
                "Accuracy": fmt(correct / len(values)),
                "AUC_C_higher": fmt(auc(labels, scores)),
                "PredictedC": str(predicted_c),
                "TrueC": str(true_c),
                "FalsePositiveAasC": str(fp),
                "FalseNegativeCasA": str(fn),
                "PrecisionC": fmt(precision),
                "RecallC": fmt(recall),
                "InterpretationGuardrail": "first_heldout_sanity_check_not_paper_grade_classifier",
            }
        )
    return rows


def write_report(metrics: list[dict[str, str]]) -> None:
    best = max(metrics, key=lambda row: float(row["AUC_C_higher"]))
    lines = [
        "# Residual-Disturbance LOOGO Validation v0.1",
        "",
        "This packet runs a first leave-one-galaxy-out sanity check for residual-based disturbance inference.",
        "",
        "## Method",
        "",
        "For each held-out galaxy, the threshold is trained only on the other galaxies as the midpoint between the A and C training medians. The held-out galaxy is then classified as C if its predictor is above that threshold.",
        "",
        "## Results",
        "",
    ]
    for row in metrics:
        lines.extend(
            [
                f"### {row['Predictor']}",
                "",
                f"- Accuracy: {row['Accuracy']}",
                f"- AUC: {row['AUC_C_higher']}",
                f"- Precision C: {row['PrecisionC']}",
                f"- Recall C: {row['RecallC']}",
                f"- False positive A-as-C: {row['FalsePositiveAasC']}",
                f"- False negative C-as-A: {row['FalseNegativeCasA']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            f"The strongest first held-out sanity check is `{best['Predictor']}` with AUC `{best['AUC_C_higher']}`. This supports the idea that residual amplitude carries disturbance information, but it is still not a paper-grade classifier.",
            "",
            "## Next Gate",
            "",
            "Freeze a second-stage classifier design before adding features: either a simple one-feature baseline kept as primary, or a strictly predeclared multifeature model with nested validation.",
            "",
            "## Generated Files",
            "",
            "- `residual_inference_loogo_predictions.csv`",
            "- `residual_inference_loogo_metric_summary.csv`",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    files.update(
        {
            "residual_inference_loogo_validation.md",
            "residual_inference_loogo_predictions.csv",
            "residual_inference_loogo_metric_summary.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["loogo_validation_status"] = "first_heldout_sanity_check_complete_not_paper_grade"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    predictions = build_predictions()
    metrics = build_metrics(predictions)
    write_csv(
        PREDICTIONS_CSV,
        predictions,
        [
            "GalaxyName",
            "TrueClass",
            "Predictor",
            "Score",
            "LOOGOThreshold",
            "PredictedClass",
            "Correct",
            "ValidationStatus",
        ],
    )
    write_csv(
        METRICS_CSV,
        metrics,
        [
            "Predictor",
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
    write_report(metrics)
    update_manifest()
    print(REPORT)
    print(f"loogo_predictions={len(predictions)}")


if __name__ == "__main__":
    main()
