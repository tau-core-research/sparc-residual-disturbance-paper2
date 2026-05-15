#!/usr/bin/env python3
"""Run a no-velocity multivariable stress test for the observer-distance hypothesis."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


SOURCE = PACKET / "distance_resolution_environment_join_v01.csv"
JOIN_OUT = PACKET / "multivariable_no_velocity_stress_join_v01.csv"
METRIC_OUT = PACKET / "multivariable_no_velocity_stress_metrics_v01.csv"
DECISION_OUT = PACKET / "multivariable_no_velocity_stress_decision_v01.csv"
REPORT = PACKET / "multivariable_no_velocity_stress_v01.md"

GUARDRAIL = "multivariable_stress_no_velocity_endpoint_no_formula_selection"
NUISANCE_FIELDS = [
    "AngularRadiusProxy_KpcPerMpc",
    "NPoints",
    "MeanErrVobsKms",
    "InclinationErrorDeg",
    "DistanceFractionalError",
    "MaxRadiusKpc",
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


def r2(y: list[float], predicted: list[float]) -> float:
    mu = mean(y)
    ss_tot = sum((value - mu) ** 2 for value in y)
    ss_res = sum((value - pred) ** 2 for value, pred in zip(y, predicted))
    if ss_tot == 0:
        return math.nan
    return 1 - ss_res / ss_tot


def model_r2(y: list[float], controls: list[list[float]]) -> float:
    xs = [[1.0] + row for row in controls]
    beta = ols_fit(xs, y)
    predicted = [sum(coef * value for coef, value in zip(beta, row)) for row in xs]
    return r2(y, predicted)


def build_rows() -> tuple[list[dict[str, str]], dict[str, list[float]]]:
    source = read_csv(SOURCE)
    score = [float(row["W_tau_eff_candidate_score_v01"]) for row in source]
    distance = [math.log(float(row["DistanceMpc"])) for row in source]
    tau_distance = [-value for value in zscore(distance)]
    nuisance_raw = {
        field: [float(row[field]) for row in source] for field in NUISANCE_FIELDS
    }
    nuisance_z = {field: zscore(values) for field, values in nuisance_raw.items()}
    controls = [
        [nuisance_z[field][i] for field in NUISANCE_FIELDS] for i in range(len(source))
    ]
    score_resid = residualize(score, controls)
    tau_distance_resid = residualize(tau_distance, controls)
    rows: list[dict[str, str]] = []
    for i, row in enumerate(source):
        rows.append(
            {
                "GalaxyName": row["GalaxyName"],
                "Class": row["Class"],
                "W_tau_eff_candidate_score_v01": row["W_tau_eff_candidate_score_v01"],
                "TauDistanceCandidate_NearerHigher_z": fmt(tau_distance[i]),
                "TauDistanceResidualAfterNuisance": fmt(tau_distance_resid[i]),
                "W_tau_eff_score_residual_after_nuisance": fmt(score_resid[i]),
                "AngularRadiusProxy_z": fmt(nuisance_z["AngularRadiusProxy_KpcPerMpc"][i]),
                "NPoints_z": fmt(nuisance_z["NPoints"][i]),
                "MeanErrVobsKms_z": fmt(nuisance_z["MeanErrVobsKms"][i]),
                "InclinationErrorDeg_z": fmt(nuisance_z["InclinationErrorDeg"][i]),
                "DistanceFractionalError_z": fmt(nuisance_z["DistanceFractionalError"][i]),
                "MaxRadiusKpc_z": fmt(nuisance_z["MaxRadiusKpc"][i]),
                "EnvironmentCuePresent": row["EnvironmentCuePresent"],
                "ReadoutUse": "observer_distance_tau_candidate_stress_no_velocity_endpoint",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    arrays = {
        "score": score,
        "tau_distance": tau_distance,
        "score_resid": score_resid,
        "tau_distance_resid": tau_distance_resid,
    }
    for field, values in nuisance_z.items():
        arrays[field] = values
    arrays["controls_r2_score"] = [model_r2(score, controls)]
    return rows, arrays


def metric_rows(rows: list[dict[str, str]], arrays: dict[str, list[float]]) -> list[dict[str, str]]:
    score = arrays["score"]
    tau_distance = arrays["tau_distance"]
    score_resid = arrays["score_resid"]
    tau_distance_resid = arrays["tau_distance_resid"]
    high_tau = [
        float(row["W_tau_eff_candidate_score_v01"])
        for row in rows
        if float(row["TauDistanceCandidate_NearerHigher_z"]) > 0
    ]
    low_tau = [
        float(row["W_tau_eff_candidate_score_v01"])
        for row in rows
        if float(row["TauDistanceCandidate_NearerHigher_z"]) <= 0
    ]
    high_resid = [
        float(row["W_tau_eff_score_residual_after_nuisance"])
        for row in rows
        if float(row["TauDistanceResidualAfterNuisance"]) > 0
    ]
    low_resid = [
        float(row["W_tau_eff_score_residual_after_nuisance"])
        for row in rows
        if float(row["TauDistanceResidualAfterNuisance"]) <= 0
    ]
    metrics = [
        {
            "Metric": "coverage_joined",
            "N": str(len(rows)),
            "Value": str(len(rows)),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_tau_distance_raw_vs_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(pearson(tau_distance, score)),
            "SecondaryValue": "nearer_higher_distance_candidate",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_nearer_vs_farther_tau_distance_raw",
            "N": str(len(rows)),
            "Value": fmt(auc_high_higher(high_tau, low_tau)),
            "SecondaryValue": "raw median sign split",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "partial_pearson_tau_distance_after_nuisance_vs_score_after_nuisance",
            "N": str(len(rows)),
            "Value": fmt(pearson(tau_distance_resid, score_resid)),
            "SecondaryValue": "controls=angular_radius;npoints;mean_err;inclination_error;distance_fractional_error;max_radius",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "partial_auc_tau_distance_residual_high_vs_low_score_residual",
            "N": str(len(rows)),
            "Value": fmt(auc_high_higher(high_resid, low_resid)),
            "SecondaryValue": "residual sign split after nuisance controls",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "nuisance_model_r2_for_w_tau_score",
            "N": str(len(rows)),
            "Value": fmt(arrays["controls_r2_score"][0]),
            "SecondaryValue": "linear nuisance-only score model no velocity endpoint",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]
    for field in NUISANCE_FIELDS:
        metrics.append(
            {
                "Metric": f"pearson_{field}_z_vs_w_tau_score",
                "N": str(len(rows)),
                "Value": fmt(pearson(arrays[field], score)),
                "SecondaryValue": "nuisance channel",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return metrics


def decision_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in metrics}
    raw = float(lookup["pearson_tau_distance_raw_vs_w_tau_score"]["Value"])
    partial = float(
        lookup[
            "partial_pearson_tau_distance_after_nuisance_vs_score_after_nuisance"
        ]["Value"]
    )
    partial_auc = float(
        lookup["partial_auc_tau_distance_residual_high_vs_low_score_residual"][
            "Value"
        ]
    )
    if raw > 0.25 and partial > 0.15 and partial_auc > 0.55:
        status = "observer_distance_candidate_survives_nuisance_stress"
        next_action = "freeze_as_hypothesis_not_formula_then_seek_external_environment_distance_validation"
    elif raw > 0.25 and partial <= 0.15:
        status = "observer_distance_candidate_weakened_by_nuisance_controls"
        next_action = "do_not_promote_distance_channel_before_better_resolution_controls"
    else:
        status = "observer_distance_candidate_not_supported"
        next_action = "treat_distance_as_observability_caveat_only"
    return [
        {
            "DecisionID": "MV01",
            "Decision": "observer_distance_tau_candidate_after_nuisance_controls",
            "Status": status,
            "Rationale": (
                "Raw tau-distance Pearson="
                + lookup["pearson_tau_distance_raw_vs_w_tau_score"]["Value"]
                + "; partial Pearson="
                + lookup[
                    "partial_pearson_tau_distance_after_nuisance_vs_score_after_nuisance"
                ]["Value"]
                + "; partial AUC="
                + lookup["partial_auc_tau_distance_residual_high_vs_low_score_residual"][
                    "Value"
                ]
                + "."
            ),
            "Blocks": "velocity_formula;field_attribution",
            "NextAction": next_action,
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "MV02",
            "Decision": "endpoint_status",
            "Status": "velocity_endpoint_still_closed",
            "Rationale": "This stress test uses only covariates and W_tau_eff score readouts; it does not fit or evaluate a velocity formula.",
            "Blocks": "S_tau_full_velocity_readout",
            "NextAction": "write_hypothesis_gate_and_require_external_validation",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    lines = [
        "# Multivariable No-Velocity Stress Test v0.1",
        "",
        "This gate tests the observer-distance Tau candidate without opening a velocity endpoint. The candidate channel is `TauDistanceCandidate_NearerHigher_z`, a nearer-higher transform of log distance. It is stressed against angular size, sampling, velocity-error, inclination-error, distance-fractional-error, and physical-radius nuisance controls.",
        "",
        "## Readout",
        "",
        f"- Joined galaxies: {lookup['coverage_joined']['Value']}",
        f"- Raw tau-distance Pearson vs W_tau_eff score: {lookup['pearson_tau_distance_raw_vs_w_tau_score']['Value']}",
        f"- Raw nearer-vs-farther AUC: {lookup['auc_nearer_vs_farther_tau_distance_raw']['Value']}",
        f"- Partial tau-distance Pearson after nuisance controls: {lookup['partial_pearson_tau_distance_after_nuisance_vs_score_after_nuisance']['Value']}",
        f"- Partial tau-distance residual AUC: {lookup['partial_auc_tau_distance_residual_high_vs_low_score_residual']['Value']}",
        f"- Nuisance-only score model R2: {lookup['nuisance_model_r2_for_w_tau_score']['Value']}",
        "",
        "## Decision",
        "",
        f"`{decisions[0]['Status']}`",
        "",
        decisions[0]["Rationale"],
        "",
        "This is hypothesis support or weakening only. It does not establish a Tau Core field, and it does not select a velocity formula.",
        "",
        "## Generated Files",
        "",
        "- `multivariable_no_velocity_stress_join_v01.csv`",
        "- `multivariable_no_velocity_stress_metrics_v01.csv`",
        "- `multivariable_no_velocity_stress_decision_v01.csv`",
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
    manifest["multivariable_no_velocity_stress_status"] = (
        "observer_distance_candidate_stress_complete_no_velocity_endpoint"
    )
    manifest["paper2_next_gate"] = "observer_distance_hypothesis_gate_external_validation"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows, arrays = build_rows()
    metrics = metric_rows(rows, arrays)
    decisions = decision_rows(metrics)
    join_fields = [
        "GalaxyName",
        "Class",
        "W_tau_eff_candidate_score_v01",
        "TauDistanceCandidate_NearerHigher_z",
        "TauDistanceResidualAfterNuisance",
        "W_tau_eff_score_residual_after_nuisance",
        "AngularRadiusProxy_z",
        "NPoints_z",
        "MeanErrVobsKms_z",
        "InclinationErrorDeg_z",
        "DistanceFractionalError_z",
        "MaxRadiusKpc_z",
        "EnvironmentCuePresent",
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
