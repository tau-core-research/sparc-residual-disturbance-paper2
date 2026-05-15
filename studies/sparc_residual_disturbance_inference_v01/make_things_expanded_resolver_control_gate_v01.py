#!/usr/bin/env python3
"""Summarize THINGS controls with the original-plus-expanded W_tau_eff resolver."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
EXPANDED = PACKET / "yu2022_alfalfa_expanded_w_tau_eff_scores_v01.csv"
TABLE3 = PACKET / "things_trachternach2008_table3_v01.csv"
TABLE3_METRICS = PACKET / "things_table3_w_tau_eff_metrics_v01.csv"
P05_METRICS = PACKET / "p05_things_non_circular_w_tau_eff_control_metrics_v01.csv"
WHISP_HOLWERDA_METRICS = PACKET / "whisp_holwerda2011_w_tau_eff_metrics_v01.csv"
WHISP_EXPANDED_METRICS = PACKET / "whisp_expanded_w_tau_eff_readout_metrics_v01.csv"

AUDIT_OUT = PACKET / "things_expanded_score_resolver_audit_v01.csv"
MATRIX_OUT = PACKET / "things_vs_whisp_control_matrix_v01.csv"
DECISION_OUT = PACKET / "things_control_gate_decision_v01.csv"
REPORT = PACKET / "things_control_gate_v01.md"

GUARDRAIL = "things_control_gate_no_velocity_endpoint_no_tau_attribution"


def fmt(value: float) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.9f}"


def metric_lookup(path: Path) -> dict[str, dict[str, str]]:
    return {row["Metric"]: row for row in read_csv(path)}


def score_index() -> dict[str, dict[str, str]]:
    scores: dict[str, dict[str, str]] = {}
    for row in read_csv(W_TAU):
        scores[row["GalaxyName"]] = {
            "ScoreSource": "frozen_original_w_tau_eff_seed",
            "Score": row["W_tau_eff_candidate_score_v01"],
        }
    for row in read_csv(EXPANDED):
        if row["W_tau_eff_readout_score_v01"] == "":
            continue
        scores.setdefault(
            row["GalaxyName"],
            {
                "ScoreSource": row["ScoreSource"],
                "Score": row["W_tau_eff_readout_score_v01"],
            },
        )
    return scores


def audit_rows() -> list[dict[str, str]]:
    scores = score_index()
    rows: list[dict[str, str]] = []
    for row in read_csv(TABLE3):
        galaxy = row["GalaxyName"]
        score = scores.get(galaxy)
        rows.append(
            {
                "GalaxyName": galaxy,
                "PublishedName": row["PublishedName"],
                "InOriginalWTauEffSeed": "yes"
                if score and score["ScoreSource"] == "frozen_original_w_tau_eff_seed"
                else "no",
                "InExpandedWTauEffResolver": "yes" if score else "no",
                "ScoreSource": score["ScoreSource"] if score else "",
                "W_tau_eff_score_resolved_v01": score["Score"] if score else "",
                "MedianNonCircularAmplitudeKms": row["MedianNonCircularAmplitudeKms"],
                "NonCircularAmplitudeOverVmaxPercent": row[
                    "NonCircularAmplitudeOverVmaxPercent"
                ],
                "AllowedUse": "resolver_coverage_audit_only",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def matrix_rows() -> list[dict[str, str]]:
    table3 = metric_lookup(TABLE3_METRICS)
    p05 = metric_lookup(P05_METRICS)
    whm = metric_lookup(WHISP_HOLWERDA_METRICS)
    whx = metric_lookup(WHISP_EXPANDED_METRICS)
    return [
        {
            "Readout": "WHISP_Holwerda2011_morphology",
            "Family": "WHISP_source_family",
            "N": whm["coverage_joined"]["N"],
            "PrimaryMetric": "auc_high_vs_low_AsymmetryA",
            "PrimaryValue": whm["auc_high_vs_low_AsymmetryA"]["Value"],
            "SecondaryMetric": "spearman_AsymmetryA_vs_w_tau_score",
            "SecondaryValue": whm["spearman_AsymmetryA_vs_w_tau_score"]["Value"],
            "ControlRole": "positive_source_family_replication",
            "Interpretation": "positive direction but WHISP-family only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Readout": "WHISP_vanEymeren2011_lopsidedness",
            "Family": "WHISP_source_family",
            "N": whx["coverage_joined"]["N"],
            "PrimaryMetric": "auc_high_vs_low_whisp_burden",
            "PrimaryValue": whx["auc_high_vs_low_whisp_burden"]["Value"],
            "SecondaryMetric": "spearman_whisp_burden_vs_w_tau_score",
            "SecondaryValue": whx["spearman_whisp_burden_vs_w_tau_score"]["Value"],
            "ControlRole": "positive_small_radial_readout",
            "Interpretation": "stronger direction but below N>=15",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Readout": "THINGS_Trachternach2008_Table3",
            "Family": "THINGS_kinematic_control",
            "N": table3["things_table3_w_tau_overlap"]["N"],
            "PrimaryMetric": "auc_high_vs_low_table3_ar",
            "PrimaryValue": table3["auc_high_vs_low_table3_ar"]["Value"],
            "SecondaryMetric": "pearson_table3_ar_vs_w_tau_score",
            "SecondaryValue": table3["pearson_table3_ar_vs_w_tau_score"]["Value"],
            "ControlRole": "non_circular_competition_control",
            "Interpretation": "does_not_absorb_WHISP_direction_in_small_overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Readout": "THINGS_P05_harmonic_control",
            "Family": "THINGS_kinematic_control",
            "N": p05["coverage_joined"]["N"],
            "PrimaryMetric": "auc_high_vs_low_p05_burden",
            "PrimaryValue": p05["auc_high_vs_low_p05_burden"]["Value"],
            "SecondaryMetric": "pearson_p05_burden_vs_w_tau_score",
            "SecondaryValue": p05["pearson_p05_burden_vs_w_tau_score"]["Value"],
            "ControlRole": "non_circular_competition_control",
            "Interpretation": "mixed_small_overlap_control_not_primary_explanation",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def decision_rows(audit: list[dict[str, str]], matrix: list[dict[str, str]]) -> list[dict[str, str]]:
    resolver_overlap = [row for row in audit if row["InExpandedWTauEffResolver"] == "yes"]
    expanded_only = [
        row
        for row in audit
        if row["InOriginalWTauEffSeed"] == "no" and row["InExpandedWTauEffResolver"] == "yes"
    ]
    table3 = next(row for row in matrix if row["Readout"] == "THINGS_Trachternach2008_Table3")
    p05 = next(row for row in matrix if row["Readout"] == "THINGS_P05_harmonic_control")
    return [
        {
            "DecisionID": "TCG01",
            "Decision": "expanded_score_resolver_effect",
            "Status": "no_new_THINGS_overlap_from_expanded_resolver",
            "N": str(len(resolver_overlap)),
            "Evidence": f"expanded_only_THINGS_rows={len(expanded_only)}",
            "NextAction": "keep_THINGS_as_small_external_control",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "TCG02",
            "Decision": "non_circular_absorption_test",
            "Status": "THINGS_controls_do_not_absorb_WHISP_direction",
            "N": table3["N"],
            "Evidence": (
                f"Table3_AUC={table3['PrimaryValue']};"
                f"Table3_Pearson={table3['SecondaryValue']};"
                f"P05_AUC={p05['PrimaryValue']};"
                f"P05_Pearson={p05['SecondaryValue']}"
            ),
            "NextAction": "proceed_to_non_WHISP_resolved_HI_replication",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "TCG03",
            "Decision": "claim_boundary",
            "Status": "control_only_below_THINGS_validation_n",
            "N": table3["N"],
            "Evidence": "THINGS exact-name overlap remains below frozen validation threshold",
            "NextAction": "do_not_claim_THINGS_validation_or_tau_attribution",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(audit: list[dict[str, str]], matrix: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    by_id = {row["DecisionID"]: row for row in decisions}
    by_readout = {row["Readout"]: row for row in matrix}
    lines = [
        "# THINGS Control Gate v0.1",
        "",
        "This packet rechecks THINGS after the expanded `W_tau_eff` score resolver. It does not fit coefficients, does not open a velocity endpoint, and does not make a Tau Core attribution.",
        "",
        "## Resolver Audit",
        "",
        f"- THINGS Table 3 rows: {len(audit)}",
        f"- Rows with resolved `W_tau_eff`: {by_id['TCG01']['N']}",
        f"- New rows from expanded resolver only: {by_id['TCG01']['Evidence'].split('=')[1]}",
        "",
        "## Competition Readout",
        "",
        f"- WHISP Holwerda AUC/Spearman: {by_readout['WHISP_Holwerda2011_morphology']['PrimaryValue']} / {by_readout['WHISP_Holwerda2011_morphology']['SecondaryValue']}",
        f"- WHISP van Eymeren AUC/Spearman: {by_readout['WHISP_vanEymeren2011_lopsidedness']['PrimaryValue']} / {by_readout['WHISP_vanEymeren2011_lopsidedness']['SecondaryValue']}",
        f"- THINGS Table 3 AUC/Pearson: {by_readout['THINGS_Trachternach2008_Table3']['PrimaryValue']} / {by_readout['THINGS_Trachternach2008_Table3']['SecondaryValue']}",
        f"- THINGS P05 AUC/Pearson: {by_readout['THINGS_P05_harmonic_control']['PrimaryValue']} / {by_readout['THINGS_P05_harmonic_control']['SecondaryValue']}",
        "",
        "## Decision",
        "",
        f"`{by_id['TCG02']['Status']}`",
        "",
        "In the currently available exact-name overlap, THINGS non-circular controls do not reproduce the WHISP-positive direction. This weakens the simplest explanation that the WHISP/`W_tau_eff` association is only a non-circular-motion amplitude effect. Because the THINGS overlap is small, the correct next step is still non-WHISP resolved-HI replication rather than Tau Core attribution.",
        "",
        "## Generated Files",
        "",
        "- `things_expanded_score_resolver_audit_v01.csv`",
        "- `things_vs_whisp_control_matrix_v01.csv`",
        "- `things_control_gate_decision_v01.csv`",
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
    for path in [AUDIT_OUT, MATRIX_OUT, DECISION_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_control_gate_status"] = (
        "THINGS_controls_do_not_absorb_WHISP_direction_small_overlap_control_only"
    )
    manifest["paper2_next_gate"] = "non_WHISP_resolved_HI_replication"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    audit = audit_rows()
    matrix = matrix_rows()
    decisions = decision_rows(audit, matrix)
    write_csv(
        AUDIT_OUT,
        audit,
        [
            "GalaxyName",
            "PublishedName",
            "InOriginalWTauEffSeed",
            "InExpandedWTauEffResolver",
            "ScoreSource",
            "W_tau_eff_score_resolved_v01",
            "MedianNonCircularAmplitudeKms",
            "NonCircularAmplitudeOverVmaxPercent",
            "AllowedUse",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        MATRIX_OUT,
        matrix,
        [
            "Readout",
            "Family",
            "N",
            "PrimaryMetric",
            "PrimaryValue",
            "SecondaryMetric",
            "SecondaryValue",
            "ControlRole",
            "Interpretation",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        DECISION_OUT,
        decisions,
        [
            "DecisionID",
            "Decision",
            "Status",
            "N",
            "Evidence",
            "NextAction",
            "InterpretationGuardrail",
        ],
    )
    write_report(audit, matrix, decisions)
    update_manifest()
    print(REPORT)
    print(f"things_resolver_overlap={decisions[0]['N']}")
    print(f"things_control_status={decisions[1]['Status']}")


if __name__ == "__main__":
    main()
