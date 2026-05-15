#!/usr/bin/env python3
"""Validate route 2 surface profiles against local SPARC references."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


ROOT = Path(__file__).resolve().parents[2]
SPARC_ROTMOD = Path("/Users/jolcsak/Projects/tau-core/data/sparc/Rotmod_LTG")
SURFACE_DENSITY = PACKET / "things_route2_validation_surface_density_profiles_v01.csv"

JOIN_OUT = PACKET / "things_route2_validation_sparc_surface_profile_join_v01.csv"
METRIC_OUT = PACKET / "things_route2_validation_sparc_surface_profile_metrics_v01.csv"
GATE_OUT = PACKET / "things_route2_velocity_solver_validation_gate_v01.csv"
REPORT = PACKET / "things_route2_velocity_solver_validation_gate_v01.md"

GUARDRAIL = "route2_velocity_solver_validation_blocked_by_surface_profile_mismatch"
GALAXIES = ["NGC2403", "NGC3198", "NGC5055"]


def read_rotmod(galaxy: str) -> list[dict[str, float]]:
    path = SPARC_ROTMOD / f"{galaxy}_rotmod.dat"
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            rows.append(
                {
                    "RadiusKpc": float(parts[0]),
                    "VgasKms": float(parts[3]),
                    "VdiskKms": float(parts[4]),
                    "VbulKms": float(parts[5]),
                    "SBdiskLsunPc2": float(parts[6]),
                    "SBbulLsunPc2": float(parts[7]),
                }
            )
    return rows


def nearest_profile(
    profiles: list[dict[str, str]], radius: float
) -> tuple[dict[str, str] | None, float]:
    if not profiles:
        return None, math.nan
    best = min(profiles, key=lambda row: abs(float(row["RadiusMidKpc"]) - radius))
    return best, abs(float(best["RadiusMidKpc"]) - radius)


def join_rows() -> list[dict[str, str]]:
    profiles = [
        row
        for row in read_csv(SURFACE_DENSITY)
        if row["SourceRole"] == "SINGS_IRAC1_3P6UM" and row["ConvertedMedian"]
    ]
    outputs = []
    for galaxy in GALAXIES:
        galaxy_profiles = [row for row in profiles if row["GalaxyName"] == galaxy]
        for ref in read_rotmod(galaxy):
            profile, delta = nearest_profile(galaxy_profiles, ref["RadiusKpc"])
            if profile is None or delta > 0.3 or ref["SBdiskLsunPc2"] <= 0:
                continue
            derived = float(profile["ConvertedMedian"])
            reference = ref["SBdiskLsunPc2"]
            frac_error = abs(derived - reference) / reference
            outputs.append(
                {
                    "GalaxyName": galaxy,
                    "RadiusKpc": f"{ref['RadiusKpc']:.6f}",
                    "NearestProfileRadiusKpc": profile["RadiusMidKpc"],
                    "RadiusDeltaKpc": f"{delta:.6f}",
                    "DerivedI3p6LsunPc2": f"{derived:.9g}",
                    "SparcSBdiskLsunPc2": f"{reference:.9g}",
                    "AbsFractionalError": f"{frac_error:.9f}",
                    "ValidationUse": "stellar_surface_profile_reference_check_only",
                    "CanRunVelocitySolverNow": "no",
                    "CanScoreMissingGalaxiesNow": "no",
                    "Guardrail": GUARDRAIL,
                }
            )
    return outputs


def median(values: list[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    n = len(ordered)
    if n % 2:
        return ordered[n // 2]
    return (ordered[n // 2 - 1] + ordered[n // 2]) / 2


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    outputs = []
    for galaxy in GALAXIES:
        subset = [row for row in rows if row["GalaxyName"] == galaxy]
        errors = [float(row["AbsFractionalError"]) for row in subset]
        pass_fraction = sum(error <= 0.5 for error in errors) / len(errors) if errors else math.nan
        med_error = median(errors)
        outputs.append(
            {
                "GalaxyName": galaxy,
                "NMatchedRadii": str(len(errors)),
                "MedianAbsFractionalError": "" if math.isnan(med_error) else f"{med_error:.9f}",
                "FractionWithin50Percent": "" if math.isnan(pass_fraction) else f"{pass_fraction:.9f}",
                "PassCondition": "median_abs_fractional_error_le_0p50_and_fraction_within_50_percent_ge_0p50",
                "ValidationStatus": "pass"
                if med_error <= 0.5 and pass_fraction >= 0.5
                else "fail_surface_profile_mismatch",
                "CanRunVelocitySolverNow": "no",
                "CanScoreMissingGalaxiesNow": "no",
                "Guardrail": GUARDRAIL,
            }
        )
    return outputs


def gate_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    passed = [row for row in metrics if row["ValidationStatus"] == "pass"]
    return [
        {
            "GateID": "R2VELVAL01",
            "Status": "surface_profile_reference_check_failed"
            if len(passed) < 3
            else "surface_profile_reference_check_passed",
            "Evidence": f"passed={len(passed)}_of_3",
            "CanRunVelocitySolverNow": "no" if len(passed) < 3 else "yes",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "freeze_background_subtraction_and_photometry_policy_before_velocity_solver"
            if len(passed) < 3
            else "run_predeclared_velocity_solver_against_SPARC_component_curves",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2VELVAL02",
            "Status": "missing_galaxy_route2_scores_blocked",
            "Evidence": "NGC925_NGC3031_not_score_ready_until_solver_validation_passes",
            "CanRunVelocitySolverNow": "no",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "do_not_apply_route2_to_missing_galaxies",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], gates: list[dict[str, str]]) -> None:
    lines = [
        "# THINGS Route 2 Velocity-Solver Validation Gate v0.1",
        "",
        "This gate checks whether the derived SINGS IRAC1 surface-density proxy is already close enough to the SPARC `SBdisk` reference profiles to justify running the velocity solver. It does not run the velocity solver and does not compute any missing-galaxy score.",
        "",
        "## Surface-Profile Check",
        "",
    ]
    for row in metrics:
        lines.append(
            f"- `{row['GalaxyName']}`: N={row['NMatchedRadii']}, median fractional error={row['MedianAbsFractionalError']}, within-50% fraction={row['FractionWithin50Percent']}, status={row['ValidationStatus']}."
        )
    lines.extend(["", "## Gate", ""])
    for gate in gates:
        lines.append(
            f"- `{gate['GateID']}`: {gate['Status']} / solver={gate['CanRunVelocitySolverNow']} / score={gate['CanScoreMissingGalaxiesNow']}."
        )
    lines.extend(
        [
            "",
            "Interpretation: the current route 2 photometry is not yet a validated route to SPARC-compatible stellar component curves. The next defensible step is a frozen background-subtraction and photometry policy, then rerun this reference check before any velocity-solver validation.",
            "",
            "No velocity component arrays are derived here.",
            "No `W_tau_eff` endpoint is opened here.",
            "",
            f"Guardrail: `{GUARDRAIL}`",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [JOIN_OUT, METRIC_OUT, GATE_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_route2_velocity_solver_validation_status"] = (
        "blocked_surface_profile_reference_check_failed_no_scores"
    )
    manifest["paper2_next_gate"] = (
        "route2_freeze_background_subtraction_photometry_policy_before_solver"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    joined = join_rows()
    metrics = metric_rows(joined)
    gates = gate_rows(metrics)
    write_csv(
        JOIN_OUT,
        joined,
        [
            "GalaxyName",
            "RadiusKpc",
            "NearestProfileRadiusKpc",
            "RadiusDeltaKpc",
            "DerivedI3p6LsunPc2",
            "SparcSBdiskLsunPc2",
            "AbsFractionalError",
            "ValidationUse",
            "CanRunVelocitySolverNow",
            "CanScoreMissingGalaxiesNow",
            "Guardrail",
        ],
    )
    write_csv(
        METRIC_OUT,
        metrics,
        [
            "GalaxyName",
            "NMatchedRadii",
            "MedianAbsFractionalError",
            "FractionWithin50Percent",
            "PassCondition",
            "ValidationStatus",
            "CanRunVelocitySolverNow",
            "CanScoreMissingGalaxiesNow",
            "Guardrail",
        ],
    )
    write_csv(
        GATE_OUT,
        gates,
        [
            "GateID",
            "Status",
            "Evidence",
            "CanRunVelocitySolverNow",
            "CanScoreMissingGalaxiesNow",
            "NextAction",
            "Guardrail",
        ],
    )
    write_report(metrics, gates)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
