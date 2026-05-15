#!/usr/bin/env python3
"""Audit whether a frozen background policy rescues route 2 photometry."""

from __future__ import annotations

import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


SPARC_ROTMOD = Path("/Users/jolcsak/Projects/tau-core/data/sparc/Rotmod_LTG")
NATIVE_PROFILES = PACKET / "things_route2_validation_surface_profiles_v01.csv"

POLICY_OUT = PACKET / "things_route2_photometry_policy_v01.csv"
JOIN_OUT = PACKET / "things_route2_photometry_policy_sparc_join_v01.csv"
METRIC_OUT = PACKET / "things_route2_photometry_policy_metrics_v01.csv"
GATE_OUT = PACKET / "things_route2_photometry_policy_gate_v01.csv"
REPORT = PACKET / "things_route2_photometry_policy_v01.md"

GUARDRAIL = "route2_photometry_policy_background_only_does_not_validate_solver"
GALAXIES = ["NGC2403", "NGC3198", "NGC5055"]
AB_ZERO_MJY_SR = 20.472
MU_TO_LSUN_PC2_OFFSET = 21.572
M_SUN_3P6_AB = 6.02
L_FACTOR = 10 ** (-0.4 * (AB_ZERO_MJY_SR - M_SUN_3P6_AB - MU_TO_LSUN_PC2_OFFSET))


