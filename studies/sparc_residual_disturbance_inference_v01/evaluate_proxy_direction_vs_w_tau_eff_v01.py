#!/usr/bin/env python3
"""Evaluate frozen P01 proxy direction against W_tau_eff candidate score."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET, ROOT


W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
EVIDENCE = (
    ROOT
    / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/external_evidence_table.csv"
)
JOIN_OUT = PACKET / "proxy_direction_w_tau_eff_join_v01.csv"
METRIC_OUT = PACKET / "proxy_direction_w_tau_eff_metric_summary_v01.csv"
REPORT = PACKET / "proxy_direction_w_tau_eff_readout_v01.md"

GUARDRAIL = "proxy_direction_readout_no_velocity_endpoint_no_coefficient_fit"


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


def auc_high_higher(rows: list[dict[str, str]], field: str) -> float:
    high = [float(row[field]) for row in rows if row["P01BurdenTier"] == "high"]
    low = [float(row[field]) for row in rows if row["P01BurdenTier"] == "low"]
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


def p01_burden(evidence_type: str) -> tuple[str, float | None]:
    low = {"regular_kinematics", "low_asymmetry"}
    high = {"disturbed_hi", "tidal", "interaction", "warp"}
    if evidence_type in low:
        return "low", 0.0
    if evidence_type == "mixed":
        return "medium", 0.5
    if evidence_type in high:
        return "high", 1.0
    return "unscored", None


def joined_rows() -> list[dict[str, str]]:
    w_tau = {row["GalaxyName"]: row for row in read_csv(W_TAU)}
    rows: list[dict[str, str]] = []
    for evidence in read_csv(EVIDENCE):
        galaxy = evidence["GalaxyName"]
        if galaxy not in w_tau:
            continue
        tier, numeric = p01_burden(evidence["EvidenceType"])
        target = w_tau[galaxy]
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": evidence["Class"],
                "EvidenceType": evidence["EvidenceType"],
                "Confidence": evidence["Confidence"],
                "QualityPass": evidence["QualityPass"],
                "ResidualBlind": evidence["ResidualBlind"],
                "P01BurdenTier": tier,
                "P01BurdenOrdinal": "" if numeric is None else fmt(numeric),
                "W_tau_eff_candidate_score_v01": target["W_tau_eff_candidate_score_v01"],
                "W_tau_eff_signed_v01": target["W_tau_eff_signed_v01"],
                "W_tau_eff_abs_v01": target["W_tau_eff_abs_v01"],
                "CandidateConfidenceTier": target["CandidateConfidenceTier"],
                "ReadoutUse": "frozen_P01_direction_vs_existing_W_tau_eff_no_velocity_endpoint",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    scored = [row for row in rows if row["P01BurdenTier"] in {"low", "medium", "high"}]
    low = [row for row in rows if row["P01BurdenTier"] == "low"]
    medium = [row for row in rows if row["P01BurdenTier"] == "medium"]
    high = [row for row in rows if row["P01BurdenTier"] == "high"]
    ordinal = [float(row["P01BurdenOrdinal"]) for row in scored]
    score = [float(row["W_tau_eff_candidate_score_v01"]) for row in scored]
    signed = [float(row["W_tau_eff_signed_v01"]) for row in scored]
    abs_weight = [float(row["W_tau_eff_abs_v01"]) for row in scored]
    return [
        {
            "Metric": "coverage_joined",
            "N": str(len(rows)),
            "Value": str(len(rows)),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "coverage_scored_low_medium_high",
            "N": str(len(scored)),
            "Value": str(len(scored)),
            "SecondaryValue": f"low={len(low)};medium={len(medium)};high={len(high)}",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "median_score_low",
            "N": str(len(low)),
            "Value": fmt(median([float(row["W_tau_eff_candidate_score_v01"]) for row in low])),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "median_score_medium",
            "N": str(len(medium)),
            "Value": fmt(median([float(row["W_tau_eff_candidate_score_v01"]) for row in medium])),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "median_score_high",
            "N": str(len(high)),
            "Value": fmt(median([float(row["W_tau_eff_candidate_score_v01"]) for row in high])),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_high_vs_low_score",
            "N": str(len(low) + len(high)),
            "Value": fmt(auc_high_higher(scored, "W_tau_eff_candidate_score_v01")),
            "SecondaryValue": "high burden expected higher",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_ordinal_vs_score",
            "N": str(len(scored)),
            "Value": fmt(pearson(ordinal, score)),
            "SecondaryValue": "low=0;medium=0.5;high=1",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_ordinal_vs_abs_w_tau",
            "N": str(len(scored)),
            "Value": fmt(pearson(ordinal, abs_weight)),
            "SecondaryValue": "low=0;medium=0.5;high=1",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_ordinal_vs_signed_w_tau",
            "N": str(len(scored)),
            "Value": fmt(pearson(ordinal, signed)),
            "SecondaryValue": "signed direction retained for diagnostics only",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    medium_value = lookup["median_score_medium"]["Value"] or "not_applicable_no_medium_cases"
    lines = [
        "# Proxy Direction vs W_tau_eff Readout v0.1",
        "",
        "This readout evaluates the frozen P01 direction against the already-defined `W_tau_eff` candidate score. It does not evaluate velocity residuals, does not fit coefficients, and does not define `S_tau_full`.",
        "",
        "## Frozen P01 Direction",
        "",
        "- `regular_kinematics` and `low_asymmetry`: low burden",
        "- `mixed`: medium burden",
        "- `disturbed_hi`, `tidal`, `interaction`, and `warp`: high burden",
        "- `other` and `no_data`: unscored for the primary directional metric",
        "",
        "## Main Readout",
        "",
        f"- Joined galaxies: {lookup['coverage_joined']['Value']}",
        f"- Scored low/medium/high galaxies: {lookup['coverage_scored_low_medium_high']['Value']} ({lookup['coverage_scored_low_medium_high']['SecondaryValue']})",
        f"- Median W_tau_eff candidate score, low burden: {lookup['median_score_low']['Value']}",
        f"- Median W_tau_eff candidate score, medium burden: {medium_value}",
        f"- Median W_tau_eff candidate score, high burden: {lookup['median_score_high']['Value']}",
        f"- AUC high-vs-low score: {lookup['auc_high_vs_low_score']['Value']}",
        f"- Pearson ordinal burden vs score: {lookup['pearson_ordinal_vs_score']['Value']}",
        "",
        "## Interpretation",
        "",
        "A positive directional readout supports using residual-blind external evidence as a broad `W_env_obs` prior. A weak, null, or reversed readout would mean that the residual-inferred candidate is not captured by this coarse source-side proxy and must not be promoted to a velocity formula.",
        "",
        "## Generated Files",
        "",
        "- `proxy_direction_w_tau_eff_join_v01.csv`",
        "- `proxy_direction_w_tau_eff_metric_summary_v01.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "proxy_direction_w_tau_eff_readout_v01.md",
            "proxy_direction_w_tau_eff_join_v01.csv",
            "proxy_direction_w_tau_eff_metric_summary_v01.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["proxy_direction_w_tau_eff_status"] = "frozen_P01_direction_readout_complete_no_velocity_endpoint"
    manifest["paper2_next_gate"] = "P07_source_family_holdout_for_w_env_obs_direction"
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
            "EvidenceType",
            "Confidence",
            "QualityPass",
            "ResidualBlind",
            "P01BurdenTier",
            "P01BurdenOrdinal",
            "W_tau_eff_candidate_score_v01",
            "W_tau_eff_signed_v01",
            "W_tau_eff_abs_v01",
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
    write_report(metrics)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
