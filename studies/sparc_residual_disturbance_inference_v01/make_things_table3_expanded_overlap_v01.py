#!/usr/bin/env python3
"""Curate THINGS Table 3 and join the expanded overlap to W_tau_eff."""

from __future__ import annotations

import json
import math

from make_packet_v01_seed import PACKET, read_csv, write_csv


W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
TABLE_OUT = PACKET / "things_trachternach2008_table3_v01.csv"
JOIN_OUT = PACKET / "things_table3_w_tau_eff_overlap_v01.csv"
METRIC_OUT = PACKET / "things_table3_w_tau_eff_metrics_v01.csv"
DECISION_OUT = PACKET / "things_table3_expansion_decision_v01.csv"
REPORT = PACKET / "things_table3_expanded_overlap_v01.md"

GUARDRAIL = "things_table3_published_control_no_velocity_endpoint"


TABLE3 = [
    ("NGC925", "NGC 925", 6.30, 9.45, 5.5, 0.000, 0.046, 3.0, 282),
    ("NGC2366", "NGC 2366", 2.94, 1.17, 5.3, 0.004, 0.066, 2.4, 252),
    ("NGC2403", "NGC 2403", 4.03, 2.60, 3.0, -0.022, 0.025, 2.9, 950),
    ("NGC2841", "NGC 2841", 6.71, math.nan, 2.6, -0.001, 0.014, 3.5, 635),
    ("NGC2903", "NGC 2903", 6.10, 13.55, 3.2, 0.006, 0.028, 2.8, 602),
    ("NGC2976", "NGC 2976", 2.81, 2.18, 3.5, -0.010, 0.018, 2.1, 147),
    ("NGC3031", "NGC 3031", 9.14, math.nan, 4.6, 0.007, 0.045, 3.0, 840),
    ("NGC3198", "NGC 3198", 4.49, 1.50, 3.0, 0.016, 0.020, 2.6, 565),
    ("IC2574", "IC 2574", 3.75, 1.36, 5.4, 0.012, 0.047, 2.7, 505),
    ("NGC3521", "NGC 3521", 8.80, 3.12, 4.2, 0.017, 0.019, 4.5, 415),
    ("NGC3621", "NGC 3621", 3.36, 5.52, 2.4, 0.002, 0.022, 2.3, 600),
    ("NGC3627", "NGC 3627", 28.49, math.nan, 14.7, -0.024, 0.071, 3.6, 165),
    ("NGC4736", "NGC 4736", 10.01, 8.79, 8.3, -0.055, 0.149, 2.5, 400),
    ("DDO154", "DDO 154", 1.61, 1.43, 3.4, 0.024, 0.033, 1.2, 325),
    ("NGC5055", "NGC 5055", 4.11, 8.38, 2.2, -0.003, 0.025, 3.1, 450),
    ("NGC6946", "NGC 6946", 7.28, math.nan, 3.6, 0.004, 0.069, 3.4, 420),
    ("NGC7331", "NGC 7331", 5.94, math.nan, 2.6, -0.003, 0.017, 4.2, 297),
    ("NGC7793", "NGC 7793", 5.08, 3.41, 3.9, -0.067, 0.085, 2.2, 372),
]


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


