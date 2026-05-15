#!/usr/bin/env python3
"""Convert validation native profiles to frozen surface-density proxies."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

from astropy.io import fits

from make_packet_v01_seed import PACKET, read_csv, write_csv


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "things_route2_solver_validation_inputs_v01"
PROFILE_IN = PACKET / "things_route2_validation_surface_profiles_v01.csv"
CONVERTED_OUT = PACKET / "things_route2_validation_surface_density_profiles_v01.csv"
BEAM_OUT = PACKET / "things_route2_validation_beam_conversion_audit_v01.csv"
SUMMARY_OUT = PACKET / "things_route2_validation_surface_density_summary_v01.csv"
GATE_OUT = PACKET / "things_route2_validation_surface_density_gate_v01.csv"
REPORT = PACKET / "things_route2_validation_surface_density_v01.md"

GUARDRAIL = "route2_validation_surface_density_conversion_no_velocity_solver_no_scores"

HI_FREQ_GHZ = 1.420405751
NHI_PER_K_KMS = 1.823e18
NHI_PER_MSUN_PC2 = 1.249e20
HELIUM_FACTOR = 1.4
AB_ZERO_MJY_SR = 20.472
MU_TO_LSUN_PC2_OFFSET = 21.572
M_SUN_3P6_AB = 6.02


def mom0_paths() -> dict[str, Path]:
    return {
        path.parent.name: path
        for path in sorted(RAW.glob("*/*MOM0*"))
        if path.suffix.lower() == ".fits"
    }


def parse_beam_from_history(path: Path) -> dict[str, str]:
    header = fits.getheader(path)
    history_cards = header.get("HISTORY", [])
    if isinstance(history_cards, str):
        history_cards = [history_cards]
    pattern = re.compile(
        r"CLEAN BMAJ=\s*([+-]?\d+\.\d+E[+-]\d+)\s+BMIN=\s*([+-]?\d+\.\d+E[+-]\d+)\s+BPA=\s*([+-]?\d+\.\d+)"
    )
    for line in history_cards:
        match = pattern.search(str(line))
        if not match:
            continue
        bmaj_deg = float(match.group(1))
        bmin_deg = float(match.group(2))
        bpa_deg = float(match.group(3))
        return {
            "GalaxyName": path.parent.name,
            "FileName": path.name,
            "BeamSource": "AIPS_CLEAN_HISTORY",
            "BmajDeg": f"{bmaj_deg:.9g}",
            "BminDeg": f"{bmin_deg:.9g}",
            "BpaDeg": f"{bpa_deg:.6f}",
            "BmajArcsec": f"{bmaj_deg * 3600.0:.6f}",
            "BminArcsec": f"{bmin_deg * 3600.0:.6f}",
            "RestFrequencyGHz": f"{HI_FREQ_GHZ:.9f}",
            "BeamParsed": "yes",
            "Guardrail": GUARDRAIL,
        }
    return {
        "GalaxyName": path.parent.name,
        "FileName": path.name,
        "BeamSource": "not_found",
        "BmajDeg": "",
        "BminDeg": "",
        "BpaDeg": "",
        "BmajArcsec": "",
        "BminArcsec": "",
        "RestFrequencyGHz": f"{HI_FREQ_GHZ:.9f}",
        "BeamParsed": "no",
        "Guardrail": GUARDRAIL,
    }


def hi_sigma_from_jy_beam_mps(value: float, beam: dict[str, str]) -> float:
    if value <= 0 or beam["BeamParsed"] != "yes":
        return math.nan
    bmaj = float(beam["BmajArcsec"])
    bmin = float(beam["BminArcsec"])
    jy_beam_kms = value / 1000.0
    k_kms = 1.222e6 * jy_beam_kms / (HI_FREQ_GHZ * HI_FREQ_GHZ * bmaj * bmin)
    sigma_hi = (NHI_PER_K_KMS * k_kms) / NHI_PER_MSUN_PC2
    return sigma_hi * HELIUM_FACTOR


def irac_lsun_pc2_from_mjy_sr(value: float) -> float:
    if value <= 0:
        return math.nan
    mu_ab = AB_ZERO_MJY_SR - 2.5 * math.log10(value)
    return 10 ** (-0.4 * (mu_ab - M_SUN_3P6_AB - MU_TO_LSUN_PC2_OFFSET))


def converted_rows(profiles: list[dict[str, str]], beams: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for row in profiles:
        native = float(row["FiniteMedianNativeUnit"])
        role = row["SourceRole"]
        if role == "THINGS_HI_MOM0":
            value = hi_sigma_from_jy_beam_mps(native, beams[row["GalaxyName"]])
            converted_name = "SigmaGasWithHelium_MsunPc2"
            conversion_status = "converted_from_MOM0_history_beam"
        elif role == "SINGS_IRAC1_3P6UM":
            value = irac_lsun_pc2_from_mjy_sr(native)
            converted_name = "I3p6_LsunPc2_AB_Msun6p02"
            conversion_status = "converted_from_MJySr_fixed_AB_solar_zero"
        else:
            value = math.nan
            converted_name = "unknown"
            conversion_status = "not_converted"
        rows.append(
            {
                "GalaxyName": row["GalaxyName"],
                "SourceRole": role,
                "BinID": row["BinID"],
                "RadiusMidKpc": row["RadiusMidKpc"],
                "NativeMedian": row["FiniteMedianNativeUnit"],
                "InputBUNIT": row["InputBUNIT"],
                "ConvertedQuantity": converted_name,
                "ConvertedMedian": "" if math.isnan(value) else f"{value:.9g}",
                "ConversionStatus": conversion_status,
                "ValidationUse": "surface_density_profile_only_not_velocity_solver",
                "CanScoreMissingGalaxiesNow": "no",
                "Guardrail": GUARDRAIL,
            }
        )
    return rows


def summary_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    outputs = []
    for galaxy in sorted({row["GalaxyName"] for row in rows}):
        for role in ["THINGS_HI_MOM0", "SINGS_IRAC1_3P6UM"]:
            subset = [row for row in rows if row["GalaxyName"] == galaxy and row["SourceRole"] == role]
            finite = [float(row["ConvertedMedian"]) for row in subset if row["ConvertedMedian"]]
            outputs.append(
                {
                    "GalaxyName": galaxy,
                    "SourceRole": role,
                    "NConvertedBins": str(len(finite)),
                    "MedianConvertedProfileValue": f"{median(finite):.9g}" if finite else "",
                    "MaxRadiusMidKpc": subset[-1]["RadiusMidKpc"] if subset else "",
                    "ConversionStatus": "converted_surface_density_proxy" if len(finite) >= 5 else "conversion_incomplete",
                    "ValidationUse": "surface_density_profile_only_not_velocity_solver",
                    "CanScoreMissingGalaxiesNow": "no",
                    "Guardrail": GUARDRAIL,
                }
            )
    return outputs


def median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    if n % 2:
        return ordered[n // 2]
    return (ordered[n // 2 - 1] + ordered[n // 2]) / 2


def gate_rows(summary: list[dict[str, str]], beams: list[dict[str, str]]) -> list[dict[str, str]]:
    complete = sorted(
        {
            row["GalaxyName"]
            for row in summary
            if row["ConversionStatus"] == "converted_surface_density_proxy"
        }
    )
    beam_ok = all(row["BeamParsed"] == "yes" for row in beams)
    return [
        {
            "GateID": "R2VALDENS01",
            "Status": "surface_density_proxy_profiles_converted_for_three_validation_galaxies"
            if len(complete) >= 3 and beam_ok
            else "surface_density_conversion_incomplete",
            "Galaxies": ";".join(complete),
            "CanValidateSolverNow": "not_until_velocity_solver_maps_surface_density_to_components",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "run_predeclared_velocity_solver_and_compare_to_SPARC_component_curves",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2VALDENS02",
            "Status": "velocity_solver_not_run",
            "Galaxies": ";".join(complete),
            "CanValidateSolverNow": "no",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "keep_surface_density_conversion_separate_from_solver_validation",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report(beams: list[dict[str, str]], summary: list[dict[str, str]], gates: list[dict[str, str]]) -> None:
    lines = [
        "# THINGS Route 2 Validation Surface-Density Conversion v0.1",
        "",
        "This packet converts the native validation profiles into frozen surface-density proxies. It uses AIPS CLEAN beam values parsed from THINGS MOM0 HISTORY cards and a fixed AB 3.6 micron luminosity conversion for SINGS IRAC1. It does not run a velocity solver and does not compute missing-galaxy scores.",
        "",
        "## Beam Audit",
        "",
    ]
    for row in beams:
        lines.append(
            f"- `{row['GalaxyName']}`: beam parsed={row['BeamParsed']}, BMAJ={row['BmajArcsec']} arcsec, BMIN={row['BminArcsec']} arcsec."
        )
    lines.extend(["", "## Conversion Summary", ""])
    for row in summary:
        lines.append(
            f"- `{row['GalaxyName']}` `{row['SourceRole']}`: {row['NConvertedBins']} bins, median {row['MedianConvertedProfileValue']}."
        )
    lines.extend(["", "## Gate", ""])
    for gate in gates:
        lines.append(
            f"- `{gate['GateID']}`: {gate['Status']} / validate={gate['CanValidateSolverNow']} / score={gate['CanScoreMissingGalaxiesNow']}."
        )
    lines.extend(
        [
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
    for path in [CONVERTED_OUT, BEAM_OUT, SUMMARY_OUT, GATE_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_route2_validation_surface_density_status"] = (
        "surface_density_proxy_profiles_converted_no_velocity_solver_no_scores"
    )
    manifest["paper2_next_gate"] = "route2_velocity_solver_validation_against_sparc_components"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    beams = [parse_beam_from_history(path) for path in mom0_paths().values()]
    beam_by_galaxy = {row["GalaxyName"]: row for row in beams}
    converted = converted_rows(read_csv(PROFILE_IN), beam_by_galaxy)
    summary = summary_rows(converted)
    gates = gate_rows(summary, beams)
    write_csv(
        BEAM_OUT,
        beams,
        [
            "GalaxyName",
            "FileName",
            "BeamSource",
            "BmajDeg",
            "BminDeg",
            "BpaDeg",
            "BmajArcsec",
            "BminArcsec",
            "RestFrequencyGHz",
            "BeamParsed",
            "Guardrail",
        ],
    )
    write_csv(
        CONVERTED_OUT,
        converted,
        [
            "GalaxyName",
            "SourceRole",
            "BinID",
            "RadiusMidKpc",
            "NativeMedian",
            "InputBUNIT",
            "ConvertedQuantity",
            "ConvertedMedian",
            "ConversionStatus",
            "ValidationUse",
            "CanScoreMissingGalaxiesNow",
            "Guardrail",
        ],
    )
    write_csv(
        SUMMARY_OUT,
        summary,
        [
            "GalaxyName",
            "SourceRole",
            "NConvertedBins",
            "MedianConvertedProfileValue",
            "MaxRadiusMidKpc",
            "ConversionStatus",
            "ValidationUse",
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
            "Galaxies",
            "CanValidateSolverNow",
            "CanScoreMissingGalaxiesNow",
            "NextAction",
            "Guardrail",
        ],
    )
    write_report(beams, summary, gates)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
