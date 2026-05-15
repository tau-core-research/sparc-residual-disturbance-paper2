#!/usr/bin/env python3
"""Audit why THINGS source-side S_tau(R) does not beat S_tau=1."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET


POINTS = PACKET / "things_source_s_tau_velocity_point_readout.csv"
EFF = PACKET / "s_tau_eff_point_pilot.csv"
POINT_OUT = PACKET / "things_source_s_tau_failure_point_audit.csv"
GALAXY_OUT = PACKET / "things_source_s_tau_failure_galaxy_audit.csv"
METRIC_OUT = PACKET / "things_source_s_tau_failure_metric_summary.csv"
REPORT = PACKET / "things_source_s_tau_failure_audit.md"

GUARDRAIL = "post_outcome_failure_diagnostic_not_rule_selection"


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


def radius_zone(radius_fraction: float) -> str:
    if radius_fraction < 0.33:
        return "inner"
    if radius_fraction < 0.67:
        return "middle"
    return "outer"


def acceleration_zone(a_n_over_a0: float) -> str:
    if a_n_over_a0 < 0.1:
        return "low_acc"
    if a_n_over_a0 < 0.3:
        return "mid_acc"
    return "high_acc"


def eff_index() -> dict[tuple[str, str, str], dict[str, str]]:
    return {
        (row["GalaxyName"], row["RadiusKpc"], row["RadiusFraction"]): row
        for row in read_csv(EFF)
    }


def point_rows() -> list[dict[str, str]]:
    empirical = eff_index()
    rows: list[dict[str, str]] = []
    for row in read_csv(POINTS):
        key = (row["GalaxyName"], row["RadiusKpc"], row["RadiusFraction"])
        if key not in empirical:
            continue
        eff = float(empirical[key]["S_tau_eff_clipped_0_2"])
        percentile = float(row["S_tau_source_percentile"])
        log = float(row["S_tau_source_log"])
        baseline_error = abs(1.0 - eff)
        percentile_error = abs(percentile - eff)
        log_error = abs(log - eff)
        radius_fraction = float(row["RadiusFraction"])
        a_n = float(row["aN_over_a0"])
        rows.append(
            {
                "GalaxyName": row["GalaxyName"],
                "Class": row["Class"],
                "RadiusKpc": row["RadiusKpc"],
                "RadiusFraction": row["RadiusFraction"],
                "RadiusZone": radius_zone(radius_fraction),
                "AccelerationZone": acceleration_zone(a_n),
                "StressDispersionOverRotationScale": row["StressDispersionOverRotationScale"],
                "Empirical_S_tau_eff_clipped": fmt(eff),
                "S_tau1": "1.000000000",
                "S_tau_source_percentile": fmt(percentile),
                "S_tau_source_log": fmt(log),
                "AbsError_S_tau1_vs_eff": fmt(baseline_error),
                "AbsError_SourcePercentile_vs_eff": fmt(percentile_error),
                "AbsError_SourceLog_vs_eff": fmt(log_error),
                "DeltaAbsError_SourcePercentileMinusS1": fmt(percentile_error - baseline_error),
                "DeltaAbsError_SourceLogMinusS1": fmt(log_error - baseline_error),
                "SourcePercentileDirection": "too_low" if percentile < eff else "too_high_or_equal",
                "SourceLogDirection": "too_low" if log < eff else "too_high_or_equal",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def group_rows(rows: list[dict[str, str]], group_field: str) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row[group_field], []).append(row)
    output: list[dict[str, str]] = []
    for group, values in sorted(grouped.items()):
        delta_percentile = [float(row["DeltaAbsError_SourcePercentileMinusS1"]) for row in values]
        delta_log = [float(row["DeltaAbsError_SourceLogMinusS1"]) for row in values]
        eff = [float(row["Empirical_S_tau_eff_clipped"]) for row in values]
        source_percentile = [float(row["S_tau_source_percentile"]) for row in values]
        source_log = [float(row["S_tau_source_log"]) for row in values]
        output.append(
            {
                group_field: group,
                "NPoints": str(len(values)),
                "MedianEmpirical_S_tau_eff": fmt(median(eff)),
                "MedianSourcePercentile": fmt(median(source_percentile)),
                "MedianSourceLog": fmt(median(source_log)),
                "MedianDeltaAbsError_SourcePercentileMinusS1": fmt(median(delta_percentile)),
                "MedianDeltaAbsError_SourceLogMinusS1": fmt(median(delta_log)),
                "FractionPointsImprovedPercentile": fmt(
                    sum(delta < 0 for delta in delta_percentile) / len(delta_percentile)
                ),
                "FractionPointsImprovedLog": fmt(sum(delta < 0 for delta in delta_log) / len(delta_log)),
                "FractionPercentileTooLow": fmt(
                    sum(row["SourcePercentileDirection"] == "too_low" for row in values) / len(values)
                ),
                "FractionLogTooLow": fmt(sum(row["SourceLogDirection"] == "too_low" for row in values) / len(values)),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return output


def galaxy_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["GalaxyName"], []).append(row)
    output: list[dict[str, str]] = []
    for galaxy, values in sorted(grouped.items()):
        delta_percentile = [float(row["DeltaAbsError_SourcePercentileMinusS1"]) for row in values]
        delta_log = [float(row["DeltaAbsError_SourceLogMinusS1"]) for row in values]
        output.append(
            {
                "GalaxyName": galaxy,
                "Class": values[0]["Class"],
                "NPoints": str(len(values)),
                "MedianDeltaAbsError_SourcePercentileMinusS1": fmt(median(delta_percentile)),
                "MedianDeltaAbsError_SourceLogMinusS1": fmt(median(delta_log)),
                "RMSDeltaAbsError_SourcePercentileMinusS1": fmt(rms(delta_percentile)),
                "RMSDeltaAbsError_SourceLogMinusS1": fmt(rms(delta_log)),
                "FractionPointsImprovedPercentile": fmt(
                    sum(delta < 0 for delta in delta_percentile) / len(delta_percentile)
                ),
                "FractionPointsImprovedLog": fmt(sum(delta < 0 for delta in delta_log) / len(delta_log)),
                "FractionPercentileTooLow": fmt(
                    sum(row["SourcePercentileDirection"] == "too_low" for row in values) / len(values)
                ),
                "FractionLogTooLow": fmt(sum(row["SourceLogDirection"] == "too_low" for row in values) / len(values)),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return output


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for group_name, values in [
        ("all", rows),
        ("A", [row for row in rows if row["Class"] == "A"]),
        ("C", [row for row in rows if row["Class"] == "C"]),
    ]:
        delta_percentile = [float(row["DeltaAbsError_SourcePercentileMinusS1"]) for row in values]
        delta_log = [float(row["DeltaAbsError_SourceLogMinusS1"]) for row in values]
        stress = [float(row["StressDispersionOverRotationScale"]) for row in values]
        eff = [float(row["Empirical_S_tau_eff_clipped"]) for row in values]
        output.append(
            {
                "Group": group_name,
                "NPoints": str(len(values)),
                "MedianDeltaAbsError_SourcePercentileMinusS1": fmt(median(delta_percentile)),
                "MedianDeltaAbsError_SourceLogMinusS1": fmt(median(delta_log)),
                "FractionPointsImprovedPercentile": fmt(
                    sum(delta < 0 for delta in delta_percentile) / len(delta_percentile)
                ),
                "FractionPointsImprovedLog": fmt(sum(delta < 0 for delta in delta_log) / len(delta_log)),
                "FractionPercentileTooLow": fmt(
                    sum(row["SourcePercentileDirection"] == "too_low" for row in values) / len(values)
                ),
                "FractionLogTooLow": fmt(sum(row["SourceLogDirection"] == "too_low" for row in values) / len(values)),
                "PearsonStress_EmpiricalS_tau_eff": fmt(pearson(stress, eff)),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    for row in group_rows(rows, "RadiusZone"):
        output.append(
            {
                "Group": f"radius_{row['RadiusZone']}",
                "NPoints": row["NPoints"],
                "MedianDeltaAbsError_SourcePercentileMinusS1": row[
                    "MedianDeltaAbsError_SourcePercentileMinusS1"
                ],
                "MedianDeltaAbsError_SourceLogMinusS1": row["MedianDeltaAbsError_SourceLogMinusS1"],
                "FractionPointsImprovedPercentile": row["FractionPointsImprovedPercentile"],
                "FractionPointsImprovedLog": row["FractionPointsImprovedLog"],
                "FractionPercentileTooLow": row["FractionPercentileTooLow"],
                "FractionLogTooLow": row["FractionLogTooLow"],
                "PearsonStress_EmpiricalS_tau_eff": "",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    for row in group_rows(rows, "AccelerationZone"):
        output.append(
            {
                "Group": f"acceleration_{row['AccelerationZone']}",
                "NPoints": row["NPoints"],
                "MedianDeltaAbsError_SourcePercentileMinusS1": row[
                    "MedianDeltaAbsError_SourcePercentileMinusS1"
                ],
                "MedianDeltaAbsError_SourceLogMinusS1": row["MedianDeltaAbsError_SourceLogMinusS1"],
                "FractionPointsImprovedPercentile": row["FractionPointsImprovedPercentile"],
                "FractionPointsImprovedLog": row["FractionPointsImprovedLog"],
                "FractionPercentileTooLow": row["FractionPercentileTooLow"],
                "FractionLogTooLow": row["FractionLogTooLow"],
                "PearsonStress_EmpiricalS_tau_eff": "",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return output


def write_report(metrics: list[dict[str, str]]) -> None:
    by_group = {row["Group"]: row for row in metrics}
    all_row = by_group["all"]
    lines = [
        "# THINGS Source-Side S_tau Failure Audit",
        "",
        "This audit explains the previous THINGS source-side velocity readout after the outcome is known. It compares source-side `S_tau(R)` candidates to the empirical `S_tau_eff(R)` diagnostic only to identify failure modes. It must not be used to choose a new rule without a subsequent freeze-and-test gate.",
        "",
        "## Main Diagnostics",
        "",
        f"- Point rows: {all_row['NPoints']}",
        f"- Median delta absolute S_tau error, percentile-minus-S1: {all_row['MedianDeltaAbsError_SourcePercentileMinusS1']}",
        f"- Fraction points improved, percentile mapping: {all_row['FractionPointsImprovedPercentile']}",
        f"- Median delta absolute S_tau error, log-minus-S1: {all_row['MedianDeltaAbsError_SourceLogMinusS1']}",
        f"- Fraction points improved, log mapping: {all_row['FractionPointsImprovedLog']}",
        f"- Fraction percentile mapping too low relative to empirical S_tau_eff: {all_row['FractionPercentileTooLow']}",
        f"- Pearson(stress, empirical S_tau_eff): {all_row['PearsonStress_EmpiricalS_tau_eff']}",
        "",
        "## Interpretation",
        "",
        "The failure mode is not merely noise. The source-side mappings often push `S_tau` below one where the empirical velocity-level diagnostic prefers values near or above one. In this overlap, stress magnitude alone is therefore an incomplete proxy for the local projection multiplier.",
        "",
        "## Next Gate",
        "",
        "Freeze a new source-side rule only after declaring its inputs and sign logic. Candidate inputs should distinguish stress type or radial context rather than using stress magnitude alone.",
        "",
        "## Generated Files",
        "",
        "- `things_source_s_tau_failure_point_audit.csv`",
        "- `things_source_s_tau_failure_galaxy_audit.csv`",
        "- `things_source_s_tau_failure_metric_summary.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "things_source_s_tau_failure_point_audit.csv",
            "things_source_s_tau_failure_galaxy_audit.csv",
            "things_source_s_tau_failure_metric_summary.csv",
            "things_source_s_tau_failure_audit.md",
        }
    )
    manifest["files"] = sorted(files)
    manifest["things_source_s_tau_failure_audit_status"] = "post_outcome_failure_diagnostic_complete"
    manifest["paper2_next_gate"] = "freeze_contextual_s_tau_rule_before_any_new_velocity_readout"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    points = point_rows()
    galaxies = galaxy_rows(points)
    metrics = metric_rows(points)
    write_csv(
        POINT_OUT,
        points,
        [
            "GalaxyName",
            "Class",
            "RadiusKpc",
            "RadiusFraction",
            "RadiusZone",
            "AccelerationZone",
            "StressDispersionOverRotationScale",
            "Empirical_S_tau_eff_clipped",
            "S_tau1",
            "S_tau_source_percentile",
            "S_tau_source_log",
            "AbsError_S_tau1_vs_eff",
            "AbsError_SourcePercentile_vs_eff",
            "AbsError_SourceLog_vs_eff",
            "DeltaAbsError_SourcePercentileMinusS1",
            "DeltaAbsError_SourceLogMinusS1",
            "SourcePercentileDirection",
            "SourceLogDirection",
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
            "MedianDeltaAbsError_SourcePercentileMinusS1",
            "MedianDeltaAbsError_SourceLogMinusS1",
            "RMSDeltaAbsError_SourcePercentileMinusS1",
            "RMSDeltaAbsError_SourceLogMinusS1",
            "FractionPointsImprovedPercentile",
            "FractionPointsImprovedLog",
            "FractionPercentileTooLow",
            "FractionLogTooLow",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        METRIC_OUT,
        metrics,
        [
            "Group",
            "NPoints",
            "MedianDeltaAbsError_SourcePercentileMinusS1",
            "MedianDeltaAbsError_SourceLogMinusS1",
            "FractionPointsImprovedPercentile",
            "FractionPointsImprovedLog",
            "FractionPercentileTooLow",
            "FractionLogTooLow",
            "PearsonStress_EmpiricalS_tau_eff",
            "InterpretationGuardrail",
        ],
    )
    write_report(metrics)
    update_manifest()
    print(REPORT)
    print(f"things_source_s_tau_failure_points={len(points)}")


if __name__ == "__main__":
    main()
