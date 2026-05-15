#!/usr/bin/env python3
"""Audit Yu et al. 2022 ALFALFA profile-asymmetry coverage."""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

from make_packet_v01_seed import PACKET, read_csv, write_csv


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/external_validation_sources_v01/yu2022_alfalfa_vizier"
ROT_DIR = Path("/Users/jolcsak/Projects/tau-core/data/sparc/Rotmod_LTG")

README_URL = "https://cdsarc.cds.unistra.fr/ftp/J/ApJS/261/21/ReadMe"
TABLE2_URL = "https://cdsarc.cds.unistra.fr/ftp/J/ApJS/261/21/table2.dat.gz"
README_RAW = RAW / "ReadMe.txt"
TABLE2_GZ = RAW / "table2.dat.gz"
TABLE2_RAW = RAW / "table2.dat"

W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"

MANIFEST_OUT = PACKET / "yu2022_alfalfa_download_manifest_v01.csv"
CATALOG_OUT = PACKET / "yu2022_alfalfa_profile_asymmetry_catalog_v01.csv"
COVERAGE_OUT = PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_v01.csv"
SUMMARY_OUT = PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_summary_v01.csv"
DECISION_OUT = PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_decision_v01.csv"
REPORT = PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_v01.md"

GUARDRAIL = "yu2022_alfalfa_coverage_no_directional_readout"


def ensure_downloads() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    if not README_RAW.exists():
        with urlopen(README_URL, timeout=90) as response:
            README_RAW.write_bytes(response.read())
    if not TABLE2_GZ.exists():
        with urlopen(TABLE2_URL, timeout=90) as response:
            TABLE2_GZ.write_bytes(response.read())
    if not TABLE2_RAW.exists():
        TABLE2_RAW.write_bytes(gzip.decompress(TABLE2_GZ.read_bytes()))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_table2_line(line: str) -> dict[str, str]:
    agc = line[4:10].strip()
    agc_num = int(agc)
    canonical = "UGC" + str(agc_num).zfill(5) if agc_num < 100000 else ""
    return {
        "AGC": agc,
        "CanonicalSPARCNameCandidate": canonical,
        "RAdeg": line[11:20].strip(),
        "DEdeg": line[21:29].strip(),
        "DistMpc": line[30:35].strip(),
        "e_DistMpc": line[36:40].strip(),
        "VcKms": line[41:46].strip(),
        "HIflux": line[50:57].strip(),
        "W85": line[66:74].strip(),
        "Af": line[79:83].strip(),
        "e_Af": line[84:88].strip(),
        "Ac": line[89:94].strip(),
        "e_Ac": line[95:100].strip(),
        "Cv": line[101:106].strip(),
        "K": line[112:118].strip(),
        "SN": line[125:132].strip(),
        "logMHI": line[138:143].strip(),
        "Notes": line[149:158].strip(),
        "Source": "Yu_etal_2022_VizieR_J_ApJS_261_21_table2",
        "AllowedUse": "global_HI_profile_asymmetry_proxy_only",
        "InterpretationGuardrail": GUARDRAIL,
    }


