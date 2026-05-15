#!/usr/bin/env python3
"""Freeze the Yu et al. 2022 ALFALFA seed-expansion queue."""

from __future__ import annotations

import json

from make_packet_v01_seed import PACKET, read_csv, write_csv


COVERAGE = PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_v01.csv"
POLICY_OUT = PACKET / "yu2022_alfalfa_seed_expansion_policy_v01.csv"
QUEUE_OUT = PACKET / "yu2022_alfalfa_seed_expansion_queue_v01.csv"
GATE_OUT = PACKET / "yu2022_alfalfa_seed_expansion_gate_v01.csv"
REPORT = PACKET / "yu2022_alfalfa_seed_expansion_freeze_v01.md"

GUARDRAIL = "yu2022_alfalfa_seed_expansion_freeze_no_directional_readout"


def quality_flag(row: dict[str, str]) -> str:
    notes = row["Notes"]
    sn = float(row["SN"]) if row["SN"] else 0.0
    if "c" in notes:
        return "caution_confused_profile"
    if sn < 20:
        return "caution_low_sn"
    return "primary_quality"


def queue_rows() -> list[dict[str, str]]:
    rows = []
    for row in read_csv(COVERAGE):
        status = row["ExpansionStatus"]
        is_existing = status == "existing_seed_overlap"
        is_candidate = status == "candidate_for_predeclared_seed_expansion"
        qflag = quality_flag(row)
        rows.append(
            {
                "CanonicalSPARCNameCandidate": row["CanonicalSPARCNameCandidate"],
                "AGC": row["AGC"],
                "InWTauEffSeed": row["InWTauEffSeed"],
                "FreezeRole": (
                    "anchor_existing_seed"
                    if is_existing
                    else "predeclared_expansion_candidate"
                    if is_candidate
                    else "excluded"
                ),
                "Af": row["Af"],
                "e_Af": row["e_Af"],
                "Ac": row["Ac"],
                "e_Ac": row["e_Ac"],
                "SN": row["SN"],
                "Notes": row["Notes"],
                "ProfileQualityFlag": qflag,
                "HasLocalSparcRotmod": row["HasLocalSparcRotmod"],
                "LocalRotmodPath": row["LocalRotmodPath"],
                "ScoringPermission": (
                    "allowed_after_expanded_scoring_script_committed"
                    if is_candidate and qflag == "primary_quality"
                    else "anchor_only_no_refit"
                    if is_existing
                    else "do_not_score"
                ),
                "DirectionalReadoutPermission": "closed_until_expanded_scores_committed",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def policy_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    candidates = [row for row in rows if row["FreezeRole"] == "predeclared_expansion_candidate"]
    primary_candidates = [
        row
        for row in candidates
        if row["ScoringPermission"] == "allowed_after_expanded_scoring_script_committed"
    ]
    anchors = [row for row in rows if row["FreezeRole"] == "anchor_existing_seed"]
    return [
        {
            "RuleID": "YU22F01",
            "Rule": "candidate_universe",
            "FrozenRule": "All Yu2022 ALFALFA rows with AGC<100000 mapped to UGC, local SPARC rotmod availability, and not already in W_tau_eff enter the expansion queue.",
            "NRows": str(len(candidates)),
            "AllowedUse": "pre_score_candidate_queue_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "RuleID": "YU22F02",
            "Rule": "primary_quality_gate",
            "FrozenRule": "Primary scoring candidates require S/N>=20 and no catalogue confusion note c. Lower-quality rows remain documented but are not scored in the first expansion pass.",
            "NRows": str(len(primary_candidates)),
            "AllowedUse": "input_quality_gate_before_scoring",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "RuleID": "YU22F03",
            "Rule": "anchor_handling",
            "FrozenRule": "Existing W_tau_eff seed overlaps are retained as anchors and must not be refit during the expansion pass.",
            "NRows": str(len(anchors)),
            "AllowedUse": "anchor_rows_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "RuleID": "YU22F04",
            "Rule": "directional_readout_lock",
            "FrozenRule": "No Af/Ac versus expanded W_tau_eff directional readout may be computed until the expanded scoring script and expanded score table are committed.",
            "NRows": "0",
            "AllowedUse": "locks_the_next_endpoint",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def gate_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    candidates = [row for row in rows if row["FreezeRole"] == "predeclared_expansion_candidate"]
    primary_candidates = [
        row
        for row in candidates
        if row["ScoringPermission"] == "allowed_after_expanded_scoring_script_committed"
    ]
    anchors = [row for row in rows if row["FreezeRole"] == "anchor_existing_seed"]
    total_after_expansion = len(primary_candidates) + len(anchors)
    return [
        {
            "GateID": "YU22G01",
            "Gate": "predeclared_candidate_queue",
            "Status": "met",
            "N": str(len(candidates)),
            "PassCondition": "candidate queue frozen before score computation",
            "NextAction": "write_expanded_w_tau_eff_scoring_script",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "GateID": "YU22G02",
            "Gate": "primary_quality_scoring_queue",
            "Status": "met" if len(primary_candidates) >= 15 else "not_met",
            "N": str(len(primary_candidates)),
            "PassCondition": "at least 15 primary-quality candidates before scoring",
            "NextAction": "score_only_primary_quality_candidates_first",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "GateID": "YU22G03",
            "Gate": "post_expansion_minimum_n",
            "Status": "met" if total_after_expansion >= 15 else "not_met",
            "N": str(total_after_expansion),
            "PassCondition": "anchors plus primary-quality expansion candidates reach N>=15",
            "NextAction": "allow_directional_readout_only_after_expanded_scores_committed",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "GateID": "YU22G04",
            "Gate": "directional_readout_permission",
            "Status": "closed",
            "N": "0",
            "PassCondition": "requires committed expanded scoring script and score table",
            "NextAction": "do_not_compute_Af_Ac_direction_yet",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(rows: list[dict[str, str]], policies: list[dict[str, str]], gates: list[dict[str, str]]) -> None:
    anchors = [row for row in rows if row["FreezeRole"] == "anchor_existing_seed"]
    candidates = [row for row in rows if row["FreezeRole"] == "predeclared_expansion_candidate"]
    primary = [
        row
        for row in candidates
        if row["ScoringPermission"] == "allowed_after_expanded_scoring_script_committed"
    ]
    lines = [
        "# Yu 2022 ALFALFA Seed-Expansion Freeze v0.1",
        "",
        "This packet freezes the Yu et al. (2022) ALFALFA profile-asymmetry seed-expansion queue. It does not calculate expanded residual scores and does not compare Af or Ac against `W_tau_eff`.",
        "",
        "## Frozen Rule",
        "",
        policies[0]["FrozenRule"],
        "",
        "The first scoring pass is restricted to primary-quality candidates: S/N>=20 and no catalogue confusion note `c`.",
        "",
        "## Counts",
        "",
        f"- Existing anchors: {len(anchors)}",
        f"- Predeclared expansion candidates: {len(candidates)}",
        f"- Primary-quality scoring candidates: {len(primary)}",
        f"- Anchors plus primary-quality candidates: {len(anchors) + len(primary)}",
        f"- Minimum N gate after expansion: {gates[2]['Status']}",
        "",
        "## Endpoint Lock",
        "",
        "`closed`",
        "",
        "The next allowed step is the expanded scoring script. The Af/Ac directional readout remains forbidden until the script and expanded score table are committed.",
        "",
        "## Generated Files",
        "",
        "- `yu2022_alfalfa_seed_expansion_policy_v01.csv`",
        "- `yu2022_alfalfa_seed_expansion_queue_v01.csv`",
        "- `yu2022_alfalfa_seed_expansion_gate_v01.csv`",
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
    manifest["yu2022_alfalfa_seed_expansion_freeze_status"] = (
        "candidate_queue_frozen_no_directional_readout"
    )
    manifest["paper2_next_gate"] = "write_expanded_w_tau_eff_scoring_script"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = queue_rows()
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
            "CanonicalSPARCNameCandidate",
            "AGC",
            "InWTauEffSeed",
            "FreezeRole",
            "Af",
            "e_Af",
            "Ac",
            "e_Ac",
            "SN",
            "Notes",
            "ProfileQualityFlag",
            "HasLocalSparcRotmod",
            "LocalRotmodPath",
            "ScoringPermission",
            "DirectionalReadoutPermission",
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
