#!/usr/bin/env python3
"""Evaluate a frozen radial/source-side S_tau(R) rule without target leakage."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET


POINTS = PACKET / "s_tau_eff_point_pilot.csv"
PREDICTIONS = PACKET / "predictive_s_tau_by_galaxy_v01.csv"
POINT_OUT = PACKET / "radial_s_tau_velocity_point_readout.csv"
GALAXY_OUT = PACKET / "radial_s_tau_velocity_galaxy_summary.csv"
METRIC_OUT = PACKET / "radial_s_tau_velocity_metric_summary.csv"
RULE_OUT = PACKET / "radial_s_tau_rule_v01.csv"
REPORT = PACKET / "radial_s_tau_rule_v01.md"


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


def radial_factor(radius_fraction: float, a_n_over_a0: float) -> tuple[float, str]:
    if radius_fraction < 0.33:
        factor = 0.90
        zone = "inner"
    elif radius_fraction < 0.67:
        factor = 0.98
        zone = "middle"
    else:
        factor = 1.06
        zone = "outer"
    if a_n_over_a0 < 0.1:
        factor += 0.04
        zone += "_low_acc_boost"
    elif a_n_over_a0 >= 0.3:
        factor -= 0.03
        zone += "_high_acc_trim"
    return factor, zone


def rule_rows() -> list[dict[str, str]]:
    return [
        {
            "RuleID": "S_tau_radial_v01",
            "Component": "inner_radius",
            "Condition": "RadiusFraction<0.33",
            "Multiplier": "0.90",
            "AllowedInputs": "EvidenceType;Confidence;RadiusFraction;aN_over_a0",
            "ForbiddenInputs": "Vobs;Vbar;Projection_RMS;residuals;S_tau_eff;Class",
            "InterpretationGuardrail": "frozen_radial_rule_not_fit_to_velocity_residuals",
        },
        {
            "RuleID": "S_tau_radial_v01",
            "Component": "middle_radius",
            "Condition": "0.33<=RadiusFraction<0.67",
            "Multiplier": "0.98",
            "AllowedInputs": "EvidenceType;Confidence;RadiusFraction;aN_over_a0",
            "ForbiddenInputs": "Vobs;Vbar;Projection_RMS;residuals;S_tau_eff;Class",
            "InterpretationGuardrail": "frozen_radial_rule_not_fit_to_velocity_residuals",
        },
        {
            "RuleID": "S_tau_radial_v01",
            "Component": "outer_radius",
            "Condition": "RadiusFraction>=0.67",
            "Multiplier": "1.06",
            "AllowedInputs": "EvidenceType;Confidence;RadiusFraction;aN_over_a0",
            "ForbiddenInputs": "Vobs;Vbar;Projection_RMS;residuals;S_tau_eff;Class",
            "InterpretationGuardrail": "frozen_radial_rule_not_fit_to_velocity_residuals",
        },
        {
            "RuleID": "S_tau_radial_v01",
            "Component": "low_acceleration",
            "Condition": "aN_over_a0<0.1",
            "Multiplier": "+0.04 additive",
            "AllowedInputs": "EvidenceType;Confidence;RadiusFraction;aN_over_a0",
            "ForbiddenInputs": "Vobs;Vbar;Projection_RMS;residuals;S_tau_eff;Class",
            "InterpretationGuardrail": "frozen_radial_rule_not_fit_to_velocity_residuals",
        },
        {
            "RuleID": "S_tau_radial_v01",
            "Component": "high_acceleration",
            "Condition": "aN_over_a0>=0.3",
            "Multiplier": "-0.03 additive",
            "AllowedInputs": "EvidenceType;Confidence;RadiusFraction;aN_over_a0",
            "ForbiddenInputs": "Vobs;Vbar;Projection_RMS;residuals;S_tau_eff;Class",
            "InterpretationGuardrail": "frozen_radial_rule_not_fit_to_velocity_residuals",
        },
    ]


def point_rows() -> list[dict[str, str]]:
    source = {
        row["GalaxyName"]: float(row["Predicted_S_tau_source_v01"])
        for row in read_csv(PREDICTIONS)
    }
    rows: list[dict[str, str]] = []
    for point in read_csv(POINTS):
        galaxy = point["GalaxyName"]
        if galaxy not in source:
            continue
        radius_fraction = float(point["RadiusFraction"])
        a_n = float(point["aN_over_a0"])
        factor, zone = radial_factor(radius_fraction, a_n)
        s_radial = min(1.15, max(0.65, source[galaxy] * factor))
        vobs = float(point["VobsKms"])
        vbar = float(point["VbarKms"])
        kernel = float(point["LogKernelAlphaLn"])
        model_s1 = vbar * (1.0 + kernel)
        model_radial = vbar * (1.0 + s_radial * kernel)
        if vobs <= 0 or model_s1 <= 0 or model_radial <= 0:
            continue
        residual_s1 = math.log(vobs / model_s1)
        residual_radial = math.log(vobs / model_radial)
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": point["Class"],
                "RadiusKpc": point["RadiusKpc"],
                "RadiusFraction": point["RadiusFraction"],
                "aN_over_a0": point["aN_over_a0"],
                "SourceS_tau": fmt(source[galaxy]),
                "RadialFactor": fmt(factor),
                "RadialZone": zone,
                "Predicted_S_tau_radial_v01": fmt(s_radial),
                "AbsLogResidual_S_tau1": fmt(abs(residual_s1)),
                "AbsLogResidual_RadialRule": fmt(abs(residual_radial)),
                "DeltaAbsLogResidual_RadialMinusS1": fmt(
                    abs(residual_radial) - abs(residual_s1)
                ),
                "InterpretationGuardrail": "radial_source_rule_velocity_readout_no_refit",
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
        radial = [float(row["AbsLogResidual_RadialRule"]) for row in values]
        deltas = [float(row["DeltaAbsLogResidual_RadialMinusS1"]) for row in values]
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": values[0]["Class"],
                "NPoints": str(len(values)),
                "RMSLogResidual_S_tau1": fmt(rms(s1)),
                "RMSLogResidual_RadialRule": fmt(rms(radial)),
                "DeltaRMS_RadialMinusS1": fmt(rms(radial) - rms(s1)),
                "FractionPointsImproved": fmt(sum(delta < 0 for delta in deltas) / len(deltas)),
                "InterpretationGuardrail": "radial_rule_vs_s_tau1_no_refit",
            }
        )
    return rows


def metric_rows(galaxies: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for klass in ["all", "A", "C"]:
        subset = galaxies if klass == "all" else [row for row in galaxies if row["Class"] == klass]
        deltas = [float(row["DeltaRMS_RadialMinusS1"]) for row in subset]
        rows.append(
            {
                "Subset": klass,
                "NGalaxies": str(len(subset)),
                "MedianDeltaRMS_RadialMinusS1": fmt(median(deltas)),
                "MeanDeltaRMS_RadialMinusS1": fmt(mean(deltas)),
                "FractionGalaxiesImproved": fmt(sum(delta < 0 for delta in deltas) / len(deltas)),
                "MedianRMS_S_tau1": fmt(median([float(row["RMSLogResidual_S_tau1"]) for row in subset])),
                "MedianRMS_RadialRule": fmt(
                    median([float(row["RMSLogResidual_RadialRule"]) for row in subset])
                ),
                "InterpretationGuardrail": "radial_velocity_residual_readout_not_refit",
            }
        )
    return rows


def write_report(metrics: list[dict[str, str]]) -> None:
    by_subset = {row["Subset"]: row for row in metrics}
    lines = [
        "# Radial S_tau Rule v0.1",
        "",
        "This gate evaluates a frozen radial/source-side `S_tau(R)` rule against the old `S_tau=1` projection baseline. The rule uses only source-side evidence metadata plus `RadiusFraction` and `aN/a0`; it does not use `Vobs`, residuals, or `S_tau_eff` to define the rule.",
        "",
        "## Main Metrics",
        "",
        f"- All-galaxy median delta RMS radial-minus-S1: {by_subset['all']['MedianDeltaRMS_RadialMinusS1']}",
        f"- All-galaxy fraction improved: {by_subset['all']['FractionGalaxiesImproved']}",
        f"- A median delta RMS: {by_subset['A']['MedianDeltaRMS_RadialMinusS1']}",
        f"- C median delta RMS: {by_subset['C']['MedianDeltaRMS_RadialMinusS1']}",
        "",
        "Negative delta means the radial rule improves over `S_tau=1`; positive delta means it worsens.",
        "",
        "## Interpretation",
        "",
        "This is a leakage-controlled radial heuristic, not a fitted physical law. It tests whether adding a predeclared radial/acceleration dependence helps more than a single galaxy-level `S_tau` value.",
        "",
        "## Generated Files",
        "",
        "- `radial_s_tau_rule_v01.csv`",
        "- `radial_s_tau_velocity_point_readout.csv`",
        "- `radial_s_tau_velocity_galaxy_summary.csv`",
        "- `radial_s_tau_velocity_metric_summary.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "radial_s_tau_rule_v01.csv",
            "radial_s_tau_rule_v01.md",
            "radial_s_tau_velocity_point_readout.csv",
            "radial_s_tau_velocity_galaxy_summary.csv",
            "radial_s_tau_velocity_metric_summary.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["radial_s_tau_rule_status"] = "frozen_radial_source_rule_no_refit_readout_complete"
    manifest["paper2_next_gate"] = "compare_global_source_vs_radial_s_tau_and_decide_paper2_scope"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rules = rule_rows()
    points = point_rows()
    galaxies = galaxy_summary(points)
    metrics = metric_rows(galaxies)
    write_csv(
        RULE_OUT,
        rules,
        [
            "RuleID",
            "Component",
            "Condition",
            "Multiplier",
            "AllowedInputs",
            "ForbiddenInputs",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        POINT_OUT,
        points,
        [
            "GalaxyName",
            "Class",
            "RadiusKpc",
            "RadiusFraction",
            "aN_over_a0",
            "SourceS_tau",
            "RadialFactor",
            "RadialZone",
            "Predicted_S_tau_radial_v01",
            "AbsLogResidual_S_tau1",
            "AbsLogResidual_RadialRule",
            "DeltaAbsLogResidual_RadialMinusS1",
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
            "RMSLogResidual_RadialRule",
            "DeltaRMS_RadialMinusS1",
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
            "MedianDeltaRMS_RadialMinusS1",
            "MeanDeltaRMS_RadialMinusS1",
            "FractionGalaxiesImproved",
            "MedianRMS_S_tau1",
            "MedianRMS_RadialRule",
            "InterpretationGuardrail",
        ],
    )
    write_report(metrics)
    update_manifest()
    print(REPORT)
    print(f"radial_s_tau_velocity_galaxies={len(galaxies)}")


if __name__ == "__main__":
    main()
