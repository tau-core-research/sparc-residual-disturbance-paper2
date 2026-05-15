#!/usr/bin/env python3
"""Evaluate frozen source-side S_tau against the S_tau=1 projection baseline."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET


POINTS = PACKET / "s_tau_eff_point_pilot.csv"
PREDICTIONS = PACKET / "predictive_s_tau_by_galaxy_v01.csv"
POINT_OUT = PACKET / "predictive_s_tau_velocity_point_readout.csv"
GALAXY_OUT = PACKET / "predictive_s_tau_velocity_galaxy_summary.csv"
METRIC_OUT = PACKET / "predictive_s_tau_velocity_metric_summary.csv"
REPORT = PACKET / "predictive_s_tau_velocity_readout.md"


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


def point_rows() -> list[dict[str, str]]:
    s_by_galaxy = {
        row["GalaxyName"]: float(row["Predicted_S_tau_source_v01"])
        for row in read_csv(PREDICTIONS)
    }
    rows: list[dict[str, str]] = []
    for point in read_csv(POINTS):
        galaxy = point["GalaxyName"]
        if galaxy not in s_by_galaxy:
            continue
        vobs = float(point["VobsKms"])
        vbar = float(point["VbarKms"])
        kernel = float(point["LogKernelAlphaLn"])
        s_source = s_by_galaxy[galaxy]
        model_s1 = vbar * (1.0 + kernel)
        model_source = vbar * (1.0 + s_source * kernel)
        if vobs <= 0 or model_s1 <= 0 or model_source <= 0:
            continue
        log_residual_s1 = math.log(vobs / model_s1)
        log_residual_source = math.log(vobs / model_source)
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": point["Class"],
                "RadiusKpc": point["RadiusKpc"],
                "RadiusFraction": point["RadiusFraction"],
                "aN_over_a0": point["aN_over_a0"],
                "VobsKms": point["VobsKms"],
                "VbarKms": point["VbarKms"],
                "Predicted_S_tau_source_v01": fmt(s_source),
                "ModelVelocity_S_tau1": fmt(model_s1),
                "ModelVelocity_SourceRule": fmt(model_source),
                "AbsLogResidual_S_tau1": fmt(abs(log_residual_s1)),
                "AbsLogResidual_SourceRule": fmt(abs(log_residual_source)),
                "DeltaAbsLogResidual_SourceMinusS1": fmt(
                    abs(log_residual_source) - abs(log_residual_s1)
                ),
                "InterpretationGuardrail": "post_freeze_velocity_readout_no_refit",
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
        source = [float(row["AbsLogResidual_SourceRule"]) for row in values]
        deltas = [float(row["DeltaAbsLogResidual_SourceMinusS1"]) for row in values]
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": values[0]["Class"],
                "NPoints": str(len(values)),
                "RMSLogResidual_S_tau1": fmt(rms(s1)),
                "RMSLogResidual_SourceRule": fmt(rms(source)),
                "MeanAbsLogResidual_S_tau1": fmt(mean(s1)),
                "MeanAbsLogResidual_SourceRule": fmt(mean(source)),
                "DeltaRMS_SourceMinusS1": fmt(rms(source) - rms(s1)),
                "FractionPointsImproved": fmt(sum(delta < 0 for delta in deltas) / len(deltas)),
                "InterpretationGuardrail": "source_rule_vs_s_tau1_no_refit",
            }
        )
    return rows


def metric_rows(galaxies: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for klass in ["all", "A", "C"]:
        subset = galaxies if klass == "all" else [row for row in galaxies if row["Class"] == klass]
        deltas = [float(row["DeltaRMS_SourceMinusS1"]) for row in subset]
        rows.append(
            {
                "Subset": klass,
                "NGalaxies": str(len(subset)),
                "MedianDeltaRMS_SourceMinusS1": fmt(median(deltas)),
                "MeanDeltaRMS_SourceMinusS1": fmt(mean(deltas)),
                "FractionGalaxiesImproved": fmt(sum(delta < 0 for delta in deltas) / len(deltas)),
                "MedianRMS_S_tau1": fmt(median([float(row["RMSLogResidual_S_tau1"]) for row in subset])),
                "MedianRMS_SourceRule": fmt(
                    median([float(row["RMSLogResidual_SourceRule"]) for row in subset])
                ),
                "InterpretationGuardrail": "velocity_residual_readout_not_refit",
            }
        )
    return rows


def write_report(metrics: list[dict[str, str]]) -> None:
    by_subset = {row["Subset"]: row for row in metrics}
    lines = [
        "# Predictive S_tau Velocity Readout",
        "",
        "This readout compares the frozen source-side `S_tau` rule with the old `S_tau=1` projection baseline on velocity-level log residuals. No coefficients are refit.",
        "",
        "## Main Metrics",
        "",
        f"- All-galaxy median delta RMS source-minus-S1: {by_subset['all']['MedianDeltaRMS_SourceMinusS1']}",
        f"- All-galaxy fraction improved: {by_subset['all']['FractionGalaxiesImproved']}",
        f"- A median delta RMS: {by_subset['A']['MedianDeltaRMS_SourceMinusS1']}",
        f"- C median delta RMS: {by_subset['C']['MedianDeltaRMS_SourceMinusS1']}",
        "",
        "Negative delta means the frozen source-side rule improves over `S_tau=1`; positive delta means it worsens.",
        "",
        "## Interpretation",
        "",
        "This is the first direct no-refit test of whether the source-side `S_tau` rule improves the TPG/projection baseline. A weak or mixed result should be treated as evidence that the simple galaxy-level evidence mapping is not yet sufficient; the next viable rule likely needs radial or kinematic source information.",
        "",
        "## Generated Files",
        "",
        "- `predictive_s_tau_velocity_point_readout.csv`",
        "- `predictive_s_tau_velocity_galaxy_summary.csv`",
        "- `predictive_s_tau_velocity_metric_summary.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "predictive_s_tau_velocity_point_readout.csv",
            "predictive_s_tau_velocity_galaxy_summary.csv",
            "predictive_s_tau_velocity_metric_summary.csv",
            "predictive_s_tau_velocity_readout.md",
        }
    )
    manifest["files"] = sorted(files)
    manifest["predictive_s_tau_velocity_status"] = "source_rule_vs_s_tau1_no_refit_readout_complete"
    manifest["paper2_next_gate"] = "radial_or_kinematic_s_tau_rule_needed_if_source_rule_weak"
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
            "aN_over_a0",
            "VobsKms",
            "VbarKms",
            "Predicted_S_tau_source_v01",
            "ModelVelocity_S_tau1",
            "ModelVelocity_SourceRule",
            "AbsLogResidual_S_tau1",
            "AbsLogResidual_SourceRule",
            "DeltaAbsLogResidual_SourceMinusS1",
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
            "RMSLogResidual_SourceRule",
            "MeanAbsLogResidual_S_tau1",
            "MeanAbsLogResidual_SourceRule",
            "DeltaRMS_SourceMinusS1",
            "FractionPointsImproved",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        METRIC_OUT,
        metrics,
        [
            "Subset",
            "NGalaxies",
            "MedianDeltaRMS_SourceMinusS1",
            "MeanDeltaRMS_SourceMinusS1",
            "FractionGalaxiesImproved",
            "MedianRMS_S_tau1",
            "MedianRMS_SourceRule",
            "InterpretationGuardrail",
        ],
    )
    write_report(metrics)
    update_manifest()
    print(REPORT)
    print(f"predictive_s_tau_velocity_galaxies={len(galaxies)}")


if __name__ == "__main__":
    main()
