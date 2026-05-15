#!/usr/bin/env python3
"""Audit the current Reynolds 2020 coverage ceiling against W_tau_eff."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
REYNOLDS = PACKET / "reynolds2020_asymmetry_catalog_v01.csv"
LVHIS_ALIAS = PACKET / "lvhis_alias_resolution_v01.csv"

CEILING_OUT = PACKET / "reynolds2020_coverage_ceiling_audit_v01.csv"
NEXT_OUT = PACKET / "reynolds2020_coverage_ceiling_next_actions_v01.csv"
REPORT = PACKET / "reynolds2020_coverage_ceiling_audit_v01.md"

GUARDRAIL = "reynolds2020_coverage_ceiling_no_velocity_endpoint"


def rows_by_survey() -> list[dict[str, str]]:
    w_tau = {row["GalaxyName"]: row for row in read_csv(W_TAU)}
    aliases = {
        row["ExternalName"]: row["CanonicalSPARCNameCandidate"]
        for row in read_csv(LVHIS_ALIAS)
    }
    catalog = read_csv(REYNOLDS)
    output = []
    for survey in ["LVHIS", "VIVA", "HALOGAS"]:
        rows = [row for row in catalog if row["Survey"] == survey]
        exact = []
        alias = []
        unmatched = []
        for row in rows:
            external = row["ExternalName"]
            if external in w_tau:
                exact.append(external)
                continue
            candidate = aliases.get(external, "")
            if candidate in w_tau:
                alias.append(candidate)
            else:
                unmatched.append(candidate or external)
        matched = exact + alias
        output.append(
            {
                "Survey": survey,
                "CatalogRows": str(len(rows)),
                "ExactWTauEffMatches": str(len(exact)),
                "AliasWTauEffMatches": str(len(alias)),
                "TotalWTauEffMatches": str(len(matched)),
                "CurrentSeedCoverageFraction": f"{len(matched) / len(rows):.9f}",
                "MatchedCanonicalNames": ";".join(sorted(matched)),
                "UnmatchedCatalogRows": str(len(unmatched)),
                "CeilingStatus": (
                    "below_minimum_directional_gate"
                    if len(matched) < 15
                    else "meets_minimum_directional_gate"
                ),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    total_rows = len(catalog)
    total_matches = sum(int(row["TotalWTauEffMatches"]) for row in output)
    output.append(
        {
            "Survey": "TOTAL",
            "CatalogRows": str(total_rows),
            "ExactWTauEffMatches": str(sum(int(row["ExactWTauEffMatches"]) for row in output)),
            "AliasWTauEffMatches": str(sum(int(row["AliasWTauEffMatches"]) for row in output)),
            "TotalWTauEffMatches": str(total_matches),
            "CurrentSeedCoverageFraction": f"{total_matches / total_rows:.9f}",
            "MatchedCanonicalNames": ";".join(
                sorted(
                    name
                    for row in output
                    for name in row["MatchedCanonicalNames"].split(";")
                    if name
                )
            ),
            "UnmatchedCatalogRows": str(total_rows - total_matches),
            "CeilingStatus": "below_minimum_directional_gate",
            "InterpretationGuardrail": GUARDRAIL,
        }
    )
    return output


def next_action_rows(total_matches: int) -> list[dict[str, str]]:
    gate_gap = max(0, 15 - total_matches)
    return [
        {
            "ActionID": "R20C01",
            "Action": "current_seed_ceiling",
            "Status": "hard_ceiling_below_gate",
            "Rationale": (
                f"The current W_tau_eff seed can provide at most {total_matches} Reynolds 2020 "
                f"matches after LVHIS alias resolution; the frozen gate needs at least 15."
            ),
            "RequiredBeforeClaim": f"add_at_least_{gate_gap}_eligible_independent_matches_or_change_source_family",
            "AllowedMove": "treat_Reynolds2020_as_small_control_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ActionID": "R20C02",
            "Action": "seed_expansion_path",
            "Status": "requires_new_frozen_residual_seed_or_external_labels",
            "Rationale": (
                "More Reynolds matches require either a frozen residual-derived score for additional SPARC "
                "galaxies in the Reynolds catalog or a separate external source family with enough overlap."
            ),
            "RequiredBeforeClaim": "freeze_inputs_before_scoring_additional_galaxies",
            "AllowedMove": "predeclare_expansion_before_any_directional_readout",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ActionID": "R20C03",
            "Action": "velocity_endpoint_status",
            "Status": "closed",
            "Rationale": "This is a coverage audit only; it does not use Vobs residuals or fit any coefficient.",
            "RequiredBeforeClaim": "none",
            "AllowedMove": "coverage_planning_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(rows: list[dict[str, str]], actions: list[dict[str, str]]) -> None:
    lookup = {row["Survey"]: row for row in rows}
    total = lookup["TOTAL"]
    lines = [
        "# Reynolds 2020 Coverage Ceiling Audit v0.1",
        "",
        "This audit asks a narrow reproducibility question: after exact-name matching and LVHIS ID resolution, how much Reynolds et al. (2020) resolved H I asymmetry coverage can the current frozen `W_tau_eff` seed possibly support?",
        "",
        "## Result",
        "",
        f"- Reynolds catalog rows: {total['CatalogRows']}",
        f"- Current seed matches after alias resolution: {total['TotalWTauEffMatches']}",
        f"- Matched names: {total['MatchedCanonicalNames']}",
        f"- Frozen minimum directional gate: 15",
        f"- Gate status: {total['CeilingStatus']}",
        "",
        "## Survey Breakdown",
        "",
    ]
    for survey in ["LVHIS", "VIVA", "HALOGAS"]:
        row = lookup[survey]
        lines.append(
            f"- {survey}: {row['TotalWTauEffMatches']}/{row['CatalogRows']} matched; names={row['MatchedCanonicalNames'] or 'none'}."
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"`{actions[0]['Status']}`",
            "",
            actions[0]["Rationale"],
            "",
            "This closes the simple-alias route. Reynolds 2020 remains useful as a small external control, especially for checking whether velocity-field asymmetry behaves differently from map asymmetry, but it cannot become a paper-grade non-WHISP validation family without a predeclared seed expansion or a different source family.",
            "",
            "## Generated Files",
            "",
            "- `reynolds2020_coverage_ceiling_audit_v01.csv`",
            "- `reynolds2020_coverage_ceiling_next_actions_v01.csv`",
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
    for path in [CEILING_OUT, NEXT_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["reynolds2020_coverage_ceiling_status"] = (
        "current_seed_hard_ceiling_below_minimum_n"
    )
    manifest["paper2_next_gate"] = (
        "predeclare_seed_expansion_or_switch_to_larger_external_family"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = rows_by_survey()
    total_matches = int([row for row in rows if row["Survey"] == "TOTAL"][0]["TotalWTauEffMatches"])
    actions = next_action_rows(total_matches)
    fields = [
        "Survey",
        "CatalogRows",
        "ExactWTauEffMatches",
        "AliasWTauEffMatches",
        "TotalWTauEffMatches",
        "CurrentSeedCoverageFraction",
        "MatchedCanonicalNames",
        "UnmatchedCatalogRows",
        "CeilingStatus",
        "InterpretationGuardrail",
    ]
    write_csv(CEILING_OUT, rows, fields)
    write_csv(
        NEXT_OUT,
        actions,
        [
            "ActionID",
            "Action",
            "Status",
            "Rationale",
            "RequiredBeforeClaim",
            "AllowedMove",
            "InterpretationGuardrail",
        ],
    )
    write_report(rows, actions)
    update_manifest()


if __name__ == "__main__":
    main()
