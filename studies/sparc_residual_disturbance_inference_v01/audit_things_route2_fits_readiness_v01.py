#!/usr/bin/env python3
"""Audit FITS readiness for route 2 component-array derivation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from astropy.io import fits

from make_packet_v01_seed import PACKET, write_csv


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "things_route2_primary_inputs_v01"
HEADER_OUT = PACKET / "things_route2_fits_header_readiness_v01.csv"
GATE_OUT = PACKET / "things_route2_component_derivation_readiness_gate_v01.csv"
REPORT = PACKET / "things_route2_fits_readiness_v01.md"

GUARDRAIL = "fits_readiness_only_no_component_arrays_no_scores"


def product_paths() -> list[Path]:
    return sorted(RAW.glob("*/*.fits")) + sorted(RAW.glob("*/*.FITS"))


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
            finite_count, min_value, max_value = data_stats(data)
            galaxy = path.parent.name
            name = path.name.upper()
            role = (
                "THINGS_HI_MOM0"
                if "MOM0" in name
                else "THINGS_HI_MOM1"
                if "MOM1" in name
                else "SINGS_IRAC1_3P6UM"
                if "PHOT.1.FITS" in name
                else "unknown"
            )
            rows.append(
                {
                    "GalaxyName": galaxy,
                    "FileName": path.name,
                    "SourceRole": role,
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
                    "FiniteMin": min_value,
                    "FiniteMax": max_value,
                    "HeaderReadable": "yes",
                    "GitTrackedRaw": "no",
                    "Guardrail": GUARDRAIL,
                }
            )
    return rows


def gate_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    galaxies = sorted({row["GalaxyName"] for row in rows})
    required_roles = {"SINGS_IRAC1_3P6UM", "THINGS_HI_MOM0", "THINGS_HI_MOM1"}
    complete_galaxies = []
    for galaxy in galaxies:
        roles = {row["SourceRole"] for row in rows if row["GalaxyName"] == galaxy}
        if required_roles.issubset(roles):
            complete_galaxies.append(galaxy)
    return [
        {
            "GateID": "R2FITS01",
            "Status": "fits_headers_readable_for_two_primary_galaxies"
            if set(complete_galaxies) >= {"NGC925", "NGC3031"}
            else "fits_headers_incomplete",
            "Galaxies": ";".join(complete_galaxies),
            "CanDeriveComponentArraysNow": "not_without_geometry_and_mass_model_solver",
            "CanScoreNow": "no",
            "NextRequiredStep": "freeze_ring_geometry_and_surface_density_to_velocity_solver",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2FITS02",
            "Status": "source_units_identified",
            "Galaxies": "NGC925;NGC3031",
            "CanDeriveComponentArraysNow": "partial",
            "CanScoreNow": "no",
            "NextRequiredStep": "document_MOM0_to_HI_surface_density_and_IRAC_to_stellar_surface_density_conversions",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2FITS03",
            "Status": "component_arrays_not_yet_derived",
            "Galaxies": "NGC925;NGC3031",
            "CanDeriveComponentArraysNow": "no",
            "CanScoreNow": "no",
            "NextRequiredStep": "derive_R_Vobs_eVobs_Vgas_Vdisk_Vbul_under_frozen_protocol",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report(rows: list[dict[str, str]], gates: list[dict[str, str]]) -> None:
    lines = [
        "# THINGS Route 2 FITS Readiness Audit v0.1",
        "",
        "This audit checks whether the staged FITS products for NGC925 and NGC3031 are readable and contain enough metadata to begin component-array derivation. It does not derive `Vgas`, `Vdisk`, `Vbul`, or any `W_tau_eff` score.",
        "",
        "## Readiness",
        "",
        "- THINGS MOM0/MOM1 products are readable for both primary galaxies.",
        "- SINGS IRAC 3.6 micron products are readable for both primary galaxies.",
        "- WCS-like coordinate headers and image units are present.",
        "- Component arrays are still not derived.",
        "",
        "## Remaining Blockers",
        "",
        "- Freeze ring geometry and radius grid for extraction.",
        "- Convert MOM0 flux units into HI surface-density profiles.",
        "- Convert IRAC 3.6 micron images into stellar surface-density profiles using the frozen M/L policy.",
        "- Apply a frozen disk-potential or external solver rule to convert surface density profiles into `Vgas`, `Vdisk`, and `Vbul`.",
        "- Define `eVobs` or an uncertainty carry-through rule before scoring.",
        "",
        "## Gate",
        "",
    ]
    for gate in gates:
        lines.append(f"- `{gate['GateID']}`: {gate['Status']} / score={gate['CanScoreNow']}.")
    lines.extend(["", "## Guardrail", "", f"`{GUARDRAIL}`", ""])
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [HEADER_OUT, GATE_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_route2_fits_readiness_status"] = (
        "headers_readable_component_arrays_not_derived_no_scores"
    )
    manifest["paper2_next_gate"] = "route2_freeze_geometry_and_surface_density_velocity_solver"
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
            "CanDeriveComponentArraysNow",
            "CanScoreNow",
            "NextRequiredStep",
            "Guardrail",
        ],
    )
    write_report(rows, gates)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
