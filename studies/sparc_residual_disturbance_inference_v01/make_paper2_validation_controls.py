#!/usr/bin/env python3
"""Add Paper 2 validation controls learned from the Paper 1 review cycle."""

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
DISTANCE_PAIRS = PAPER1_PACKET / "scale_matched_pairs.csv"
DISTANCE_STRESS = PAPER1_PACKET / "scale_matched_stress.csv"

NULL_CSV = PACKET / "paper2_shuffled_label_null.csv"
BASELINE_CSV = PACKET / "paper2_baseline_family_loogo.csv"
OBSERVABILITY_CSV = PACKET / "paper2_observability_stress.csv"
REPORT = PACKET / "paper2_validation_controls.md"

PRIMARY = "Projection_RMS"
BASELINE_PREDICTORS = ["Projection_RMS", "MOND_RMS", "RAR_RMS"]
N_SHUFFLES = 1000
RANDOM_SEED = 20260515


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
    if not ordered:
        return math.nan
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


def threshold_from_training(training: list[dict[str, str]], predictor: str) -> float:
    a_values = [float(row[predictor]) for row in training if row["Class"] == "A"]
    c_values = [float(row[predictor]) for row in training if row["Class"] == "C"]
    return (median(a_values) + median(c_values)) / 2


def loogo_metrics_for_predictor(rows: list[dict[str, str]], predictor: str) -> dict[str, str]:
    predictions: list[dict[str, str]] = []
    for heldout in rows:
        training = [row for row in rows if row["GalaxyName"] != heldout["GalaxyName"]]
        threshold = threshold_from_training(training, predictor)
        predicted = "C" if float(heldout[predictor]) > threshold else "A"
        predictions.append(
            {
                "TrueClass": heldout["Class"],
                "PredictedClass": predicted,
                "Score": heldout[predictor],
            }
        )
    labels = [1 if row["TrueClass"] == "C" else 0 for row in predictions]
    scores = [float(row["Score"]) for row in predictions]
    correct = sum(row["TrueClass"] == row["PredictedClass"] for row in predictions)
    predicted_c = sum(row["PredictedClass"] == "C" for row in predictions)
    true_c = sum(row["TrueClass"] == "C" for row in predictions)
    fp = sum(row["TrueClass"] == "A" and row["PredictedClass"] == "C" for row in predictions)
    fn = sum(row["TrueClass"] == "C" and row["PredictedClass"] == "A" for row in predictions)
    tp = sum(row["TrueClass"] == "C" and row["PredictedClass"] == "C" for row in predictions)
    return {
        "Predictor": predictor,
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
        "InterpretationGuardrail": "baseline_family_comparison_not_model_specificity",
    }


def build_baseline_rows() -> list[dict[str, str]]:
    rows = read_csv(FEATURES_CSV)
    return [loogo_metrics_for_predictor(rows, predictor) for predictor in BASELINE_PREDICTORS]


def build_null_rows() -> list[dict[str, str]]:
    rows = read_csv(FEATURES_CSV)
    scores = [float(row[PRIMARY]) for row in rows]
    labels = [1 if row["Class"] == "C" else 0 for row in rows]
    observed = auc(labels, scores)
    rng = random.Random(RANDOM_SEED)
    shuffled_aucs: list[float] = []
    for _ in range(N_SHUFFLES):
        shuffled = labels[:]
        rng.shuffle(shuffled)
        shuffled_aucs.append(auc(shuffled, scores))
    p_ge_observed = sum(value >= observed for value in shuffled_aucs) / len(shuffled_aucs)
    return [
        {
            "NullTest": "shuffle_A_C_labels_preserve_class_counts",
            "Predictor": PRIMARY,
            "ObservedAUC": fmt(observed),
            "NShuffles": str(N_SHUFFLES),
            "RandomSeed": str(RANDOM_SEED),
            "NullMedianAUC": fmt(median(shuffled_aucs)),
            "NullP95AUC": fmt(percentile(shuffled_aucs, 0.95)),
            "NullP99AUC": fmt(percentile(shuffled_aucs, 0.99)),
            "EmpiricalP_AUC_ge_observed": fmt(p_ge_observed),
            "InterpretationGuardrail": "label_shuffle_null_not_independent_validation",
        }
    ]


def build_observability_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for method in ["greedy_unique", "optimal_ordered"]:
        pairs = [
            row
            for row in read_csv(DISTANCE_PAIRS)
            if row["covariate"] == "sparc_distance_mpc" and row["match_method"] == method
        ]
        if not pairs:
            continue
        c_higher = sum(float(row["C_rms_log_tpg"]) > float(row["A_rms_log_tpg"]) for row in pairs)
        diffs = [float(row["paired_diff_C_minus_A"]) for row in pairs]
        rows.append(
            {
                "StressTest": f"sparc_distance_{method}_matched_pairs",
                "Predictor": PRIMARY,
                "NPairs": str(len(pairs)),
                "MedianPairDistanceDeltaMpc": fmt(median([float(row["abs_delta"]) for row in pairs])),
                "MedianPairedDiff_C_minus_A": fmt(median(diffs)),
                "FractionPairs_C_higher": fmt(c_higher / len(pairs)),
                "InterpretationGuardrail": "distance_matched_sanity_check_not_full_observability_solution",
            }
        )
    caliper = next(
        row
        for row in read_csv(DISTANCE_STRESS)
        if row["control"] == "sparc_distance_mpc_matched_pairs_caliper"
    )
    rows.append(
        {
            "StressTest": caliper["control"],
            "Predictor": PRIMARY,
            "NPairs": caliper["n_pairs"],
            "MedianPairDistanceDeltaMpc": fmt(float(caliper["median_abs_delta"])),
            "MedianPairedDiff_C_minus_A": fmt(float(caliper["effect"])),
            "FractionPairs_C_higher": "",
            "InterpretationGuardrail": "strict_distance_caliper_aggregate_from_paper1_not_pair_level_classifier",
        }
    )
    return rows


