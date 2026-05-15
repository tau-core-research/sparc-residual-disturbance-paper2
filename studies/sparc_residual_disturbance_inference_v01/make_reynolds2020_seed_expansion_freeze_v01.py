#!/usr/bin/env python3
"""Freeze a predeclared Reynolds 2020 W_tau_eff seed-expansion plan."""

from __future__ import annotations

import json
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
REYNOLDS = PACKET / "reynolds2020_asymmetry_catalog_v01.csv"
LVHIS_ALIAS = PACKET / "lvhis_alias_resolution_v01.csv"

POLICY_OUT = PACKET / "reynolds2020_seed_expansion_policy_v01.csv"
QUEUE_OUT = PACKET / "reynolds2020_seed_expansion_candidate_queue_v01.csv"
GATE_OUT = PACKET / "reynolds2020_seed_expansion_gate_v01.csv"
REPORT = PACKET / "reynolds2020_seed_expansion_freeze_v01.md"

GUARDRAIL = "reynolds2020_seed_expansion_freeze_no_directional_readout"


def canonical_external_name(row: dict[str, str], aliases: dict[str, str]) -> tuple[str, str]:
    if row["Survey"] == "LVHIS":
        return aliases.get(row["ExternalName"], ""), "lvhis_database_optical_id_alias"
    return row["ExternalName"], "survey_name_as_canonical_candidate"


def has_any_asymmetry(row: dict[str, str]) -> bool:
    return bool(row["Amap"] or row["Avel"])


def has_velocity_asymmetry(row: dict[str, str]) -> bool:
    return bool(row["Avel"])