def median(values: list[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    n = len(ordered)
    if n % 2:
        return ordered[n // 2]
    return (ordered[n // 2 - 1] + ordered[n // 2]) / 2


def read_rotmod(galaxy: str) -> list[dict[str, float]]:
    rows = []
    with (SPARC_ROTMOD / f"{galaxy}_rotmod.dat").open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            rows.append({"RadiusKpc": float(parts[0]), "SBdiskLsunPc2": float(parts[6])})
    return rows


def irac_profiles() -> dict[str, list[dict[str, str]]]:
    rows = [
        row
        for row in read_csv(NATIVE_PROFILES)
        if row["SourceRole"] == "SINGS_IRAC1_3P6UM"
    ]
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["GalaxyName"], []).append(row)
    return grouped


def policy_rows(grouped: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    rows = []
    for galaxy in GALAXIES:
        profiles = grouped[galaxy]
        radii = [float(row["RadiusMidKpc"]) for row in profiles]
        max_radius = max(radii)
        outer = [
            float(row["FiniteMedianNativeUnit"])
            for row in profiles
            if float(row["RadiusMidKpc"]) >= 0.8 * max_radius
        ]
        background = median(outer)
        rows.append(
            {
                "GalaxyName": galaxy,
                "PolicyID": "R2PHOT01",
                "FrozenPolicy": "subtract_outer_20_percent_radius_median_from_IRAC1_native_profile_floor_at_zero",
                "BackgroundNativeMJySr": f"{background:.9g}",
                "OuterAnnulusStartFraction": "0.8",
                "AllowedInputs": "IRAC1_native_radial_profile;fixed_geometry",
                "ForbiddenInputs": "SPARC_SBdisk;Vobs;residuals;W_tau_eff;missing_galaxy_score_direction",
                "ValidationUse": "photometry_policy_stress_test_only_not_solver",
                "CanRunVelocitySolverNow": "no",
                "CanScoreMissingGalaxiesNow": "no",
                "Guardrail": GUARDRAIL,
            }
        )
    return rows


def corrected_lsun(native_mjy_sr: float, background: float) -> float:
    return max(0.0, native_mjy_sr - background) * L_FACTOR


def nearest_profile(
    profiles: list[dict[str, str]], radius: float
) -> tuple[dict[str, str] | None, float]:
    if not profiles:
        return None, math.nan
    best = min(profiles, key=lambda row: abs(float(row["RadiusMidKpc"]) - radius))
    return best, abs(float(best["RadiusMidKpc"]) - radius)


def join_rows(grouped: dict[str, list[dict[str, str]]], policies: list[dict[str, str]]) -> list[dict[str, str]]:
    background = {
        row["GalaxyName"]: float(row["BackgroundNativeMJySr"]) for row in policies
    }
    outputs = []
    for galaxy in GALAXIES:
        profiles = grouped[galaxy]
        for ref in read_rotmod(galaxy):
            profile, delta = nearest_profile(profiles, ref["RadiusKpc"])
            if profile is None or delta > 0.3 or ref["SBdiskLsunPc2"] <= 0:
                continue
            native = float(profile["FiniteMedianNativeUnit"])
            corrected = corrected_lsun(native, background[galaxy])
            reference = ref["SBdiskLsunPc2"]
            frac_error = abs(corrected - reference) / reference
            outputs.append(
                {
                    "GalaxyName": galaxy,
                    "RadiusKpc": f"{ref['RadiusKpc']:.6f}",
                    "NearestProfileRadiusKpc": profile["RadiusMidKpc"],
                    "RadiusDeltaKpc": f"{delta:.6f}",
                    "NativeMedianMJySr": f"{native:.9g}",
                    "BackgroundNativeMJySr": f"{background[galaxy]:.9g}",
                    "CorrectedI3p6LsunPc2": f"{corrected:.9g}",
                    "SparcSBdiskLsunPc2": f"{reference:.9g}",
                    "AbsFractionalError": f"{frac_error:.9f}",
                    "ValidationUse": "photometry_policy_stress_test_only_not_solver",
                    "CanRunVelocitySolverNow": "no",
                    "CanScoreMissingGalaxiesNow": "no",
                    "Guardrail": GUARDRAIL,
                }
            )
    return outputs


def metric_rows(joined: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for galaxy in GALAXIES:
        subset = [row for row in joined if row["GalaxyName"] == galaxy]
        errors = [float(row["AbsFractionalError"]) for row in subset]
        pass_fraction = sum(error <= 0.5 for error in errors) / len(errors) if errors else math.nan
        med_error = median(errors)
        rows.append(
            {
                "GalaxyName": galaxy,
                "NMatchedRadii": str(len(errors)),
                "MedianAbsFractionalError": "" if math.isnan(med_error) else f"{med_error:.9f}",
                "FractionWithin50Percent": "" if math.isnan(pass_fraction) else f"{pass_fraction:.9f}",
                "PassCondition": "median_abs_fractional_error_le_0p50_and_fraction_within_50_percent_ge_0p50",
                "ValidationStatus": "pass"
                if med_error <= 0.5 and pass_fraction >= 0.5
                else "fail_background_only_photometry_policy",
                "CanRunVelocitySolverNow": "no",
                "CanScoreMissingGalaxiesNow": "no",
                "Guardrail": GUARDRAIL,
            }
        )
    return rows


def gate_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    passed = [row for row in metrics if row["ValidationStatus"] == "pass"]
    return [
        {
            "GateID": "R2PHOTG01",
            "Status": "background_only_photometry_policy_failed_reference_check"
            if len(passed) < 3
            else "background_only_photometry_policy_passed_reference_check",
            "Evidence": f"passed={len(passed)}_of_3",
            "CanRunVelocitySolverNow": "no" if len(passed) < 3 else "yes",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "do_not_run_velocity_solver_until_SPARC_photometry_or_mass_model_source_is_recovered",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2PHOTG02",
            "Status": "route2_missing_galaxy_expansion_remains_blocked",
            "Evidence": "simple_background_subtraction_does_not_reproduce_SPARC_SBdisk",
            "CanRunVelocitySolverNow": "no",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "prefer_recovering_published_mass_model_columns_or_document_route2_as_closed_for_now",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report(
    policies: list[dict[str, str]],
    metrics: list[dict[str, str]],
    gates: list[dict[str, str]],
) -> None:
    lines = [
        "# THINGS Route 2 Photometry Policy Audit v0.1",
        "",
        "This audit freezes a simple, source-only background policy for SINGS IRAC1 profiles: subtract the median native MJy/sr value in the outer 20 percent of the extracted radial profile and floor at zero. The policy does not use SPARC `SBdisk`, velocity residuals, `W_tau_eff`, or missing-galaxy score direction.",
        "",
        "## Frozen Backgrounds",
        "",
    ]
    for row in policies:
        lines.append(
            f"- `{row['GalaxyName']}`: background={row['BackgroundNativeMJySr']} MJy/sr."
        )
    lines.extend(["", "## Reference Check", ""])
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
            "Conclusion: simple source-only background subtraction does not validate route 2 stellar photometry against SPARC `SBdisk`. The route2 velocity-solver path remains blocked unless published mass-model columns are recovered or a more complete, pre-registered photometry/decomposition pipeline is introduced and validated.",
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
    for path in [POLICY_OUT, JOIN_OUT, METRIC_OUT, GATE_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_route2_photometry_policy_status"] = (
        "background_only_policy_failed_sparc_reference_check_solver_blocked"
    )
    manifest["paper2_next_gate"] = (
        "route2_recover_published_mass_model_columns_or_close_route2_expansion"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    grouped = irac_profiles()
    policies = policy_rows(grouped)
    joined = join_rows(grouped, policies)
    metrics = metric_rows(joined)
    gates = gate_rows(metrics)
    write_csv(
        POLICY_OUT,
        policies,
        [
            "GalaxyName",
            "PolicyID",
            "FrozenPolicy",
            "BackgroundNativeMJySr",
            "OuterAnnulusStartFraction",
            "AllowedInputs",
            "ForbiddenInputs",
            "ValidationUse",
            "CanRunVelocitySolverNow",
            "CanScoreMissingGalaxiesNow",
            "Guardrail",
        ],
    )
    write_csv(
        JOIN_OUT,
        joined,
        [
            "GalaxyName",
            "RadiusKpc",
            "NearestProfileRadiusKpc",
            "RadiusDeltaKpc",
            "NativeMedianMJySr",
            "BackgroundNativeMJySr",
            "CorrectedI3p6LsunPc2",
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
    write_report(policies, metrics, gates)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
