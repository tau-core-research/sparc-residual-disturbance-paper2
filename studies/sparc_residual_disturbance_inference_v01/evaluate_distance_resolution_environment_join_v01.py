#!/usr/bin/env python3
"""Join distance, resolution, and environment controls before any formula endpoint."""

from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

from make_packet_v01_seed import PACKET, ROOT, read_csv, write_csv


TAU_CORE = ROOT.parent / "tau-core"
SPARC_TABLE1 = TAU_CORE / "data/external/SPARC_Table1.txt"
ENV_SOURCE = (
    TAU_CORE
    / "studies/sparc_residual_coherence_test_v01/coherence_labels_v03_external_proxy_high_candidate.csv"
)
POINT_MAP = ROOT / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/taucore_specificity_point_map.csv"
W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
P09_JOIN = PACKET / "p09_observability_decomposition_join_v01.csv"

JOIN_OUT = PACKET / "distance_resolution_environment_join_v01.csv"
METRIC_OUT = PACKET / "distance_resolution_environment_metrics_v01.csv"
DECISION_OUT = PACKET / "distance_resolution_environment_decision_v01.csv"
REPORT = PACKET / "distance_resolution_environment_join_v01.md"

GUARDRAIL = "distance_resolution_environment_control_no_formula_endpoint"


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


def parse_sparc_table1() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for line in SPARC_TABLE1.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 7:
            continue
        name, hubble_type, distance, distance_error, qd, inclination, inc_error = parts[:7]
        rows[name] = {
            "GalaxyName": name,
            "HubbleType": hubble_type,
            "DistanceMpc": distance,
            "DistanceErrorMpc": distance_error,
            "DistanceQualityFlag_QD": qd,
            "SPARCInclinationDeg": inclination,
            "SPARCInclinationErrorDeg": inc_error,
        }
    return rows


def max_radius_by_galaxy() -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for row in read_csv(POINT_MAP):
        grouped.setdefault(row["GalaxyName"], []).append(float(row["RadiusKpc"]))
    return {galaxy: max(values) for galaxy, values in grouped.items()}


def extract_float(pattern: str, text: str) -> str:
    match = re.search(pattern, text)
    return match.group(1) if match else ""


def environment_rows() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in read_csv(ENV_SOURCE):
        notes = row.get("Notes", "")
        label_reason = row.get("LabelReason", "")
        text = f"{label_reason}; {notes}"
        theta1 = extract_float(r"Theta1=([-+]?\d+(?:\.\d+)?)", text)
        theta5 = extract_float(r"Theta5=([-+]?\d+(?:\.\d+)?)", text)
        thetaj = extract_float(r"Thetaj=([-+]?\d+(?:\.\d+)?)", text)
        main_disturber = extract_float(r"main_disturber=([^;,\"]+)", text)
        has_env = "Karachentsev" in text or "environment" in text.lower()
        out[row["GalaxyName"]] = {
            "EnvTheta1": theta1,
            "EnvTheta5": theta5,
            "EnvThetaj": thetaj,
            "EnvMainDisturber": main_disturber,
            "EnvironmentCuePresent": "true" if has_env else "false",
        }
    return out


def split_column(rows: list[dict[str, str]], value_field: str, split_field: str) -> None:
    values = [float(row[value_field]) for row in rows if row[value_field] != ""]
    cutoff = median(values)
    for row in rows:
        if row[value_field] == "":
            row[split_field] = "missing"
        else:
            row[split_field] = "high" if float(row[value_field]) > cutoff else "low"
        row[f"{split_field}MedianCutoff"] = fmt(cutoff)


