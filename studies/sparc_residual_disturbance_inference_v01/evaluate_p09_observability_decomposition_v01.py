#!/usr/bin/env python3
"""Evaluate galaxy-level P09 observability decomposition against W_tau_eff."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET, ROOT, read_csv, write_csv


TAU_CORE = ROOT.parent / "tau-core"
WORKBOOK = (
    TAU_CORE
    / "studies/sparc_residual_coherence_test_v01/external_proxy_review_workbook_v05_final.csv"
)
W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"

JOIN_OUT = PACKET / "p09_observability_decomposition_join_v01.csv"
METRIC_OUT = PACKET / "p09_observability_decomposition_metrics_v01.csv"
DECISION_OUT = PACKET / "p09_observability_decomposition_decision_v01.csv"
REPORT = PACKET / "p09_observability_decomposition_v01.md"

GUARDRAIL = "p09_observability_decomposition_not_bias_erasure_not_attribution"


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
        avg = (i + 1 + j) / 2
        for k in range(i, j):
            ranks[indexed[k][0]] = avg
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


def bin_inclination(value: float) -> str:
    if value < 45:
        return "face_on_lt45"
    if value < 60:
        return "mid_45_60"
    if value < 75:
        return "inclined_60_75"
    return "edge_on_ge75"


def geometry_channel(inclination: float) -> float:
    edge_component = max(0.0, (inclination - 60.0) / 25.0)
    face_component = max(0.0, (45.0 - inclination) / 20.0)
    return max(edge_component, face_component)


def reconstruction_risk(
    n_points: float,
    mean_err_vobs: float,
    inc_err: float,
    med_n_points: float,
    med_mean_err: float,
    med_inc_err: float,
) -> float:
    point_component = med_n_points / n_points if n_points else math.nan
    err_component = mean_err_vobs / med_mean_err if med_mean_err else math.nan
    inc_component = inc_err / med_inc_err if med_inc_err else math.nan
    return mean([point_component, err_component, inc_component])


def joined_rows() -> list[dict[str, str]]:
    workbook = {row["GalaxyName"]: row for row in read_csv(WORKBOOK)}
    w_rows = read_csv(W_TAU)
    matched = [workbook[row["GalaxyName"]] for row in w_rows if row["GalaxyName"] in workbook]
    med_n = median([float(row["NPoints"]) for row in matched])
    med_err = median([float(row["MeanErrVobsKms"]) for row in matched])
    med_inc_err = median([float(row["InclinationErrorDeg"]) for row in matched])

    rows: list[dict[str, str]] = []
    for target in w_rows:
        galaxy = target["GalaxyName"]
        if galaxy not in workbook:
            continue
        obs = workbook[galaxy]
        inclination = float(obs["InclinationDeg"])
        inc_err = float(obs["InclinationErrorDeg"])
        mean_err = float(obs["MeanErrVobsKms"])
        n_points = float(obs["NPoints"])
        geom = geometry_channel(inclination)
        recon = reconstruction_risk(n_points, mean_err, inc_err, med_n, med_err, med_inc_err)
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": target["Class"],
                "NPoints": obs["NPoints"],
                "MeanErrVobsKms": obs["MeanErrVobsKms"],
                "InclinationDeg": obs["InclinationDeg"],
                "InclinationErrorDeg": obs["InclinationErrorDeg"],
                "InclinationBin": bin_inclination(inclination),
                "ObserverGeometryChannel_v01": fmt(geom),
                "ReconstructionRiskChannel_v01": fmt(recon),
                "W_tau_eff_candidate_score_v01": target["W_tau_eff_candidate_score_v01"],
                "W_tau_eff_abs_v01": target["W_tau_eff_abs_v01"],
                "W_tau_eff_signed_v01": target["W_tau_eff_signed_v01"],
                "CandidateConfidenceTier": target["CandidateConfidenceTier"],
                "ReviewerDecision": obs["ReviewerDecision"],
                "EvidenceType": obs["EvidenceType"],
                "ResidualBlindCheck": obs["ResidualBlindCheck"],
                "ReadoutUse": "P09_observability_decomposition_no_velocity_endpoint",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    geom_cut = median([float(row["ObserverGeometryChannel_v01"]) for row in rows])
    recon_cut = median([float(row["ReconstructionRiskChannel_v01"]) for row in rows])
    for row in rows:
        row["ObserverGeometrySplit"] = (
            "high" if float(row["ObserverGeometryChannel_v01"]) > geom_cut else "low"
        )
        row["ReconstructionRiskSplit"] = (
            "high" if float(row["ReconstructionRiskChannel_v01"]) > recon_cut else "low"
        )
        row["ObserverGeometryMedianCutoff"] = fmt(geom_cut)
        row["ReconstructionRiskMedianCutoff"] = fmt(recon_cut)
    return rows


def split_auc(rows: list[dict[str, str]], split_field: str) -> float:
    high = [
        float(row["W_tau_eff_candidate_score_v01"])
        for row in rows
        if row[split_field] == "high"
    ]
    low = [
        float(row["W_tau_eff_candidate_score_v01"])
        for row in rows
        if row[split_field] == "low"
    ]
    return auc_high_higher(high, low)


def grouped_medians(rows: list[dict[str, str]], group_field: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for group in sorted({row[group_field] for row in rows}):
        subset = [row for row in rows if row[group_field] == group]
        out.append(
            {
                "Metric": f"median_score_by_{group_field}_{group}",
                "N": str(len(subset)),
                "Value": fmt(
                    median([float(row["W_tau_eff_candidate_score_v01"]) for row in subset])
                ),
                "SecondaryValue": group,
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return out


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    score = [float(row["W_tau_eff_candidate_score_v01"]) for row in rows]
    abs_w = [float(row["W_tau_eff_abs_v01"]) for row in rows]
    geom = [float(row["ObserverGeometryChannel_v01"]) for row in rows]
    recon = [float(row["ReconstructionRiskChannel_v01"]) for row in rows]
    inclination = [float(row["InclinationDeg"]) for row in rows]
    inc_err = [float(row["InclinationErrorDeg"]) for row in rows]
    mean_err = [float(row["MeanErrVobsKms"]) for row in rows]
    n_points = [float(row["NPoints"]) for row in rows]
    out = [
        {
            "Metric": "coverage_joined",
            "N": str(len(rows)),
            "Value": str(len(rows)),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_observer_geometry_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(geom, score)),
            "SecondaryValue": "line-of-sight geometry channel",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "spearman_observer_geometry_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(spearman(geom, score)),
            "SecondaryValue": "rank line-of-sight geometry channel",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_high_vs_low_observer_geometry",
            "N": str(len(rows)),
            "Value": fmt(split_auc(rows, "ObserverGeometrySplit")),
            "SecondaryValue": "median split of geometry channel",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_reconstruction_risk_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(recon, score)),
            "SecondaryValue": "measurement/deprojection reconstruction risk channel",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "spearman_reconstruction_risk_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(spearman(recon, score)),
            "SecondaryValue": "rank reconstruction risk channel",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_high_vs_low_reconstruction_risk",
            "N": str(len(rows)),
            "Value": fmt(split_auc(rows, "ReconstructionRiskSplit")),
            "SecondaryValue": "median split of reconstruction risk channel",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_inclination_deg_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(inclination, score)),
            "SecondaryValue": "raw inclination",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_inclination_error_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(inc_err, score)),
            "SecondaryValue": "deprojection uncertainty proxy",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_mean_err_vobs_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(mean_err, score)),
            "SecondaryValue": "velocity error proxy",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_n_points_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(n_points, score)),
            "SecondaryValue": "sampling/coverage proxy",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_observer_geometry_vs_abs_w_tau",
            "N": str(len(rows)),
            "Value": fmt(pearson(geom, abs_w)),
            "SecondaryValue": "absolute residual-inferred weight",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_reconstruction_risk_vs_abs_w_tau",
            "N": str(len(rows)),
            "Value": fmt(pearson(recon, abs_w)),
            "SecondaryValue": "absolute residual-inferred weight",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]
    out.extend(grouped_medians(rows, "InclinationBin"))
    out.extend(grouped_medians(rows, "ObserverGeometrySplit"))
    out.extend(grouped_medians(rows, "ReconstructionRiskSplit"))
    return out


def decision_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in metrics}
    geom_auc = float(lookup["auc_high_vs_low_observer_geometry"]["Value"])
    recon_auc = float(lookup["auc_high_vs_low_reconstruction_risk"]["Value"])
    geom_p = float(lookup["pearson_observer_geometry_vs_w_tau_score"]["Value"])
    recon_p = float(lookup["pearson_reconstruction_risk_vs_w_tau_score"]["Value"])
    if recon_auc >= 0.65 or recon_p >= 0.35:
        status = "ordinary_observability_risk_competes_with_signal"
        next_action = "do_not_open_velocity_endpoint_before_distance_resolution_regression"
    elif geom_auc >= 0.6 or geom_p >= 0.25:
        status = "observer_geometry_channel_present_reconstruction_risk_weak"
        next_action = "treat_geometry_as_candidate_tau_core_channel_not_as_erased_bias"
    else:
        status = "no_strong_observability_absorption_detected"
        next_action = "proceed_to_distance_resolution_environment_join_before_formula"
    return [
        {
            "DecisionID": "P09D01",
            "Decision": "observability_decomposition_vs_W_tau_eff_candidate_score",
            "Status": status,
            "Rationale": (
                "Observer-geometry Pearson="
                + lookup["pearson_observer_geometry_vs_w_tau_score"]["Value"]
                + "; AUC="
                + lookup["auc_high_vs_low_observer_geometry"]["Value"]
                + "; reconstruction-risk Pearson="
                + lookup["pearson_reconstruction_risk_vs_w_tau_score"]["Value"]
                + "; AUC="
                + lookup["auc_high_vs_low_reconstruction_risk"]["Value"]
                + "."
            ),
            "Blocks": "simple_bias_erasure_claim;velocity_formula",
            "NextAction": next_action,
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "P09D02",
            "Decision": "tau_core_interpretation_policy",
            "Status": "decompose_observability_do_not_delete_it",
            "Rationale": "Tau Core permits observer-dependent weights, so inclination/observability must be separated into ordinary reconstruction risk and candidate observer-geometry channel.",
            "Blocks": "claims_that_observability_is_only_a_nuisance",
            "NextAction": "carry_observer_geometry_channel_forward_as_hypothesis_with_controls",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    lines = [
        "# P09 Observability Decomposition v0.1",
        "",
        "This gate treats observability as a decomposition problem, not as something to erase automatically. The goal is to separate ordinary reconstruction risk from a possible observer-geometry channel compatible with Tau Core's observer-centered framing.",
        "",
        "## Channels",
        "",
        "- `ObserverGeometryChannel_v01`: line-of-sight geometry pressure from low- and high-inclination viewing geometry.",
        "- `ReconstructionRiskChannel_v01`: ordinary measurement/deprojection risk from `NPoints`, `MeanErrVobsKms`, and `InclinationErrorDeg`.",
        "",
        "## Readout",
        "",
        f"- Joined galaxies: {lookup['coverage_joined']['Value']}",
        f"- Observer geometry Pearson vs W_tau_eff score: {lookup['pearson_observer_geometry_vs_w_tau_score']['Value']}",
        f"- Observer geometry AUC high-vs-low: {lookup['auc_high_vs_low_observer_geometry']['Value']}",
        f"- Reconstruction risk Pearson vs W_tau_eff score: {lookup['pearson_reconstruction_risk_vs_w_tau_score']['Value']}",
        f"- Reconstruction risk AUC high-vs-low: {lookup['auc_high_vs_low_reconstruction_risk']['Value']}",
        "",
        "## Decision",
        "",
        f"`{decisions[0]['Status']}`",
        "",
        decisions[0]["Rationale"],
        "",
        "This does not prove Tau Core attribution. It does say that observer geometry should not be dismissed as mere nuisance before distance, resolution, and environment joins are run.",
        "",
        "## Generated Files",
        "",
        "- `p09_observability_decomposition_join_v01.csv`",
        "- `p09_observability_decomposition_metrics_v01.csv`",
        "- `p09_observability_decomposition_decision_v01.csv`",
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
    manifest["p09_observability_decomposition_status"] = (
        "galaxy_level_observability_decomposition_complete_no_velocity_endpoint"
    )
    manifest["paper2_next_gate"] = "distance_resolution_environment_join_before_formula"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = joined_rows()
    metrics = metric_rows(rows)
    decisions = decision_rows(metrics)
    join_fields = [
        "GalaxyName",
        "Class",
        "NPoints",
        "MeanErrVobsKms",
        "InclinationDeg",
        "InclinationErrorDeg",
        "InclinationBin",
        "ObserverGeometryChannel_v01",
        "ReconstructionRiskChannel_v01",
        "W_tau_eff_candidate_score_v01",
        "W_tau_eff_abs_v01",
        "W_tau_eff_signed_v01",
        "CandidateConfidenceTier",
        "ReviewerDecision",
        "EvidenceType",
        "ResidualBlindCheck",
        "ReadoutUse",
        "InterpretationGuardrail",
        "ObserverGeometrySplit",
        "ReconstructionRiskSplit",
        "ObserverGeometryMedianCutoff",
        "ReconstructionRiskMedianCutoff",
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
