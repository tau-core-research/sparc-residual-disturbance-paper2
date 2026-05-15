#!/usr/bin/env python3
"""Compute an empirical S_tau_eff(R) pilot from SPARC rotmod inputs.

The raw SPARC rotmod files are not redistributed in this repository. To
regenerate this optional pilot, set SPARC_ROTMOD_DIR to a local directory that
contains `*_rotmod.dat` files. The committed outputs are derived tables only.
"""

from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path

from make_packet_v01_seed import PACKET, ROOT


POINT_MAP = (
    ROOT
    / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/taucore_specificity_point_map.csv"
)
DEFAULT_ROTMOD_DIR = ROOT / "data/sparc/Rotmod_LTG"
POINT_OUT = PACKET / "s_tau_eff_point_pilot.csv"
GALAXY_OUT = PACKET / "s_tau_eff_galaxy_summary.csv"
REPORT = PACKET / "s_tau_eff_pilot.md"

ALPHA = 0.360
UDISK = 0.5
UBUL = 0.7
CLIP_LOW = 0.0
CLIP_HIGH = 2.0


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


def signed_square(value: float) -> float:
    return value * abs(value)


def median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    if not ordered:
        return math.nan
    if n % 2:
        return ordered[n // 2]
    return (ordered[n // 2 - 1] + ordered[n // 2]) / 2


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


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


def parse_rotmod(path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 8:
            continue
        rows.append(
            {
                "RadiusKpc": float(parts[0]),
                "Vobs": max(0.0, float(parts[1])),
                "ErrVobs": max(0.0, float(parts[2])),
                "Vgas": float(parts[3]),
                "Vdisk": max(0.0, float(parts[4])),
                "Vbul": max(0.0, float(parts[5])),
            }
        )
    return rows


def rotmod_directory() -> Path:
    configured = os.environ.get("SPARC_ROTMOD_DIR")
    return Path(configured) if configured else DEFAULT_ROTMOD_DIR


def rotmod_index(root: Path) -> dict[str, list[dict[str, float]]]:
    if not root.exists():
        raise FileNotFoundError(
            f"SPARC rotmod directory not found: {root}. Set SPARC_ROTMOD_DIR."
        )
    index: dict[str, list[dict[str, float]]] = {}
    for path in sorted(root.glob("*_rotmod.dat")):
        galaxy = path.name.split("_rotmod", maxsplit=1)[0]
        index[galaxy] = parse_rotmod(path)
    return index


def nearest_rotmod_row(
    rows: list[dict[str, float]], radius_kpc: float
) -> tuple[dict[str, float], float]:
    nearest = min(rows, key=lambda row: abs(row["RadiusKpc"] - radius_kpc))
    return nearest, abs(nearest["RadiusKpc"] - radius_kpc)


def point_rows() -> list[dict[str, str]]:
    rotmods = rotmod_index(rotmod_directory())
    output: list[dict[str, str]] = []
    for point in read_csv(POINT_MAP):
        galaxy = point["GalaxyName"]
        if galaxy not in rotmods:
            continue
        radius = float(point["RadiusKpc"])
        rot, radius_delta = nearest_rotmod_row(rotmods[galaxy], radius)
        vbar2 = (
            signed_square(rot["Vgas"])
            + UDISK * rot["Vdisk"] * rot["Vdisk"]
            + UBUL * rot["Vbul"] * rot["Vbul"]
        )
        if vbar2 <= 0:
            continue
        vbar = math.sqrt(vbar2)
        a_n = float(point["aN_over_a0"])
        log_kernel = ALPHA * math.log1p(1.0 / a_n) if a_n > 0 else math.nan
        if not math.isfinite(log_kernel) or log_kernel <= 0:
            continue
        s_eff = (rot["Vobs"] / vbar - 1.0) / log_kernel
        s_clip = min(CLIP_HIGH, max(CLIP_LOW, s_eff))
        output.append(
            {
                "GalaxyName": galaxy,
                "Class": point["Class"],
                "RadiusKpc": point["RadiusKpc"],
                "RadiusFraction": point["RadiusFraction"],
                "RadiusDeltaKpc": fmt(radius_delta),
                "aN_over_a0": point["aN_over_a0"],
                "VobsKms": fmt(rot["Vobs"]),
                "VbarKms": fmt(vbar),
                "LogKernelAlphaLn": fmt(log_kernel),
                "S_tau_eff_raw": fmt(s_eff),
                "S_tau_eff_clipped_0_2": fmt(s_clip),
                "AbsResidualProjection": point["AbsResidualProjection"],
                "InterpretationGuardrail": "empirical_backsolved_diagnostic_not_predictive_model",
            }
        )
    return output


def galaxy_summary(points: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in points:
        grouped.setdefault(row["GalaxyName"], []).append(row)
    rows: list[dict[str, str]] = []
    for galaxy, values in sorted(grouped.items()):
        s_values = [float(row["S_tau_eff_clipped_0_2"]) for row in values]
        raw_values = [float(row["S_tau_eff_raw"]) for row in values]
        radii = [float(row["RadiusFraction"]) for row in values]
        residuals = [float(row["AbsResidualProjection"]) for row in values]
        low_acc = [
            float(row["S_tau_eff_clipped_0_2"])
            for row in values
            if float(row["aN_over_a0"]) < 0.1
        ]
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": values[0]["Class"],
                "NPoints": str(len(values)),
                "Median_S_tau_eff_clipped": fmt(median(s_values)),
                "Mean_S_tau_eff_clipped": fmt(mean(s_values)),
                "RMSDeviationFromOne": fmt(rms([value - 1.0 for value in s_values])),
                "RawFractionBelowZero": fmt(sum(value < 0.0 for value in raw_values) / len(raw_values)),
                "RawFractionAboveTwo": fmt(sum(value > 2.0 for value in raw_values) / len(raw_values)),
                "LowAccelerationMedian_S_tau": fmt(median(low_acc)),
                "RadiusPearson_S_tau": fmt(pearson(radii, s_values)),
                "ResidualPearson_S_tau": fmt(pearson(residuals, s_values)),
                "InterpretationGuardrail": "derived_from_vobs_not_heldout_prediction",
            }
        )
    return rows


def class_median(rows: list[dict[str, str]], klass: str, field: str) -> float:
    return median([float(row[field]) for row in rows if row["Class"] == klass and row[field] != ""])


def write_report(summary: list[dict[str, str]], n_points: int) -> None:
    a_median = class_median(summary, "A", "Median_S_tau_eff_clipped")
    c_median = class_median(summary, "C", "Median_S_tau_eff_clipped")
    a_dev = class_median(summary, "A", "RMSDeviationFromOne")
    c_dev = class_median(summary, "C", "RMSDeviationFromOne")
    lines = [
        "# Effective S_tau Pilot",
        "",
        "This pilot back-solves an empirical `S_tau_eff(R)` from local SPARC rotmod inputs using the fixed velocity-level projection prescription.",
        "",
        "```text",
        "S_tau_eff(R) = (Vobs/Vbar - 1) / [alpha ln(1 + 1/(aN/a0))]",
        "```",
        "",
        "The raw SPARC rotmod files are not redistributed here. The committed tables are derived diagnostics only.",
        "",
        "## Summary",
        "",
        f"- Point rows: {n_points}",
        f"- A median galaxy-level clipped S_tau: {fmt(a_median)}",
        f"- C median galaxy-level clipped S_tau: {fmt(c_median)}",
        f"- A median RMS deviation from S_tau=1: {fmt(a_dev)}",
        f"- C median RMS deviation from S_tau=1: {fmt(c_dev)}",
        "",
        "## Interpretation",
        "",
        "`S_tau=1` is the old TPG/projection baseline. Values near one indicate that the fixed logarithmic multiplier is close to the observed velocity level. Large deviations identify galaxies or radial zones where a local structural term would have to carry substantial information.",
        "",
        "This is not a predictive model yet. It is a diagnostic map derived from `Vobs`, so it cannot be used as independent validation. The next gate is to freeze a source-side or kinematic rule that predicts `S_tau` without using the target residual.",
        "",
        "## Generated Files",
        "",
        "- `s_tau_eff_point_pilot.csv`",
        "- `s_tau_eff_galaxy_summary.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "s_tau_eff_point_pilot.csv",
            "s_tau_eff_galaxy_summary.csv",
            "s_tau_eff_pilot.md",
        }
    )
    manifest["files"] = sorted(files)
    manifest["s_tau_eff_pilot_status"] = "empirical_backsolved_diagnostic_ready"
    manifest["paper2_next_gate"] = "freeze_predictive_s_tau_rule_without_vobs_target_leakage"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    points = point_rows()
    summary = galaxy_summary(points)
    write_csv(
        POINT_OUT,
        points,
        [
            "GalaxyName",
            "Class",
            "RadiusKpc",
            "RadiusFraction",
            "RadiusDeltaKpc",
            "aN_over_a0",
            "VobsKms",
            "VbarKms",
            "LogKernelAlphaLn",
            "S_tau_eff_raw",
            "S_tau_eff_clipped_0_2",
            "AbsResidualProjection",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        GALAXY_OUT,
        summary,
        [
            "GalaxyName",
            "Class",
            "NPoints",
            "Median_S_tau_eff_clipped",
            "Mean_S_tau_eff_clipped",
            "RMSDeviationFromOne",
            "RawFractionBelowZero",
            "RawFractionAboveTwo",
            "LowAccelerationMedian_S_tau",
            "RadiusPearson_S_tau",
            "ResidualPearson_S_tau",
            "InterpretationGuardrail",
        ],
    )
    write_report(summary, len(points))
    update_manifest()
    print(REPORT)
    print(f"s_tau_eff_points={len(points)}")


if __name__ == "__main__":
    main()
