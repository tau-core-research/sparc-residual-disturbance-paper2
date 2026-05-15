#!/usr/bin/env python3
"""Evaluate P05 THINGS non-circular controls against W_tau_eff."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
P05 = PACKET / "systematics_control_things_harmonic_summary_v01.csv"
JOIN_OUT = PACKET / "p05_things_non_circular_w_tau_eff_control_join_v01.csv"
METRIC_OUT = PACKET / "p05_things_non_circular_w_tau_eff_control_metrics_v01.csv"
DECISION_OUT = PACKET / "p05_things_non_circular_w_tau_eff_control_decision_v01.csv"
REPORT = PACKET / "p05_things_non_circular_w_tau_eff_control_v01.md"

CONTROL_FIELDS = [
    "MedianNonCircularAmplitudeKms",
    "MedianNonCircularAmplitudeInner1KpcKms",
    "NonCircularAmplitudeOverVmaxPercent",
    "MedianAbsResidualVelocityAfterHarmonicKms",
]
GUARDRAIL = "p05_non_circular_control_no_velocity_endpoint_no_attribution"


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


def rank(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + 1 + j) / 2
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float:
    return pearson(rank(xs), rank(ys))


def auc_high_higher(high: list[float], low: list[float]) -> float:
    if not high or not low:
        return math.nan
    wins = 0.0
    total = 0
    for h in high:
        for l in low:
            total += 1
            if h > l:
                wins += 1
            elif h == l:
                wins += 0.5
    return wins / total


def parse_float(value: str) -> float:
    return float(value) if value != "" else math.nan


def normalized_burden(row: dict[str, str], medians: dict[str, float]) -> float:
    ratios: list[float] = []
    for field in CONTROL_FIELDS:
        value = parse_float(row[field])
        if not math.isnan(value) and medians[field] != 0:
            ratios.append(value / medians[field])
    return mean(ratios)


def joined_rows() -> list[dict[str, str]]:
    w_tau = {row["GalaxyName"]: row for row in read_csv(W_TAU)}
    p05_rows = [row for row in read_csv(P05) if row["GalaxyName"] in w_tau]
    medians = {
        field: median(
            [parse_float(row[field]) for row in p05_rows if row.get(field, "") != ""]
        )
        for field in CONTROL_FIELDS
    }
    rows: list[dict[str, str]] = []
    for p05 in p05_rows:
        target = w_tau[p05["GalaxyName"]]
        burden = normalized_burden(p05, medians)
        rows.append(
            {
                "GalaxyName": p05["GalaxyName"],
                "Class": target["Class"],
                "P05NonCircularBurden_v01": fmt(burden),
                "W_tau_eff_candidate_score_v01": target["W_tau_eff_candidate_score_v01"],
                "W_tau_eff_abs_v01": target["W_tau_eff_abs_v01"],
                "W_tau_eff_signed_v01": target["W_tau_eff_signed_v01"],
                "HistoryImprovement_PositiveIsBetter": target[
                    "HistoryImprovement_PositiveIsBetter"
                ],
                "MedianNonCircularAmplitudeKms": p05["MedianNonCircularAmplitudeKms"],
                "MedianNonCircularAmplitudeInner1KpcKms": p05[
                    "MedianNonCircularAmplitudeInner1KpcKms"
                ],
                "NonCircularAmplitudeOverVmaxPercent": p05[
                    "NonCircularAmplitudeOverVmaxPercent"
                ],
                "MedianAbsResidualVelocityAfterHarmonicKms": p05[
                    "MedianAbsResidualVelocityAfterHarmonicKms"
                ],
                "ReadoutUse": "P05_THINGS_non_circular_control_no_velocity_endpoint",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    cutoff = median([float(row["P05NonCircularBurden_v01"]) for row in rows])
    for row in rows:
        row["P05BurdenSplit"] = (
            "high" if float(row["P05NonCircularBurden_v01"]) > cutoff else "low"
        )
        row["P05BurdenMedianCutoff"] = fmt(cutoff)
    return rows


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    outputs: list[dict[str, str]] = [
        {
            "Metric": "coverage_joined",
            "N": str(len(rows)),
            "Value": str(len(rows)),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        }
    ]
    score = [float(row["W_tau_eff_candidate_score_v01"]) for row in rows]
    abs_w = [float(row["W_tau_eff_abs_v01"]) for row in rows]
    history = [float(row["HistoryImprovement_PositiveIsBetter"]) for row in rows]
    burden = [float(row["P05NonCircularBurden_v01"]) for row in rows]
    high = [
        float(row["W_tau_eff_candidate_score_v01"])
        for row in rows
        if row["P05BurdenSplit"] == "high"
    ]
    low = [
        float(row["W_tau_eff_candidate_score_v01"])
        for row in rows
        if row["P05BurdenSplit"] == "low"
    ]
    outputs.extend(
        [
            {
                "Metric": "pearson_p05_burden_vs_w_tau_score",
                "N": str(len(rows)),
                "Value": fmt(pearson(burden, score)),
                "SecondaryValue": "higher non-circular burden expected higher W_tau_eff candidate score if P05 absorbs signal",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "spearman_p05_burden_vs_w_tau_score",
                "N": str(len(rows)),
                "Value": fmt(spearman(burden, score)),
                "SecondaryValue": "rank control for small overlap",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "pearson_p05_burden_vs_abs_w_tau",
                "N": str(len(rows)),
                "Value": fmt(pearson(burden, abs_w)),
                "SecondaryValue": "absolute residual-inferred weight",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "pearson_p05_burden_vs_history_improvement",
                "N": str(len(rows)),
                "Value": fmt(pearson(burden, history)),
                "SecondaryValue": "history diagnostic control",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "median_score_low_p05_burden",
                "N": str(len(low)),
                "Value": fmt(median(low)),
                "SecondaryValue": "",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "median_score_high_p05_burden",
                "N": str(len(high)),
                "Value": fmt(median(high)),
                "SecondaryValue": "",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "auc_high_vs_low_p05_burden",
                "N": str(len(rows)),
                "Value": fmt(auc_high_higher(high, low)),
                "SecondaryValue": "median split within P05 overlap",
                "InterpretationGuardrail": GUARDRAIL,
            },
        ]
    )
    for field in CONTROL_FIELDS:
        values = [parse_float(row[field]) for row in rows if row[field] != ""]
        paired_score = [
            float(row["W_tau_eff_candidate_score_v01"]) for row in rows if row[field] != ""
        ]
        outputs.append(
            {
                "Metric": f"pearson_{field}_vs_w_tau_score",
                "N": str(len(values)),
                "Value": fmt(pearson(values, paired_score)),
                "SecondaryValue": "single published non-circular control column",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return outputs


def decision_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in metrics}
    pearson_burden = float(lookup["pearson_p05_burden_vs_w_tau_score"]["Value"])
    auc_burden = float(lookup["auc_high_vs_low_p05_burden"]["Value"])
    if pearson_burden >= 0.5 and auc_burden >= 0.7:
        status = "strong_competing_explanation_in_small_overlap"
        next_action = "treat_non_circular_motion_as_primary_competitor_before_formula"
    elif pearson_burden > 0 and auc_burden > 0.5:
        status = "partial_competitor_in_small_overlap"
        next_action = "keep_P05_as_required_control_and_expand_overlap"
    else:
        status = "does_not_absorb_direction_in_small_overlap"
        next_action = "retain_P05_control_but_proceed_to_P09_observability_join"
    return [
        {
            "DecisionID": "P05D01",
            "Decision": "non_circular_control_vs_W_tau_eff_candidate_score",
            "Status": status,
            "Rationale": (
                "P05 burden Pearson="
                + lookup["pearson_p05_burden_vs_w_tau_score"]["Value"]
                + "; AUC="
                + lookup["auc_high_vs_low_p05_burden"]["Value"]
                + " on seven THINGS galaxies."
            ),
            "Blocks": "tau_core_attribution;velocity_formula",
            "NextAction": next_action,
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "P05D02",
            "Decision": "endpoint_status",
            "Status": "velocity_endpoint_still_closed",
            "Rationale": "Seven galaxies are sufficient for a control warning, not for coefficient selection.",
            "Blocks": "S_tau_full_coefficient_selection",
            "NextAction": "no_velocity_readout_until_P05_and_P09_controls_are_documented",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    decision = decisions[0]
    lines = [
        "# P05 THINGS Non-Circular Control v0.1",
        "",
        "This readout joins the sanitized P05 THINGS harmonic non-circular control summary to `W_tau_eff`. It uses only published non-circular or harmonic-control columns and does not use velocity residuals as predictors.",
        "",
        "## Readout",
        "",
        f"- Joined galaxies: {lookup['coverage_joined']['Value']}",
        f"- Pearson P05 burden vs W_tau_eff candidate score: {lookup['pearson_p05_burden_vs_w_tau_score']['Value']}",
        f"- Spearman P05 burden vs W_tau_eff candidate score: {lookup['spearman_p05_burden_vs_w_tau_score']['Value']}",
        f"- Median W_tau_eff score, low P05 burden: {lookup['median_score_low_p05_burden']['Value']}",
        f"- Median W_tau_eff score, high P05 burden: {lookup['median_score_high_p05_burden']['Value']}",
        f"- AUC high-vs-low P05 burden: {lookup['auc_high_vs_low_p05_burden']['Value']}",
        "",
        "## Decision",
        "",
        f"`{decision['Status']}`",
        "",
        decision["Rationale"],
        "",
        "This is a small-overlap control. It can block overinterpretation, but it cannot by itself fit or reject a Tau Core formula.",
        "",
        "## Generated Files",
        "",
        "- `p05_things_non_circular_w_tau_eff_control_join_v01.csv`",
        "- `p05_things_non_circular_w_tau_eff_control_metrics_v01.csv`",
        "- `p05_things_non_circular_w_tau_eff_control_decision_v01.csv`",
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
    manifest["p05_things_non_circular_control_status"] = (
        "small_overlap_control_complete_no_velocity_endpoint"
    )
    manifest["paper2_next_gate"] = "P09_galaxy_level_inclination_observability_join"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = joined_rows()
    metrics = metric_rows(rows)
    decisions = decision_rows(metrics)
    join_fields = [
        "GalaxyName",
        "Class",
        "P05NonCircularBurden_v01",
        "W_tau_eff_candidate_score_v01",
        "W_tau_eff_abs_v01",
        "W_tau_eff_signed_v01",
        "HistoryImprovement_PositiveIsBetter",
        "MedianNonCircularAmplitudeKms",
        "MedianNonCircularAmplitudeInner1KpcKms",
        "NonCircularAmplitudeOverVmaxPercent",
        "MedianAbsResidualVelocityAfterHarmonicKms",
        "ReadoutUse",
        "InterpretationGuardrail",
        "P05BurdenSplit",
        "P05BurdenMedianCutoff",
    ]
    metric_fields = ["Metric", "N", "Value", "SecondaryValue", "InterpretationGuardrail"]
    decision_fields = [
        "DecisionID",
        "Decision",
        "Status",
        "Rationale",
        "Blocks",
        "NextAction",
        "InterpretationGuardrail",
    ]
    write_csv(JOIN_OUT, rows, join_fields)
    write_csv(METRIC_OUT, metrics, metric_fields)
    write_csv(DECISION_OUT, decisions, decision_fields)
    write_report(metrics, decisions)
    update_manifest()


if __name__ == "__main__":
    main()