def catalog_rows() -> list[dict[str, str]]:
    return [
        parse_table2_line(line)
        for line in TABLE2_RAW.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def manifest_rows() -> list[dict[str, str]]:
    rows = []
    for filename, url, path in [
        ("ReadMe.txt", README_URL, README_RAW),
        ("table2.dat.gz", TABLE2_URL, TABLE2_GZ),
        ("table2.dat", "derived_from_table2.dat.gz", TABLE2_RAW),
    ]:
        rows.append(
            {
                "FileName": filename,
                "LocalRawPath": str(path.relative_to(ROOT)),
                "Status": "downloaded" if path.exists() else "missing",
                "Bytes": str(path.stat().st_size) if path.exists() else "0",
                "SHA256": sha256(path) if path.exists() else "",
                "SourceURL": url,
                "PublicPacketUse": "derived_catalog_and_coverage_only",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def coverage_rows(catalog: list[dict[str, str]]) -> list[dict[str, str]]:
    w_tau = {row["GalaxyName"]: row for row in read_csv(W_TAU)}
    rotmods = {path.stem.replace("_rotmod", ""): path for path in ROT_DIR.glob("*_rotmod.dat")}
    rows = []
    for row in catalog:
        canonical = row["CanonicalSPARCNameCandidate"]
        in_seed = canonical in w_tau
        has_rotmod = canonical in rotmods
        if not (in_seed or has_rotmod):
            continue
        rows.append(
            {
                **row,
                "InWTauEffSeed": "yes" if in_seed else "no",
                "Class": w_tau[canonical]["Class"] if in_seed else "",
                "W_tau_eff_candidate_score_v01": (
                    w_tau[canonical]["W_tau_eff_candidate_score_v01"] if in_seed else ""
                ),
                "HasLocalSparcRotmod": "yes" if has_rotmod else "no",
                "LocalRotmodPath": str(rotmods[canonical]) if has_rotmod else "",
                "ExpansionStatus": (
                    "existing_seed_overlap"
                    if in_seed
                    else "candidate_for_predeclared_seed_expansion"
                    if has_rotmod
                    else "not_expandable_without_rotmod"
                ),
                "ReadoutPermission": "coverage_only_no_directional_readout",
            }
        )
    return rows


def summary_rows(catalog: list[dict[str, str]], coverage: list[dict[str, str]]) -> list[dict[str, str]]:
    seed = [row for row in coverage if row["InWTauEffSeed"] == "yes"]
    rotmod = [row for row in coverage if row["HasLocalSparcRotmod"] == "yes"]
    expansion = [
        row
        for row in coverage
        if row["ExpansionStatus"] == "candidate_for_predeclared_seed_expansion"
    ]
    return [
        {
            "Metric": "yu2022_catalog_rows",
            "N": str(len(catalog)),
            "Value": str(len(catalog)),
            "SecondaryValue": "ALFALFA_table2",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "current_w_tau_eff_seed_overlap",
            "N": str(len(seed)),
            "Value": str(len(seed)),
            "SecondaryValue": ";".join(row["CanonicalSPARCNameCandidate"] for row in seed),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "local_sparc_rotmod_overlap",
            "N": str(len(rotmod)),
            "Value": str(len(rotmod)),
            "SecondaryValue": ";".join(row["CanonicalSPARCNameCandidate"] for row in rotmod),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "new_seed_expansion_candidates",
            "N": str(len(expansion)),
            "Value": str(len(expansion)),
            "SecondaryValue": ";".join(row["CanonicalSPARCNameCandidate"] for row in expansion),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "minimum_n_gate_after_potential_expansion",
            "N": str(len(rotmod)),
            "Value": "met" if len(rotmod) >= 15 else "not_met",
            "SecondaryValue": "requires_N_ge_15_before_directional_readout",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def decision_rows(summary: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in summary}
    return [
        {
            "DecisionID": "YU22D01",
            "Decision": "Yu2022_ALFALFA_profile_asymmetry_coverage",
            "Status": "promising_for_predeclared_seed_expansion",
            "Rationale": (
                "Current seed overlap="
                + lookup["current_w_tau_eff_seed_overlap"]["Value"]
                + "; local SPARC rotmod overlap="
                + lookup["local_sparc_rotmod_overlap"]["Value"]
                + "; potential expansion gate="
                + lookup["minimum_n_gate_after_potential_expansion"]["Value"]
                + "."
            ),
            "Blocks": "immediate_directional_readout",
            "NextAction": "freeze_yu2022_seed_expansion_queue_before_scoring",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "YU22D02",
            "Decision": "directional_readout_status",
            "Status": "closed",
            "Rationale": "This packet is coverage-only and does not compare Af/Ac against W_tau_eff.",
            "Blocks": "ALFALFA_asymmetry_validation_claim",
            "NextAction": "predeclare_expansion_rule_and_minimum_rotmod_gate",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(summary: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in summary}
    lines = [
        "# Yu 2022 ALFALFA Profile-Asymmetry Coverage v0.1",
        "",
        "This packet ingests the Yu et al. (2022) ALFALFA integrated H I profile-asymmetry catalogue from VizieR and checks coverage against the current `W_tau_eff` seed and the locally available SPARC rotmod inventory. It is a coverage audit only.",
        "",
        "## Result",
        "",
        f"- Yu et al. catalogue rows: {lookup['yu2022_catalog_rows']['Value']}",
        f"- Current `W_tau_eff` seed overlap: {lookup['current_w_tau_eff_seed_overlap']['Value']}",
        f"- Local SPARC rotmod overlap: {lookup['local_sparc_rotmod_overlap']['Value']}",
        f"- New seed-expansion candidates: {lookup['new_seed_expansion_candidates']['Value']}",
        f"- Potential N>=15 gate after expansion: {lookup['minimum_n_gate_after_potential_expansion']['Value']}",
        "",
        "## Decision",
        "",
        f"`{decisions[0]['Status']}`",
        "",
        decisions[0]["Rationale"],
        "",
        "Yu et al. (2022) is a stronger next external family than Reynolds for this repo because UGC/AGC naming gives a larger SPARC rotmod overlap. The next allowed step is to freeze the expansion rule before computing any expanded residual score.",
        "",
        "## Generated Files",
        "",
        "- `yu2022_alfalfa_download_manifest_v01.csv`",
        "- `yu2022_alfalfa_profile_asymmetry_catalog_v01.csv`",
        "- `yu2022_alfalfa_profile_asymmetry_coverage_v01.csv`",
        "- `yu2022_alfalfa_profile_asymmetry_coverage_summary_v01.csv`",
        "- `yu2022_alfalfa_profile_asymmetry_coverage_decision_v01.csv`",
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
    for path in [MANIFEST_OUT, CATALOG_OUT, COVERAGE_OUT, SUMMARY_OUT, DECISION_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["yu2022_alfalfa_coverage_status"] = (
        "promising_for_predeclared_seed_expansion_no_directional_readout"
    )
    manifest["paper2_next_gate"] = "freeze_yu2022_seed_expansion_queue_before_scoring"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    ensure_downloads()
    catalog = catalog_rows()
    coverage = coverage_rows(catalog)
    summary = summary_rows(catalog, coverage)
    decisions = decision_rows(summary)
    write_csv(
        MANIFEST_OUT,
        manifest_rows(),
        [
            "FileName",
            "LocalRawPath",
            "Status",
            "Bytes",
            "SHA256",
            "SourceURL",
            "PublicPacketUse",
            "InterpretationGuardrail",
        ],
    )
    catalog_fields = [
        "AGC",
        "CanonicalSPARCNameCandidate",
        "RAdeg",
        "DEdeg",
        "DistMpc",
        "e_DistMpc",
        "VcKms",
        "HIflux",
        "W85",
        "Af",
        "e_Af",
        "Ac",
        "e_Ac",
        "Cv",
        "K",
        "SN",
        "logMHI",
        "Notes",
        "Source",
        "AllowedUse",
        "InterpretationGuardrail",
    ]
    write_csv(CATALOG_OUT, catalog, catalog_fields)
    write_csv(
        COVERAGE_OUT,
        coverage,
        catalog_fields
        + [
            "InWTauEffSeed",
            "Class",
            "W_tau_eff_candidate_score_v01",
            "HasLocalSparcRotmod",
            "LocalRotmodPath",
            "ExpansionStatus",
            "ReadoutPermission",
        ],
    )
    write_csv(
        SUMMARY_OUT,
        summary,
        ["Metric", "N", "Value", "SecondaryValue", "InterpretationGuardrail"],
    )
    write_csv(
        DECISION_OUT,
        decisions,
        [
            "DecisionID",
            "Decision",
            "Status",
            "Rationale",
            "Blocks",
            "NextAction",
            "InterpretationGuardrail",
        ],
    )
    write_report(summary, decisions)
    update_manifest()


if __name__ == "__main__":
    main()
