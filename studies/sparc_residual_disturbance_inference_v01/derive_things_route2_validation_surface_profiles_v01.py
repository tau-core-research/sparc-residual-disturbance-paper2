#!/usr/bin/env python3
"""Derive blind surface-brightness profiles for route 2 solver validation."""

from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales

from make_packet_v01_seed import PACKET, write_csv


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "things_route2_solver_validation_inputs_v01"
PROFILE_OUT = PACKET / "things_route2_validation_surface_profiles_v01.csv"
SUMMARY_OUT = PACKET / "things_route2_validation_surface_profile_summary_v01.csv"
GATE_OUT = PACKET / "things_route2_validation_surface_profile_gate_v01.csv"
REPORT = PACKET / "things_route2_validation_surface_profiles_v01.md"

GUARDRAIL = "route2_validation_surface_profiles_no_velocity_solver_no_scores"


GEOMETRY = {
    "NGC2403": {
        "ra_deg": 15 * (7 + 36 / 60 + 51.1 / 3600),
        "dec_deg": 65 + 36 / 60 + 2.9 / 3600,
        "distance_mpc": 3.2,
        "inclination_deg": 62.9,
        "pa_deg": 123.7,
    },
    "NGC3198": {
        "ra_deg": 15 * (10 + 19 / 60 + 55.0 / 3600),
        "dec_deg": 45 + 32 / 60 + 58.9 / 3600,
        "distance_mpc": 13.8,
        "inclination_deg": 71.5,
        "pa_deg": 215.0,
    },
    "NGC5055": {
        "ra_deg": 15 * (13 + 15 / 60 + 49.2 / 3600),
        "dec_deg": 42 + 1 / 60 + 45.3 / 3600,
        "distance_mpc": 10.1,
        "inclination_deg": 59.0,
        "pa_deg": 101.8,
    },
}


def product_paths() -> list[Path]:
    return sorted(RAW.glob("*/*.fits")) + sorted(RAW.glob("*/*.FITS"))


def source_role(path: Path) -> str:
    name = path.name.upper()
    if "MOM0" in name:
        return "THINGS_HI_MOM0"
    if "PHOT.1.FITS" in name:
        return "SINGS_IRAC1_3P6UM"
    return "unknown"


def is_tracked(path: Path) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path.relative_to(ROOT))],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def image_and_wcs(path: Path) -> tuple[np.ndarray, WCS, fits.Header]:
    with fits.open(path, memmap=True) as hdul:
        header = hdul[0].header
        data = np.squeeze(np.asarray(hdul[0].data, dtype=float))
    return data, WCS(header).celestial, header


def radius_map_kpc(shape: tuple[int, int], wcs: WCS, geometry: dict[str, float]) -> np.ndarray:
    y, x = np.indices(shape)
    cx, cy = wcs.world_to_pixel_values(geometry["ra_deg"], geometry["dec_deg"])
    scales_deg = proj_plane_pixel_scales(wcs)
    pixel_scale_arcsec = float(np.mean(np.abs(scales_deg)) * 3600.0)
    dx_arcsec = (x - cx) * pixel_scale_arcsec
    dy_arcsec = (y - cy) * pixel_scale_arcsec
    pa = math.radians(geometry["pa_deg"])
    major = dx_arcsec * math.sin(pa) + dy_arcsec * math.cos(pa)
    minor = -dx_arcsec * math.cos(pa) + dy_arcsec * math.sin(pa)
    cos_i = max(math.cos(math.radians(geometry["inclination_deg"])), 1e-3)
    deprojected_arcsec = np.sqrt(major * major + (minor / cos_i) ** 2)
    return deprojected_arcsec * geometry["distance_mpc"] * 1000.0 / 206265.0


def radial_profile(path: Path) -> list[dict[str, str]]:
    galaxy = path.parent.name
    role = source_role(path)
    geometry = GEOMETRY[galaxy]
    data, wcs, header = image_and_wcs(path)
    radii = radius_map_kpc(data.shape, wcs, geometry)
    finite = np.isfinite(data) & np.isfinite(radii)
    if not np.any(finite):
        return []
    max_radius = min(float(np.nanpercentile(radii[finite], 95)), 50.0)
    bin_width = 0.5
    edges = np.arange(0.0, max_radius + bin_width, bin_width)
    rows = []
    for idx, (r0, r1) in enumerate(zip(edges[:-1], edges[1:]), start=1):
        mask = finite & (radii >= r0) & (radii < r1)
        values = data[mask]
        if values.size < 25:
            continue
        rows.append(
            {
                "GalaxyName": galaxy,
                "SourceRole": role,
                "BinID": str(idx),
                "RadiusInnerKpc": f"{r0:.6f}",
                "RadiusOuterKpc": f"{r1:.6f}",
                "RadiusMidKpc": f"{(r0 + r1) / 2:.6f}",
                "PixelCount": str(int(values.size)),
                "FiniteMeanNativeUnit": f"{float(np.nanmean(values)):.9g}",
                "FiniteMedianNativeUnit": f"{float(np.nanmedian(values)):.9g}",
                "FiniteStdNativeUnit": f"{float(np.nanstd(values)):.9g}",
                "InputBUNIT": str(header.get("BUNIT", "")),
                "GeometrySource": "deBlok_THINGS_adopted_parameters_table",
                "DistanceMpc": f"{geometry['distance_mpc']:.1f}",
                "InclinationDeg": f"{geometry['inclination_deg']:.1f}",
                "PositionAngleDeg": f"{geometry['pa_deg']:.1f}",
                "GitTrackedRaw": "yes" if is_tracked(path) else "no",
                "ValidationUse": "surface_profile_extraction_only_not_velocity_solver",
                "CanScoreMissingGalaxiesNow": "no",
                "Guardrail": GUARDRAIL,
            }
        )
    return rows


