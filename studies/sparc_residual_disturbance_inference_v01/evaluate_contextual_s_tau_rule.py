#!/usr/bin/env python3
"""Freeze and evaluate a conservative contextual THINGS S_tau(R) rule."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET


POINTS = PACKET / "things_source_s_tau_velocity_point_readout.csv"
RULE_OUT = PACKET / "contextual_s_tau_rule_v01.csv"
POINT_OUT = PACKET / "contextual_s_tau_velocity_point_readout.csv"
GALAXY_OUT = PACKET / "contextual_s_tau_velocity_galaxy_summary.csv"
METRIC_OUT = PACKET / "contextual_s_tau_velocity_metric_summary.csv"
REPORT = PACKET / "contextual_s_tau_rule_v01.md"

GUARDRAIL = "contextual_s_tau_rule_post_audit_candidate_not_validation"


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


def contextual_s_tau(radius_fraction: float, a_n_over_a0: float, stress: float) -> tuple[float, str]:
    s_tau = 1.0
    components: list[str] = ["base_1p00"]
    if a_n_over_a0 < 0.1:
        s_tau += 0.04
        components.append("low_acc_plus_0p04")
    elif a_n_over_a0 >= 0.3:
        s_tau += 0.02
        components.append("high_acc_plus_0p02")
    if radius_fraction >= 0.67:
        s_tau += 0.03
        components.append("outer_plus_0p03")
    elif radius_fraction < 0.33:
        s_tau += 0.02
        components.append("inner_plus_0p02")
    if stress >= 2.0:
        s_tau -= 0.08
        components.append("very_high_stress_minus_0p08")
    elif stress >= 1.0:
        s_tau -= 0.04
        components.append("high_stress_minus_0p04")
    elif stress < 0.25:
        s_tau += 0.03
        components.append("low_stress_plus_0p03")
    return min(1.12, max(0.88, s_tau)), ";".join(components)


def velocity_residual(vobs: float, vbar: float, kernel: float, s_tau: float) -> tuple[float, float]:
    model = vbar * (1.0 + s_tau * kernel)
    if vobs <= 0 or model <= 0:
        return math.nan, math.nan
    return model, abs(math.log(vobs / model))


def rule_rows() -> list[dict[str, str]]:
    rows = [
        ("base", "all points", "1.00", "S_tau starts at the old projection baseline"),
        ("low_acceleration", "aN_over_a0<0.1", "+0.04", "low-acceleration points receive a small positive allowance"),
        ("high_acceleration", "aN_over_a0>=0.3", "+0.02", "high-acceleration points are kept close to the baseline"),
        ("outer_radius", "RadiusFraction>=0.67", "+0.03", "outer disks receive a small positive allowance"),
        ("inner_radius", "RadiusFraction<0.33", "+0.02", "inner points are protected against over-suppression"),
        ("very_high_stress", "StressDispersionOverRotationScale>=2.0", "-0.08", "strong stress can suppress coherence but only weakly"),
        ("high_stress", "1.0<=StressDispersionOverRotationScale<2.0", "-0.04", "moderate stress applies a small suppression"),
        ("low_stress", "StressDispersionOverRotationScale<0.25", "+0.03", "very low stress receives a small coherence allowance"),
        ("bounds", "after additive components", "[0.88, 1.12]", "the rule is deliberately conservative around S_tau=1"),
    ]
    return [
        {
            "RuleID": "S_tau_contextual_v01",
            "Component": component,
            "Condition": condition,
            "AdditiveOrBound": adjustment,
            "Rationale": rationale,
            "AllowedInputs": "RadiusFraction;aN_over_a0;StressDispersionOverRotationScale",
            "ForbiddenInputs": "Vobs;Vbar;residuals;S_tau_eff;Class;outcome_selected_mapping",
            "InterpretationGuardrail": GUARDRAIL,
        }
        for component, condition, adjustment, rationale in rows
    ]


def point_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in read_csv(POINTS):
        radius_fraction = float(row["RadiusFraction"])
        a_n = float(row["aN_over_a0"])
        stress = float(row["StressDispersionOverRotationScale"])
        s_tau, components = contextual_s_tau(radius_fraction, a_n, stress)
        vobs = float(row["VobsKms"])
        vbar = float(row["VbarKms"])
        model_s1 = float(row["ModelVelocity_S_tau1"])
        residual_s1 = float(row["AbsLogResidual_S_tau1"])
        kernel = (model_s1 / vbar) - 1.0
        model_contextual, residual_contextual = velocity_residual(vobs, vbar, kernel, s_tau)
        if math.isnan(residual_contextual):
            continue
        rows.append(
            {
                "GalaxyName": row["GalaxyName"],
                "Class": row["Class"],
                "RadiusKpc": row["RadiusKpc"],
                "RadiusFraction": row["RadiusFraction"],
                "aN_over_a0": row["aN_over_a0"],
                "StressDispersionOverRotationScale": row["StressDispersionOverRotationScale"],
                "Predicted_S_tau_contextual_v01": fmt(s_tau),
                "ContextualComponents": components,
                "ModelVelocity_S_tau1": fmt(model_s1),
                "ModelVelocity_ContextualRule": fmt(model_contextual),
                "AbsLogResidual_S_tau1": fmt(residual_s1),
                "AbsLogResidual_ContextualRule": fmt(residual_contextual),
                "DeltaAbsLogResidual_ContextualMinusS1": fmt(residual_contextual - residual_s1),
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
        contextual = [float(row["AbsLogResidual_ContextualRule"]) for row in values]
        deltas = [float(row["DeltaAbsLogResidual_ContextualMinusS1"]) for row in values]
        s_values = [float(row["Predicted_S_tau_contextual_v01"]) for row in values]
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": values[0]["Class"],
                "NPoints": str(len(values)),
                "MedianPredicted_S_tau_contextual": fmt(median(s_values)),
                "RMSLogResidual_S_tau1": fmt(rms(s1)),
                "RMSLogResidual_ContextualRule": fmt(rms(contextual)),
                "DeltaRMS_ContextualMinusS1": fmt(rms(contextual) - rms(s1)),
                "FractionPointsImproved": fmt(sum(delta < 0 for delta in deltas) / len(deltas)),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def metric_rows(galaxies: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for klass in ["all", "A", "C"]:
        subset = galaxies if klass == "all" else [row for row in galaxies if row["Class"] == klass]
        deltas = [float(row["DeltaRMS_ContextualMinusS1"]) for row in subset]
        rows.append(
            {
                "Subset": klass,
                "NGalaxies": str(len(subset)),
                "MedianDeltaRMS_ContextualMinusS1": fmt(median(deltas)),
                "MeanDeltaRMS_ContextualMinusS1": fmt(mean(deltas)),
                "FractionGalaxiesImproved": fmt(sum(delta < 0 for delta in deltas) / len(deltas)),
                "MedianRMS_S_tau1": fmt(median([float(row["RMSLogResidual_S_tau1"]) for row in subset])),
                "MedianRMS_ContextualRule": fmt(
                    median([float(row["RMSLogResidual_ContextualRule"]) for row in subset])
                ),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def write_report(metrics: list[dict[str, str]]) -> None:
    by_subset = {row["Subset"]: row for row in metrics}
    lines = [
        "# Contextual S_tau Rule v0.1",
        "",
        "This gate freezes a conservative contextual THINGS `S_tau(R)` candidate after the source-side failure audit. It is a post-audit candidate, not validation. The rule stays close to `S_tau=1` and uses only radius fraction, acceleration regime, and the THINGS stress proxy.",
        "",
        "## Rule Summary",
        "",
        "- Start at `S_tau=1.00`.",
        "- Apply small additive context terms for low acceleration, radius zone, and stress level.",
        "- Bound the result to `[0.88, 1.12]`.",
        "- Forbidden inputs: `Vobs`, `Vbar`, residuals, empirical `S_tau_eff`, A/C class, and outcome-selected mapping choice.",
        "",
        "## Velocity Readout",
        "",
        f"- All-galaxy median delta RMS contextual-minus-S1: {by_subset['all']['MedianDeltaRMS_ContextualMinusS1']}",
        f"- All-galaxy fraction improved: {by_subset['all']['FractionGalaxiesImproved']}",
        f"- A median delta RMS: {by_subset['A']['MedianDeltaRMS_ContextualMinusS1']}",
        f"- C median delta RMS: {by_subset['C']['MedianDeltaRMS_ContextualMinusS1']}",
        "",
        "Negative delta means the contextual rule improves over `S_tau=1`; positive delta means it worsens.",
        "",
        "## Interpretation",
        "",
        "This rule tests whether a small, context-aware local term is safer than a direct stress-to-suppression mapping. Because the rule was motivated after inspecting a failure mode, any positive result remains hypothesis-generating until a held-out source-family gate is run.",
        "",
        "## Generated Files",
        "",
        "- `contextual_s_tau_rule_v01.csv`",
        "- `contextual_s_tau_velocity_point_readout.csv`",
        "- `contextual_s_tau_velocity_galaxy_summary.csv`",
        "- `contextual_s_tau_velocity_metric_summary.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "contextual_s_tau_rule_v01.csv",
            "contextual_s_tau_rule_v01.md",
            "contextual_s_tau_velocity_point_readout.csv",
            "contextual_s_tau_velocity_galaxy_summary.csv",
            "contextual_s_tau_velocity_metric_summary.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["contextual_s_tau_rule_status"] = "post_audit_candidate_velocity_readout_complete"
    manifest["paper2_next_gate"] = "heldout_source_family_test_required_for_contextual_s_tau"
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
            "AdditiveOrBound",
            "Rationale",
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
            "StressDispersionOverRotationScale",
            "Predicted_S_tau_contextual_v01",
            "ContextualComponents",
            "ModelVelocity_S_tau1",
            "ModelVelocity_ContextualRule",
            "AbsLogResidual_S_tau1",
            "AbsLogResidual_ContextualRule",
            "DeltaAbsLogResidual_ContextualMinusS1",
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
            "MedianPredicted_S_tau_contextual",
            "RMSLogResidual_S_tau1",
            "RMSLogResidual_ContextualRule",
            "DeltaRMS_ContextualMinusS1",
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
            "MedianDeltaRMS_ContextualMinusS1",
            "MeanDeltaRMS_ContextualMinusS1",
            "FractionGalaxiesImproved",
            "MedianRMS_S_tau1",
            "MedianRMS_ContextualRule",
            "InterpretationGuardrail",
        ],
    )
    write_report(metrics)
    update_manifest()
    print(REPORT)
    print(f"contextual_s_tau_velocity_galaxies={len(galaxies)}")


if __name__ == "__main__":
    main()
