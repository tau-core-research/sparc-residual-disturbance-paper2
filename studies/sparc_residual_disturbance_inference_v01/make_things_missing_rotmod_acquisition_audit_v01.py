#!/usr/bin/env python3
"""Audit acquisition options for missing THINGS Table 3 rotmod-like inputs."""

from __future__ import annotations

import json
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


TABLE3 = PACKET / "things_trachternach2008_table3_v01.csv"
SCORES = PACKET / "things_table3_expanded_w_tau_eff_scores_v01.csv"
AUDIT_OUT = PACKET / "things_missing_rotmod_acquisition_audit_v01.csv"
PLAN_OUT = PACKET / "things_missing_rotmod_acquisition_plan_v01.csv"
REPORT = PACKET / "things_missing_rotmod_acquisition_audit_v01.md"

GUARDRAIL = "things_missing_rotmod_acquisition_audit_no_synthetic_mass_model"


KNOWN_SOURCES = {
    "NGC925": {
        "LiteratureStatus": "THINGS rotation curve exists; compatible baryonic components not present locally",
        "PrimarySource": "de_Blok_etal_2008_THINGS_mass_models",
        "SourceURL": "https://arxiv.org/abs/0810.2100",
        "AcquisitionClass": "possible_if_THINGS_mass_model_tables_are_recovered",
        "Blocker": "need Vgas,Vdisk,Vbul or equivalent baryonic mass model on the rotation-curve grid",
    },
    "NGC3031": {
        "LiteratureStatus": "THINGS Table 3 object; no local SPARC rotmod and no recovered compatible mass-model table",
        "PrimarySource": "de_Blok_etal_2008_THINGS_mass_models",
        "SourceURL": "https://arxiv.org/abs/0810.2100",
        "AcquisitionClass": "possible_if_THINGS_mass_model_tables_are_recovered",
        "Blocker": "need compatible baryonic decomposition; do not infer from image data in this packet",
    },
    "NGC3621": {
        "LiteratureStatus": "external HI rotation-curve literature exists, including later MeerKAT work; no local SPARC rotmod",
        "PrimarySource": "MHONGOOSE_early_observations_NGC3621",
        "SourceURL": "https://academic.oup.com/mnras/article/482/1/1248/5132879",
        "AcquisitionClass": "possible_but_not_clean_THINGS_Table3_completion",
        "Blocker": "may require cross-survey mass-model reconstruction rather than direct SPARC-like rotmod ingestion",
    },
    "NGC3627": {
        "LiteratureStatus": "THINGS Table 3 object; no local SPARC rotmod and no recovered compatible mass-model table",
        "PrimarySource": "de_Blok_etal_2008_THINGS_mass_models",
        "SourceURL": "https://arxiv.org/abs/0810.2100",
        "AcquisitionClass": "possible_if_THINGS_mass_model_tables_are_recovered",
        "Blocker": "strong interaction/bar system; compatible baryonic decomposition needed before scoring",
    },
    "NGC4736": {
        "LiteratureStatus": "multiple rotation-curve sources exist; THINGS/global-disc comparisons exist, but no local SPARC rotmod",
        "PrimarySource": "de_Blok_etal_2008_and_other_NGC4736_rotation_curve_literature",
        "SourceURL": "https://arxiv.org/abs/0810.2100",
        "AcquisitionClass": "possible_but_high_systematics_risk",
        "Blocker": "ringed galaxy with multiple rotation-curve versions; avoid mixing non-SPARC baryonic model without a frozen conversion rule",
    },
}


