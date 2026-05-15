#!/usr/bin/env python3
"""Download structured external-source metadata for Paper 2 validation expansion."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from make_packet_v01_seed import PACKET, write_csv


ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = ROOT / "data/raw/external_validation_sources_v01"

DOWNLOAD_MANIFEST = PACKET / "external_source_download_manifest_v01.csv"
HALOGAS_INDEX = PACKET / "halogas_zenodo_file_index_v01.csv"
REPORT = PACKET / "external_source_download_manifest_v01.md"

GUARDRAIL = "raw_downloads_local_only_public_packet_derived_index_only"

SOURCES = [
    {
        "SourceID": "SRC01",
        "Family": "THINGS harmonic controls",
        "URL": "https://arxiv.org/abs/0810.2116",
        "LocalPath": "things/trachternach_2008_arxiv_abs.html",
        "Kind": "html",
    },
    {
        "SourceID": "SRC01",
        "Family": "THINGS harmonic controls",
        "URL": "https://arxiv.org/pdf/0810.2116",
        "LocalPath": "things/trachternach_2008_arxiv.pdf",
        "Kind": "pdf",
    },
    {
        "SourceID": "SRC02",
        "Family": "LITTLE THINGS pressure-support controls",
        "URL": "https://science.nrao.edu/science/surveys/littlethings/data",
        "LocalPath": "littlethings/nrao_littlethings_data.html",
        "Kind": "html",
    },
    {
        "SourceID": "SRC03",
        "Family": "HALOGAS linewidth/cube stress",
        "URL": "https://zenodo.org/api/records/2552349",
        "LocalPath": "halogas/zenodo_2552349_record.json",
        "Kind": "json",
    },
    {
        "SourceID": "SRC03",
        "Family": "HALOGAS linewidth/cube stress",
        "URL": "https://www.astron.nl/halogas/data.php",
        "LocalPath": "halogas/astron_halogas_data.html",
        "Kind": "html",
    },
    {
        "SourceID": "SRC04",
        "Family": "non-WHISP resolved HI asymmetry",
        "URL": "https://doi.org/10.1093/mnras/staa597",
        "LocalPath": "non_whisp_asymmetry/reynolds_2020_doi_landing.html",
        "Kind": "html",
    },
    {
        "SourceID": "SRC05",
        "Family": "SPARC metadata",
        "URL": "https://astroweb.cwru.edu/SPARC/",
        "LocalPath": "sparc/sparc_home.html",
        "Kind": "html",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, path: Path) -> tuple[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "curl",
        "-L",
        "--fail",
        "--retry",
        "3",
        "--connect-timeout",
        "20",
        "--max-time",
        "180",
        "-A",
        "sparc-paper2-validation-downloader/0.1",
        "-o",
        str(path),
        url,
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return "failed", result.stderr.strip().replace("\n", " ")[:500]
    return "downloaded", ""


def download_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source in SOURCES:
        local = RAW_ROOT / source["LocalPath"]
        status, error = download(source["URL"], local)
        exists = local.exists()
        rows.append(
            {
                "SourceID": source["SourceID"],
                "Family": source["Family"],
                "Kind": source["Kind"],
                "URL": source["URL"],
                "LocalRawPath": str(local.relative_to(ROOT)),
                "Status": status,
                "Bytes": str(local.stat().st_size) if exists else "0",
                "SHA256": sha256(local) if exists else "",
                "Hostname": urlparse(source["URL"]).netloc,
                "PublicPacketUse": "derived_index_only",
                "Error": error,
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def halogas_rows() -> list[dict[str, str]]:
    record_path = RAW_ROOT / "halogas/zenodo_2552349_record.json"
    if not record_path.exists():
        return []
    record = json.loads(record_path.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for file_info in record.get("files", []):
        key = file_info.get("key", "")
        links = file_info.get("links", {})
        checksum = file_info.get("checksum", "")
        rows.append(
            {
                "FileName": key,
                "Bytes": str(file_info.get("size", "")),
                "Checksum": checksum,
                "DownloadURL": links.get("self", ""),
                "CandidateSPARCOverlap": candidate_overlap_from_name(key),
                "SuggestedUse": suggested_use_from_name(key),
                "RedistributionPolicy": "do_not_commit_raw_file_commit_derived_summary_only",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def candidate_overlap_from_name(name: str) -> str:
    upper = name.upper().replace(" ", "")
    candidates = ["NGC2403", "NGC3198", "NGC4559", "NGC5055", "NGC5585"]
    hits = [candidate for candidate in candidates if candidate in upper]
    return ";".join(hits)


def suggested_use_from_name(name: str) -> str:
    lower = name.lower()
    if "cube" in lower:
        return "optional_local_cube_stress_derivation"
    if "mom2" in lower:
        return "linewidth_or_dispersion_proxy"
    if "mom1" in lower:
        return "velocity_field_context"
    if "mom0" in lower or "coldens" in lower:
        return "hi_distribution_context"
    return "metadata_or_auxiliary"


def write_report(downloads: list[dict[str, str]], halogas: list[dict[str, str]]) -> None:
    ok = [row for row in downloads if row["Status"] == "downloaded"]
    failed = [row for row in downloads if row["Status"] != "downloaded"]
    candidate_halogas = [row for row in halogas if row["CandidateSPARCOverlap"]]
    lines = [
        "# External Source Download Manifest v0.1",
        "",
        "This packet records structured local downloads for the external-validation expansion. Raw downloaded files are stored under `data/raw/` and are intentionally excluded from git. The public packet contains only derived manifests and indexes.",
        "",
        "## Download Summary",
        "",
        f"- Sources attempted: {len(downloads)}",
        f"- Sources downloaded: {len(ok)}",
        f"- Sources failed: {len(failed)}",
        f"- HALOGAS indexed files: {len(halogas)}",
        f"- HALOGAS files matching candidate SPARC overlap names: {len(candidate_halogas)}",
        "",
        "## Next Step",
        "",
        "Use the local source files to build alias crossmatch tables before downloading large raw cubes. Large FITS products should remain local unless a specific derived summary requires them.",
        "",
        "## Generated Files",
        "",
        "- `external_source_download_manifest_v01.csv`",
        "- `halogas_zenodo_file_index_v01.csv`",
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
    for path in [DOWNLOAD_MANIFEST, HALOGAS_INDEX, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["external_source_download_manifest_status"] = (
        "source_metadata_downloaded_raw_files_local_only"
    )
    manifest["paper2_next_gate"] = "source_alias_crossmatch_before_large_cube_downloads"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    downloads = download_rows()
    halogas = halogas_rows()
    download_fields = [
        "SourceID",
        "Family",
        "Kind",
        "URL",
        "LocalRawPath",
        "Status",
        "Bytes",
        "SHA256",
        "Hostname",
        "PublicPacketUse",
        "Error",
        "InterpretationGuardrail",
    ]
    halogas_fields = [
        "FileName",
        "Bytes",
        "Checksum",
        "DownloadURL",
        "CandidateSPARCOverlap",
        "SuggestedUse",
        "RedistributionPolicy",
        "InterpretationGuardrail",
    ]
    write_csv(DOWNLOAD_MANIFEST, downloads, download_fields)
    write_csv(HALOGAS_INDEX, halogas, halogas_fields)
    write_report(downloads, halogas)
    update_manifest()


if __name__ == "__main__":
    main()
