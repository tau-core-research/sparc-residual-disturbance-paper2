#!/usr/bin/env python3
"""Summarize external source-family validation status for Paper 2."""

from __future__ import annotations

import json
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


STATUS_OUT = PACKET / "external_validation_status_board_v01.csv"
DECISION_OUT = PACKET / "external_validation_status_decision_v01.csv"
REPORT = PACKET / "external_validation_status_board_v01.md"

GUARDRAIL = "external_validation_status_no_velocity_endpoint_no_tau_core_claim"


def metric_lookup(path: Path) -> dict[str, dict[str, str]]:
    return {row["Metric"]: row for row in read_csv(path)}


def decision_lookup(path: Path, key: str = "DecisionID") -> dict[str, dict[str, str]]:
    return {row[key]: row for row in read_csv(path)}


def coverage_lookup() -> dict[str, dict[str, str]]:
    return {row["Family"]: row for row in read_csv(PACKET / "w_env_obs_systematics_competition_coverage_v01.csv")}


def status_rows() -> list[dict[str, str]]:
    coverage = coverage_lookup()
    p07 = metric_lookup(PACKET / "p07_whisp_w_tau_eff_holdout_metric_summary_v01.csv")
    p05 = metric_lookup(PACKET / "p05_things_non_circular_w_tau_eff_control_metrics_v01.csv")
    p05d = decision_lookup(PACKET / "p05_things_non_circular_w_tau_eff_control_decision_v01.csv")
    odw = metric_lookup(PACKET / "observer_distance_whisp_external_validation_metrics_v01.csv")
    odwd = decision_lookup(PACKET / "observer_distance_whisp_external_validation_decision_v01.csv")
    r20 = metric_lookup(PACKET / "reynolds2020_asymmetry_crossmatch_metrics_v01.csv")
    lvh = metric_lookup(PACKET / "reynolds2020_lvh_alias_resolved_metrics_v01.csv")

    return [
        {
            "FamilyID": "P07",
            "Family": "WHISP resolved HI asymmetry",
            "JoinedN": coverage["P07_WHISP_lopsidedness"]["JoinedWithWTauEff"],
            "Classes": coverage["P07_WHISP_lopsidedness"]["Classes"],
            "Readout": "W_tau_eff source-family direction",
            "PrimaryMetric": f"AUC={p07['auc_high_vs_low_whisp_burden']['Value']};Pearson={p07['pearson_whisp_burden_vs_w_tau_score']['Value']}",
            "Status": "positive_small_source_family_sanity_check",
            "Limitation": "small and class-imbalanced overlap",
            "EndpointPermission": "no_velocity_endpoint",
            "NextAction": "retain_as_supporting_direction_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "FamilyID": "ODW",
            "Family": "WHISP observer-distance stress",
            "JoinedN": odw["coverage_joined"]["Value"],
            "Classes": odw["class_coverage"]["Value"],
            "Readout": "observer-distance hypothesis after WHISP controls",
            "PrimaryMetric": (
                f"rawPearson={odw['pearson_tau_distance_raw_vs_w_tau_score']['Value']};"
                f"partialPearson={odw['partial_pearson_tau_distance_after_whisp_controls']['Value']};"
                f"partialAUC={odw['partial_auc_tau_distance_after_whisp_controls']['Value']}"
            ),
            "Status": odwd["ODW01"]["Status"],
            "Limitation": "not class-balanced and does not reproduce after WHISP/systematics controls",
            "EndpointPermission": "no_velocity_endpoint",
            "NextAction": "do_not_promote_observer_distance_hypothesis_before_other_external_checks",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "FamilyID": "P05",
            "Family": "THINGS harmonic non-circular motions",
            "JoinedN": coverage["P05_THINGS_harmonic_non_circular"]["JoinedWithWTauEff"],
            "Classes": coverage["P05_THINGS_harmonic_non_circular"]["Classes"],
            "Readout": "non-circular control versus W_tau_eff",
            "PrimaryMetric": f"Pearson={p05['pearson_p05_burden_vs_w_tau_score']['Value']};AUC={p05['auc_high_vs_low_p05_burden']['Value']}",
            "Status": p05d["P05D01"]["Status"],
            "Limitation": "small overlap and galaxy-level control only",
            "EndpointPermission": "no_velocity_endpoint",
            "NextAction": "retain_as_required_control_and_expand_overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "FamilyID": "P06",
            "Family": "LITTLE THINGS pressure support",
            "JoinedN": coverage["P06_LITTLE_THINGS_pressure"]["JoinedWithWTauEff"],
            "Classes": coverage["P06_LITTLE_THINGS_pressure"]["Classes"],
            "Readout": "pressure-support coverage check",
            "PrimaryMetric": "N=2 usable overlap",
            "Status": "too_small_for_directional_validation",
            "Limitation": "very small overlap",
            "EndpointPermission": "no_velocity_endpoint",
            "NextAction": "expand_or_replace_with_larger_pressure_support_catalogue",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "FamilyID": "P08",
            "Family": "HALOGAS linewidth stress",
            "JoinedN": coverage["P08_HALOGAS_linewidth"]["JoinedWithWTauEff"],
            "Classes": coverage["P08_HALOGAS_linewidth"]["Classes"],
            "Readout": "external linewidth stress coverage check",
            "PrimaryMetric": "N=5 usable overlap",
            "Status": "weak_small_overlap_control_only",
            "Limitation": "weak small-overlap control",
            "EndpointPermission": "no_velocity_endpoint",
            "NextAction": "expand_linewidth_or_velocity_field_source_family",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "FamilyID": "R20",
            "Family": "Reynolds 2020 resolved HI asymmetry",
            "JoinedN": r20["exact_w_tau_eff_crossmatch_rows"]["Value"],
            "Classes": "A;C",
            "Readout": "non-WHISP resolved HI asymmetry exact-name crossmatch",
            "PrimaryMetric": f"AmapPearson={r20['pearson_amap_vs_w_tau_score']['Value']};AvelPearson={r20['pearson_avel_vs_w_tau_score']['Value']}",
            "Status": "catalog_ingested_exact_overlap_below_minimum_n",
            "Limitation": "exact-name overlap is HALOGAS-only and below the frozen minimum N",
            "EndpointPermission": "no_velocity_endpoint",
            "NextAction": "resolve_LVHIS_aliases_before_directional_claim",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "FamilyID": "LVH",
            "Family": "LVHIS alias-resolved Reynolds 2020 asymmetry",
            "JoinedN": lvh["alias_resolved_w_tau_eff_crossmatch_rows"]["Value"],
            "Classes": "A;C",
            "Readout": "non-WHISP resolved HI asymmetry after LVHIS ID resolution",
            "PrimaryMetric": f"AmapPearson={lvh['pearson_amap_vs_w_tau_score_alias_resolved']['Value']};AvelPearson={lvh['pearson_avel_vs_w_tau_score_alias_resolved']['Value']};AvelAUC={lvh['auc_c_higher_avel_alias_resolved']['Value']}",
            "Status": "alias_resolution_improves_overlap_but_below_minimum_n",
            "Limitation": "N=6 remains below the frozen N>=15 validation gate",
            "EndpointPermission": "no_velocity_endpoint",
            "NextAction": "expand_seed_or_add_independent_alias_catalogue_before_directional_claim",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def decision_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    negative = [row for row in rows if row["Status"] == "direction_not_reproduced_in_small_whisp_overlap"]
    too_small = [row for row in rows if "too_small" in row["Status"] or "weak_small" in row["Status"]]
    p07_positive = any(row["FamilyID"] == "P07" and row["Status"].startswith("positive") for row in rows)
    if negative and p07_positive:
        status = "mixed_external_validation_supporting_w_tau_direction_not_observer_distance"
        next_action = "prioritize_non_whisp_THINGS_LITTLE_THINGS_HALOGAS_expansion_before_formula"
    else:
        status = "external_validation_inconclusive"
        next_action = "expand_external_source_families_before_formula"
    return [
        {
            "DecisionID": "EVS01",
            "Decision": "external_source_family_status",
            "Status": status,
            "Rationale": (
                "WHISP supports the broad W_tau_eff direction, but the WHISP observer-distance "
                "stress does not reproduce after controls; Reynolds/LVHIS alias resolution improves "
                "non-WHISP overlap but remains below the frozen minimum N."
            ),
            "Blocks": "velocity_formula;field_attribution;observer_distance_claim",
            "NextAction": next_action,
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "EVS02",
            "Decision": "velocity_endpoint_status",
            "Status": "closed",
            "Rationale": (
                f"{len(negative)} negative observer-distance validation and "
                f"{len(too_small)} too-small/weak source-family controls are not enough for a velocity endpoint."
            ),
            "Blocks": "S_tau_full_velocity_readout",
            "NextAction": "freeze_expanded_external_validation_targets",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(rows: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lines = [
        "# External Validation Status Board v0.1",
        "",
        "This board summarizes the current external source-family validation status after the WHISP observer-distance stress test. It is a status readout only: it does not fit coefficients, does not open a velocity endpoint, and does not claim a Tau Core field detection.",
        "",
        "## Summary",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"- {row['FamilyID']} ({row['Family']}): {row['Status']}; {row['PrimaryMetric']}.",
            ]
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- EVS01: `{decisions[0]['Status']}`",
            f"- EVS02: `{decisions[1]['Status']}`",
            "",
            "The broad `W_tau_eff` direction still has a positive WHISP source-family sanity check, but the observer-distance hypothesis is not externally validated by WHISP after controls. The Reynolds/LVHIS alias path improves non-WHISP resolved-HI overlap but remains below the frozen directional gate. The next productive step is therefore expanded non-WHISP validation with enough overlap for directional tests.",
            "",
            "Current support is therefore for the broad residual-inferred weight direction, not for the observer-distance interpretation.",
            "",
            "## Generated Files",
            "",
            "- `external_validation_status_board_v01.csv`",
            "- `external_validation_status_decision_v01.csv`",
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
    for path in [STATUS_OUT, DECISION_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["external_validation_status_board_status"] = (
        "mixed_external_validation_status_complete_no_velocity_endpoint"
    )
    manifest["paper2_next_gate"] = "expanded_non_whisp_external_validation_targets"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = status_rows()
    decisions = decision_rows(rows)
    status_fields = [
        "FamilyID",
        "Family",
        "JoinedN",
        "Classes",
        "Readout",
        "PrimaryMetric",
        "Status",
        "Limitation",
        "EndpointPermission",
        "NextAction",
        "InterpretationGuardrail",
    ]
    decision_fields = [
        "DecisionID",
        "Decision",
        "Status",
        "Rationale",
        "Blocks",
        "NextAction",
        "InterpretationGuardrail",
    ]
    write_csv(STATUS_OUT, rows, status_fields)
    write_csv(DECISION_OUT, decisions, decision_fields)
    write_report(rows, decisions)
    update_manifest()


if __name__ == "__main__":
    main()