def profile_rows() -> list[dict[str, str]]:
    rows = []
    for path in product_paths():
        rows.extend(radial_profile(path))
    return rows


def summary_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    outputs = []
    for galaxy in sorted({row["GalaxyName"] for row in rows}):
        for role in ["THINGS_HI_MOM0", "SINGS_IRAC1_3P6UM"]:
            subset = [row for row in rows if row["GalaxyName"] == galaxy and row["SourceRole"] == role]
            outputs.append(
                {
                    "GalaxyName": galaxy,
                    "SourceRole": role,
                    "NProfileBins": str(len(subset)),
                    "MaxRadiusMidKpc": subset[-1]["RadiusMidKpc"] if subset else "",
                    "InputBUNIT": subset[0]["InputBUNIT"] if subset else "",
                    "ProfileStatus": "derived_native_unit_profile" if len(subset) >= 5 else "insufficient_profile_bins",
                    "ValidationUse": "surface_profile_extraction_only_not_velocity_solver",
                    "CanScoreMissingGalaxiesNow": "no",
                    "Guardrail": GUARDRAIL,
                }
            )
    return outputs


def gate_rows(summary: list[dict[str, str]]) -> list[dict[str, str]]:
    complete = []
    for galaxy in sorted({row["GalaxyName"] for row in summary}):
        galaxy_rows = [row for row in summary if row["GalaxyName"] == galaxy]
        if all(row["ProfileStatus"] == "derived_native_unit_profile" for row in galaxy_rows):
            complete.append(galaxy)
    return [
        {
            "GateID": "R2VALPROF01",
            "Status": "native_unit_surface_profiles_derived_for_three_validation_galaxies"
            if len(complete) >= 3
            else "native_unit_surface_profiles_incomplete",
            "Galaxies": ";".join(complete),
            "CanValidateSolverNow": "not_until_native_profiles_are_converted_to_surface_density",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "convert_MOM0_and_IRAC_profiles_under_frozen_policy_then_compare_solver_to_SPARC_components",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2VALPROF02",
            "Status": "velocity_solver_not_run",
            "Galaxies": ";".join(complete),
            "CanValidateSolverNow": "no",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "keep_profile_gate_separate_from_component_velocity_solver",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report(summary: list[dict[str, str]], gates: list[dict[str, str]]) -> None:
    lines = [
        "# THINGS Route 2 Validation Surface Profiles v0.1",
        "",
        "This packet derives native-unit radial surface-brightness profiles for the staged solver-validation galaxies using frozen THINGS/de Blok geometry. It does not convert these profiles into mass surface density, does not run a velocity solver, and does not compute any missing-galaxy score.",
        "",
        "## Summary",
        "",
    ]
    for row in summary:
        lines.append(
            f"- `{row['GalaxyName']}` `{row['SourceRole']}`: {row['NProfileBins']} bins, max radius {row['MaxRadiusMidKpc']} kpc, unit `{row['InputBUNIT']}`."
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
    for path in [PROFILE_OUT, SUMMARY_OUT, GATE_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_route2_validation_surface_profile_status"] = (
        "native_unit_profiles_derived_no_velocity_solver_no_scores"
    )
    manifest["paper2_next_gate"] = (
        "route2_convert_validation_profiles_to_surface_density_and_validate_solver"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = profile_rows()
    summary = summary_rows(rows)
    gates = gate_rows(summary)
    fields = [
        "GalaxyName",
        "SourceRole",
        "BinID",
        "RadiusInnerKpc",
        "RadiusOuterKpc",
        "RadiusMidKpc",
        "PixelCount",
        "FiniteMeanNativeUnit",
        "FiniteMedianNativeUnit",
        "FiniteStdNativeUnit",
        "InputBUNIT",
        "GeometrySource",
        "DistanceMpc",
        "InclinationDeg",
        "PositionAngleDeg",
        "GitTrackedRaw",
        "ValidationUse",
        "CanScoreMissingGalaxiesNow",
        "Guardrail",
    ]
    write_csv(PROFILE_OUT, rows, fields)
    write_csv(
        SUMMARY_OUT,
        summary,
        [
            "GalaxyName",
            "SourceRole",
            "NProfileBins",
            "MaxRadiusMidKpc",
            "InputBUNIT",
            "ProfileStatus",
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
    write_report(summary, gates)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
