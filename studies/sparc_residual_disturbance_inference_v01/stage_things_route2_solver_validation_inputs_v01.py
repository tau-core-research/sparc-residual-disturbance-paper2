#!/usr/bin/env python3
"""Stage raw inputs for the THINGS route 2 solver validation gate."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from urllib.request import urlopen

from make_packet_v01_seed import PACKET, write_csv


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "things_route2_solver_validation_inputs_v01"
MANIFEST = PACKET / "things_route2_solver_validation_input_staging_manifest_v01.csv"
GATE = PACKET / "things_route2_solver_validation_input_staging_gate_v01.csv"
REPORT = PACKET / "things_route2_solver_validation_input_staging_v01.md"

GUARDRAIL = "route2_solver_validation_inputs_staged_raw_ignored_no_scores"

PRODUCTS = [
    (
        "NGC2403",
        "THINGS_HI_MOM0_NA",
        "NGC_2403_NA_MOM0_THINGS.FITS",
        "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_2403_NA_MOM0_THINGS.FITS",
        "validation_gas_surface_density_candidate",
    ),
    (
        "NGC2403",
        "SINGS_IRAC1_3P6UM",
        "ngc2403_v7.phot.1.fits",
        "https://irsa.ipac.caltech.edu/data/SPITZER/SINGS/galaxies/ngc2403/IRAC/ngc2403_v7.phot.1.fits",
        "validation_stellar_3p6um_candidate",
    ),
    (
        "NGC3198",
        "THINGS_HI_MOM0_NA",
        "NGC_3198_NA_MOM0_THINGS.FITS",
        "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_3198_NA_MOM0_THINGS.FITS",
        "validation_gas_surface_density_candidate",
    ),
    (
        "NGC3198",
        "SINGS_IRAC1_3P6UM",
        "ngc3198_v7.phot.1.fits",
        "https://irsa.ipac.caltech.edu/data/SPITZER/SINGS/galaxies/ngc3198/IRAC/ngc3198_v7.phot.1.fits",
        "validation_stellar_3p6um_candidate",
    ),
    (
        "NGC5055",
        "THINGS_HI_MOM0_NA",
        "NGC_5055_NA_MOM0_THINGS.FITS",
        "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_5055_NA_MOM0_THINGS.FITS",
        "validation_gas_surface_density_candidate",
    ),
    (
        "NGC5055",
        "SINGS_IRAC1_3P6UM",
        "ngc5055_v7.phot.1.fits",
        "https://irsa.ipac.caltech.edu/data/SPITZER/SINGS/galaxies/ngc5055/IRAC/ngc5055_v7.phot.1.fits",
        "validation_stellar_3p6um_candidate",
    ),
]


def download(url: str, path: Path) -> None:
    if path.exists() and path.stat().st_size > 0:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with urlopen(url, timeout=180) as response, tmp.open("wb") as handle:
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
                "ValidationUse": "solver_reconstruction_accuracy_only_not_tau_endpoint",
                "CanScoreMissingGalaxiesNow": "no",
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
        if {row["SourceRole"] for row in galaxy_rows}
        == {"THINGS_HI_MOM0_NA", "SINGS_IRAC1_3P6UM"}
        and all(row["Exists"] == "yes" for row in galaxy_rows)
        and all(row["GitTracked"] == "no" for row in galaxy_rows)
    ]
    pass_minimum = len(complete) >= 3
    return [
        {
            "GateID": "R2VALSTAGE01",
            "Status": "validation_raw_inputs_staged_for_three_overlap_galaxies"
            if pass_minimum
            else "validation_raw_inputs_incomplete",
            "Galaxies": ";".join(sorted(complete)),
            "NCompleteGalaxies": str(len(complete)),
            "CanValidateSolverNow": "yes" if pass_minimum else "no",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "derive_blind_component_profiles_and_compare_to_SPARC_reference",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2VALSTAGE02",
            "Status": "validation_raw_inputs_not_git_tracked",
            "Galaxies": ";".join(sorted(complete)),
            "NCompleteGalaxies": str(len(complete)),
            "CanValidateSolverNow": "yes" if pass_minimum else "no",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "keep_public_packet_to_urls_checksums_only",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report(rows: list[dict[str, str]], gates: list[dict[str, str]]) -> None:
    total_size = sum(int(row["SizeBytes"]) for row in rows)
    lines = [
        "# THINGS Route 2 Solver Validation Input Staging v0.1",
        "",
        "This packet stages the raw source products needed for the first solver-validation pass. Raw files remain outside git; the public packet stores source URLs, sizes, and SHA256 checksums only.",
        "",
        f"- Staged files: {len(rows)}",
        f"- Total staged bytes: {total_size}",
        "- Validation galaxies: `NGC2403`, `NGC3198`, `NGC5055`.",
        "- Required products per galaxy: THINGS NA MOM0 and SINGS IRAC1 3.6 micron image.",
        "- No missing-galaxy score is computed here.",
        "- No `W_tau_eff` endpoint is opened here.",
        "",
        "## Gate",
        "",
    ]
    for row in gates:
        lines.append(
            f"- `{row['GateID']}`: {row['Status']} / validate={row['CanValidateSolverNow']} / score={row['CanScoreMissingGalaxiesNow']}."
        )
    lines.extend(["", "## Guardrail", "", f"`{GUARDRAIL}`", ""])
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [MANIFEST, GATE, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_route2_solver_validation_input_staging_status"] = (
        "three_overlap_validation_raw_inputs_staged_ignored_no_scores"
    )
    manifest["paper2_next_gate"] = (
        "route2_blind_component_profile_derivation_validation_against_sparc_reference"
    )
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
            "ValidationUse",
            "CanScoreMissingGalaxiesNow",
            "Guardrail",
        ],
    )
    write_csv(
        GATE,
        gates,
        [
            "GateID",
            "Status",
            "Galaxies",
            "NCompleteGalaxies",
            "CanValidateSolverNow",
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
