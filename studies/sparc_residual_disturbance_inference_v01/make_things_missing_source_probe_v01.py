#!/usr/bin/env python3
"""Record source-probe outcomes for the missing THINGS mass-model rows."""

from __future__ import annotations

import json
from pathlib import Path

from make_packet_v01_seed import PACKET, write_csv


PROBE_OUT = PACKET / "things_missing_mass_model_source_probe_v01.csv"
DECISION_OUT = PACKET / "things_missing_mass_model_source_probe_decision_v01.csv"
REPORT = PACKET / "things_missing_mass_model_source_probe_v01.md"


MISSING = "NGC925;NGC3031;NGC3621;NGC3627;NGC4736"
GUARDRAIL = "source_probe_no_raw_data_redistribution_no_synthetic_mass_models"


def probe_rows() -> list[dict[str, str]]:
    return [
        {
            "SourceID": "SPARC_ROTMod_LTG",
            "SourceName": "SPARC Rotmod_LTG.zip",
            "URL": "https://astroweb.cwru.edu/SPARC/Rotmod_LTG.zip",
            "ProbeResult": "no_missing_five_found",
            "RelevantRows": "",
            "UsableForWtauEff": "no",
            "Reason": "the public SPARC LTG rotmod archive does not contain NGC925, NGC3031, NGC3621, NGC3627, or NGC4736",
            "NextUse": "negative_source_audit_only",
            "Guardrail": GUARDRAIL,
        },
        {
            "SourceID": "SPARC_TABLE2_MRT",
            "SourceName": "SPARC MassModels_Lelli2016c.mrt",
            "URL": "https://astroweb.cwru.edu/SPARC/MassModels_Lelli2016c.mrt",
            "ProbeResult": "no_missing_five_found",
            "RelevantRows": "",
            "UsableForWtauEff": "no",
            "Reason": "the public SPARC machine-readable mass-model table does not list the missing THINGS rows",
            "NextUse": "negative_source_audit_only",
            "Guardrail": GUARDRAIL,
        },
        {
            "SourceID": "THINGS_DATA_PRODUCTS",
            "SourceName": "THINGS HI data products",
            "URL": "https://www2.mpia-hd.mpg.de/THINGS/Data.html",
            "ProbeResult": "hi_fits_products_exist_for_missing_five",
            "RelevantRows": MISSING,
            "UsableForWtauEff": "not_directly",
            "Reason": "HI moment maps and cubes are available, but W_tau_eff requires baryonic velocity components or a frozen mass-model reconstruction rule",
            "NextUse": "input_to_future_mass_model_pipeline_only",
            "Guardrail": GUARDRAIL,
        },
        {
            "SourceID": "DEBLOK2008_ARXIV_SOURCE",
            "SourceName": "de Blok et al. 2008 arXiv source",
            "URL": "https://arxiv.org/e-print/0810.2100",
            "ProbeResult": "tex_has_global_fit_tables_and_figures_not_machine_rotmod_columns",
            "RelevantRows": MISSING,
            "UsableForWtauEff": "not_directly",
            "Reason": "the source package documents the mass-model analysis but does not expose SPARC-style per-radius Vobs,Vgas,Vdisk,Vbul data tables for the missing rows",
            "NextUse": "citation_and_manual_recovery_candidate_only",
            "Guardrail": GUARDRAIL,
        },
    ]


def decision_rows() -> list[dict[str, str]]:
    return [
        {
            "DecisionID": "TMSP01",
            "Status": "SPARC_public_rotmod_does_not_resolve_missing_five",
            "RequiredForN15": "at_least_two_public_per_radius_baryonic_mass_models",
            "AllowedNextAction": "recover_published_mass_model_tables_or_build_frozen_reconstruction_pipeline",
            "ForbiddenAction": "claim_THINGS_N15_or_score_from_rotation_curve_only",
        },
        {
            "DecisionID": "TMSP02",
            "Status": "THINGS_HI_products_are_available_but_not_score_ready",
            "RequiredForN15": "Vobs_Vgas_Vdisk_Vbul_or_frozen_equivalent",
            "AllowedNextAction": "treat_THINGS_FITS_as_future_pipeline_inputs",
            "ForbiddenAction": "mix_HI_FITS_with_unfrozen_stellar_model",
        },
    ]


def write_report(rows: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lines = [
        "# THINGS Missing Mass-Model Source Probe v0.1",
        "",
        "This probe records the source-level status for the five unresolved THINGS Table 3 galaxies: NGC925, NGC3031, NGC3621, NGC3627, and NGC4736.",
        "",
        "## Result",
        "",
        "The public SPARC LTG rotmod archive and SPARC machine-readable mass-model table do not resolve the missing five. The THINGS data page provides HI FITS products for the missing galaxies, but those products are not direct `W_tau_eff` inputs because the score requires baryonic velocity components or a frozen mass-model reconstruction rule.",
        "",
        "## Current Gate",
        "",
        "THINGS can move from N=13 to N>=15 only after at least two missing galaxies receive public per-radius baryonic mass-model columns (`Vobs`, `Vgas`, `Vdisk`, `Vbul`) or a committed equivalent reconstruction rule.",
        "",
        "## Source Probe Table",
        "",
    ]
    for row in rows:
        lines.append(
            f"- `{row['SourceID']}`: {row['ProbeResult']} ({row['UsableForWtauEff']})."
        )
    lines.extend(
        [
            "",
            "## Decisions",
            "",
        ]
    )
    for row in decisions:
        lines.append(f"- `{row['DecisionID']}`: {row['Status']}.")
    lines.extend(
        [
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
    for path in [PROBE_OUT, DECISION_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_missing_mass_model_source_probe_status"] = (
        "SPARC_negative_THINGS_HI_available_but_not_score_ready"
    )
    manifest["paper2_next_gate"] = (
        "recover_two_public_THINGS_baryonic_mass_models_or_build_frozen_reconstruction_pipeline"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = probe_rows()
    decisions = decision_rows()
    write_csv(
        PROBE_OUT,
        rows,
        [
            "SourceID",
            "SourceName",
            "URL",
            "ProbeResult",
            "RelevantRows",
            "UsableForWtauEff",
            "Reason",
            "NextUse",
            "Guardrail",
        ],
    )
    write_csv(
        DECISION_OUT,
        decisions,
        [
            "DecisionID",
            "Status",
            "RequiredForN15",
            "AllowedNextAction",
            "ForbiddenAction",
        ],
    )
    write_report(rows, decisions)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
