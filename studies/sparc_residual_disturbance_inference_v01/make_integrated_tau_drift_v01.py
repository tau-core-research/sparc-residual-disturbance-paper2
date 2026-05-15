#!/usr/bin/env python3
"""Measure cumulative radial drift in the fixed TPG/projection residual."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET


POINTS = PACKET / "s_tau_eff_point_pilot.csv"
POINT_OUT = PACKET / "integrated_tau_drift_point_trace_v01.csv"
GALAXY_OUT = PACKET / "integrated_tau_drift_galaxy_summary_v01.csv"
METRIC_OUT = PACKET / "integrated_tau_drift_metric_summary_v01.csv"
REPORT = PACKET / "integrated_tau_drift_v01.md"

GUARDRAIL = "signed_residual_drift_diagnostic_not_predictive_s_tau_rule"
BREAK_THRESHOLD = 0.15


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


def rms(values: list[float]) -> float:
    return math.sqrt(mean([value * value for value in values])) if values else math.nan


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


def auc_c_higher(rows: list[dict[str, str]], field: str) -> float:
    positives = [float(row[field]) for row in rows if row["Class"] == "C" and row[field] != ""]
    negatives = [float(row[field]) for row in rows if row["Class"] == "A" and row[field] != ""]
    if not positives or not negatives:
        return math.nan
    wins = 0.0
    total = 0
    for pos in positives:
        for neg in negatives:
            total += 1
            if pos > neg:
                wins += 1
            elif pos == neg:
                wins += 0.5
    return wins / total


def max_same_sign_run(values: list[float]) -> int:
    best = 0
    current = 0
    last_sign = 0
    for value in values:
        sign = 1 if value > 0 else -1 if value < 0 else 0
        if sign == 0:
            current = 0
            last_sign = 0
            continue
        if sign == last_sign:
            current += 1
        else:
            current = 1
            last_sign = sign
        best = max(best, current)
    return best


def signed_residual(row: dict[str, str]) -> float:
    vobs = float(row["VobsKms"])
    vbar = float(row["VbarKms"])
    kernel = float(row["LogKernelAlphaLn"])
    model = vbar * (1.0 + kernel)
    if vobs <= 0 or model <= 0:
        return math.nan
    return math.log(vobs / model)


def grouped_points() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(POINTS):
        grouped.setdefault(row["GalaxyName"], []).append(row)
    for values in grouped.values():
        values.sort(key=lambda row: float(row["RadiusFraction"]))
    return grouped


def point_and_galaxy_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    point_rows: list[dict[str, str]] = []
    galaxy_rows: list[dict[str, str]] = []
    for galaxy, points in sorted(grouped_points().items()):
        cumulative = 0.0
        cumulative_abs_max = 0.0
        signed_values: list[float] = []
        cumulative_values: list[float] = []
        first_break_radius = math.nan
        for index, point in enumerate(points, start=1):
            residual = signed_residual(point)
            if math.isnan(residual):
                continue
            signed_values.append(residual)
            cumulative += residual
            cumulative_mean = cumulative / len(signed_values)
            cumulative_values.append(cumulative_mean)
            cumulative_abs_max = max(cumulative_abs_max, abs(cumulative_mean))
            if math.isnan(first_break_radius) and abs(cumulative_mean) >= BREAK_THRESHOLD:
                first_break_radius = float(point["RadiusFraction"])
            point_rows.append(
                {
                    "GalaxyName": galaxy,
                    "Class": point["Class"],
                    "PointIndex": str(index),
                    "RadiusKpc": point["RadiusKpc"],
                    "RadiusFraction": point["RadiusFraction"],
                    "aN_over_a0": point["aN_over_a0"],
                    "SignedLogResidual_TPG": fmt(residual),
                    "AbsLogResidual_TPG": fmt(abs(residual)),
                    "CumulativeMeanSignedResidual": fmt(cumulative_mean),
                    "CumulativeSignedResidual": fmt(cumulative),
                    "S_tau_eff_clipped_0_2": point["S_tau_eff_clipped_0_2"],
                    "InterpretationGuardrail": GUARDRAIL,
                }
            )
        positive_fraction = sum(value > 0 for value in signed_values) / len(signed_values)
        sign_imbalance = abs(positive_fraction - 0.5) * 2.0
        final_drift = cumulative_values[-1]
        drift_slope = pearson(
            [float(row["RadiusFraction"]) for row in points[: len(signed_values)]],
            cumulative_values,
        )
        galaxy_rows.append(
            {
                "GalaxyName": galaxy,
                "Class": points[0]["Class"],
                "NPoints": str(len(signed_values)),
                "FinalMeanSignedResidual": fmt(final_drift),
                "AbsFinalMeanSignedResidual": fmt(abs(final_drift)),
                "MaxAbsCumulativeMeanResidual": fmt(cumulative_abs_max),
                "RMSAbsResidual": fmt(rms([abs(value) for value in signed_values])),
                "MeanAbsResidual": fmt(mean([abs(value) for value in signed_values])),
                "PositiveResidualFraction": fmt(positive_fraction),
                "SignImbalance": fmt(sign_imbalance),
                "MaxSameSignRunFraction": fmt(max_same_sign_run(signed_values) / len(signed_values)),
                "FirstBreakRadiusFraction_abs0p15": fmt(first_break_radius),
                "CumulativeDriftRadiusPearson": fmt(drift_slope),
                "Median_S_tau_eff_clipped": fmt(
                    median([float(row["S_tau_eff_clipped_0_2"]) for row in points])
                ),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return point_rows, galaxy_rows


def metric_rows(galaxies: list[dict[str, str]]) -> list[dict[str, str]]:
    fields = [
        "AbsFinalMeanSignedResidual",
        "MaxAbsCumulativeMeanResidual",
        "SignImbalance",
        "MaxSameSignRunFraction",
        "RMSAbsResidual",
        "CumulativeDriftRadiusPearson",
    ]
    rows: list[dict[str, str]] = []
    for klass in ["all", "A", "C"]:
        subset = galaxies if klass == "all" else [row for row in galaxies if row["Class"] == klass]
        for field in fields:
            values = [float(row[field]) for row in subset if row[field] != ""]
            rows.append(
                {
                    "Group": klass,
                    "Metric": field,
                    "NGalaxies": str(len(values)),
                    "Median": fmt(median(values)),
                    "Mean": fmt(mean(values)),
                    "AUC_C_higher": fmt(auc_c_higher(galaxies, field)) if klass == "all" else "",
                    "InterpretationGuardrail": GUARDRAIL,
                }
            )
    return rows


def write_report(metrics: list[dict[str, str]], galaxies: list[dict[str, str]]) -> None:
    lookup = {(row["Group"], row["Metric"]): row for row in metrics}
    lines = [
        "# Integrated Tau Drift v0.1",
        "",
        "This diagnostic tests whether the fixed TPG/projection baseline departs from the observed rotation curves through cumulative radial drift rather than pointwise random scatter. It uses signed log residuals from the already fixed `S_tau=1` prescription.",
        "",
        "## Definitions",
        "",
        "- `SignedLogResidual_TPG = ln(Vobs / V_TPG)`.",
        "- `CumulativeMeanSignedResidual(R)` is the running mean of signed residuals from the inner radius to `R`.",
        "- `MaxAbsCumulativeMeanResidual` measures the strongest integrated drift amplitude.",
        "- `SignImbalance` measures whether residuals have a persistent sign rather than alternating randomly.",
        "- `FirstBreakRadiusFraction_abs0p15` is the first radius fraction where the absolute cumulative mean exceeds 0.15.",
        "",
        "## Main Results",
        "",
        f"- Galaxies: {len(galaxies)}",
        f"- Median max cumulative drift, all: {lookup[('all', 'MaxAbsCumulativeMeanResidual')]['Median']}",
        f"- Median max cumulative drift, A: {lookup[('A', 'MaxAbsCumulativeMeanResidual')]['Median']}",
        f"- Median max cumulative drift, C: {lookup[('C', 'MaxAbsCumulativeMeanResidual')]['Median']}",
        f"- AUC(C higher) for max cumulative drift: {lookup[('all', 'MaxAbsCumulativeMeanResidual')]['AUC_C_higher']}",
        f"- AUC(C higher) for sign imbalance: {lookup[('all', 'SignImbalance')]['AUC_C_higher']}",
        f"- AUC(C higher) for same-sign run fraction: {lookup[('all', 'MaxSameSignRunFraction')]['AUC_C_higher']}",
        "",
        "## Interpretation",
        "",
        "This is not an `S_tau` rule and not a validation claim. It asks whether TPG departures have memory-like radial structure. If cumulative drift and sign persistence separate disturbed systems better than raw pointwise scatter, the next model should treat `S_tau` as an integrated or history-dependent quantity rather than as an independent local constant.",
        "",
        "## Generated Files",
        "",
        "- `integrated_tau_drift_point_trace_v01.csv`",
        "- `integrated_tau_drift_galaxy_summary_v01.csv`",
        "- `integrated_tau_drift_metric_summary_v01.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "integrated_tau_drift_v01.md",
            "integrated_tau_drift_point_trace_v01.csv",
            "integrated_tau_drift_galaxy_summary_v01.csv",
            "integrated_tau_drift_metric_summary_v01.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["integrated_tau_drift_status"] = "signed_residual_cumulative_drift_diagnostic_complete"
    manifest["paper2_next_gate"] = "test_history_dependent_s_tau_candidate_from_drift_features"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    points, galaxies = point_and_galaxy_rows()
    metrics = metric_rows(galaxies)
    write_csv(
        POINT_OUT,
        points,
        [
            "GalaxyName",
            "Class",
            "PointIndex",
            "RadiusKpc",
            "RadiusFraction",
            "aN_over_a0",
            "SignedLogResidual_TPG",
            "AbsLogResidual_TPG",
            "CumulativeMeanSignedResidual",
            "CumulativeSignedResidual",
            "S_tau_eff_clipped_0_2",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        GALAXY_OUT,
        galaxies,
        [
            "GalaxyName",
            "Class",
            "NPoints",
            "FinalMeanSignedResidual",
            "AbsFinalMeanSignedResidual",
            "MaxAbsCumulativeMeanResidual",
            "RMSAbsResidual",
            "MeanAbsResidual",
            "PositiveResidualFraction",
            "SignImbalance",
            "MaxSameSignRunFraction",
            "FirstBreakRadiusFraction_abs0p15",
            "CumulativeDriftRadiusPearson",
            "Median_S_tau_eff_clipped",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        METRIC_OUT,
        metrics,
        [
            "Group",
            "Metric",
            "NGalaxies",
            "Median",
            "Mean",
            "AUC_C_higher",
            "InterpretationGuardrail",
        ],
    )
    write_report(metrics, galaxies)
    update_manifest()
    print(REPORT)
    print(f"integrated_tau_drift_galaxies={len(galaxies)}")


if __name__ == "__main__":
    main()
