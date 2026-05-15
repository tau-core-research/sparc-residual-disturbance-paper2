#!/usr/bin/env python3
"""Audit FITS readiness for route 2 solver-validation inputs."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
from astropy.io import fits

from make_packet_v01_seed import PACKET, write_csv


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "things_route2_solver_validation_inputs_v01"
HEADER_OUT = PACKET / "things_route2_solver_validation_fits_header_v01.csv"
GATE_OUT = PACKET / "things_route2_solver_validation_fits_gate_v01.csv"
REPORT = PACKET / "things_route2_solver_validation_fits_v01.md"

GUARDRAIL = "route2_solver_validation_fits_readiness_no_component_arrays_no_scores"


def product_paths() -> list[Path]:
    return sorted(RAW.glob("*/*.fits")) + sorted(RAW.glob("*/*.FITS"))


def is_tracked(path: Path) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path.relative_to(ROOT))],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def source_role(path: Path) -> str:
    name = path.name.upper()
    if "MOM0" in name:
        return "THINGS_HI_MOM0"
    if "PHOT.1.FITS" in name:
        return "SINGS_IRAC1_3P6UM"
    return "unknown"


def data_stats(data: np.ndarray | None) -> tuple[str, str, str]:
    if data is None:
        return "", "", ""
    arr = np.asarray(data, dtype=float)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return "0", "", ""
    return str(int(finite.size)), f"{float(np.nanmin(finite)):.9g}", f"{float(np.nanmax(finite)):.9g}"


def header_rows() -> list[dict[str, str]]:
    rows = []
    for path in product_paths():
        with fits.open(path, memmap=True) as hdul:
            header = hdul[0].header
            data = hdul[0].data
            finite_count, finite_min, finite_max = data_stats(data)
            rows.append(
                {
                    "GalaxyName": path.parent.name,
                    "FileName": path.name,
                    "SourceRole": source_role(path),
                    "Shape": "x".join(str(part) for part in getattr(data, "shape", ())),
                    "Object": str(header.get("OBJECT", "")),
                    "Telescope": str(header.get("TELESCOP", "")),
                    "Instrument": str(header.get("INSTRUME", "")),
                    "BUNIT": str(header.get("BUNIT", "")),
                    "CTYPE1": str(header.get("CTYPE1", "")),
                    "CTYPE2": str(header.get("CTYPE2", "")),
                    "CRVAL1": str(header.get("CRVAL1", "")),
                    "CRVAL2": str(header.get("CRVAL2", "")),
                    "CRPIX1": str(header.get("CRPIX1", "")),
                    "CRPIX2": str(header.get("CRPIX2", "")),
                    "CDELT1": str(header.get("CDELT1", "")),
                    "CDELT2": str(header.get("CDELT2", "")),
                    "FinitePixelCount": finite_count,
                    "FiniteMin": finite_min,
                    "FiniteMax": finite_max,
                    "HeaderReadable": "yes",
                    "GitTrackedRaw": "yes" if is_tracked(path) else "no",
                    "ValidationUse": "solver_reconstruction_accuracy_only_not_tau_endpoint",
                    "CanScoreMissingGalaxiesNow": "no",
                    "Guardrail": GUARDRAIL,
                }
            )
    return rows


def gate_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_galaxy: dict[str, set[str]] = {}
    for row in rows:
        by_galaxy.setdefault(row["GalaxyName"], set()).add(row["SourceRole"])
    complete = [
        galaxy
        for galaxy, roles in by_galaxy.items()
        if {"THINGS_HI_MOM0", "SINGS_IRAC1_3P6UM"}.issubset(roles)
    ]
    units = {(row["SourceRole"], row["BUNIT"]) for row in rows}
    expected_units = {
        ("THINGS_HI_MOM0", "JY/B*M/S"),
        ("SINGS_IRAC1_3P6UM", "MJy/sr"),
    }
    unit_status = "source_units_identified" if expected_units.issubset(units) else "source_units_incomplete"
    return [
        {
            "GateID": "R2VALFITS01",
            "Status": "validation_fits_headers_readable_for_three_overlap_galaxies"
            if len(complete) >= 3
            else "validation_fits_headers_incomplete",
            "Galaxies": ";".join(sorted(complete)),
            "CanDeriveValidationProfilesNow": "partial_after_geometry_profile_extraction_script",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "derive_blind_surface_density_profiles_for_solver_validation",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2VALFITS02",
            "Status": unit_status,
            "Galaxies": ";".join(sorted(complete)),
            "CanDeriveValidationProfilesNow": "partial",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "apply_frozen_MOM0_and_IRAC_conversion_policy",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2VALFITS03",
            "Status": "component_arrays_not_yet_derived",
            "Galaxies": ";".join(sorted(complete)),
            "CanDeriveValidationProfilesNow": "no",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "validate_component_reconstruction_against_existing_SPARC_curves_before_missing_scores",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report(rows: list[dict[str, str]], gates: list[dict[str, str]]) -> None:
    lines = [
        "# THINGS Route 2 Solver Validation FITS Audit v0.1",
        "",
        "This audit checks the FITS headers and units for the staged solver-validation inputs. It does not derive surface-density profiles, component velocity curves, or any missing-galaxy `W_tau_eff` score.",
        "",
        "## Readiness",
        "",
        "- THINGS MOM0 validation products are readable for NGC2403, NGC3198, and NGC5055.",
        "- SINGS IRAC1 validation products are readable for NGC2403, NGC3198, and NGC5055.",
        "- MOM0 uses `JY/B*M/S`; IRAC1 uses `MJy/sr`.",
        "- Raw files remain outside git.",
        "",
        "## Gate",
        "",
    ]
    for gate in gates:
        lines.append(
            f"- `{gate['GateID']}`: {gate['Status']} / validate={gate['CanDeriveValidationProfilesNow']} / score={gate['CanScoreMissingGalaxiesNow']}."
        )
    lines.extend(
        [
            "",
            "No component arrays are derived here.",
            "No missing-galaxy score is computed here.",
            "",
            "## Guardrail",
            "",
            f"`{GUARDRAIL}`",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [HEADER_OUT, GATE_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_route2_solver_validation_fits_status"] = (
        "validation_fits_headers_units_readable_no_component_arrays_no_scores"
    )
    manifest["paper2_next_gate"] = (
        "route2_blind_surface_density_profile_derivation_for_solver_validation"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = header_rows()
    gates = gate_rows(rows)
    write_csv(
        HEADER_OUT,
        rows,
        [
            "GalaxyName",
            "FileName",
            "SourceRole",
            "Shape",
            "Object",
            "Telescope",
            "Instrument",
            "BUNIT",
            "CTYPE1",
            "CTYPE2",
            "CRVAL1",
            "CRVAL2",
            "CRPIX1",
            "CRPIX2",
            "CDELT1",
            "CDELT2",
            "FinitePixelCount",
            "FiniteMin",
            "FiniteMax",
            "HeaderReadable",
            "GitTrackedRaw",
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
            "CanDeriveValidationProfilesNow",
            "CanScoreMissingGalaxiesNow",
            "NextAction",
            "Guardrail",
        ],
    )
    write_report(rows, gates)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