def joined_rows() -> list[dict[str, str]]:
    sparc = parse_sparc_table1()
    env = environment_rows()
    max_radius = max_radius_by_galaxy()
    p09 = {row["GalaxyName"]: row for row in read_csv(P09_JOIN)}
    rows: list[dict[str, str]] = []
    for target in read_csv(W_TAU):
        galaxy = target["GalaxyName"]
        if galaxy not in sparc or galaxy not in p09:
            continue
        meta = sparc[galaxy]
        obs = p09[galaxy]
        environment = env.get(galaxy, {})
        distance = float(meta["DistanceMpc"])
        distance_error = float(meta["DistanceErrorMpc"])
        n_points = float(obs["NPoints"])
        max_r = max_radius[galaxy]
        angular_radius_proxy = max_r / distance if distance else math.nan
        distance_frac_error = distance_error / distance if distance else math.nan
        theta_values = [
            float(environment[field])
            for field in ["EnvTheta1", "EnvTheta5", "EnvThetaj"]
            if environment.get(field, "") != ""
        ]
        env_max_theta = max(theta_values) if theta_values else math.nan
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": target["Class"],
                "DistanceMpc": meta["DistanceMpc"],
                "DistanceErrorMpc": meta["DistanceErrorMpc"],
                "DistanceFractionalError": fmt(distance_frac_error),
                "DistanceQualityFlag_QD": meta["DistanceQualityFlag_QD"],
                "NPoints": obs["NPoints"],
                "MeanErrVobsKms": obs["MeanErrVobsKms"],
                "InclinationErrorDeg": obs["InclinationErrorDeg"],
                "MaxRadiusKpc": fmt(max_r),
                "AngularRadiusProxy_KpcPerMpc": fmt(angular_radius_proxy),
                "ReconstructionRiskChannel_v01": obs["ReconstructionRiskChannel_v01"],
                "EnvTheta1": environment.get("EnvTheta1", ""),
                "EnvTheta5": environment.get("EnvTheta5", ""),
                "EnvThetaj": environment.get("EnvThetaj", ""),
                "EnvMaxTheta": fmt(env_max_theta),
                "EnvMainDisturber": environment.get("EnvMainDisturber", ""),
                "EnvironmentCuePresent": environment.get("EnvironmentCuePresent", "false"),
                "W_tau_eff_candidate_score_v01": target["W_tau_eff_candidate_score_v01"],
                "W_tau_eff_abs_v01": target["W_tau_eff_abs_v01"],
                "ReadoutUse": "distance_resolution_environment_join_no_formula_endpoint",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    for value_field, split_field in [
        ("DistanceMpc", "DistanceSplit"),
        ("DistanceFractionalError", "DistanceFractionalErrorSplit"),
        ("NPoints", "NPointsSplit"),
        ("MaxRadiusKpc", "MaxRadiusSplit"),
        ("AngularRadiusProxy_KpcPerMpc", "AngularRadiusProxySplit"),
        ("ReconstructionRiskChannel_v01", "ReconstructionRiskSplit"),
        ("EnvMaxTheta", "EnvMaxThetaSplit"),
    ]:
        split_column(rows, value_field, split_field)
    return rows


