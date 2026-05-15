#!/usr/bin/env python3
"""Evaluate Yu et al. 2022 ALFALFA Af/Ac direction against frozen W_tau_eff scores."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


COVERAGE = PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_v01.csv"
SCORES = PACKET / "yu2022_alfalfa_expanded_w_tau_eff_scores_v01.csv"
JOIN_OUT = PACKET / "yu2022_alfalfa_af_ac_w_tau_eff_join_v01.csv"
METRIC_OUT = PACKET / "yu2022_alfalfa_af_ac_w_tau_eff_metrics_v01.csv"
DECISION_OUT = PACKET / "yu2022_alfalfa_af_ac_w_tau_eff_decision_v01.csv"
REPORT = PACKET / "yu2022_alfalfa_af_ac_directional_readout_v01.md"

GUARDRAIL = "yu2022_alfalfa_af_ac_directional_readout_no_fit_no_claim"


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


def indexed(path: Path, key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in read_csv(path)}


def proxy_values(row: dict[str, str]) -> dict[str, float]:
    af = float(row["Af"])
    ac = float(row["Ac"])
    return {
        "Af": af,
        "Ac": ac,
        "MaxAfAc": max(af, ac),
        "MeanAfAc": (af + ac) / 2.0,
        "LogMaxAfAc": math.log(max(af, ac)),
        "ExcessMaxAfAc": max(af, ac) - 1.0,
    }


def asymmetry_tier(max_af_ac: float) -> str:
    if max_af_ac >= 1.20:
        return "high_profile_asymmetry"
    if max_af_ac >= 1.10:
        return "medium_profile_asymmetry"
    return "low_profile_asymmetry"


def joined_rows() -> list[dict[str, str]]:
    coverage = indexed(COVERAGE, "CanonicalSPARCNameCandidate")
    rows: list[dict[str, str]] = []
    for score in read_csv(SCORES):
        if score["W_tau_eff_readout_score_v01"] == "":
            continue
        galaxy = score["GalaxyName"]
        source = coverage[galaxy]
        proxy = proxy_values(source)
        rows.append(
            {
                "GalaxyName": galaxy,
                "AGC": score["AGC"],
                "FreezeRole": score["FreezeRole"],
                "ScoreSource": score["ScoreSource"],
                "Af": source["Af"],
                "Ac": source["Ac"],
                "MaxAfAc": fmt(proxy["MaxAfAc"]),
                "MeanAfAc": fmt(proxy["MeanAfAc"]),
                "LogMaxAfAc": fmt(proxy["LogMaxAfAc"]),
                "ExcessMaxAfAc": fmt(proxy["ExcessMaxAfAc"]),
                "ProfileAsymmetryTier": asymmetry_tier(proxy["MaxAfAc"]),
                "SN": source["SN"],
                "W_tau_eff_readout_score_v01": score["W_tau_eff_readout_score_v01"],
                "W_tau_eff_signed_v01": score["W_tau_eff_signed_v01"],
                "W_tau_eff_abs_v01": score["W_tau_eff_abs_v01"],
                "CandidateConfidenceTier": score["CandidateConfidenceTier"],
                "ReadoutUse": "frozen_yu2022_af_ac_direction_vs_committed_w_tau_eff_score",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    score = [float(row["W_tau_eff_readout_score_v01"]) for row in rows]
    signed = [float(row["W_tau_eff_signed_v01"]) for row in rows]
    abs_weight = [float(row["W_tau_eff_abs_v01"]) for row in rows]
    high = [row for row in rows if row["ProfileAsymmetryTier"] == "high_profile_asymmetry"]
    low = [row for row in rows if row["ProfileAsymmetryTier"] == "low_profile_asymmetry"]
    medium = [row for row in rows if row["ProfileAsymmetryTier"] == "medium_profile_asymmetry"]
    metrics = [
        {
            "Metric": "coverage_directional_readout_rows",
            "N": str(len(rows)),
            "Value": str(len(rows)),
            "SecondaryValue": (
                f"low={len(low)};medium={len(medium)};high={len(high)}"
            ),
            "InterpretationGuardrail": GUARDRAIL,
        }
    ]
    for proxy in ["Af", "Ac", "MaxAfAc", "MeanAfAc", "LogMaxAfAc", "ExcessMaxAfAc"]:
        values = [float(row[proxy]) for row in rows]
        metrics.extend(
            [
                {
                    "Metric": f"pearson_{proxy}_vs_w_tau_score",
                    "N": str(len(rows)),
                    "Value": fmt(pearson(values, score)),
                    "SecondaryValue": "higher profile asymmetry expected higher W_tau_eff",
                    "InterpretationGuardrail": GUARDRAIL,
                },
                {
                    "Metric": f"spearman_{proxy}_vs_w_tau_score",
                    "N": str(len(rows)),
                    "Value": fmt(spearman(values, score)),
                    "SecondaryValue": "rank direction only",
                    "InterpretationGuardrail": GUARDRAIL,
                },
            ]
        )
    metrics.extend(
        [
            {
                "Metric": "auc_high_vs_low_profile_asymmetry_score",
                "N": str(len(high) + len(low)),
                "Value": fmt(
                    auc_high_higher(
                        [float(row["W_tau_eff_readout_score_v01"]) for row in high],
                        [float(row["W_tau_eff_readout_score_v01"]) for row in low],
                    )
                ),
                "SecondaryValue": "high profile asymmetry expected higher",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "median_score_low_profile_asymmetry",
                "N": str(len(low)),
                "Value": fmt(median([float(row["W_tau_eff_readout_score_v01"]) for row in low])),
                "SecondaryValue": "",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "median_score_medium_profile_asymmetry",
                "N": str(len(medium)),
                "Value": fmt(
                    median([float(row["W_tau_eff_readout_score_v01"]) for row in medium])
                ),
                "SecondaryValue": "",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "median_score_high_profile_asymmetry",
                "N": str(len(high)),
                "Value": fmt(median([float(row["W_tau_eff_readout_score_v01"]) for row in high])),
                "SecondaryValue": "",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "pearson_logmaxafac_vs_abs_w_tau",
                "N": str(len(rows)),
                "Value": fmt(pearson([float(row["LogMaxAfAc"]) for row in rows], abs_weight)),
                "SecondaryValue": "absolute residual-weight direction",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "pearson_logmaxafac_vs_signed_w_tau",
                "N": str(len(rows)),
                "Value": fmt(pearson([float(row["LogMaxAfAc"]) for row in rows], signed)),
                "SecondaryValue": "signed direction retained as diagnostic only",
                "InterpretationGuardrail": GUARDRAIL,
            },
        ]
    )
    return metrics


def decision_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in metrics}
    n = int(lookup["coverage_directional_readout_rows"]["N"])
    rho = float(lookup["spearman_LogMaxAfAc_vs_w_tau_score"]["Value"])
    auc = float(lookup["auc_high_vs_low_profile_asymmetry_score"]["Value"])
    support = rho > 0 and auc > 0.5
    return [
        {
            "DecisionID": "YU22R01",
            "Decision": "directional_signal_status",
            "Status": "weak_positive" if support else "not_supported",
            "N": str(n),
            "PassCondition": "Spearman(LogMaxAfAc,W_tau_eff)>0 and high-vs-low AUC>0.5",
            "NextAction": "treat_as_external_hint_not_validation_if_effect_is_weak",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "YU22R02",
            "Decision": "claim_boundary",
            "Status": "no_model_validation_claim",
            "N": str(n),
            "PassCondition": "Yu Af/Ac is global HI profile asymmetry, not a direct local S_tau field measurement",
            "NextAction": "seek_spatially_resolved_or_held_out_kinematic_proxy",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    decisions_by_id = {row["DecisionID"]: row for row in decisions}
    lines = [
        "# Yu 2022 ALFALFA Af/Ac Directional Readout v0.1",
        "",
        "This packet evaluates whether global ALFALFA HI profile asymmetry from Yu et al. (2022) points in the expected direction against the committed expanded `W_tau_eff` score. It does not fit coefficients and does not validate a Tau Core field model.",
        "",
        "## Frozen Direction",
        "",
        "The predeclared directional expectation is that larger global HI profile asymmetry (`Af`/`Ac`) should be associated with larger residual-inferred `W_tau_eff` score.",
        "",
        "## Main Readout",
        "",
        f"- Readout rows: {lookup['coverage_directional_readout_rows']['Value']} ({lookup['coverage_directional_readout_rows']['SecondaryValue']})",
        f"- Spearman(LogMaxAfAc, W_tau_eff score): {lookup['spearman_LogMaxAfAc_vs_w_tau_score']['Value']}",
        f"- Pearson(LogMaxAfAc, W_tau_eff score): {lookup['pearson_LogMaxAfAc_vs_w_tau_score']['Value']}",
        f"- AUC high-vs-low profile asymmetry: {lookup['auc_high_vs_low_profile_asymmetry_score']['Value']}",
        f"- Median score low/medium/high: {lookup['median_score_low_profile_asymmetry']['Value']} / {lookup['median_score_medium_profile_asymmetry']['Value']} / {lookup['median_score_high_profile_asymmetry']['Value']}",
        f"- Directional signal status: {decisions_by_id['YU22R01']['Status']}",
        "",
        "## Interpretation",
        "",
        "This is a source-side external hint, not a validation. `Af` and `Ac` are global unresolved HI profile asymmetry measures, whereas `W_tau_eff` is a residual-shape score derived from rotation-curve structure. A positive but weak readout would support continued external validation work; it would not establish a physical Tau Core map.",
        "",
        "## Generated Files",
        "",
        "- `yu2022_alfalfa_af_ac_w_tau_eff_join_v01.csv`",
        "- `yu2022_alfalfa_af_ac_w_tau_eff_metrics_v01.csv`",
        "- `yu2022_alfalfa_af_ac_w_tau_eff_decision_v01.csv`",
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
    manifest["yu2022_alfalfa_af_ac_directional_readout_status"] = (
        "weak_external_source_side_directional_hint_not_validation"
    )
    manifest["paper2_next_gate"] = "spatially_resolved_or_held_out_kinematic_proxy_validation"
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
            "AGC",
            "FreezeRole",
            "ScoreSource",
            "Af",
            "Ac",
            "MaxAfAc",
            "MeanAfAc",
            "LogMaxAfAc",
            "ExcessMaxAfAc",
            "ProfileAsymmetryTier",
            "SN",
            "W_tau_eff_readout_score_v01",
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
    write_csv(
        DECISION_OUT,
        decisions,
        [
            "DecisionID",
            "Decision",
            "Status",
            "N",
            "PassCondition",
            "NextAction",
            "InterpretationGuardrail",
        ],
    )
    write_report(metrics, decisions)
    update_manifest()
    print(REPORT)
    print(f"yu2022_directional_rows={len(rows)}")
    print(f"yu2022_directional_status={decisions[0]['Status']}")


if __name__ == "__main__":
    main()
