#!/usr/bin/env python3
"""Stage primary THINGS route 2 source products outside the public packet."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path
from urllib.request import urlopen

from make_packet_v01_seed import PACKET, write_csv


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "things_route2_primary_inputs_v01"
MANIFEST = PACKET / "things_route2_primary_input_staging_manifest_v01.csv"
GATE = PACKET / "things_route2_primary_input_staging_gate_v01.csv"
REPORT = PACKET / "things_route2_primary_input_staging_v01.md"

GUARDRAIL = "route2_primary_inputs_staged_raw_ignored_no_scores"


PRODUCTS = [
    (
        "NGC925",
        "THINGS_HI_MOM0_NA",
        "NGC_925_NA_MOM0_THINGS.FITS",
        "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_925_NA_MOM0_THINGS.FITS",
        "gas_surface_density_candidate",
    ),
    (
        "NGC925",
        "THINGS_HI_MOM1_NA",
        "NGC_925_NA_MOM1_THINGS.FITS",
        "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_925_NA_MOM1_THINGS.FITS",
        "velocity_field_candidate",
    ),
    (
        "NGC925",
        "THINGS_HI_MOM0_RO",
        "NGC_925_RO_MOM0_THINGS.FITS",
        "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_925_RO_MOM0_THINGS.FITS",
        "gas_surface_density_crosscheck_candidate",
    ),
    (
        "NGC925",
        "THINGS_HI_MOM1_RO",
        "NGC_925_RO_MOM1_THINGS.FITS",
        "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_925_RO_MOM1_THINGS.FITS",
        "velocity_field_crosscheck_candidate",
    ),
    (
        "NGC925",
        "SINGS_IRAC1_3P6UM",
        "ngc0925_v7.phot.1.fits",
        "https://irsa.ipac.caltech.edu/data/SPITZER/SINGS/galaxies/ngc0925/IRAC/ngc0925_v7.phot.1.fits",
        "stellar_3p6um_candidate",
    ),
    (
        "NGC3031",
        "THINGS_HI_MOM0_NA",
        "NGC_3031_NA_MOM0_THINGS.FITS",
        "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_3031_NA_MOM0_THINGS.FITS",
        "gas_surface_density_candidate",
    ),
    (
        "NGC3031",
        "THINGS_HI_MOM1_NA",
        "NGC_3031_NA_MOM1_THINGS.FITS",
        "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_3031_NA_MOM1_THINGS.FITS",
        "velocity_field_candidate",
    ),
    (
        "NGC3031",
        "THINGS_HI_MOM0_RO",
        "NGC_3031_RO_MOM0_THINGS.FITS",
        "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_3031_RO_MOM0_THINGS.FITS",
        "gas_surface_density_crosscheck_candidate",
    ),
    (
        "NGC3031",
        "THINGS_HI_MOM1_RO",
        "NGC_3031_RO_MOM1_THINGS.FITS",
        "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_3031_RO_MOM1_THINGS.FITS",
        "velocity_field_crosscheck_candidate",
    ),
    (
        "NGC3031",
        "SINGS_IRAC1_3P6UM",
        "ngc3031_v7.phot.1.fits",
        "https://irsa.ipac.caltech.edu/data/SPITZER/SINGS/galaxies/ngc3031/IRAC/ngc3031_v7.phot.1.fits",
        "stellar_3p6um_candidate",
    ),
]


def download(url: str, path: Path) -> None:
    if path.exists() and path.stat().st_size > 0:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with urlopen(url, timeout=120) as response, tmp.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    tmp.replace(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_tracked(path: Path) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path.relative_to(ROOT))],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def stage_inputs() -> list[dict[str, str]]:
    rows = []
    for galaxy, role, filename, url, use in PRODUCTS:
        local_path = RAW / galaxy / filename
        download(url, local_path)
        rows.append(
            {
                "GalaxyName": galaxy,
                "SourceRole": role,
                "Use": use,
                "URL": url,
                "LocalIgnoredPath": str(local_path.relative_to(ROOT)),
                "SizeBytes": str(local_path.stat().st_size),
                "SHA256": sha256(local_path),
                "Exists": "yes",
                "GitTracked": "yes" if is_tracked(local_path) else "no",
                "RedistributionPolicy": "raw_file_ignored_source_url_and_checksum_only",
                "Guardrail": GUARDRAIL,
            }
        )
    return rows


def gate_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_galaxy: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_galaxy.setdefault(row["GalaxyName"], []).append(row)
    complete = [
        galaxy
        for galaxy, galaxy_rows in by_galaxy.items()
        if len(galaxy_rows) == 5
        and all(row["Exists"] == "yes" for row in galaxy_rows)
        and all(row["GitTracked"] == "no" for row in galaxy_rows)
    ]
    return [
        {
            "GateID": "R2STAGE01",
            "Status": "primary_raw_inputs_staged_for_two_galaxies"
            if set(complete) >= {"NGC925", "NGC3031"}
            else "primary_raw_inputs_incomplete",
            "Galaxies": ";".join(sorted(complete)),
            "CanScoreNow": "no",
            "NextAction": "derive_component_arrays_under_frozen_protocol",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2STAGE02",
            "Status": "raw_inputs_not_git_tracked",
            "Galaxies": "NGC925;NGC3031",
            "CanScoreNow": "no",
            "NextAction": "keep_public_packet_to_urls_checksums_only",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report(rows: list[dict[str, str]], gates: list[dict[str, str]]) -> None:
    total_size = sum(int(row["SizeBytes"]) for row in rows)
    lines = [
        "# THINGS Route 2 Primary Input Staging v0.1",
        "",
        "This packet stages the primary raw source products for NGC925 and NGC3031 outside the public reproducibility packet. It records URLs, local ignored paths, file sizes, and SHA256 checksums only.",
        "",
        f"- Staged files: {len(rows)}",
        f"- Total staged bytes: {total_size}",
        "- Raw files are under `data/raw/`, which is ignored by git.",
        "- No `W_tau_eff` score is computed here.",
        "",
        "## Gate",
        "",
    ]
    for row in gates:
        lines.append(f"- `{row['GateID']}`: {row['Status']} ({row['CanScoreNow']}).")
    lines.extend(["", "## Guardrail", "", f"`{GUARDRAIL}`", ""])
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [MANIFEST, GATE, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_route2_primary_input_staging_status"] = (
        "NGC925_NGC3031_raw_inputs_staged_ignored_no_scores"
    )
    manifest["paper2_next_gate"] = "route2_component_array_derivation_for_NGC925_NGC3031"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = stage_inputs()
    gates = gate_rows(rows)
    write_csv(
        MANIFEST,
        rows,
        [
            "GalaxyName",
            "SourceRole",
            "Use",
            "URL",
            "LocalIgnoredPath",
            "SizeBytes",
            "SHA256",
            "Exists",
            "GitTracked",
            "RedistributionPolicy",
            "Guardrail",
        ],
    )
    write_csv(
        GATE,
        gates,
        ["GateID", "Status", "Galaxies", "CanScoreNow", "NextAction", "Guardrail"],
    )
    write_report(rows, gates)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
