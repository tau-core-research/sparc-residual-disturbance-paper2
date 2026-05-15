#!/usr/bin/env python3
"""Build the seed packet for residual-based disturbance inference."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "studies/sparc_residual_disturbance_inference_v01"
PACKET = STUDY / "packet_v01_seed"
PAPER1_PACKET = ROOT / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced"
POINT_MAP = PAPER1_PACKET / "taucore_specificity_point_map.csv"

RESIDUALS = ["AbsResidualProjection", "AbsResidualMONDSimple", "AbsResidualRAR"]
PRIMARY_FEATURES = [
    "Projection_RMS",
    "Projection_OuterInnerRatio",
    "Projection_RadiusPearson",
    "Projection_LowAccelerationMean",
    "ProjectionMinusMOND_Mean",
    "ProjectionMinusRAR_Mean",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def median(values: list[float]) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    n = len(ordered)
    if n % 2:
        return ordered[n // 2]
    return (ordered[n // 2 - 1] + ordered[n // 2]) / 2


def rms(values: list[float]) -> float:
    return math.sqrt(mean([value * value for value in values]))


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return math.nan
    mx = mean(xs)
    my = mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denom = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    if denom == 0:
        return math.nan
    return sum(x * y for x, y in zip(dx, dy)) / denom


def fmt(value: float) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.9f}"


def grouped_points() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(POINT_MAP):
        grouped.setdefault(row["GalaxyName"], []).append(row)
    return grouped


def feature_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for galaxy, points in sorted(grouped_points().items()):
        radii = [float(row["RadiusFraction"]) for row in points]
        output = {
            "GalaxyName": galaxy,
            "Class": points[0]["Class"],
            "NPoints": str(len(points)),
        }
        for residual in RESIDUALS:
            values = [float(row[residual]) for row in points]
            inner = [float(row[residual]) for row in points if row["RadiusBin"].startswith("inner")]
            outer = [float(row[residual]) for row in points if row["RadiusBin"].startswith("outer")]
            low_acc = [float(row[residual]) for row in points if row["AccelerationBin"] == "aN/a0<0.1"]
            inner_mean = mean(inner) if inner else mean(values)
            outer_mean = mean(outer) if outer else mean(values)
            prefix = residual.removeprefix("AbsResidual").replace("MONDSimple", "MOND")
            output[f"{prefix}_Mean"] = fmt(mean(values))
            output[f"{prefix}_Median"] = fmt(median(values))
            output[f"{prefix}_RMS"] = fmt(rms(values))
            output[f"{prefix}_OuterInnerRatio"] = fmt(outer_mean / inner_mean if inner_mean else math.nan)
            output[f"{prefix}_RadiusPearson"] = fmt(pearson(radii, values))
            output[f"{prefix}_LowAccelerationMean"] = fmt(mean(low_acc) if low_acc else mean(values))
            output[f"{prefix}_OutlierFraction_gt_0p15"] = fmt(
                sum(value > 0.15 for value in values) / len(values)
            )
        output["ProjectionMinusMOND_Mean"] = fmt(
            mean([float(row["ProjectionMinusMONDAbs"]) for row in points])
        )
        output["ProjectionMinusRAR_Mean"] = fmt(
            mean([float(row["ProjectionMinusRARAbs"]) for row in points])
        )
        output["InferenceUse"] = "feature_extraction_only_not_external_validation"
        rows.append(output)
    return rows


def auc_for_feature(rows: list[dict[str, str]], feature: str) -> float:
    positives = [float(row[feature]) for row in rows if row["Class"] == "C" and row[feature] != ""]
    negatives = [float(row[feature]) for row in rows if row["Class"] == "A" and row[feature] != ""]
    if not positives or not negatives:
        return math.nan
    wins = 0.0
    total = 0
    for pos in positives:
        for neg in negatives:
            total += 1
            if pos > neg:
                wins += 1
            elif pos == neg:
                wins += 0.5
    return wins / total


def fractional_ranks(values: list[float]) -> list[float]:
    if len(values) <= 1:
        return [0.0 for _ in values]
    pairs = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0 for _ in values]
    for rank, (_, index) in enumerate(pairs):
        ranks[index] = rank / (len(values) - 1)
    return ranks


def score_rows(features: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    scored = [dict(row) for row in features]
    for feature in PRIMARY_FEATURES:
        ranks = fractional_ranks([float(row[feature]) for row in scored])
        for row, rank in zip(scored, ranks):
            row[f"Rank_{feature}"] = fmt(rank)
    for row in scored:
        row["ResidualDisturbanceScore_v01"] = fmt(
            mean([float(row[f"Rank_{feature}"]) for feature in PRIMARY_FEATURES])
        )
        row["ScoreRule"] = "mean_rank_projection_shape_and_comparator_difference_features"

    metrics = []
    for feature in PRIMARY_FEATURES + ["ResidualDisturbanceScore_v01"]:
        metrics.append(
            {
                "Predictor": feature,
                "Target": "Class_C_vs_A",
                "NGalaxies": str(len(scored)),
                "NA": str(sum(row["Class"] == "A" for row in scored)),
                "NC": str(sum(row["Class"] == "C" for row in scored)),
                "AUC_C_higher": fmt(auc_for_feature(scored, feature)),
                "InterpretationGuardrail": "exploratory_in_sample_diagnostic_not_heldout_validation",
            }
        )
    return scored, metrics


def write_protocol(path: Path, metrics: list[dict[str, str]]) -> None:
    score = next(row for row in metrics if row["Predictor"] == "ResidualDisturbanceScore_v01")
    lines = [
        "# Residual-Disturbance Inference Seed Packet v0.1",
        "",
        "This packet starts the reverse diagnostic branch: infer disturbance/coherence candidates from residual structure.",
        "The working hypothesis is that residual structure itself can be used as a diagnostic fingerprint, not merely as model error.",
        "",
        "## Question",
        "",
        "Can galaxy-level residual features act as a diagnostic fingerprint for externally reviewed A/C disturbance class?",
        "",
        "## Feature Families",
        "",
        "- residual amplitude: mean, median, RMS",
        "- radial structure: outer/inner ratio and radius-residual correlation",
        "- low-acceleration burden: mean residual in `aN/a0<0.1` points",
        "- comparator structure: Projection-minus-MOND and Projection-minus-RAR absolute-residual differences",
        "",
        "## Seed Score",
        "",
        "`ResidualDisturbanceScore_v01` is the mean rank of six predeclared projection/comparator features. Higher score means more C-like residual structure.",
        "",
        "## Seed Result",
        "",
        f"- In-sample AUC for `ResidualDisturbanceScore_v01`: {score['AUC_C_higher']}",
        f"- Galaxies: {score['NGalaxies']} (`A={score['NA']}`, `C={score['NC']}`)",
        "",
        "## Interpretation",
        "",
        "This is useful only as a diagnostic pilot. It does not replace the residual-blind Paper 1 audit, because here the residuals are intentionally used as predictors.",
        "",
        "## Next Gate",
        "",
        "The next step must freeze a held-out validation design: leave-one-galaxy-out, source-family holdout, or train/test split by evidence source. Do not promote in-sample AUC to a paper-grade claim.",
        "",
        "## Generated Files",
        "",
        "- `residual_feature_table.csv`",
        "- `residual_disturbance_score_v01.csv`",
        "- `residual_inference_metric_summary.csv`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest() -> None:
    manifest = {
        "packet": "sparc_residual_disturbance_inference_v01/packet_v01_seed",
        "status": "seed_in_sample_diagnostic_not_validation",
        "source_point_map": str(POINT_MAP.relative_to(ROOT)),
        "files": [
            "README.md",
            "packet_manifest.json",
            "residual_disturbance_inference_seed.md",
            "residual_feature_table.csv",
            "residual_disturbance_score_v01.csv",
            "residual_inference_metric_summary.csv",
        ],
        "guardrail": "residuals_are_predictors_here_not_blinded_labels",
    }
    (PACKET / "packet_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    PACKET.mkdir(parents=True, exist_ok=True)
    (PACKET / "README.md").write_text(
        "# Residual-Disturbance Inference Packet v0.1\n\n"
        "Seed packet for residual-pattern-to-disturbance diagnostics. This is exploratory and in-sample only.\n",
        encoding="utf-8",
    )
    features = feature_rows()
    scored, metrics = score_rows(features)
    feature_fields = list(features[0].keys())
    score_fields = list(scored[0].keys())
    write_csv(PACKET / "residual_feature_table.csv", features, feature_fields)
    write_csv(PACKET / "residual_disturbance_score_v01.csv", scored, score_fields)
    write_csv(
        PACKET / "residual_inference_metric_summary.csv",
        metrics,
        ["Predictor", "Target", "NGalaxies", "NA", "NC", "AUC_C_higher", "InterpretationGuardrail"],
    )
    write_protocol(PACKET / "residual_disturbance_inference_seed.md", metrics)
    write_manifest()
    print(PACKET / "residual_disturbance_inference_seed.md")
    print(f"feature_galaxies={len(features)}")


if __name__ == "__main__":
    main()
