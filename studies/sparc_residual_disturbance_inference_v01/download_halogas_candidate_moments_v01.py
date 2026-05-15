#!/usr/bin/env python3
"""Download HALOGAS candidate moment maps for local derived-feature work."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

from make_packet_v01_seed import PACKET, write_csv


ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = ROOT / "data/raw/external_validation_sources_v01/halogas/files"
INDEX = PACKET / "halogas_zenodo_file_index_v01.csv"
OUT = PACKET / "halogas_candidate_moment_downloads_v01.csv"
REPORT = PACKET / "halogas_candidate_moment_downloads_v01.md"

GUARDRAIL = "halogas_raw_fits_local_only_commit_derived_manifest_only"


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_index() -> list[dict[str, str]]:
    with INDEX.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [
        row
        for row in rows
        if row["CandidateSPARCOverlap"] and "cube" not in row["FileName"].lower()
    ]


def download(row: dict[str, str], path: Path) -> tuple[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    expected_md5 = row["Checksum"].replace("md5:", "")
    if path.exists() and md5(path) == expected_md5:
        return "already_present_verified", ""
    command = [
        "curl",
        "-L",
        "--fail",
        "--retry",
        "3",
        "--connect-timeout",
        "20",
        "--max-time",
        "300",
        "-A",
        "sparc-paper2-halogas-downloader/0.1",
        "-o",
        str(path),
        row["DownloadURL"],
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return "failed", result.stderr.strip().replace("\n", " ")[:500]
    actual = md5(path)
    if actual != expected_md5:
        return "downloaded_md5_mismatch", f"expected {expected_md5}; actual {actual}"
    return "downloaded_verified", ""


def download_rows() -> list[dict[str, str]]:
    outputs: list[dict[str, str]] = []
    for row in read_index():
        local = RAW_ROOT / row["FileName"]
        status, error = download(row, local)
        exists = local.exists()
        actual_md5 = md5(local) if exists else ""
        outputs.append(
            {
                "GalaxyName": row["CandidateSPARCOverlap"],
                "FileName": row["FileName"],
                "SuggestedUse": row["SuggestedUse"],
                "LocalRawPath": str(local.relative_to(ROOT)),
                "ExpectedBytes": row["Bytes"],
                "ActualBytes": str(local.stat().st_size) if exists else "0",
                "ExpectedChecksum": row["Checksum"],
                "ActualMD5": actual_md5,
                "Status": status,
                "Error": error,
                "PublicPacketUse": "derived_manifest_only",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return outputs


def write_report(rows: list[dict[str, str]]) -> None:
    verified = [
        row
        for row in rows
        if row["Status"] in {"downloaded_verified", "already_present_verified"}
    ]
    failed = [row for row in rows if row["Status"] not in {"downloaded_verified", "already_present_verified"}]
    galaxies = sorted({row["GalaxyName"] for row in verified})
    total_bytes = sum(int(row["ActualBytes"]) for row in verified)
    lines = [
        "# HALOGAS Candidate Moment Downloads v0.1",
        "",
        "This manifest records local downloads of HALOGAS candidate moment and column-density FITS files. Large cubes are intentionally excluded from this step. Raw FITS files remain under `data/raw/` and are not committed.",
        "",
        "## Summary",
        "",
        f"- Candidate non-cube files attempted: {len(rows)}",
        f"- Verified files: {len(verified)}",
        f"- Failed or mismatched files: {len(failed)}",
        f"- Verified galaxies: {';'.join(galaxies)}",
        f"- Verified bytes: {total_bytes}",
        "",
        "## Generated Files",
        "",
        "- `halogas_candidate_moment_downloads_v01.csv`",
        "",
        "## Guardrail",
        "",
        f"`{GUARDRAIL}`",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["halogas_candidate_moment_downloads_status"] = (
        "candidate_moment_maps_downloaded_and_md5_verified_local_raw_only"
    )
    manifest["paper2_next_gate"] = "source_alias_crossmatch_and_halogas_moment_feature_derivation"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = download_rows()
    fields = [
        "GalaxyName",
        "FileName",
        "SuggestedUse",
        "LocalRawPath",
        "ExpectedBytes",
        "ActualBytes",
        "ExpectedChecksum",
        "ActualMD5",
        "Status",
        "Error",
        "PublicPacketUse",
        "InterpretationGuardrail",
    ]
    write_csv(OUT, rows, fields)
    write_report(rows)
    update_manifest()


if __name__ == "__main__":
    main()