def table_rows() -> list[dict[str, str]]:
    outputs = []
    for row in TABLE3:
        (
            canonical,
            published,
            ar,
            ar_1kpc,
            ar_over_vmax,
            eps,
            eps_err,
            mresid,
            rmax,
        ) = row
        outputs.append(
            {
                "GalaxyName": canonical,
                "PublishedName": published,
                "MedianNonCircularAmplitudeKms": fmt(ar),
                "MedianNonCircularAmplitudeInner1KpcKms": fmt(ar_1kpc),
                "NonCircularAmplitudeOverVmaxPercent": fmt(ar_over_vmax),
                "PotentialElongationMean": fmt(eps),
                "PotentialElongationUncertainty": fmt(eps_err),
                "MedianAbsResidualVelocityAfterHarmonicKms": fmt(mresid),
                "RmaxArcsec": fmt(rmax),
                "Source": "Trachternach_etal_2008_Table3",
                "AllowedUse": "published_non_circular_motion_control_only",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return outputs


def join_rows(table: list[dict[str, str]]) -> list[dict[str, str]]:
    w_tau = {row["GalaxyName"]: row for row in read_csv(W_TAU)}
    outputs = []
    for row in table:
        if row["GalaxyName"] not in w_tau:
            continue
        target = w_tau[row["GalaxyName"]]
        outputs.append(
            {
                **row,
                "Class": target["Class"],
                "W_tau_eff_candidate_score_v01": target[
                    "W_tau_eff_candidate_score_v01"
                ],
                "CandidateConfidenceTier": target["CandidateConfidenceTier"],
                "ReadoutUse": "THINGS_Table3_expanded_overlap_no_velocity_endpoint",
            }
        )
    return outputs


def metric_rows(joined: list[dict[str, str]]) -> list[dict[str, str]]:
    valid = [
        row
        for row in joined
        if row["MedianNonCircularAmplitudeKms"] and row["W_tau_eff_candidate_score_v01"]
    ]
    burden = [float(row["MedianNonCircularAmplitudeKms"]) for row in valid]
    score = [float(row["W_tau_eff_candidate_score_v01"]) for row in valid]
    cutoff = median(burden)
    high = [
        float(row["W_tau_eff_candidate_score_v01"])
        for row in valid
        if float(row["MedianNonCircularAmplitudeKms"]) > cutoff
    ]
    low = [
        float(row["W_tau_eff_candidate_score_v01"])
        for row in valid
        if float(row["MedianNonCircularAmplitudeKms"]) <= cutoff
    ]
    return [
        {
            "Metric": "things_table3_total_rows",
            "N": str(len(TABLE3)),
            "Value": str(len(TABLE3)),
            "SecondaryValue": "published Table 3 rows",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "things_table3_w_tau_overlap",
            "N": str(len(joined)),
            "Value": str(len(joined)),
            "SecondaryValue": ";".join(sorted({row["Class"] for row in joined})),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_table3_ar_vs_w_tau_score",
            "N": str(len(valid)),
            "Value": fmt(pearson(burden, score)),
            "SecondaryValue": "Table3 median non-circular amplitude vs W_tau_eff",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_high_vs_low_table3_ar",
            "N": str(len(valid)),
            "Value": fmt(auc_high_higher(high, low)),
            "SecondaryValue": "median split on Table3 median non-circular amplitude",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "minimum_directional_n_gate",
            "N": str(len(valid)),
            "Value": "not_met",
            "SecondaryValue": "requires N>=12 from frozen target plan",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def decision_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in metrics}
    return [
        {
            "DecisionID": "T3D01",
            "Decision": "THINGS_Table3_expansion_gate",
            "Status": "expanded_overlap_available_but_below_minimum_n",
            "Rationale": (
                "Overlap N="
                + lookup["things_table3_w_tau_overlap"]["Value"]
                + "; frozen minimum N=12."
            ),
            "Blocks": "paper_grade_THINGS_external_validation_claim",
            "NextAction": "retain_as_small_control_seek_non_WHISP_asymmetry_or_additional_THINGS_compatible_sources",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "T3D02",
            "Decision": "velocity_endpoint_status",
            "Status": "closed",
            "Rationale": "Published THINGS harmonic quantities are external controls only.",
            "Blocks": "S_tau_full_velocity_formula",
            "NextAction": "do_not_fit_coefficients_on_THINGS_Table3_overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    lines = [
        "# THINGS Table 3 Expanded Overlap v0.1",
        "",
        "This packet curates the published THINGS harmonic-decomposition Table 3 values and joins the exact-name overlap to `W_tau_eff`. It is an external-control readout only and does not open a velocity endpoint.",
        "",
        "## Metrics",
        "",
        f"- Published Table 3 rows: {lookup['things_table3_total_rows']['Value']}",
        f"- `W_tau_eff` overlap: {lookup['things_table3_w_tau_overlap']['Value']}",
        f"- Pearson Ar vs W_tau_eff: {lookup['pearson_table3_ar_vs_w_tau_score']['Value']}",
        f"- AUC high-vs-low Ar: {lookup['auc_high_vs_low_table3_ar']['Value']}",
        f"- Minimum N gate: {lookup['minimum_directional_n_gate']['Value']}",
        "",
        "## Decision",
        "",
        f"`{decisions[0]['Status']}`",
        "",
        decisions[0]["Rationale"],
        "",
        "## Generated Files",
        "",
        "- `things_trachternach2008_table3_v01.csv`",
        "- `things_table3_w_tau_eff_overlap_v01.csv`",
        "- `things_table3_w_tau_eff_metrics_v01.csv`",
        "- `things_table3_expansion_decision_v01.csv`",
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
    for path in [TABLE_OUT, JOIN_OUT, METRIC_OUT, DECISION_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_table3_expanded_overlap_status"] = (
        "published_table3_overlap_complete_below_minimum_n_no_velocity_endpoint"
    )
    manifest["paper2_next_gate"] = "non_WHISP_resolved_HI_asymmetry_crossmatch"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    table = table_rows()
    joined = join_rows(table)
    metrics = metric_rows(joined)
    decisions = decision_rows(metrics)
    table_fields = [
        "GalaxyName",
        "PublishedName",
        "MedianNonCircularAmplitudeKms",
        "MedianNonCircularAmplitudeInner1KpcKms",
        "NonCircularAmplitudeOverVmaxPercent",
        "PotentialElongationMean",
        "PotentialElongationUncertainty",
        "MedianAbsResidualVelocityAfterHarmonicKms",
        "RmaxArcsec",
        "Source",
        "AllowedUse",
        "InterpretationGuardrail",
    ]
    join_fields = table_fields + [
        "Class",
        "W_tau_eff_candidate_score_v01",
        "CandidateConfidenceTier",
        "ReadoutUse",
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
    write_csv(TABLE_OUT, table, table_fields)
    write_csv(JOIN_OUT, joined, join_fields)
    write_csv(METRIC_OUT, metrics, metric_fields)
    write_csv(DECISION_OUT, decisions, decision_fields)
    write_report(metrics, decisions)
    update_manifest()


if __name__ == "__main__":
    main()
