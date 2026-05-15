#!/usr/bin/env python3
"""Audit published mass-model recovery options for missing THINGS rows."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from make_packet_v01_seed import PACKET, write_csv


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "things_mass_model_recovery_sources_v01"

AUDIT_OUT = PACKET / "things_published_mass_model_recovery_audit_v02.csv"
SOURCE_OUT = PACKET / "things_published_mass_model_source_manifest_v02.csv"
DECISION_OUT = PACKET / "things_published_mass_model_recovery_decision_v02.csv"
REPORT = PACKET / "things_published_mass_model_recovery_v02.md"

MISSING = ["NGC925", "NGC3031", "NGC3621", "NGC3627", "NGC4736"]
GUARDRAIL = "published_mass_model_recovery_no_synthetic_columns_no_scores"

SOURCES = [
    {
        "SourceID": "SPARC_ROTMOD_LTG",
        "Description": "SPARC Newtonian mass-model rotmod archive",
        "URL": "https://astroweb.case.edu/SPARC/Rotmod_LTG.zip",
        "LocalPath": RAW / "Rotmod_LTG.zip",
        "ExpectedUse": "machine_per_radius_R_Vobs_eVobs_Vgas_Vdisk_Vbul_if_galaxy_present",
    },
    {
        "SourceID": "SPARC_TABLE2_MRT",
        "Description": "SPARC machine-readable mass-model table",
        "URL": "https://astroweb.case.edu/SPARC/MassModels_Lelli2016c.mrt",
        "LocalPath": RAW / "MassModels_Lelli2016c.mrt",
        "ExpectedUse": "machine_mass_model_summary_and_per_radius_status_check",
    },
    {
        "SourceID": "SPARC_MASS_MODEL_FIGURES",
        "Description": "SPARC mass-model figure archive",
        "URL": "https://astroweb.case.edu/SPARC/MassModels_LTG.zip",
        "LocalPath": RAW / "MassModels_LTG.zip",
        "ExpectedUse": "figure_presence_only_not_machine_columns",
    },
    {
        "SourceID": "DEBLOK2008_ARXIV_SOURCE",
        "Description": "de Blok et al. 2008 THINGS arXiv source package",
        "URL": "https://arxiv.org/e-print/0810.2100",
        "LocalPath": Path("/tmp/things_deblok_source/deblok_astroph.tex"),
        "ExpectedUse": "method_global_fit_tables_geometry_ML_policy_but_not_machine_per_radius_columns",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_manifest_rows() -> list[dict[str, str]]:
    rows = []
    for source in SOURCES:
        path = source["LocalPath"]
        rows.append(
            {
                "SourceID": source["SourceID"],
                "Description": source["Description"],
                "URL": source["URL"],
                "LocalRawPath": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                "Exists": "yes" if path.exists() else "no",
                "SizeBytes": str(path.stat().st_size) if path.exists() else "",
                "SHA256": sha256(path) if path.exists() and path.is_file() else "",
                "ExpectedUse": source["ExpectedUse"],
                "RedistributionPolicy": "raw_source_not_tracked_manifest_only",
                "Guardrail": GUARDRAIL,
            }
        )
    return rows


def zip_names(path: Path) -> list[str]:
    if not path.exists():
        return []
    with zipfile.ZipFile(path) as handle:
        return handle.namelist()


def text_contains(path: Path, galaxy: str) -> bool:
    if not path.exists() or not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")
    variants = {galaxy, galaxy.replace("NGC", "NGC "), galaxy.replace("NGC", "NGC_")}
    return any(variant in text for variant in variants)


def audit_rows() -> list[dict[str, str]]:
    rotmod_names = zip_names(RAW / "Rotmod_LTG.zip")
    figure_names = zip_names(RAW / "MassModels_LTG.zip")
    table_path = RAW / "MassModels_Lelli2016c.mrt"
    deblok_path = Path("/tmp/things_deblok_source/deblok_astroph.tex")
    rows = []
    for galaxy in MISSING:
        rotmod_hits = [name for name in rotmod_names if galaxy.lower() in name.lower()]
        figure_hits = [name for name in figure_names if galaxy.lower() in name.lower()]
        table_hit = text_contains(table_path, galaxy)
        deblok_hit = text_contains(deblok_path, galaxy)
        direct_available = bool(rotmod_hits) or table_hit
        rows.append(
            {
                "GalaxyName": galaxy,
                "SparcRotmodMachineColumns": "present" if rotmod_hits else "absent",
                "SparcRotmodHits": ";".join(rotmod_hits),
                "SparcTable2MachineEntry": "present" if table_hit else "absent",
                "SparcMassModelFigure": "present" if figure_hits else "absent",
                "DeblokArxivSourceMentionsGalaxy": "yes" if deblok_hit else "no",
                "RecoveredScoreReadyColumns": "yes" if direct_available else "no",
                "RequiredColumns": "R;Vobs;eVobs;Vgas;Vdisk;Vbul_or_frozen_zero_bulge",
                "RecoveryStatus": "score_ready_machine_columns_recovered"
                if direct_available
                else "published_machine_columns_not_recovered",
                "AllowedNextUse": "score_ready_input"
                if direct_available
                else "source_status_audit_only",
                "ForbiddenUse": "extract_numeric_columns_from_plots_or_tune_reconstruction_to_score",
                "Guardrail": GUARDRAIL,
            }
        )
    return rows


def decision_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    recovered = [row["GalaxyName"] for row in rows if row["RecoveredScoreReadyColumns"] == "yes"]
    return [
        {
            "DecisionID": "TPMMR02D01",
            "Decision": "published_machine_mass_model_recovery",
            "Status": "insufficient_for_THINGS_N15"
            if len(recovered) < 2
            else "sufficient_for_THINGS_N15_candidate_scoring",
            "Evidence": f"score_ready_recovered={len(recovered)}",
            "RecoveredGalaxies": ";".join(recovered),
            "Blocks": "THINGS_missing_galaxy_W_tau_eff_scoring"
            if len(recovered) < 2
            else "",
            "NextAction": "contact_authors_or_search_supplementary_archives_for_original_ROTMod_tables"
            if len(recovered) < 2
            else "stage_recovered_columns_and_score_under_frozen_protocol",
            "Guardrail": GUARDRAIL,
        },
        {
            "DecisionID": "TPMMR02D02",
            "Decision": "route2_policy",
            "Status": "keep_route2_blocked_no_synthetic_mass_models",
            "Evidence": "official_SPARC_and_deBlok_sources_do_not_expose_missing_per_radius_columns",
            "RecoveredGalaxies": ";".join(recovered),
            "Blocks": "velocity_solver_shortcut",
            "NextAction": "do_not_score_NGC925_NGC3031_from_plots_or_unvalidated_photometry",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report(
    manifest: list[dict[str, str]],
    audit: list[dict[str, str]],
    decisions: list[dict[str, str]],
) -> None:
    lines = [
        "# THINGS Published Mass-Model Recovery Audit v0.2",
        "",
        "This audit rechecks whether published machine-readable mass-model columns can be recovered for the missing THINGS Table 3 galaxies. It explicitly separates official machine-readable tables from figures, paper text, and reconstruction inputs.",
        "",
        "## Sources Checked",
        "",
    ]
    for row in manifest:
        lines.append(
            f"- `{row['SourceID']}`: exists={row['Exists']}, size={row['SizeBytes']}, use={row['ExpectedUse']}."
        )
    lines.extend(["", "## Recovery Results", ""])
    for row in audit:
        lines.append(
            f"- `{row['GalaxyName']}`: SPARC rotmod={row['SparcRotmodMachineColumns']}, SPARC Table2={row['SparcTable2MachineEntry']}, deBlok source mention={row['DeblokArxivSourceMentionsGalaxy']}, recovered={row['RecoveredScoreReadyColumns']}."
        )
    lines.extend(["", "## Decision", ""])
    for row in decisions:
        lines.append(
            f"- `{row['DecisionID']}`: {row['Status']} ({row['Evidence']})."
        )
    lines.extend(
        [
            "",
            "Conclusion: the published machine-readable route still does not recover score-ready `R,Vobs,eVobs,Vgas,Vdisk,Vbul` rows for at least two of the missing galaxies. The route remains blocked unless original ROTMOD-style tables are obtained from an author/supplementary archive or another citable machine-readable source.",
            "",
            "No synthetic mass-model columns are created here.",
            "No `W_tau_eff` score is computed here.",
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
    for path in [AUDIT_OUT, SOURCE_OUT, DECISION_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_published_mass_model_recovery_v02_status"] = (
        "official_machine_sources_checked_missing_columns_not_recovered_no_scores"
    )
    manifest["paper2_next_gate"] = (
        "route2_contact_authors_or_find_supplementary_rotmod_tables"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    manifest = source_manifest_rows()
    audit = audit_rows()
    decisions = decision_rows(audit)
    write_csv(
        SOURCE_OUT,
        manifest,
        [
            "SourceID",
            "Description",
            "URL",
            "LocalRawPath",
            "Exists",
            "SizeBytes",
            "SHA256",
            "ExpectedUse",
            "RedistributionPolicy",
            "Guardrail",
        ],
    )
    write_csv(
        AUDIT_OUT,
        audit,
        [
            "GalaxyName",
            "SparcRotmodMachineColumns",
            "SparcRotmodHits",
            "SparcTable2MachineEntry",
            "SparcMassModelFigure",
            "DeblokArxivSourceMentionsGalaxy",
            "RecoveredScoreReadyColumns",
            "RequiredColumns",
            "RecoveryStatus",
            "AllowedNextUse",
            "ForbiddenUse",
            "Guardrail",
        ],
    )
    write_csv(
        DECISION_OUT,
        decisions,
        [
            "DecisionID",
            "Decision",
            "Status",
            "Evidence",
            "RecoveredGalaxies",
            "Blocks",
            "NextAction",
            "Guardrail",
        ],
    )
    write_report(manifest, audit, decisions)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
