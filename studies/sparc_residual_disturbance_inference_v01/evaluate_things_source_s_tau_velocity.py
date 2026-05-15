#!/usr/bin/env python3
"""Evaluate THINGS source-side S_tau(R) against the S_tau=1 velocity baseline."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET


POINTS = PACKET / "s_tau_eff_point_pilot.csv"
SOURCE_STAU = PACKET / "path_b_source_only_stau_readout_joined_points.csv"
POINT_OUT = PACKET / "things_source_s_tau_velocity_point_readout.csv"
GALAXY_OUT = PACKET / "things_source_s_tau_velocity_galaxy_summary.csv"
METRIC_OUT = PACKET / "things_source_s_tau_velocity_metric_summary.csv"
REPORT = PACKET / "things_source_s_tau_velocity_readout.md"

GUARDRAIL = "things_source_s_tau_velocity_readout_no_refit_not_validation"


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


def point_index() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(POINTS):
        grouped.setdefault(row["GalaxyName"], []).append(row)
    return grouped


def nearest_point(
    candidates: list[dict[str, str]], radius_kpc: float, radius_fraction: float
) -> tuple[dict[str, str], float]:
    best = min(
        candidates,
        key=lambda row: (
            abs(float(row["RadiusKpc"]) - radius_kpc),
            abs(float(row["RadiusFraction"]) - radius_fraction),
        ),
    )
    return best, abs(float(best["RadiusKpc"]) - radius_kpc)


def velocity_residual(vobs: float, vbar: float, kernel: float, s_tau: float) -> tuple[float, float]:
    model = vbar * (1.0 + s_tau * kernel)
    if vobs <= 0 or model <= 0:
        return math.nan, math.nan
    return model, abs(math.log(vobs / model))


def point_rows() -> list[dict[str, str]]:
    indexed = point_index()
    rows: list[dict[str, str]] = []
    for source in read_csv(SOURCE_STAU):
        galaxy = source["GalaxyName"]
        if galaxy not in indexed:
            continue
        radius_kpc = float(source["SPARC_RadiusKpc"])
        radius_fraction = float(source["SPARC_RadiusFraction"])
        point, join_delta = nearest_point(indexed[galaxy], radius_kpc, radius_fraction)
        vobs = float(point["VobsKms"])
        vbar = float(point["VbarKms"])
        kernel = float(point["LogKernelAlphaLn"])
        s_percentile = float(source["S_tau_source_percentile"])
        s_log = float(source["S_tau_source_log"])
        model_s1, residual_s1 = velocity_residual(vobs, vbar, kernel, 1.0)
        model_percentile, residual_percentile = velocity_residual(vobs, vbar, kernel, s_percentile)
        model_log, residual_log = velocity_residual(vobs, vbar, kernel, s_log)
        if any(math.isnan(value) for value in [residual_s1, residual_percentile, residual_log]):
            continue
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": point["Class"],
                "RadiusKpc": point["RadiusKpc"],
                "RadiusFraction": point["RadiusFraction"],
                "JoinRadiusDeltaKpc": fmt(join_delta),
                "StressDispersionOverRotationScale": source["StressDispersionOverRotationScale"],
                "S_tau_source_percentile": fmt(s_percentile),
                "S_tau_source_log": fmt(s_log),
                "aN_over_a0": point["aN_over_a0"],
                "VobsKms": point["VobsKms"],
                "VbarKms": point["VbarKms"],
                "ModelVelocity_S_tau1": fmt(model_s1),
                "ModelVelocity_SourcePercentile": fmt(model_percentile),
                "ModelVelocity_SourceLog": fmt(model_log),
                "AbsLogResidual_S_tau1": fmt(residual_s1),
                "AbsLogResidual_SourcePercentile": fmt(residual_percentile),
                "AbsLogResidual_SourceLog": fmt(residual_log),
                "DeltaAbsLogResidual_SourcePercentileMinusS1": fmt(
                    residual_percentile - residual_s1
                ),
                "DeltaAbsLogResidual_SourceLogMinusS1": fmt(residual_log - residual_s1),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def galaxy_summary(points: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in points:
        grouped.setdefault(row["GalaxyName"], []).append(row)
    rows: list[dict[str, str]] = []
    for galaxy, values in sorted(grouped.items()):
        s1 = [float(row["AbsLogResidual_S_tau1"]) for row in values]
        percentile = [float(row["AbsLogResidual_SourcePercentile"]) for row in values]
        log = [float(row["AbsLogResidual_SourceLog"]) for row in values]
        delta_percentile = [
            float(row["DeltaAbsLogResidual_SourcePercentileMinusS1"]) for row in values
        ]
        delta_log = [float(row["DeltaAbsLogResidual_SourceLogMinusS1"]) for row in values]
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": values[0]["Class"],
                "NPoints": str(len(values)),
                "RMSLogResidual_S_tau1": fmt(rms(s1)),
                "RMSLogResidual_SourcePercentile": fmt(rms(percentile)),
                "RMSLogResidual_SourceLog": fmt(rms(log)),
                "DeltaRMS_SourcePercentileMinusS1": fmt(rms(percentile) - rms(s1)),
                "DeltaRMS_SourceLogMinusS1": fmt(rms(log) - rms(s1)),
                "FractionPointsImprovedPercentile": fmt(
                    sum(delta < 0 for delta in delta_percentile) / len(delta_percentile)
                ),
                "FractionPointsImprovedLog": fmt(sum(delta < 0 for delta in delta_log) / len(delta_log)),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def metric_rows(galaxies: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for klass in ["all", "A", "C"]:
        subset = galaxies if klass == "all" else [row for row in galaxies if row["Class"] == klass]
        delta_percentile = [float(row["DeltaRMS_SourcePercentileMinusS1"]) for row in subset]
        delta_log = [float(row["DeltaRMS_SourceLogMinusS1"]) for row in subset]
        rows.append(
            {
                "Subset": klass,
                "NGalaxies": str(len(subset)),
                "MedianDeltaRMS_SourcePercentileMinusS1": fmt(median(delta_percentile)),
                "MeanDeltaRMS_SourcePercentileMinusS1": fmt(mean(delta_percentile)),
                "FractionGalaxiesImprovedPercentile": fmt(
                    sum(delta < 0 for delta in delta_percentile) / len(delta_percentile)
                ),
                "MedianDeltaRMS_SourceLogMinusS1": fmt(median(delta_log)),
                "MeanDeltaRMS_SourceLogMinusS1": fmt(mean(delta_log)),
                "FractionGalaxiesImprovedLog": fmt(
                    sum(delta < 0 for delta in delta_log) / len(delta_log)
                ),
                "MedianRMS_S_tau1": fmt(
                    median([float(row["RMSLogResidual_S_tau1"]) for row in subset])
                ),
                "MedianRMS_SourcePercentile": fmt(
                    median([float(row["RMSLogResidual_SourcePercentile"]) for row in subset])
                ),
                "MedianRMS_SourceLog": fmt(
                    median([float(row["RMSLogResidual_SourceLog"]) for row in subset])
                ),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def write_report(metrics: list[dict[str, str]], points: list[dict[str, str]]) -> None:
    by_subset = {row["Subset"]: row for row in metrics}
    galaxies = sorted({row["GalaxyName"] for row in points})
    lines = [
        "# THINGS Source-Side S_tau(R) Velocity Readout",
        "",
        "This gate evaluates the copied THINGS ring-level source-side `S_tau(R)` readout against the old `S_tau=1` velocity baseline. It reports both bounded mappings from the source packet and does not select one by outcome.",
        "",
        "## Scope",
        "",
        f"- Joined points: {len(points)}",
        f"- THINGS-overlap galaxies: {len(galaxies)} ({', '.join(galaxies)})",
        "- Input signal: kinematic stress proxy from source-side THINGS ring metadata.",
        "- Forbidden use: no coefficient refit, no target-residual training, no model selection between mappings.",
        "",
        "## Main Metrics",
        "",
        f"- All-galaxy median delta RMS percentile-minus-S1: {by_subset['all']['MedianDeltaRMS_SourcePercentileMinusS1']}",
        f"- All-galaxy fraction improved, percentile mapping: {by_subset['all']['FractionGalaxiesImprovedPercentile']}",
        f"- All-galaxy median delta RMS log-minus-S1: {by_subset['all']['MedianDeltaRMS_SourceLogMinusS1']}",
        f"- All-galaxy fraction improved, log mapping: {by_subset['all']['FractionGalaxiesImprovedLog']}",
        f"- A median delta RMS, percentile/log: {by_subset['A']['MedianDeltaRMS_SourcePercentileMinusS1']} / {by_subset['A']['MedianDeltaRMS_SourceLogMinusS1']}",
        f"- C median delta RMS, percentile/log: {by_subset['C']['MedianDeltaRMS_SourcePercentileMinusS1']} / {by_subset['C']['MedianDeltaRMS_SourceLogMinusS1']}",
        "",
        "Negative delta means the source-side `S_tau(R)` mapping improves over `S_tau=1`; positive delta means it worsens.",
        "",
        "## Interpretation",
        "",
        "This is a small-overlap, source-only kinematic sanity check. It is useful if it indicates whether ring-level stress is a better direction than a single galaxy-level source score, but it is not external validation and not a Tau Core proof. A mixed or negative result means that the next `S_tau` gate needs a better held-out mapping rather than outcome-selected tuning.",
        "",
        "## Generated Files",
        "",
        "- `things_source_s_tau_velocity_point_readout.csv`",
        "- `things_source_s_tau_velocity_galaxy_summary.csv`",
        "- `things_source_s_tau_velocity_metric_summary.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "path_b_source_only_stau_readout.md",
            "path_b_source_only_stau_readout_joined_points.csv",
            "things_source_s_tau_velocity_point_readout.csv",
            "things_source_s_tau_velocity_galaxy_summary.csv",
            "things_source_s_tau_velocity_metric_summary.csv",
            "things_source_s_tau_velocity_readout.md",
        }
    )
    manifest["files"] = sorted(files)
    manifest["things_source_s_tau_velocity_status"] = (
        "things_source_only_s_tau_velocity_readout_complete_no_refit"
    )
    manifest["paper2_next_gate"] = "compare_things_source_s_tau_before_expanding_external_validation"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    points = point_rows()
    galaxies = galaxy_summary(points)
    metrics = metric_rows(galaxies)
    write_csv(
        POINT_OUT,
        points,
        [
            "GalaxyName",
            "Class",
            "RadiusKpc",
            "RadiusFraction",
            "JoinRadiusDeltaKpc",
            "StressDispersionOverRotationScale",
            "S_tau_source_percentile",
            "S_tau_source_log",
            "aN_over_a0",
            "VobsKms",
            "VbarKms",
            "ModelVelocity_S_tau1",
            "ModelVelocity_SourcePercentile",
            "ModelVelocity_SourceLog",
            "AbsLogResidual_S_tau1",
            "AbsLogResidual_SourcePercentile",
            "AbsLogResidual_SourceLog",
            "DeltaAbsLogResidual_SourcePercentileMinusS1",
            "DeltaAbsLogResidual_SourceLogMinusS1",
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
            "RMSLogResidual_S_tau1",
            "RMSLogResidual_SourcePercentile",
            "RMSLogResidual_SourceLog",
            "DeltaRMS_SourcePercentileMinusS1",
            "DeltaRMS_SourceLogMinusS1",
            "FractionPointsImprovedPercentile",
            "FractionPointsImprovedLog",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        METRIC_OUT,
        metrics,
        [
            "Subset",
            "NGalaxies",
            "MedianDeltaRMS_SourcePercentileMinusS1",
            "MeanDeltaRMS_SourcePercentileMinusS1",
            "FractionGalaxiesImprovedPercentile",
            "MedianDeltaRMS_SourceLogMinusS1",
            "MeanDeltaRMS_SourceLogMinusS1",
            "FractionGalaxiesImprovedLog",
            "MedianRMS_S_tau1",
            "MedianRMS_SourcePercentile",
            "MedianRMS_SourceLog",
            "InterpretationGuardrail",
        ],
    )
    write_report(metrics, points)
    update_manifest()
    print(REPORT)
    print(f"things_source_s_tau_velocity_galaxies={len(galaxies)}")


if __name__ == "__main__":
    main()