def audit_rows() -> list[dict[str, str]]:
    scored = {row["GalaxyName"]: row for row in read_csv(SCORES)}
    rows = []
    for row in read_csv(TABLE3):
        galaxy = row["GalaxyName"]
        score = scored.get(galaxy, {})
        if score.get("W_tau_eff_score_resolved_v01", "") != "":
            status = "already_resolved"
        elif score.get("HasLocalSparcRotmod") == "no":
            status = "missing_local_sparc_rotmod"
        else:
            status = "unresolved_other"
        known = KNOWN_SOURCES.get(
            galaxy,
            {
                "LiteratureStatus": "",
                "PrimarySource": "",
                "SourceURL": "",
                "AcquisitionClass": "",
                "Blocker": "",
            },
        )
        rows.append(
            {
                "GalaxyName": galaxy,
                "PublishedName": row["PublishedName"],
                "CurrentStatus": status,
                "HasLocalSparcRotmod": score.get("HasLocalSparcRotmod", ""),
                "CurrentScoreStatus": score.get("ScoringStatus", ""),
                "LiteratureStatus": known["LiteratureStatus"],
                "PrimarySource": known["PrimarySource"],
                "SourceURL": known["SourceURL"],
                "AcquisitionClass": known["AcquisitionClass"],
                "Blocker": known["Blocker"],
                "AllowedNextUse": (
                    "score_only_if_public_mass_model_columns_are_recovered_and_conversion_rule_is_frozen"
                    if status == "missing_local_sparc_rotmod"
                    else "already_in_THINGS_control_readout"
                    if status == "already_resolved"
                    else "audit_only"
                ),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def plan_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    missing = [row for row in rows if row["CurrentStatus"] == "missing_local_sparc_rotmod"]
    possible = [
        row
        for row in missing
        if row["AcquisitionClass"]
        in {
            "possible_if_THINGS_mass_model_tables_are_recovered",
            "possible_but_not_clean_THINGS_Table3_completion",
            "possible_but_high_systematics_risk",
        }
    ]
    return [
        {
            "StepID": "TMA01",
            "Step": "recover_original_THINGS_mass_model_tables",
            "TargetGalaxies": ";".join(row["GalaxyName"] for row in missing),
            "MinimumSuccess": "at_least_two_missing_galaxies_with_Vobs_Vgas_Vdisk_Vbul",
            "AllowedAction": "download_or_transcribe_public_tables_only",
            "ForbiddenAction": "synthetic_baryonic_components_or_fit_to_W_tau_eff",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "StepID": "TMA02",
            "Step": "freeze_conversion_rule",
            "TargetGalaxies": ";".join(row["GalaxyName"] for row in possible),
            "MinimumSuccess": "document_units_radius_grid_and_ML_assumptions_before_scoring",
            "AllowedAction": "score_after_conversion_rule_is_committed",
            "ForbiddenAction": "score_first_then_decide_conversion",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "StepID": "TMA03",
            "Step": "fallback_if_mass_models_not_recovered",
            "TargetGalaxies": ";".join(row["GalaxyName"] for row in missing),
            "MinimumSuccess": "none",
            "AllowedAction": "keep_THINGS_at_N13_control_only_and_continue_non_WHISP_replication",
            "ForbiddenAction": "claim_THINGS_N15_validation",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(rows: list[dict[str, str]], plan: list[dict[str, str]]) -> None:
    missing = [row for row in rows if row["CurrentStatus"] == "missing_local_sparc_rotmod"]
    resolved = [row for row in rows if row["CurrentStatus"] == "already_resolved"]
    lines = [
        "# THINGS Missing Rotmod Acquisition Audit v0.1",
        "",
        "This packet audits whether the remaining THINGS Table 3 galaxies can be added to the expanded `W_tau_eff` control readout. It does not create synthetic mass models and does not score galaxies without compatible baryonic components.",
        "",
        "## Current State",
        "",
        f"- THINGS Table 3 rows: {len(rows)}",
        f"- Currently resolved with `W_tau_eff`: {len(resolved)}",
        f"- Missing local SPARC-like rotmod inputs: {len(missing)}",
        f"- Missing galaxies: {', '.join(row['GalaxyName'] for row in missing)}",
        "",
        "## Finding",
        "",
        "THINGS can only be pushed from N=13 to N>=15 if at least two of the missing galaxies receive public, compatible mass-model columns (`Vobs`, `Vgas`, `Vdisk`, `Vbul` or an explicitly frozen equivalent). Published rotation curves alone are insufficient for the current `W_tau_eff` score, because the score depends on the baryonic baseline.",
        "",
        "## Next Action",
        "",
        plan[0]["AllowedAction"] + "; " + plan[1]["AllowedAction"] + ".",
        "",
        "## Generated Files",
        "",
        "- `things_missing_rotmod_acquisition_audit_v01.csv`",
        "- `things_missing_rotmod_acquisition_plan_v01.csv`",
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
    for path in [AUDIT_OUT, PLAN_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_missing_rotmod_acquisition_status"] = (
        "need_public_mass_model_columns_for_two_missing_THINGS_galaxies"
    )
    manifest["paper2_next_gate"] = "recover_THINGS_mass_model_tables_or_continue_non_WHISP_replication"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = audit_rows()
    plan = plan_rows(rows)
    write_csv(
        AUDIT_OUT,
        rows,
        [
            "GalaxyName",
            "PublishedName",
            "CurrentStatus",
            "HasLocalSparcRotmod",
            "CurrentScoreStatus",
            "LiteratureStatus",
            "PrimarySource",
            "SourceURL",
            "AcquisitionClass",
            "Blocker",
            "AllowedNextUse",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        PLAN_OUT,
        plan,
        [
            "StepID",
            "Step",
            "TargetGalaxies",
            "MinimumSuccess",
            "AllowedAction",
            "ForbiddenAction",
            "InterpretationGuardrail",
        ],
    )
    write_report(rows, plan)
    update_manifest()
    print(REPORT)
    print("things_missing_rotmod_count=5")
    print("minimum_needed_for_N15=2")


if __name__ == "__main__":
    main()
