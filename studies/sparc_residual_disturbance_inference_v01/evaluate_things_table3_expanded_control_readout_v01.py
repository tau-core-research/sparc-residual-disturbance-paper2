#!/usr/bin/env python3
"""Evaluate the expanded THINGS Table 3 non-circular control readout."""

from __future__ import annotations

import json
import math

from make_packet_v01_seed import PACKET, read_csv, write_csv


SCORES = PACKET / "things_table3_expanded_w_tau_eff_scores_v01.csv"
JOIN_OUT = PACKET / "things_table3_expanded_control_readout_join_v01.csv"
METRIC_OUT = PACKET / "things_table3_expanded_control_readout_metrics_v01.csv"
DECISION_OUT = PACKET / "things_table3_expanded_control_readout_decision_v01.csv"
REPORT = PACKET / "things_table3_expanded_control_readout_v01.md"

GUARDRAIL = "things_table3_expanded_control_readout_no_velocity_endpoint"


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
    for high_value in high:
        for low_value in low:
            total += 1
            if high_value > low_value:
                wins += 1
            elif high_value == low_value:
                wins += 0.5
    return wins / total


def joined_rows() -> list[dict[str, str]]:
    rows = [
        row
        for row in read_csv(SCORES)
        if row["W_tau_eff_score_resolved_v01"] != ""
    ]
    cutoff = median([float(row["MedianNonCircularAmplitudeKms"]) for row in rows])
    pct_cutoff = median([float(row["NonCircularAmplitudeOverVmaxPercent"]) for row in rows])
    for row in rows:
        row["ArSplit"] = (
            "high" if float(row["MedianNonCircularAmplitudeKms"]) > cutoff else "low"
        )
        row["ArMedianCutoff"] = fmt(cutoff)
        row["ArOverVmaxSplit"] = (
            "high"
            if float(row["NonCircularAmplitudeOverVmaxPercent"]) > pct_cutoff
            else "low"
        )
        row["ArOverVmaxMedianCutoff"] = fmt(pct_cutoff)
        row["ReadoutUse"] = "THINGS_Table3_expanded_control_no_velocity_endpoint"
        row["InterpretationGuardrail"] = GUARDRAIL
    return rows


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    score = [float(row["W_tau_eff_score_resolved_v01"]) for row in rows]
    ar = [float(row["MedianNonCircularAmplitudeKms"]) for row in rows]
    pct = [float(row["NonCircularAmplitudeOverVmaxPercent"]) for row in rows]
    residual = [float(row["MedianAbsResidualVelocityAfterHarmonicKms"]) for row in rows]
    high_ar = [
        float(row["W_tau_eff_score_resolved_v01"]) for row in rows if row["ArSplit"] == "high"
    ]
    low_ar = [
        float(row["W_tau_eff_score_resolved_v01"]) for row in rows if row["ArSplit"] == "low"
    ]
    high_pct = [
        float(row["W_tau_eff_score_resolved_v01"])
        for row in rows
        if row["ArOverVmaxSplit"] == "high"
    ]
    low_pct = [
        float(row["W_tau_eff_score_resolved_v01"])
        for row in rows
        if row["ArOverVmaxSplit"] == "low"
    ]
    return [
        {
            "Metric": "coverage_joined",
            "N": str(len(rows)),
            "Value": str(len(rows)),
            "SecondaryValue": "expanded THINGS Table 3 resolver rows",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_Ar_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(ar, score)),
            "SecondaryValue": "median non-circular amplitude",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "spearman_Ar_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(spearman(ar, score)),
            "SecondaryValue": "rank direction",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_high_vs_low_Ar",
            "N": str(len(rows)),
            "Value": fmt(auc_high_higher(high_ar, low_ar)),
            "SecondaryValue": "median split by median non-circular amplitude",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_ArOverVmaxPercent_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(pct, score)),
            "SecondaryValue": "non-circular amplitude over Vmax percent",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_high_vs_low_ArOverVmaxPercent",
            "N": str(len(rows)),
            "Value": fmt(auc_high_higher(high_pct, low_pct)),
            "SecondaryValue": "median split by non-circular over Vmax percent",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_HarmonicResidualVelocity_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(residual, score)),
            "SecondaryValue": "median absolute residual velocity after harmonic fit",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "median_score_low_Ar",
            "N": str(len(low_ar)),
            "Value": fmt(median(low_ar)),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "median_score_high_Ar",
            "N": str(len(high_ar)),
            "Value": fmt(median(high_ar)),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def decision_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in metrics}
    auc = float(lookup["auc_high_vs_low_Ar"]["Value"])
    pearson_value = float(lookup["pearson_Ar_vs_w_tau_score"]["Value"])
    return [
        {
            "DecisionID": "T3R01",
            "Decision": "expanded_THINGS_non_circular_absorption",
            "Status": "does_not_absorb_WHISP_direction"
            if auc <= 0.5 or pearson_value <= 0
            else "partial_positive_control",
            "N": lookup["coverage_joined"]["N"],
            "Evidence": (
                f"Ar_AUC={lookup['auc_high_vs_low_Ar']['Value']};"
                f"Ar_Pearson={lookup['pearson_Ar_vs_w_tau_score']['Value']};"
                f"Ar_Spearman={lookup['spearman_Ar_vs_w_tau_score']['Value']}"
            ),
            "NextAction": "continue_to_non_WHISP_resolved_HI_replication",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "T3R02",
            "Decision": "claim_boundary",
            "Status": "control_only_below_N15",
            "N": lookup["coverage_joined"]["N"],
            "Evidence": "expanded THINGS Table 3 remains below N>=15",
            "NextAction": "do_not_claim_THINGS_validation",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    lines = [
        "# THINGS Table 3 Expanded Control Readout v0.1",
        "",
        "This packet evaluates the expanded THINGS Table 3 control readout after scoring all Table 3 galaxies with available local SPARC rotmods. It remains a non-circular-motion control and does not open a velocity endpoint.",
        "",
        "## Main Readout",
        "",
        f"- Joined rows: {lookup['coverage_joined']['Value']}",
        f"- Pearson Ar vs W_tau_eff score: {lookup['pearson_Ar_vs_w_tau_score']['Value']}",
        f"- Spearman Ar vs W_tau_eff score: {lookup['spearman_Ar_vs_w_tau_score']['Value']}",
        f"- AUC high-vs-low Ar: {lookup['auc_high_vs_low_Ar']['Value']}",
        f"- Pearson Ar/Vmax vs W_tau_eff score: {lookup['pearson_ArOverVmaxPercent_vs_w_tau_score']['Value']}",
        f"- AUC high-vs-low Ar/Vmax: {lookup['auc_high_vs_low_ArOverVmaxPercent']['Value']}",
        f"- Decision: {decisions[0]['Status']}",
        "",
        "## Interpretation",
        "",
        "The expanded THINGS control still does not reproduce the WHISP-positive direction. In this overlap, larger published non-circular amplitudes do not imply larger `W_tau_eff` scores. This weakens a simple non-circular-amplitude-only explanation, while remaining below the N>=15 validation threshold.",
        "",
        "## Generated Files",
        "",
        "- `things_table3_expanded_control_readout_join_v01.csv`",
        "- `things_table3_expanded_control_readout_metrics_v01.csv`",
        "- `things_table3_expanded_control_readout_decision_v01.csv`",
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
    manifest["things_table3_expanded_control_readout_status"] = (
        "does_not_absorb_WHISP_direction_control_only_below_N15"
    )
    manifest["paper2_next_gate"] = "non_WHISP_resolved_HI_replication"
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
            "PublishedName",
            "MedianNonCircularAmplitudeKms",
            "ArSplit",
            "ArMedianCutoff",
            "NonCircularAmplitudeOverVmaxPercent",
            "ArOverVmaxSplit",
            "ArOverVmaxMedianCutoff",
            "MedianAbsResidualVelocityAfterHarmonicKms",
            "HasLocalSparcRotmod",
            "LocalRotmodPath",
            "ScoreSource",
            "ScoringStatus",
            "NPoints",
            "W_tau_eff_score_resolved_v01",
            "W_tau_eff_abs_v01",
            "W_tau_eff_signed_v01",
            "CandidateConfidenceTier",
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
    print(f"things_expanded_control_rows={len(rows)}")
    print(f"things_expanded_control_status={decisions[0]['Status']}")


if __name__ == "__main__":
    main()
