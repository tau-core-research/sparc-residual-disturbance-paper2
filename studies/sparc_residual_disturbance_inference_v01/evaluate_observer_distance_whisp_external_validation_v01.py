#!/usr/bin/env python3
"""Evaluate WHISP source-family external validation for the observer-distance gate."""

from __future__ import annotations

import json
import math

from make_packet_v01_seed import PACKET, read_csv, write_csv


WHISP = PACKET / "p07_whisp_w_tau_eff_holdout_join_v01.csv"
DRE = PACKET / "distance_resolution_environment_join_v01.csv"

JOIN_OUT = PACKET / "observer_distance_whisp_external_validation_join_v01.csv"
METRIC_OUT = PACKET / "observer_distance_whisp_external_validation_metrics_v01.csv"
DECISION_OUT = PACKET / "observer_distance_whisp_external_validation_decision_v01.csv"
REPORT = PACKET / "observer_distance_whisp_external_validation_v01.md"

GUARDRAIL = "whisp_external_validation_no_velocity_endpoint_no_formula_selection"
CONTROL_FIELDS = [
    "WHISP_BurdenScore_v01",
    "AngularRadiusProxy_KpcPerMpc",
    "NPoints",
    "MeanErrVobsKms",
    "InclinationErrorDeg",
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


def std(values: list[float]) -> float:
    mu = mean(values)
    return math.sqrt(mean([(value - mu) ** 2 for value in values]))


def zscore(values: list[float]) -> list[float]:
    mu = mean(values)
    sigma = std(values)
    if sigma == 0:
        return [0.0 for _ in values]
    return [(value - mu) / sigma for value in values]


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return math.nan
    zx = zscore(xs)
    zy = zscore(ys)
    return mean([x * y for x, y in zip(zx, zy)])


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


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(vector)
    aug = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(aug[row][col]))
        if abs(aug[pivot][col]) < 1e-12:
            continue
        aug[col], aug[pivot] = aug[pivot], aug[col]
        div = aug[col][col]
        aug[col] = [value / div for value in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            aug[row] = [
                value - factor * aug[col][i] for i, value in enumerate(aug[row])
            ]
    return [aug[row][-1] for row in range(n)]


def ols_fit(xs: list[list[float]], y: list[float]) -> list[float]:
    p = len(xs[0])
    xtx = [[0.0 for _ in range(p)] for _ in range(p)]
    xty = [0.0 for _ in range(p)]
    ridge = 1e-8
    for row, target in zip(xs, y):
        for i in range(p):
            xty[i] += row[i] * target
            for j in range(p):
                xtx[i][j] += row[i] * row[j]
    for i in range(p):
        xtx[i][i] += ridge
    return solve_linear_system(xtx, xty)


def residualize(y: list[float], controls: list[list[float]]) -> list[float]:
    xs = [[1.0] + row for row in controls]
    beta = ols_fit(xs, y)
    return [
        target - sum(coef * value for coef, value in zip(beta, row))
        for target, row in zip(y, xs)
    ]


def joined_rows() -> tuple[list[dict[str, str]], dict[str, list[float]]]:
    dre = {row["GalaxyName"]: row for row in read_csv(DRE)}
    rows: list[dict[str, str]] = []
    for whisp in read_csv(WHISP):
        galaxy = whisp["GalaxyName"]
        meta = dre[galaxy]
        distance = math.log(float(meta["DistanceMpc"]))
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": whisp["Class"],
                "W_tau_eff_candidate_score_v01": whisp["W_tau_eff_candidate_score_v01"],
                "WHISP_BurdenScore_v01": whisp["WHISP_BurdenScore_v01"],
                "DistanceMpc": meta["DistanceMpc"],
                "AngularRadiusProxy_KpcPerMpc": meta["AngularRadiusProxy_KpcPerMpc"],
                "NPoints": meta["NPoints"],
                "MeanErrVobsKms": meta["MeanErrVobsKms"],
                "InclinationErrorDeg": meta["InclinationErrorDeg"],
                "LogDistance": fmt(distance),
                "ReadoutUse": "WHISP_observer_distance_external_validation_no_velocity_endpoint",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    score = [float(row["W_tau_eff_candidate_score_v01"]) for row in rows]
    tau_distance = [-value for value in zscore([float(row["LogDistance"]) for row in rows])]
    controls_z = {
        field: zscore([float(row[field]) for row in rows]) for field in CONTROL_FIELDS
    }
    controls = [[controls_z[field][i] for field in CONTROL_FIELDS] for i in range(len(rows))]
    score_resid = residualize(score, controls)
    tau_distance_resid = residualize(tau_distance, controls)
    cutoff = median(tau_distance)
    resid_cutoff = median(tau_distance_resid)
    for i, row in enumerate(rows):
        row["TauDistanceCandidate_NearerHigher_z"] = fmt(tau_distance[i])
        row["TauDistanceResidualAfterWHISPControls"] = fmt(tau_distance_resid[i])
        row["W_tau_eff_score_residual_after_WHISP_controls"] = fmt(score_resid[i])
        row["TauDistanceSplit"] = "high" if tau_distance[i] > cutoff else "low"
        row["TauDistanceResidualSplit"] = (
            "high" if tau_distance_resid[i] > resid_cutoff else "low"
        )
    arrays = {
        "score": score,
        "tau_distance": tau_distance,
        "score_resid": score_resid,
        "tau_distance_resid": tau_distance_resid,
    }
    return rows, arrays


def metric_rows(
    rows: list[dict[str, str]], arrays: dict[str, list[float]]
) -> list[dict[str, str]]:
    raw_high = [
        float(row["W_tau_eff_candidate_score_v01"])
        for row in rows
        if row["TauDistanceSplit"] == "high"
    ]
    raw_low = [
        float(row["W_tau_eff_candidate_score_v01"])
        for row in rows
        if row["TauDistanceSplit"] == "low"
    ]
    resid_high = [
        float(row["W_tau_eff_score_residual_after_WHISP_controls"])
        for row in rows
        if row["TauDistanceResidualSplit"] == "high"
    ]
    resid_low = [
        float(row["W_tau_eff_score_residual_after_WHISP_controls"])
        for row in rows
        if row["TauDistanceResidualSplit"] == "low"
    ]
    return [
        {
            "Metric": "coverage_joined",
            "N": str(len(rows)),
            "Value": str(len(rows)),
            "SecondaryValue": "WHISP overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "class_coverage",
            "N": str(len(rows)),
            "Value": ";".join(sorted({row["Class"] for row in rows})),
            "SecondaryValue": "source-family sanity check not class-balanced validation",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_tau_distance_raw_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(arrays["tau_distance"], arrays["score"])),
            "SecondaryValue": "nearer-higher within WHISP overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_nearer_vs_farther_tau_distance_raw",
            "N": str(len(rows)),
            "Value": fmt(auc_high_higher(raw_high, raw_low)),
            "SecondaryValue": "median split within WHISP overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "partial_pearson_tau_distance_after_whisp_controls",
            "N": str(len(rows)),
            "Value": fmt(pearson(arrays["tau_distance_resid"], arrays["score_resid"])),
            "SecondaryValue": "controls=WHISP burden;angular radius;npoints;mean_err;inclination_error",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "partial_auc_tau_distance_after_whisp_controls",
            "N": str(len(rows)),
            "Value": fmt(auc_high_higher(resid_high, resid_low)),
            "SecondaryValue": "residual median split within WHISP overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def decision_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in metrics}
    partial = float(lookup["partial_pearson_tau_distance_after_whisp_controls"]["Value"])
    partial_auc = float(lookup["partial_auc_tau_distance_after_whisp_controls"]["Value"])
    if partial > 0 and partial_auc > 0.55:
        status = "direction_reproduced_in_small_whisp_overlap"
        next_action = "repeat_on_THINGS_LITTLE_THINGS_HALOGAS_small_overlaps"
    else:
        status = "direction_not_reproduced_in_small_whisp_overlap"
        next_action = "do_not_promote_observer_distance_hypothesis_before_other_external_checks"
    return [
        {
            "DecisionID": "ODW01",
            "Decision": "WHISP_observer_distance_external_validation",
            "Status": status,
            "Rationale": (
                "raw Pearson="
                + lookup["pearson_tau_distance_raw_vs_w_tau_score"]["Value"]
                + "; partial Pearson="
                + lookup["partial_pearson_tau_distance_after_whisp_controls"]["Value"]
                + "; partial AUC="
                + lookup["partial_auc_tau_distance_after_whisp_controls"]["Value"]
                + "."
            ),
            "Blocks": "velocity_formula;field_attribution",
            "NextAction": next_action,
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "ODW02",
            "Decision": "endpoint_status",
            "Status": "velocity_endpoint_still_closed",
            "Rationale": "The WHISP overlap is small and class-limited; it is source-family validation only.",
            "Blocks": "S_tau_full_velocity_readout",
            "NextAction": "require_additional_external_source_family",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    lines = [
        "# Observer-Distance WHISP External Validation v0.1",
        "",
        "This readout tests the observer-distance hypothesis inside the WHISP source-family overlap. It does not open a velocity endpoint and it is not class-balanced; the current overlap contains only C-class galaxies.",
        "",
        "## Readout",
        "",
        f"- Joined WHISP galaxies: {lookup['coverage_joined']['Value']}",
        f"- Class coverage: {lookup['class_coverage']['Value']}",
        f"- Raw tau-distance Pearson: {lookup['pearson_tau_distance_raw_vs_w_tau_score']['Value']}",
        f"- Raw tau-distance AUC: {lookup['auc_nearer_vs_farther_tau_distance_raw']['Value']}",
        f"- Partial Pearson after WHISP controls: {lookup['partial_pearson_tau_distance_after_whisp_controls']['Value']}",
        f"- Partial AUC after WHISP controls: {lookup['partial_auc_tau_distance_after_whisp_controls']['Value']}",
        "",
        "## Decision",
        "",
        f"`{decisions[0]['Status']}`",
        "",
        decisions[0]["Rationale"],
        "",
        "This is a small source-family sanity check. It can support or weaken the hypothesis direction, but it cannot validate a Tau Core field or velocity formula.",
        "",
        "## Generated Files",
        "",
        "- `observer_distance_whisp_external_validation_join_v01.csv`",
        "- `observer_distance_whisp_external_validation_metrics_v01.csv`",
        "- `observer_distance_whisp_external_validation_decision_v01.csv`",
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
    manifest["observer_distance_whisp_external_validation_status"] = (
        "small_source_family_validation_complete_no_velocity_endpoint"
    )
    manifest["paper2_next_gate"] = "observer_distance_things_littlethings_halogas_validation"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows, arrays = joined_rows()
    metrics = metric_rows(rows, arrays)
    decisions = decision_rows(metrics)
    join_fields = [
        "GalaxyName",
        "Class",
        "W_tau_eff_candidate_score_v01",
        "WHISP_BurdenScore_v01",
        "DistanceMpc",
        "AngularRadiusProxy_KpcPerMpc",
        "NPoints",
        "MeanErrVobsKms",
        "InclinationErrorDeg",
        "LogDistance",
        "TauDistanceCandidate_NearerHigher_z",
        "TauDistanceResidualAfterWHISPControls",
        "W_tau_eff_score_residual_after_WHISP_controls",
        "TauDistanceSplit",
        "TauDistanceResidualSplit",
        "ReadoutUse",
        "InterpretationGuardrail",
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