def values(rows: list[dict[str, str]], field: str) -> tuple[list[float], list[float]]:
    paired = [
        (float(row[field]), float(row["W_tau_eff_candidate_score_v01"]))
        for row in rows
        if row[field] != ""
    ]
    return [item[0] for item in paired], [item[1] for item in paired]


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


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    metrics = [
        {
            "Metric": "coverage_joined",
            "N": str(len(rows)),
            "Value": str(len(rows)),
            "SecondaryValue": "",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "environment_cue_coverage",
            "N": str(sum(1 for row in rows if row["EnvironmentCuePresent"] == "true")),
            "Value": str(sum(1 for row in rows if row["EnvironmentCuePresent"] == "true")),
            "SecondaryValue": "rows with residual-blind environment cue text",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]
    for field in [
        "DistanceMpc",
        "DistanceFractionalError",
        "NPoints",
        "MeanErrVobsKms",
        "InclinationErrorDeg",
        "MaxRadiusKpc",
        "AngularRadiusProxy_KpcPerMpc",
        "ReconstructionRiskChannel_v01",
        "EnvMaxTheta",
    ]:
        xs, score = values(rows, field)
        metrics.append(
            {
                "Metric": f"pearson_{field}_vs_w_tau_score",
                "N": str(len(xs)),
                "Value": fmt(pearson(xs, score)),
                "SecondaryValue": "continuous control channel",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
        metrics.append(
            {
                "Metric": f"spearman_{field}_vs_w_tau_score",
                "N": str(len(xs)),
                "Value": fmt(spearman(xs, score)),
                "SecondaryValue": "rank control channel",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    for split in [
        "DistanceSplit",
        "DistanceFractionalErrorSplit",
        "NPointsSplit",
        "MaxRadiusSplit",
        "AngularRadiusProxySplit",
        "ReconstructionRiskSplit",
        "EnvMaxThetaSplit",
    ]:
        non_missing = [row for row in rows if row[split] != "missing"]
        high = [
            float(row["W_tau_eff_candidate_score_v01"])
            for row in non_missing
            if row[split] == "high"
        ]
        low = [
            float(row["W_tau_eff_candidate_score_v01"])
            for row in non_missing
            if row[split] == "low"
        ]
        metrics.extend(
            [
                {
                    "Metric": f"median_score_high_{split}",
                    "N": str(len(high)),
                    "Value": fmt(median(high)),
                    "SecondaryValue": split,
                    "InterpretationGuardrail": GUARDRAIL,
                },
                {
                    "Metric": f"median_score_low_{split}",
                    "N": str(len(low)),
                    "Value": fmt(median(low)),
                    "SecondaryValue": split,
                    "InterpretationGuardrail": GUARDRAIL,
                },
                {
                    "Metric": f"auc_high_vs_low_{split}",
                    "N": str(len(non_missing)),
                    "Value": fmt(split_auc(non_missing, split)),
                    "SecondaryValue": "median split",
                    "InterpretationGuardrail": GUARDRAIL,
                },
            ]
        )
    return metrics


def decision_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in metrics}
    recon_auc = float(lookup["auc_high_vs_low_ReconstructionRiskSplit"]["Value"])
    angular_auc = float(lookup["auc_high_vs_low_AngularRadiusProxySplit"]["Value"])
    distance_auc = float(lookup["auc_high_vs_low_DistanceSplit"]["Value"])
    env_auc_text = lookup["auc_high_vs_low_EnvMaxThetaSplit"]["Value"]
    env_auc = float(env_auc_text) if env_auc_text else math.nan
    if recon_auc >= 0.65 and angular_auc <= 0.5:
        status = "reconstruction_risk_remains_primary_observability_blocker"
    elif angular_auc >= 0.65 or distance_auc >= 0.65:
        status = "distance_resolution_channel_competes_with_signal"
    elif not math.isnan(env_auc) and env_auc >= 0.65:
        status = "environment_channel_competes_with_signal"
    else:
        status = "no_single_distance_resolution_environment_channel_absorbs_signal"
    return [
        {
            "DecisionID": "DRE01",
            "Decision": "distance_resolution_environment_vs_W_tau_eff_candidate_score",
            "Status": status,
            "Rationale": (
                "Reconstruction-risk AUC="
                + lookup["auc_high_vs_low_ReconstructionRiskSplit"]["Value"]
                + "; angular-radius AUC="
                + lookup["auc_high_vs_low_AngularRadiusProxySplit"]["Value"]
                + "; distance AUC="
                + lookup["auc_high_vs_low_DistanceSplit"]["Value"]
                + "; environment-theta AUC="
                + env_auc_text
                + "."
            ),
            "Blocks": "S_tau_full_formula;field_attribution",
            "NextAction": "freeze_multivariable_no_velocity_endpoint_stress_test",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "DRE02",
            "Decision": "endpoint_status",
            "Status": "velocity_endpoint_still_closed",
            "Rationale": "These are covariate decomposition controls, not formula coefficients.",
            "Blocks": "velocity_formula",
            "NextAction": "only_after_multivariable_stress_and_external_environment_coverage",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    lines = [
        "# Distance, Resolution, and Environment Join v0.1",
        "",
        "This gate decomposes the P09 observability blocker before any velocity formula is opened. It joins derived SPARC distance controls, rotation-curve sampling/resolution proxies, and residual-blind environment cue fields.",
        "",
        "## Readout",
        "",
        f"- Joined galaxies: {lookup['coverage_joined']['Value']}",
        f"- Environment cue coverage: {lookup['environment_cue_coverage']['Value']}",
        f"- Reconstruction-risk AUC: {lookup['auc_high_vs_low_ReconstructionRiskSplit']['Value']}",
        f"- Distance AUC: {lookup['auc_high_vs_low_DistanceSplit']['Value']}",
        f"- Angular-radius proxy AUC: {lookup['auc_high_vs_low_AngularRadiusProxySplit']['Value']}",
        f"- Environment-theta AUC: {lookup['auc_high_vs_low_EnvMaxThetaSplit']['Value']}",
        "",
        "## Decision",
        "",
        f"`{decisions[0]['Status']}`",
        "",
        decisions[0]["Rationale"],
        "",
        "The result is a covariate gate only. It may motivate a later multivariable stress test, but it does not select or validate a Tau Core velocity formula.",
        "",
        "## Generated Files",
        "",
        "- `distance_resolution_environment_join_v01.csv`",
        "- `distance_resolution_environment_metrics_v01.csv`",
        "- `distance_resolution_environment_decision_v01.csv`",
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
    manifest["distance_resolution_environment_join_status"] = (
        "covariate_decomposition_complete_no_formula_endpoint"
    )
    manifest["paper2_next_gate"] = "multivariable_no_velocity_endpoint_stress_test"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = joined_rows()
    metrics = metric_rows(rows)
    decisions = decision_rows(metrics)
    join_fields = [
        "GalaxyName",
        "Class",
        "DistanceMpc",
        "DistanceErrorMpc",
        "DistanceFractionalError",
        "DistanceQualityFlag_QD",
        "NPoints",
        "MeanErrVobsKms",
        "InclinationErrorDeg",
        "MaxRadiusKpc",
        "AngularRadiusProxy_KpcPerMpc",
        "ReconstructionRiskChannel_v01",
        "EnvTheta1",
        "EnvTheta5",
        "EnvThetaj",
        "EnvMaxTheta",
        "EnvMainDisturber",
        "EnvironmentCuePresent",
        "W_tau_eff_candidate_score_v01",
        "W_tau_eff_abs_v01",
        "ReadoutUse",
        "InterpretationGuardrail",
        "DistanceSplit",
        "DistanceSplitMedianCutoff",
        "DistanceFractionalErrorSplit",
        "DistanceFractionalErrorSplitMedianCutoff",
        "NPointsSplit",
        "NPointsSplitMedianCutoff",
        "MaxRadiusSplit",
        "MaxRadiusSplitMedianCutoff",
        "AngularRadiusProxySplit",
        "AngularRadiusProxySplitMedianCutoff",
        "ReconstructionRiskSplit",
        "ReconstructionRiskSplitMedianCutoff",
        "EnvMaxThetaSplit",
        "EnvMaxThetaSplitMedianCutoff",
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