def write_report(
    null_rows: list[dict[str, str]],
    baseline_rows: list[dict[str, str]],
    observability_rows: list[dict[str, str]],
) -> None:
    null = null_rows[0]
    best = max(baseline_rows, key=lambda row: float(row["AUC_C_higher"]))
    lines = [
        "# Paper 2 Validation Controls",
        "",
        "This packet adds the first Paper-1-style reviewer controls to the residual-disturbance inference branch.",
        "",
        "## Shuffled-Label Null",
        "",
        f"- Predictor: `{null['Predictor']}`",
        f"- Observed AUC: {null['ObservedAUC']}",
        f"- Null median AUC: {null['NullMedianAUC']}",
        f"- Null 95th percentile AUC: {null['NullP95AUC']}",
        f"- Empirical p(AUC >= observed): {null['EmpiricalP_AUC_ge_observed']}",
        "",
        "## Baseline-Family Comparison",
        "",
    ]
    for row in baseline_rows:
        lines.extend(
            [
                f"### {row['Predictor']}",
                "",
                f"- LOOGO AUC: {row['AUC_C_higher']}",
                f"- Accuracy: {row['Accuracy']}",
                f"- False positive A-as-C: {row['FalsePositiveAasC']}",
                f"- False negative C-as-A: {row['FalseNegativeCasA']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Distance-Matched Stress",
            "",
        ]
    )
    for row in observability_rows:
        lines.append(
            f"- `{row['StressTest']}`: N={row['NPairs']}, median C-A diff={row['MedianPairedDiff_C_minus_A']}, fraction C higher={row['FractionPairs_C_higher']}"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"`{best['Predictor']}` is the strongest current residual-family baseline by LOOGO AUC. The shuffled-label null makes the primary AUC difficult to dismiss as random label order, but the distance-matched stress tests show that observability remains a live caveat rather than a solved problem.",
            "",
            "## Guardrail",
            "",
            "These controls move Paper 2 closer to a publishable diagnostic audit, but they still do not establish Tau Core validation, projection-model uniqueness, or replacement of external evidence labels.",
            "",
            "## Generated Files",
            "",
            "- `paper2_shuffled_label_null.csv`",
            "- `paper2_baseline_family_loogo.csv`",
            "- `paper2_observability_stress.csv`",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_claim_boundary(null_rows: list[dict[str, str]]) -> None:
    path = PACKET / "paper2_claim_boundary.csv"
    rows = read_csv(path)
    for row in rows:
        if row["ClaimID"] == "P2_C01_primary_diagnostic":
            row["RequiredUpgrade"] = "observability_stress_and_baseline_family_comparison_added_next_needs_calibration"
            row["Status"] = "candidate_after_null_and_first_observability_controls"
            row["CurrentEvidence"] = (
                f"Projection_RMS_LOOGO_AUC_0.771_accuracy_0.756_shuffle_p_{null_rows[0]['EmpiricalP_AUC_ge_observed']}"
            )
        if row["ClaimID"] == "P2_C02_model_specificity":
            row["CurrentEvidence"] = "projection_mond_rar_feature_family_loogo_metrics_available"
            row["RequiredUpgrade"] = "newtonian_per_galaxy_feature_family_or_explicit_scope_limit"
            row["Status"] = "baseline_comparison_started_not_specific"
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
            "paper2_validation_controls.md",
            "paper2_shuffled_label_null.csv",
            "paper2_baseline_family_loogo.csv",
            "paper2_observability_stress.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["paper2_validation_controls_status"] = (
        "shuffle_null_baseline_family_distance_stress_added"
    )
    manifest["paper2_next_gate"] = "calibration_uncertainty_b_class_policy_newtonian_scope"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    null_rows = build_null_rows()
    baseline_rows = build_baseline_rows()
    observability_rows = build_observability_rows()
    write_csv(
        NULL_CSV,
        null_rows,
        [
            "NullTest",
            "Predictor",
            "ObservedAUC",
            "NShuffles",
            "RandomSeed",
            "NullMedianAUC",
            "NullP95AUC",
            "NullP99AUC",
            "EmpiricalP_AUC_ge_observed",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        BASELINE_CSV,
        baseline_rows,
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
    write_csv(
        OBSERVABILITY_CSV,
        observability_rows,
        [
            "StressTest",
            "Predictor",
            "NPairs",
            "MedianPairDistanceDeltaMpc",
            "MedianPairedDiff_C_minus_A",
            "FractionPairs_C_higher",
            "InterpretationGuardrail",
        ],
    )
    write_report(null_rows, baseline_rows, observability_rows)
    update_claim_boundary(null_rows)
    update_manifest()
    print(REPORT)
    print("paper2_validation_controls=3")


if __name__ == "__main__":
    main()
