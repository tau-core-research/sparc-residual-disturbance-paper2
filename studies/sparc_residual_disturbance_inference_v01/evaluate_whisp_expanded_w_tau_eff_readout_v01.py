#!/usr/bin/env python3
"""Evaluate WHISP lopsidedness against original-plus-expanded W_tau_eff scores."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv
from evaluate_p07_whisp_holdout_v01 import ASYMMETRY_FIELDS


W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
EXPANDED = PACKET / "yu2022_alfalfa_expanded_w_tau_eff_scores_v01.csv"
WHISP = PACKET / "whisp_vaneymeren2011_overlap.csv"

JOIN_OUT = PACKET / "whisp_expanded_w_tau_eff_readout_join_v01.csv"
METRIC_OUT = PACKET / "whisp_expanded_w_tau_eff_readout_metrics_v01.csv"
DECISION_OUT = PACKET / "whisp_expanded_w_tau_eff_readout_decision_v01.csv"
REPORT = PACKET / "whisp_expanded_w_tau_eff_readout_v01.md"

GUARDRAIL = "whisp_expanded_readout_no_velocity_endpoint_no_refit"


def fmt(value: float) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.9f}"


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def median(values: list[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    n = len(ordered)
    if n % 2:
        return ordered[n // 2]
    return (ordered[n // 2 - 1] + ordered[n // 2]) / 2


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


def ranks(values: list[float]) -> list[float]:
    pairs = sorted((value, index) for index, value in enumerate(values))
    output = [0.0 for _ in values]
    i = 0
    while i < len(pairs):
        j = i + 1
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        rank = (i + j - 1) / 2.0
        for _, index in pairs[i:j]:
            output[index] = rank
        i = j
    return output


def spearman(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return math.nan
    return pearson(ranks(xs), ranks(ys))


def auc_high_higher(high: list[float], low: list[float]) -> float:
    if not high or not low:
        return math.nan
    wins = 0.0
    total = 0
    for h_value in high:
        for l_value in low:
            total += 1
            if h_value > l_value:
                wins += 1
            elif h_value == l_value:
                wins += 0.5
    return wins / total


def whisp_burden(row: dict[str, str]) -> float:
    values = [float(row[field]) for field in ASYMMETRY_FIELDS if row.get(field, "") != ""]
    return mean(values)


def whisp_radial_contrast(row: dict[str, str]) -> float:
    outer = [
        float(row[field])
        for field in ["A1_outer_gt_R25", "A2_outer_gt_R25", "A3_outer_gt_R25"]
        if row.get(field, "") != ""
    ]
    inner = [
        float(row[field])
        for field in ["A1_inner_lt_R25", "A2_inner_lt_R25", "A3_inner_lt_R25"]
        if row.get(field, "") != ""
    ]
    return mean(outer) - mean(inner)


def score_index() -> dict[str, dict[str, str]]:
    scores: dict[str, dict[str, str]] = {}
    for row in read_csv(W_TAU):
        scores[row["GalaxyName"]] = {
            "Score": row["W_tau_eff_candidate_score_v01"],
            "Abs": row["W_tau_eff_abs_v01"],
            "Signed": row["W_tau_eff_signed_v01"],
            "ScoreSource": "frozen_original_w_tau_eff_seed",
            "CandidateConfidenceTier": row["CandidateConfidenceTier"],
        }
    for row in read_csv(EXPANDED):
        if row["W_tau_eff_readout_score_v01"] == "":
            continue
        scores.setdefault(
            row["GalaxyName"],
            {
                "Score": row["W_tau_eff_readout_score_v01"],
                "Abs": row["W_tau_eff_abs_v01"],
                "Signed": row["W_tau_eff_signed_v01"],
                "ScoreSource": row["ScoreSource"],
                "CandidateConfidenceTier": row["CandidateConfidenceTier"],
            },
        )
    return scores


def joined_rows() -> list[dict[str, str]]:
    scores = score_index()
    rows: list[dict[str, str]] = []
    for whisp in read_csv(WHISP):
        galaxy = whisp["GalaxyName"]
        if galaxy not in scores:
            continue
        score = scores[galaxy]
        burden = whisp_burden(whisp)
        radial_contrast = whisp_radial_contrast(whisp)
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": whisp["Class"],
                "WHISP_BurdenScore_v01": fmt(burden),
                "WHISP_RadialContrast_outer_minus_inner_v01": fmt(radial_contrast),
                "EpsilonKin": whisp["EpsilonKin"],
                "W_tau_eff_score_resolved_v01": score["Score"],
                "W_tau_eff_abs_v01": score["Abs"],
                "W_tau_eff_signed_v01": score["Signed"],
                "ScoreSource": score["ScoreSource"],
                "CandidateConfidenceTier": score["CandidateConfidenceTier"],
                "A1_outer_gt_R25": whisp["A1_outer_gt_R25"],
                "A2_outer_gt_R25": whisp["A2_outer_gt_R25"],
                "A3_outer_gt_R25": whisp["A3_outer_gt_R25"],
                "A1_1ltRwlt2": whisp["A1_1ltRwlt2"],
                "A2_1ltRwlt2": whisp["A2_1ltRwlt2"],
                "A3_1ltRwlt2": whisp["A3_1ltRwlt2"],
                "ReadoutUse": "WHISP_full_overlap_original_plus_expanded_W_tau_eff_no_refit",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    cutoff = median([float(row["WHISP_BurdenScore_v01"]) for row in rows])
    radial_cutoff = median(
        [float(row["WHISP_RadialContrast_outer_minus_inner_v01"]) for row in rows]
    )
    for row in rows:
        row["WHISP_BurdenSplit"] = (
            "high" if float(row["WHISP_BurdenScore_v01"]) > cutoff else "low"
        )
        row["WHISP_BurdenMedianCutoff"] = fmt(cutoff)
        row["WHISP_RadialContrastSplit"] = (
            "high_outer_contrast"
            if float(row["WHISP_RadialContrast_outer_minus_inner_v01"]) > radial_cutoff
            else "low_outer_contrast"
        )
        row["WHISP_RadialContrastMedianCutoff"] = fmt(radial_cutoff)
    return rows


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    burden = [float(row["WHISP_BurdenScore_v01"]) for row in rows]
    radial = [float(row["WHISP_RadialContrast_outer_minus_inner_v01"]) for row in rows]
    epsilon = [float(row["EpsilonKin"]) for row in rows if row["EpsilonKin"] != ""]
    score = [float(row["W_tau_eff_score_resolved_v01"]) for row in rows]
    score_for_epsilon = [
        float(row["W_tau_eff_score_resolved_v01"]) for row in rows if row["EpsilonKin"] != ""
    ]
    high = [
        float(row["W_tau_eff_score_resolved_v01"])
        for row in rows
        if row["WHISP_BurdenSplit"] == "high"
    ]
    low = [
        float(row["W_tau_eff_score_resolved_v01"])
        for row in rows
        if row["WHISP_BurdenSplit"] == "low"
    ]
    radial_high = [
        float(row["W_tau_eff_score_resolved_v01"])
        for row in rows
        if row["WHISP_RadialContrastSplit"] == "high_outer_contrast"
    ]
    radial_low = [
        float(row["W_tau_eff_score_resolved_v01"])
        for row in rows
        if row["WHISP_RadialContrastSplit"] == "low_outer_contrast"
    ]
    original_n = sum(row["ScoreSource"] == "frozen_original_w_tau_eff_seed" for row in rows)
    expanded_n = len(rows) - original_n
    return [
        {
            "Metric": "coverage_joined",
            "N": str(len(rows)),
            "Value": str(len(rows)),
            "SecondaryValue": f"original_seed={original_n};expanded={expanded_n}",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_whisp_burden_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(burden, score)),
            "SecondaryValue": "higher WHISP burden expected higher W_tau_eff score",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "spearman_whisp_burden_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(spearman(burden, score)),
            "SecondaryValue": "rank direction",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_high_vs_low_whisp_burden",
            "N": str(len(rows)),
            "Value": fmt(auc_high_higher(high, low)),
            "SecondaryValue": "median split within expanded WHISP overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "median_score_low_whisp_burden",
            "N": str(len(low)),
            "Value": fmt(median(low)),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "median_score_high_whisp_burden",
            "N": str(len(high)),
            "Value": fmt(median(high)),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_radial_contrast_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(radial, score)),
            "SecondaryValue": "outer-minus-inner WHISP asymmetry contrast",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_high_vs_low_radial_contrast",
            "N": str(len(rows)),
            "Value": fmt(auc_high_higher(radial_high, radial_low)),
            "SecondaryValue": "median split by outer-minus-inner contrast",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_epsilon_kin_vs_w_tau_score",
            "N": str(len(epsilon)),
            "Value": fmt(pearson(epsilon, score_for_epsilon)),
            "SecondaryValue": "kinematic lopsidedness column",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def decision_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in metrics}
    auc = float(lookup["auc_high_vs_low_whisp_burden"]["Value"])
    pearson_value = float(lookup["pearson_whisp_burden_vs_w_tau_score"]["Value"])
    return [
        {
            "DecisionID": "WXR01",
            "Decision": "expanded_whisp_direction",
            "Status": "positive_but_not_paper_grade"
            if auc > 0.5 and pearson_value > 0
            else "not_supported",
            "N": lookup["coverage_joined"]["N"],
            "Evidence": (
                f"AUC={lookup['auc_high_vs_low_whisp_burden']['Value']};"
                f"Pearson={lookup['pearson_whisp_burden_vs_w_tau_score']['Value']};"
                f"Spearman={lookup['spearman_whisp_burden_vs_w_tau_score']['Value']}"
            ),
            "NextAction": "freeze_THINGS_control_then_seek_non_WHISP_replication_N_ge_15",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "WXR02",
            "Decision": "radial_contrast_channel",
            "Status": "diagnostic_only",
            "N": lookup["coverage_joined"]["N"],
            "Evidence": (
                f"Pearson={lookup['pearson_radial_contrast_vs_w_tau_score']['Value']};"
                f"AUC={lookup['auc_high_vs_low_radial_contrast']['Value']}"
            ),
            "NextAction": "do_not_promote_radial_contrast_before_independent_controls",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    decisions_by_id = {row["DecisionID"]: row for row in decisions}
    lines = [
        "# WHISP Expanded W_tau_eff Readout v0.1",
        "",
        "This packet re-evaluates the WHISP lopsidedness/asymmetry family after the Yu-expanded `W_tau_eff` score table made four additional WHISP overlaps usable. Original seed scores are retained without refit; expanded scores are used only where the original seed had no score.",
        "",
        "## Main Readout",
        "",
        f"- Joined galaxies: {lookup['coverage_joined']['Value']} ({lookup['coverage_joined']['SecondaryValue']})",
        f"- Pearson WHISP burden vs W_tau_eff score: {lookup['pearson_whisp_burden_vs_w_tau_score']['Value']}",
        f"- Spearman WHISP burden vs W_tau_eff score: {lookup['spearman_whisp_burden_vs_w_tau_score']['Value']}",
        f"- AUC high-vs-low WHISP burden: {lookup['auc_high_vs_low_whisp_burden']['Value']}",
        f"- Median W_tau_eff score low/high burden: {lookup['median_score_low_whisp_burden']['Value']} / {lookup['median_score_high_whisp_burden']['Value']}",
        f"- Radial contrast Pearson/AUC: {lookup['pearson_radial_contrast_vs_w_tau_score']['Value']} / {lookup['auc_high_vs_low_radial_contrast']['Value']}",
        f"- Kinematic epsilon Pearson: {lookup['pearson_epsilon_kin_vs_w_tau_score']['Value']}",
        f"- Decision: {decisions_by_id['WXR01']['Status']}",
        "",
        "## Interpretation",
        "",
        "The expanded WHISP overlap remains directionally positive, but the sample is still below the frozen N>=15 external-validation gate. This strengthens the case for a WHISP-style radial/asymmetry branch, while keeping the result below paper-grade validation status.",
        "",
        "## Generated Files",
        "",
        "- `whisp_expanded_w_tau_eff_readout_join_v01.csv`",
        "- `whisp_expanded_w_tau_eff_readout_metrics_v01.csv`",
        "- `whisp_expanded_w_tau_eff_readout_decision_v01.csv`",
        "",
        "## Guardrail",
        "",
        f"`{GUARDRAIL}`",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [JOIN_OUT, METRIC_OUT, DECISION_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["whisp_expanded_w_tau_eff_readout_status"] = (
        "positive_but_below_external_validation_minimum_n"
    )
    manifest["paper2_next_gate"] = "THINGS_control_then_non_WHISP_replication_N_ge_15"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = joined_rows()
    metrics = metric_rows(rows)
    decisions = decision_rows(metrics)
    write_csv(
        JOIN_OUT,
        rows,
        [
            "GalaxyName",
            "Class",
            "WHISP_BurdenScore_v01",
            "WHISP_BurdenSplit",
            "WHISP_BurdenMedianCutoff",
            "WHISP_RadialContrast_outer_minus_inner_v01",
            "WHISP_RadialContrastSplit",
            "WHISP_RadialContrastMedianCutoff",
            "EpsilonKin",
            "W_tau_eff_score_resolved_v01",
            "W_tau_eff_abs_v01",
            "W_tau_eff_signed_v01",
            "ScoreSource",
            "CandidateConfidenceTier",
            "A1_outer_gt_R25",
            "A2_outer_gt_R25",
            "A3_outer_gt_R25",
            "A1_1ltRwlt2",
            "A2_1ltRwlt2",
            "A3_1ltRwlt2",
            "ReadoutUse",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        METRIC_OUT,
        metrics,
        ["Metric", "N", "Value", "SecondaryValue", "InterpretationGuardrail"],
    )
    write_csv(
        DECISION_OUT,
        decisions,
        [
            "DecisionID",
            "Decision",
            "Status",
            "N",
            "Evidence",
            "NextAction",
            "InterpretationGuardrail",
        ],
    )
    write_report(metrics, decisions)
    update_manifest()
    print(REPORT)
    print(f"whisp_expanded_rows={len(rows)}")
    print(f"whisp_expanded_status={decisions[0]['Status']}")


if __name__ == "__main__":
    main()