def candidate_rows() -> list[dict[str, str]]:
    existing = {row["GalaxyName"] for row in read_csv(W_TAU)}
    aliases = {
        row["ExternalName"]: row["CanonicalSPARCNameCandidate"]
        for row in read_csv(LVHIS_ALIAS)
    }
    rows = []
    for row in read_csv(REYNOLDS):
        canonical, mode = canonical_external_name(row, aliases)
        already_seeded = canonical in existing
        eligible_name = bool(canonical) and canonical.upper() != "NEW"
        usable_proxy = has_any_asymmetry(row)
        expansion_status = (
            "already_in_frozen_seed"
            if already_seeded
            else "predeclared_candidate_pending_sparc_rotmod_audit"
            if eligible_name and usable_proxy
            else "excluded_before_scoring"
        )
        exclusion_reason = ""
        if expansion_status == "excluded_before_scoring":
            if not eligible_name:
                exclusion_reason = "no_resolved_canonical_name"
            elif not usable_proxy:
                exclusion_reason = "no_reynolds_asymmetry_proxy_available"
        priority = "high" if has_velocity_asymmetry(row) else "medium" if usable_proxy else "excluded"
        rows.append(
            {
                "Survey": row["Survey"],
                "ExternalName": row["ExternalName"],
                "CanonicalSPARCNameCandidate": canonical,
                "CanonicalizationMode": mode,
                "AmapAvailable": "yes" if row["Amap"] else "no",
                "AvelAvailable": "yes" if row["Avel"] else "no",
                "AlreadyInWTauEffSeed": "yes" if already_seeded else "no",
                "ExpansionStatus": expansion_status,
                "PreScorePriority": priority,
                "RequiredNextAudit": (
                    "none_existing_seed"
                    if already_seeded
                    else "sparc_rotmod_availability_and_minimum_radial_points"
                    if expansion_status.startswith("predeclared")
                    else "none_excluded"
                ),
                "ExclusionReason": exclusion_reason,
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def policy_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    candidates = [
        row
        for row in rows
        if row["ExpansionStatus"] == "predeclared_candidate_pending_sparc_rotmod_audit"
    ]
    high = [row for row in candidates if row["PreScorePriority"] == "high"]
    existing = [row for row in rows if row["AlreadyInWTauEffSeed"] == "yes"]
    return [
        {
            "RuleID": "R20F01",
            "Rule": "candidate_universe",
            "FrozenRule": "All Reynolds2020 rows with a resolved canonical name, at least one published asymmetry proxy, and not already in W_tau_eff enter the expansion queue.",
            "NRows": str(len(candidates)),
            "AllowedUse": "pre_score_candidate_queue_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "RuleID": "R20F02",
            "Rule": "scoring_gate",
            "FrozenRule": "A queued galaxy may receive an expanded W_tau_eff score only if a public SPARC rotmod/mass-model input is available and passes the minimum radial-point audit.",
            "NRows": "pending",
            "AllowedUse": "eligibility_gate_before_any_directional_readout",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "RuleID": "R20F03",
            "Rule": "proxy_priority",
            "FrozenRule": "Rows with Reynolds Avel are high-priority because the alias-resolved pilot hinted that velocity-field asymmetry may separate C/A better than map asymmetry; this priority is for acquisition only.",
            "NRows": str(len(high)),
            "AllowedUse": "acquisition_priority_not_model_training",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "RuleID": "R20F04",
            "Rule": "existing_seed_handling",
            "FrozenRule": "Already-seeded galaxies remain fixed and must not be refit as part of the expansion; they are used only as anchor/control rows.",
            "NRows": str(len(existing)),
            "AllowedUse": "anchor_rows_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "RuleID": "R20F05",
            "Rule": "directional_readout_lock",
            "FrozenRule": "No Reynolds Amap/Avel versus expanded W_tau_eff directional result may be computed until the rotmod availability audit and expanded scoring script are committed.",
            "NRows": "0",
            "AllowedUse": "locks_the_next_endpoint",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def gate_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    candidates = [
        row
        for row in rows
        if row["ExpansionStatus"] == "predeclared_candidate_pending_sparc_rotmod_audit"
    ]
    high = [row for row in candidates if row["PreScorePriority"] == "high"]
    return [
        {
            "GateID": "R20G01",
            "Gate": "predeclared_candidate_queue",
            "Status": "met",
            "N": str(len(candidates)),
            "PassCondition": "candidate queue is frozen before score computation",
            "NextAction": "run_sparc_rotmod_availability_audit",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "GateID": "R20G02",
            "Gate": "high_priority_velocity_asymmetry_queue",
            "Status": "met" if high else "not_met",
            "N": str(len(high)),
            "PassCondition": "at least 15 high-priority Avel rows are available before rotmod audit",
            "NextAction": "prioritize_Avel_rows_for_input_availability_check",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "GateID": "R20G03",
            "Gate": "directional_readout_permission",
            "Status": "closed",
            "N": "0",
            "PassCondition": "requires committed rotmod audit plus committed expanded scoring table",
            "NextAction": "do_not_compute_Amap_Avel_direction_yet",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(rows: list[dict[str, str]], policies: list[dict[str, str]], gates: list[dict[str, str]]) -> None:
    candidates = [
        row
        for row in rows
        if row["ExpansionStatus"] == "predeclared_candidate_pending_sparc_rotmod_audit"
    ]
    high = [row for row in candidates if row["PreScorePriority"] == "high"]
    existing = [row for row in rows if row["AlreadyInWTauEffSeed"] == "yes"]
    excluded = [row for row in rows if row["ExpansionStatus"] == "excluded_before_scoring"]
    by_survey = {
        survey: sum(row["Survey"] == survey for row in candidates)
        for survey in ["LVHIS", "VIVA", "HALOGAS"]
    }
    lines = [
        "# Reynolds 2020 Seed-Expansion Freeze v0.1",
        "",
        "This packet freezes the candidate universe for a possible Reynolds et al. (2020) `W_tau_eff` seed expansion. It intentionally does not calculate any new residual score and does not compare Reynolds asymmetry against an expanded score.",
        "",
        "## Frozen Candidate Rule",
        "",
        policies[0]["FrozenRule"],
        "",
        "A queued galaxy still needs a separate public SPARC rotmod/mass-model availability audit before any expanded `W_tau_eff` score can be generated.",
        "",
        "## Counts",
        "",
        f"- Reynolds rows: {len(rows)}",
        f"- Already in frozen seed: {len(existing)}",
        f"- Predeclared expansion candidates: {len(candidates)}",
        f"- High-priority candidates with Avel: {len(high)}",
        f"- Excluded before scoring: {len(excluded)}",
        f"- Candidate breakdown: LVHIS={by_survey['LVHIS']}; VIVA={by_survey['VIVA']}; HALOGAS={by_survey['HALOGAS']}",
        "",
        "## Endpoint Lock",
        "",
        "`closed`",
        "",
        "The next allowed step is an input-availability audit. A Reynolds Amap/Avel directional readout is still forbidden until the availability audit and expanded scoring table are generated and committed.",
        "",
        "## Generated Files",
        "",
        "- `reynolds2020_seed_expansion_policy_v01.csv`",
        "- `reynolds2020_seed_expansion_candidate_queue_v01.csv`",
        "- `reynolds2020_seed_expansion_gate_v01.csv`",
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
    for path in [POLICY_OUT, QUEUE_OUT, GATE_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["reynolds2020_seed_expansion_freeze_status"] = (
        "candidate_queue_frozen_no_directional_readout"
    )
    manifest["paper2_next_gate"] = "sparc_rotmod_availability_audit_for_reynolds_expansion"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = candidate_rows()
    policies = policy_rows(rows)
    gates = gate_rows(rows)
    write_csv(
        POLICY_OUT,
        policies,
        ["RuleID", "Rule", "FrozenRule", "NRows", "AllowedUse", "InterpretationGuardrail"],
    )
    write_csv(
        QUEUE_OUT,
        rows,
        [
            "Survey",
            "ExternalName",
            "CanonicalSPARCNameCandidate",
            "CanonicalizationMode",
            "AmapAvailable",
            "AvelAvailable",
            "AlreadyInWTauEffSeed",
            "ExpansionStatus",
            "PreScorePriority",
            "RequiredNextAudit",
            "ExclusionReason",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        GATE_OUT,
        gates,
        [
            "GateID",
            "Gate",
            "Status",
            "N",
            "PassCondition",
            "NextAction",
            "InterpretationGuardrail",
        ],
    )
    write_report(rows, policies, gates)
    update_manifest()


if __name__ == "__main__":
    main()
