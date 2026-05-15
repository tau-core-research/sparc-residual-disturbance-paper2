#!/usr/bin/env python3
"""Rank the next spatially resolved or kinematic proxy gate after Yu Af/Ac."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


WHISP = PACKET / "p07_whisp_w_tau_eff_holdout_metric_summary_v01.csv"
THINGS = PACKET / "p05_things_non_circular_w_tau_eff_control_metrics_v01.csv"
HALOGAS = PACKET / "halogas_moment_proxy_metrics_v01.csv"
YU = PACKET / "yu2022_alfalfa_af_ac_w_tau_eff_metrics_v01.csv"
INVENTORY = PACKET / "source_side_history_proxy_inventory_v01.csv"

MATRIX_OUT = PACKET / "spatial_kinematic_proxy_next_gate_matrix_v01.csv"
DECISION_OUT = PACKET / "spatial_kinematic_proxy_next_gate_decision_v01.csv"
REPORT = PACKET / "spatial_kinematic_proxy_next_gate_v01.md"

GUARDRAIL = "spatial_kinematic_proxy_gate_no_new_endpoint_fit"


def metric_lookup(path: Path) -> dict[str, dict[str, str]]:
    return {row["Metric"]: row for row in read_csv(path)}


def inventory_lookup() -> dict[str, dict[str, str]]:
    return {row["ProxyID"]: row for row in read_csv(INVENTORY)}


def source_rows() -> list[dict[str, str]]:
    inv = inventory_lookup()
    whisp = metric_lookup(WHISP)
    things = metric_lookup(THINGS)
    halogas = metric_lookup(HALOGAS)
    yu = metric_lookup(YU)
    rows = [
        {
            "CandidateGate": "WHISP_P07_radial_lopsidedness_family",
            "ProxyIDs": "P07",
            "ResolutionClass": inv["P07"]["Resolution"],
            "ReadinessTier": inv["P07"]["ReadinessTier"],
            "CoverageN": whisp["coverage_joined"]["N"],
            "PrimaryMetric": "auc_high_vs_low_whisp_burden",
            "PrimaryValue": whisp["auc_high_vs_low_whisp_burden"]["Value"],
            "SecondaryMetric": "pearson_whisp_burden_vs_w_tau_score",
            "SecondaryValue": whisp["pearson_whisp_burden_vs_w_tau_score"]["Value"],
            "ResultDirection": "positive_small_holdout",
            "UseNext": "primary_source_family_extension",
            "Reason": "best existing external direction and contains radial/asymmetry information",
            "RequiredNextAction": "expand_or_rebuild_WHISP_style_radial_asymmetry_join_before_any_velocity_formula",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "CandidateGate": "THINGS_P03_P05_kinematic_control",
            "ProxyIDs": "P03;P05",
            "ResolutionClass": f"{inv['P03']['Resolution']};{inv['P05']['Resolution']}",
            "ReadinessTier": f"{inv['P03']['ReadinessTier']};{inv['P05']['ReadinessTier']}",
            "CoverageN": things["coverage_joined"]["N"],
            "PrimaryMetric": "auc_high_vs_low_p05_burden",
            "PrimaryValue": things["auc_high_vs_low_p05_burden"]["Value"],
            "SecondaryMetric": "pearson_NonCircularAmplitudeOverVmaxPercent_vs_w_tau_score",
            "SecondaryValue": things[
                "pearson_NonCircularAmplitudeOverVmaxPercent_vs_w_tau_score"
            ]["Value"],
            "ResultDirection": "mixed_control_signal",
            "UseNext": "mandatory_systematics_competition_control",
            "Reason": "most kinematically targeted control, but small overlap and mixed sign",
            "RequiredNextAction": "keep_as_competition_control_for_WHISP_or_any_radial_proxy",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "CandidateGate": "Yu2022_ALFALFA_global_profile_asymmetry",
            "ProxyIDs": "YU22",
            "ResolutionClass": "global_unresolved_profile",
            "ReadinessTier": "coverage_large_but_not_spatially_resolved",
            "CoverageN": yu["coverage_directional_readout_rows"]["N"],
            "PrimaryMetric": "auc_high_vs_low_profile_asymmetry_score",
            "PrimaryValue": yu["auc_high_vs_low_profile_asymmetry_score"]["Value"],
            "SecondaryMetric": "spearman_LogMaxAfAc_vs_w_tau_score",
            "SecondaryValue": yu["spearman_LogMaxAfAc_vs_w_tau_score"]["Value"],
            "ResultDirection": "not_supported",
            "UseNext": "negative_control_or_coverage_reference",
            "Reason": "larger N but unresolved global Af/Ac does not track W_tau_eff",
            "RequiredNextAction": "do_not_use_as_primary_tau_proxy_without_spatial_or_kinematic refinement",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "CandidateGate": "HALOGAS_LR_cube_moment_stress",
            "ProxyIDs": "P08",
            "ResolutionClass": inv["P08"]["Resolution"],
            "ReadinessTier": inv["P08"]["ReadinessTier"],
            "CoverageN": halogas["coverage_joined"]["N"],
            "PrimaryMetric": "auc_high_vs_low_halogas_moment_stress",
            "PrimaryValue": halogas["auc_high_vs_low_halogas_moment_stress"]["Value"],
            "SecondaryMetric": "pearson_halogas_moment_stress_vs_w_tau_score",
            "SecondaryValue": halogas["pearson_halogas_moment_stress_vs_w_tau_score"]["Value"],
            "ResultDirection": "small_overlap_weak",
            "UseNext": "control_only_until_overlap_expands",
            "Reason": "cube-derived but only five overlaps and no separation",
            "RequiredNextAction": "do_not_prioritize_before_WHISP_or_THINGS",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]
    return rows


def decision_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    whisp = next(row for row in rows if row["CandidateGate"].startswith("WHISP"))
    things = next(row for row in rows if row["CandidateGate"].startswith("THINGS"))
    yu = next(row for row in rows if row["CandidateGate"].startswith("Yu2022"))
    return [
        {
            "DecisionID": "SKG01",
            "Decision": "primary_next_gate",
            "Status": "select_WHISP_radial_lopsidedness_extension",
            "Evidence": (
                f"WHISP N={whisp['CoverageN']} AUC={whisp['PrimaryValue']} "
                f"Pearson={whisp['SecondaryValue']}"
            ),
            "NextAction": "build_predeclared_WHISP_style_radial_asymmetry_expansion_or_holdout_packet",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "SKG02",
            "Decision": "mandatory_control",
            "Status": "retain_THINGS_non_circular_competition_control",
            "Evidence": (
                f"THINGS N={things['CoverageN']} P05_AUC={things['PrimaryValue']} "
                f"non_circular_over_vmax_Pearson={things['SecondaryValue']}"
            ),
            "NextAction": "do_not_interpret_WHISP_signal_without_THINGS_style_kinematic_control",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "SKG03",
            "Decision": "negative_proxy_boundary",
            "Status": "do_not_promote_Yu_global_Af_Ac",
            "Evidence": (
                f"Yu N={yu['CoverageN']} AUC={yu['PrimaryValue']} "
                f"Spearman={yu['SecondaryValue']}"
            ),
            "NextAction": "use_Yu_as_negative_control_or_coverage_reference_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(rows: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    by_decision = {row["DecisionID"]: row for row in decisions}
    lines = [
        "# Spatial/Kinematic Proxy Next Gate v0.1",
        "",
        "This packet ranks the next validation direction after the Yu et al. (2022) global `Af/Ac` readout. It does not fit a new endpoint, does not change `W_tau_eff`, and does not define a velocity formula.",
        "",
        "## Decision",
        "",
        f"- Primary next gate: {by_decision['SKG01']['Status']}",
        f"- Mandatory control: {by_decision['SKG02']['Status']}",
        f"- Negative proxy boundary: {by_decision['SKG03']['Status']}",
        "",
        "## Rationale",
        "",
        "The global ALFALFA profile-asymmetry readout has useful coverage but does not point in the expected direction. The next useful proxy must therefore be more spatially resolved, more radial, or more kinematically targeted.",
        "",
        "WHISP is prioritized because it already gives the strongest external source-family readout in this packet and includes HI lopsidedness/asymmetry quantities with radial structure. THINGS remains mandatory as a non-circular-motion competition control, because a positive disturbance/residual relation could still be ordinary kinematic disequilibrium rather than a Tau Core environment/observer field.",
        "",
        "## Generated Files",
        "",
        "- `spatial_kinematic_proxy_next_gate_matrix_v01.csv`",
        "- `spatial_kinematic_proxy_next_gate_decision_v01.csv`",
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
    for path in [MATRIX_OUT, DECISION_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["spatial_kinematic_proxy_next_gate_status"] = (
        "WHISP_radial_lopsidedness_extension_selected_THINGS_control_required"
    )
    manifest["paper2_next_gate"] = "WHISP_radial_lopsidedness_expansion_with_THINGS_control"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = source_rows()
    decisions = decision_rows(rows)
    write_csv(
        MATRIX_OUT,
        rows,
        [
            "CandidateGate",
            "ProxyIDs",
            "ResolutionClass",
            "ReadinessTier",
            "CoverageN",
            "PrimaryMetric",
            "PrimaryValue",
            "SecondaryMetric",
            "SecondaryValue",
            "ResultDirection",
            "UseNext",
            "Reason",
            "RequiredNextAction",
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
            "Evidence",
            "NextAction",
            "InterpretationGuardrail",
        ],
    )
    write_report(rows, decisions)
    update_manifest()
    print(REPORT)
    print("primary_next_gate=WHISP_radial_lopsidedness_extension")
    print("mandatory_control=THINGS_non_circular_competition_control")


if __name__ == "__main__":
    main()
