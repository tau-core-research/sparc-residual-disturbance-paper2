#!/usr/bin/env python3
"""Evaluate HALOGAS moment proxy against W_tau_eff without opening velocity endpoint."""

from __future__ import annotations

import csv
import json
import math

from make_packet_v01_seed import PACKET, read_csv, write_csv


JOIN = PACKET / "halogas_moment_w_tau_eff_join_v01.csv"
METRICS = PACKET / "halogas_moment_proxy_metrics_v01.csv"
DECISION = PACKET / "halogas_moment_proxy_decision_v01.csv"
REPORT = PACKET / "halogas_moment_proxy_readout_v01.md"

GUARDRAIL = "halogas_moment_proxy_small_overlap_no_velocity_endpoint"


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


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    score = [float(row["W_tau_eff_candidate_score_v01"]) for row in rows]
    stress = [float(row["HALOGAS_moment_stress_proxy_v01"]) for row in rows]
    cutoff = median(stress)
    high = [
        float(row["W_tau_eff_candidate_score_v01"])
        for row in rows
        if float(row["HALOGAS_moment_stress_proxy_v01"]) > cutoff
    ]
    low = [
        float(row["W_tau_eff_candidate_score_v01"])
        for row in rows
        if float(row["HALOGAS_moment_stress_proxy_v01"]) <= cutoff
    ]
    class_set = ";".join(sorted({row["Class"] for row in rows}))
    return [
        {
            "Metric": "coverage_joined",
            "N": str(len(rows)),
            "Value": str(len(rows)),
            "SecondaryValue": class_set,
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_halogas_moment_stress_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(stress, score)),
            "SecondaryValue": "higher HALOGAS moment proxy expected higher W_tau_eff if aligned",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_high_vs_low_halogas_moment_stress",
            "N": str(len(rows)),
            "Value": fmt(auc_high_higher(high, low)),
            "SecondaryValue": "median split; high stress expected higher W_tau_eff if aligned",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "median_score_low_halogas_moment_stress",
            "N": str(len(low)),
            "Value": fmt(median(low)),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "median_score_high_halogas_moment_stress",
            "N": str(len(high)),
            "Value": fmt(median(high)),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def decision_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in metrics}
    pearson_value = float(lookup["pearson_halogas_moment_stress_vs_w_tau_score"]["Value"])
    auc_value = float(lookup["auc_high_vs_low_halogas_moment_stress"]["Value"])
    if pearson_value >= 0.3 and auc_value >= 0.6:
        status = "positive_but_small_halogas_support"
        next_action = "expand_HALOGAS_or_non_WHISP_HI_family_before_claim"
    else:
        status = "weak_or_null_halogas_moment_proxy_control"
        next_action = "retain_HALOGAS_as_weak_control_prioritize_THINGS_or_non_WHISP_asymmetry"
    return [
        {
            "DecisionID": "HMP01",
            "Decision": "HALOGAS_moment_proxy_vs_W_tau_eff",
            "Status": status,
            "Rationale": (
                "Pearson="
                + lookup["pearson_halogas_moment_stress_vs_w_tau_score"]["Value"]
                + "; AUC="
                + lookup["auc_high_vs_low_halogas_moment_stress"]["Value"]
                + "; N="
                + lookup["coverage_joined"]["N"]
                + "."
            ),
            "Blocks": "velocity_formula;strong_external_validation_claim",
            "NextAction": next_action,
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "HMP02",
            "Decision": "endpoint_status",
            "Status": "velocity_endpoint_still_closed",
            "Rationale": "Five HALOGAS overlap galaxies are sufficient only for a weak control readout.",
            "Blocks": "S_tau_full_velocity_readout",
            "NextAction": "do_not_fit_coefficients_on_HALOGAS_overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    lines = [
        "# HALOGAS Moment Proxy Readout v0.1",
        "",
        "This readout tests whether derived HALOGAS moment-map proxy features align with `W_tau_eff`. It is a small-overlap external control and does not open a velocity endpoint.",
        "",
        "## Metrics",
        "",
        f"- Joined galaxies: {lookup['coverage_joined']['Value']} ({lookup['coverage_joined']['SecondaryValue']})",
        f"- Pearson: {lookup['pearson_halogas_moment_stress_vs_w_tau_score']['Value']}",
        f"- AUC high-vs-low stress: {lookup['auc_high_vs_low_halogas_moment_stress']['Value']}",
        "",
        "## Decision",
        "",
        f"`{decisions[0]['Status']}`",
        "",
        decisions[0]["Rationale"],
        "",
        "## Generated Files",
        "",
        "- `halogas_moment_proxy_metrics_v01.csv`",
        "- `halogas_moment_proxy_decision_v01.csv`",
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
    for path in [METRICS, DECISION, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["halogas_moment_proxy_readout_status"] = (
        "small_overlap_weak_or_null_control_complete_no_velocity_endpoint"
    )
    manifest["paper2_next_gate"] = "THINGS_or_non_WHISP_asymmetry_expansion"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = read_csv(JOIN)
    metrics = metric_rows(rows)
    decisions = decision_rows(metrics)
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
    write_csv(METRICS, metrics, metric_fields)
    write_csv(DECISION, decisions, decision_fields)
    write_report(metrics, decisions)
    update_manifest()


if __name__ == "__main__":
    main()
