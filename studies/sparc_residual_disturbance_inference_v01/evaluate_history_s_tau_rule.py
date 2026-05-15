#!/usr/bin/env python3
"""Evaluate a causal history-dependent S_tau readout from inner residual drift."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET


POINTS = PACKET / "s_tau_eff_point_pilot.csv"
RULE_OUT = PACKET / "history_s_tau_rule_v01.csv"
POINT_OUT = PACKET / "history_s_tau_velocity_point_readout.csv"
GALAXY_OUT = PACKET / "history_s_tau_velocity_galaxy_summary.csv"
METRIC_OUT = PACKET / "history_s_tau_velocity_metric_summary.csv"
REPORT = PACKET / "history_s_tau_rule_v01.md"

GAIN = 0.50
S_LOW = 0.50
S_HIGH = 1.50
GUARDRAIL = "causal_inner_residual_history_readout_not_external_prediction"


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


def signed_residual(vobs: float, model: float) -> float:
    if vobs <= 0 or model <= 0:
        return math.nan
    return math.log(vobs / model)


def grouped_points() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(POINTS):
        grouped.setdefault(row["GalaxyName"], []).append(row)
    for rows in grouped.values():
        rows.sort(key=lambda row: float(row["RadiusFraction"]))
    return grouped


def rule_rows() -> list[dict[str, str]]:
    rows = [
        ("baseline", "first point or no previous state", "S_tau=1.00"),
        (
            "history_state",
            "for point i>1",
            "HistoryState=mean signed TPG residual over points 1..i-1",
        ),
        ("update", "for point i>1", f"S_tau=clip(1 + {GAIN:.2f}*HistoryState, {S_LOW:.2f}, {S_HIGH:.2f})"),
        ("causality", "current point", "current Vobs/residual is not used to set current S_tau"),
    ]
    return [
        {
            "RuleID": "S_tau_history_v01",
            "Component": component,
            "Condition": condition,
            "Definition": definition,
            "AllowedInputs": "inner_radius_signed_TPG_residual_history",
            "ForbiddenInputs": "current_point_residual;future_points;S_tau_eff;Class;external_label",
            "InterpretationGuardrail": GUARDRAIL,
        }
        for component, condition, definition in rows
    ]


def point_rows() -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for galaxy, rows in sorted(grouped_points().items()):
        previous_signed_residuals: list[float] = []
        for index, row in enumerate(rows, start=1):
            vobs = float(row["VobsKms"])
            vbar = float(row["VbarKms"])
            kernel = float(row["LogKernelAlphaLn"])
            model_s1 = vbar * (1.0 + kernel)
            residual_s1 = signed_residual(vobs, model_s1)
            history_state = mean(previous_signed_residuals) if previous_signed_residuals else 0.0
            s_history = min(S_HIGH, max(S_LOW, 1.0 + GAIN * history_state))
            model_history = vbar * (1.0 + s_history * kernel)
            residual_history = signed_residual(vobs, model_history)
            if math.isnan(residual_s1) or math.isnan(residual_history):
                continue
            output.append(
                {
                    "GalaxyName": galaxy,
                    "Class": row["Class"],
                    "PointIndex": str(index),
                    "RadiusKpc": row["RadiusKpc"],
                    "RadiusFraction": row["RadiusFraction"],
                    "aN_over_a0": row["aN_over_a0"],
                    "HistoryStatePriorMeanSignedResidual": fmt(history_state),
                    "Predicted_S_tau_history_v01": fmt(s_history),
                    "ModelVelocity_S_tau1": fmt(model_s1),
                    "ModelVelocity_HistoryRule": fmt(model_history),
                    "SignedLogResidual_S_tau1": fmt(residual_s1),
                    "SignedLogResidual_HistoryRule": fmt(residual_history),
                    "AbsLogResidual_S_tau1": fmt(abs(residual_s1)),
                    "AbsLogResidual_HistoryRule": fmt(abs(residual_history)),
                    "DeltaAbsLogResidual_HistoryMinusS1": fmt(abs(residual_history) - abs(residual_s1)),
                    "InterpretationGuardrail": GUARDRAIL,
                }
            )
            previous_signed_residuals.append(residual_s1)
    return output


def galaxy_summary(points: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in points:
        grouped.setdefault(row["GalaxyName"], []).append(row)
    output: list[dict[str, str]] = []
    for galaxy, rows in sorted(grouped.items()):
        s1 = [float(row["AbsLogResidual_S_tau1"]) for row in rows]
        history = [float(row["AbsLogResidual_HistoryRule"]) for row in rows]
        deltas = [float(row["DeltaAbsLogResidual_HistoryMinusS1"]) for row in rows]
        outer_rows = [row for row in rows if float(row["RadiusFraction"]) >= 0.5]
        outer_deltas = [float(row["DeltaAbsLogResidual_HistoryMinusS1"]) for row in outer_rows]
        output.append(
            {
                "GalaxyName": galaxy,
                "Class": rows[0]["Class"],
                "NPoints": str(len(rows)),
                "RMSLogResidual_S_tau1": fmt(rms(s1)),
                "RMSLogResidual_HistoryRule": fmt(rms(history)),
                "DeltaRMS_HistoryMinusS1": fmt(rms(history) - rms(s1)),
                "MedianDeltaAbsLogResidual_HistoryMinusS1": fmt(median(deltas)),
                "FractionPointsImproved": fmt(sum(delta < 0 for delta in deltas) / len(deltas)),
                "OuterFractionPointsImproved": fmt(
                    sum(delta < 0 for delta in outer_deltas) / len(outer_deltas)
                )
                if outer_deltas
                else "",
                "MedianPredicted_S_tau_history": fmt(
                    median([float(row["Predicted_S_tau_history_v01"]) for row in rows])
                ),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return output


def metric_rows(galaxies: list[dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for klass in ["all", "A", "C"]:
        subset = galaxies if klass == "all" else [row for row in galaxies if row["Class"] == klass]
        deltas = [float(row["DeltaRMS_HistoryMinusS1"]) for row in subset]
        median_deltas = [float(row["MedianDeltaAbsLogResidual_HistoryMinusS1"]) for row in subset]
        output.append(
            {
                "Subset": klass,
                "NGalaxies": str(len(subset)),
                "MedianDeltaRMS_HistoryMinusS1": fmt(median(deltas)),
                "MeanDeltaRMS_HistoryMinusS1": fmt(mean(deltas)),
                "FractionGalaxiesImproved": fmt(sum(delta < 0 for delta in deltas) / len(deltas)),
                "MedianPointwiseDeltaAbsResidual": fmt(median(median_deltas)),
                "MedianRMS_S_tau1": fmt(median([float(row["RMSLogResidual_S_tau1"]) for row in subset])),
                "MedianRMS_HistoryRule": fmt(
                    median([float(row["RMSLogResidual_HistoryRule"]) for row in subset])
                ),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return output


def write_report(metrics: list[dict[str, str]]) -> None:
    by_subset = {row["Subset"]: row for row in metrics}
    lines = [
        "# History-Dependent S_tau Rule v0.1",
        "",
        "This readout tests a causal integrated `S_tau` candidate. For each radial point, the current `S_tau` is set from the mean signed TPG residual of the inner points only. The current point residual, future points, empirical `S_tau_eff`, and A/C label are forbidden inputs.",
        "",
        "## Rule",
        "",
        f"`S_tau_history(R_i) = clip(1 + {GAIN:.2f} * mean_{{j<i}} signed_residual_TPG(R_j), {S_LOW:.2f}, {S_HIGH:.2f})`.",
        "",
        "The first point in each galaxy uses `S_tau=1` because it has no inner history.",
        "",
        "## Velocity Readout",
        "",
        f"- All-galaxy median delta RMS history-minus-S1: {by_subset['all']['MedianDeltaRMS_HistoryMinusS1']}",
        f"- All-galaxy fraction improved: {by_subset['all']['FractionGalaxiesImproved']}",
        f"- A median delta RMS: {by_subset['A']['MedianDeltaRMS_HistoryMinusS1']}",
        f"- C median delta RMS: {by_subset['C']['MedianDeltaRMS_HistoryMinusS1']}",
        "",
        "Negative delta means the history rule improves over `S_tau=1`; positive delta means it worsens.",
        "",
        "## Interpretation",
        "",
        "This is not an external prediction, because it learns from inner observed residuals of the same galaxy. Its role is narrower: test whether an integrated radial state can carry useful information for outer points. A positive result would motivate a source-side proxy for the history state; a null result would weaken the integrated `S_tau` path.",
        "",
        "## Generated Files",
        "",
        "- `history_s_tau_rule_v01.csv`",
        "- `history_s_tau_velocity_point_readout.csv`",
        "- `history_s_tau_velocity_galaxy_summary.csv`",
        "- `history_s_tau_velocity_metric_summary.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "history_s_tau_rule_v01.csv",
            "history_s_tau_rule_v01.md",
            "history_s_tau_velocity_point_readout.csv",
            "history_s_tau_velocity_galaxy_summary.csv",
            "history_s_tau_velocity_metric_summary.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["history_s_tau_rule_status"] = "causal_inner_residual_history_readout_complete"
    manifest["paper2_next_gate"] = "seek_source_side_proxy_for_integrated_history_state"
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
            "Definition",
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
            "PointIndex",
            "RadiusKpc",
            "RadiusFraction",
            "aN_over_a0",
            "HistoryStatePriorMeanSignedResidual",
            "Predicted_S_tau_history_v01",
            "ModelVelocity_S_tau1",
            "ModelVelocity_HistoryRule",
            "SignedLogResidual_S_tau1",
            "SignedLogResidual_HistoryRule",
            "AbsLogResidual_S_tau1",
            "AbsLogResidual_HistoryRule",
            "DeltaAbsLogResidual_HistoryMinusS1",
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
            "RMSLogResidual_HistoryRule",
            "DeltaRMS_HistoryMinusS1",
            "MedianDeltaAbsLogResidual_HistoryMinusS1",
            "FractionPointsImproved",
            "OuterFractionPointsImproved",
            "MedianPredicted_S_tau_history",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        METRIC_OUT,
        metrics,
        [
            "Subset",
            "NGalaxies",
            "MedianDeltaRMS_HistoryMinusS1",
            "MeanDeltaRMS_HistoryMinusS1",
            "FractionGalaxiesImproved",
            "MedianPointwiseDeltaAbsResidual",
            "MedianRMS_S_tau1",
            "MedianRMS_HistoryRule",
            "InterpretationGuardrail",
        ],
    )
    write_report(metrics)
    update_manifest()
    print(REPORT)
    print(f"history_s_tau_velocity_galaxies={len(galaxies)}")


if __name__ == "__main__":
    main()
