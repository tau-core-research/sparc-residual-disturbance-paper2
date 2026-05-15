#!/usr/bin/env python3
"""Evaluate the frozen P07 WHISP holdout direction against W_tau_eff."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET


W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
WHISP = PACKET / "whisp_vaneymeren2011_overlap.csv"
JOIN_OUT = PACKET / "p07_whisp_w_tau_eff_holdout_join_v01.csv"
METRIC_OUT = PACKET / "p07_whisp_w_tau_eff_holdout_metric_summary_v01.csv"
REPORT = PACKET / "p07_whisp_w_tau_eff_holdout_v01.md"

ASYMMETRY_FIELDS = [
    "A1_outer_gt_R25",
    "A1_inner_lt_R25",
    "A2_outer_gt_R25",
    "A2_inner_lt_R25",
    "A3_outer_gt_R25",
    "A3_inner_lt_R25",
    "A1_1ltRwlt2",
    "A2_1ltRwlt2",
    "A3_1ltRwlt2",
    "EpsilonKin",
]
GUARDRAIL = "p07_source_family_holdout_no_velocity_endpoint_no_coefficient_fit"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


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


def whisp_burden(row: dict[str, str]) -> float:
    values = [float(row[field]) for field in ASYMMETRY_FIELDS if row.get(field, "") != ""]
    return mean(values)


def joined_rows() -> list[dict[str, str]]:
    w_tau = {row["GalaxyName"]: row for row in read_csv(W_TAU)}
    raw: list[dict[str, str]] = []
    for whisp in read_csv(WHISP):
        galaxy = whisp["GalaxyName"]
        if galaxy not in w_tau:
            continue
        target = w_tau[galaxy]
        burden = whisp_burden(whisp)
        raw.append(
            {
                "GalaxyName": galaxy,
                "Class": whisp["Class"],
                "WHISP_BurdenScore_v01": fmt(burden),
                "W_tau_eff_candidate_score_v01": target["W_tau_eff_candidate_score_v01"],
                "W_tau_eff_abs_v01": target["W_tau_eff_abs_v01"],
                "W_tau_eff_signed_v01": target["W_tau_eff_signed_v01"],
                "A1_outer_gt_R25": whisp["A1_outer_gt_R25"],
                "A2_outer_gt_R25": whisp["A2_outer_gt_R25"],
                "A3_outer_gt_R25": whisp["A3_outer_gt_R25"],
                "EpsilonKin": whisp["EpsilonKin"],
                "ReadoutUse": "P07_WHISP_source_family_holdout_no_velocity_endpoint",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    cutoff = median([float(row["WHISP_BurdenScore_v01"]) for row in raw])
    for row in raw:
        row["WHISP_BurdenSplit"] = "high" if float(row["WHISP_BurdenScore_v01"]) > cutoff else "low"
        row["WHISP_BurdenMedianCutoff"] = fmt(cutoff)
    return raw


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    burden = [float(row["WHISP_BurdenScore_v01"]) for row in rows]
    score = [float(row["W_tau_eff_candidate_score_v01"]) for row in rows]
    abs_weight = [float(row["W_tau_eff_abs_v01"]) for row in rows]
    high = [float(row["W_tau_eff_candidate_score_v01"]) for row in rows if row["WHISP_BurdenSplit"] == "high"]
    low = [float(row["W_tau_eff_candidate_score_v01"]) for row in rows if row["WHISP_BurdenSplit"] == "low"]
    return [
        {
            "Metric": "coverage_joined",
            "N": str(len(rows)),
            "Value": str(len(rows)),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_whisp_burden_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(burden, score)),
            "SecondaryValue": "higher WHISP burden expected higher W_tau_eff candidate score",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_whisp_burden_vs_abs_w_tau",
            "N": str(len(rows)),
            "Value": fmt(pearson(burden, abs_weight)),
            "SecondaryValue": "absolute residual-inferred weight",
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
            "Metric": "auc_high_vs_low_whisp_burden",
            "N": str(len(high) + len(low)),
            "Value": fmt(auc_high_higher(high, low)),
            "SecondaryValue": "median split within WHISP overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    lines = [
        "# P07 WHISP Source-Family Holdout v0.1",
        "",
        "This readout evaluates the frozen P07 WHISP lopsidedness/asymmetry source family against `W_tau_eff`. It does not evaluate velocity residuals, does not fit coefficients, and does not define `S_tau_full`.",
        "",
        "## Frozen WHISP Burden",
        "",
        "`WHISP_BurdenScore_v01` is the mean of available published HI asymmetry amplitudes (`A1`, `A2`, `A3`) across inner/outer/radial windows plus `EpsilonKin`. Higher burden is expected to align with higher `W_tau_eff` candidate score.",
        "",
        "## Main Readout",
        "",
        f"- Joined galaxies: {lookup['coverage_joined']['Value']}",
        f"- Pearson WHISP burden vs W_tau_eff candidate score: {lookup['pearson_whisp_burden_vs_w_tau_score']['Value']}",
        f"- Pearson WHISP burden vs abs W_tau_eff: {lookup['pearson_whisp_burden_vs_abs_w_tau']['Value']}",
        f"- Median W_tau_eff score, low WHISP burden: {lookup['median_score_low_whisp_burden']['Value']}",
        f"- Median W_tau_eff score, high WHISP burden: {lookup['median_score_high_whisp_burden']['Value']}",
        f"- AUC high-vs-low WHISP burden: {lookup['auc_high_vs_low_whisp_burden']['Value']}",
        "",
        "## Interpretation",
        "",
        "A positive holdout readout supports the idea that a source-side HI asymmetry family carries part of the same `W_env_obs` direction as the broad P01 prior. Because the overlap is small and class-balanced controls are limited, this is a source-family sanity check rather than a final validation.",
        "",
        "## Generated Files",
        "",
        "- `p07_whisp_w_tau_eff_holdout_join_v01.csv`",
        "- `p07_whisp_w_tau_eff_holdout_metric_summary_v01.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "whisp_vaneymeren2011_overlap.csv",
            "p07_whisp_w_tau_eff_holdout_v01.md",
            "p07_whisp_w_tau_eff_holdout_join_v01.csv",
            "p07_whisp_w_tau_eff_holdout_metric_summary_v01.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["p07_whisp_holdout_status"] = "source_family_holdout_complete_no_velocity_endpoint"
    manifest["paper2_next_gate"] = "P03_P04_THINGS_small_overlap_sanity_or_systematics_competition"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = joined_rows()
    metrics = metric_rows(rows)
    write_csv(
        JOIN_OUT,
        rows,
        [
            "GalaxyName",
            "Class",
            "WHISP_BurdenScore_v01",
            "WHISP_BurdenSplit",
            "WHISP_BurdenMedianCutoff",
            "W_tau_eff_candidate_score_v01",
            "W_tau_eff_abs_v01",
            "W_tau_eff_signed_v01",
            "A1_outer_gt_R25",
            "A2_outer_gt_R25",
            "A3_outer_gt_R25",
            "EpsilonKin",
            "ReadoutUse",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        METRIC_OUT,
        metrics,
        ["Metric", "N", "Value", "SecondaryValue", "InterpretationGuardrail"],
    )
    write_report(metrics)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
