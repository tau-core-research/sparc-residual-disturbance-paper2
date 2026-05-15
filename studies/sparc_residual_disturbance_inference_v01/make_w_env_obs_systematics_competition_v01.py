#!/usr/bin/env python3
"""Build the W_env_obs systematics competition gate."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from make_packet_v01_seed import PACKET, ROOT, read_csv, write_csv


TAU_CORE = ROOT.parent / "tau-core"
TAU_PACKET = TAU_CORE / "studies/sparc_radial_s_tau_pilot_v01/packet_v01_seed"
PAPER1_TAU_PACKET = (
    TAU_CORE
    / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced"
)

W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
P01_METRICS = PACKET / "proxy_direction_w_tau_eff_metric_summary_v01.csv"
P07_METRICS = PACKET / "p07_whisp_w_tau_eff_holdout_metric_summary_v01.csv"
P05_METRICS = PACKET / "p05_things_non_circular_w_tau_eff_control_metrics_v01.csv"
P05_DECISIONS = PACKET / "p05_things_non_circular_w_tau_eff_control_decision_v01.csv"
P09_METRICS = PACKET / "p09_observability_decomposition_metrics_v01.csv"
P09_DECISIONS = PACKET / "p09_observability_decomposition_decision_v01.csv"

THINGS_HARMONIC_SRC = TAU_PACKET / "things_published_harmonic_residual_joined_galaxies.csv"
LITTLE_PRESSURE_SRC = TAU_PACKET / "littlethings_pressure_support_galaxy_summary.csv"
HALOGAS_SRC = TAU_PACKET / "path_b_halogas_h07_lr_cube_galaxy_summary.csv"
INCLINATION_SRC = PAPER1_TAU_PACKET / "inclination_systematics_summary.csv"

THINGS_HARMONIC_OUT = PACKET / "systematics_control_things_harmonic_summary_v01.csv"
LITTLE_PRESSURE_OUT = PACKET / "systematics_control_littlethings_pressure_summary_v01.csv"
HALOGAS_OUT = PACKET / "systematics_control_halogas_linewidth_summary_v01.csv"
INCLINATION_OUT = PACKET / "systematics_control_inclination_summary_v01.csv"

MATRIX_OUT = PACKET / "w_env_obs_systematics_competition_matrix_v01.csv"
COVERAGE_OUT = PACKET / "w_env_obs_systematics_competition_coverage_v01.csv"
READINESS_OUT = PACKET / "w_env_obs_systematics_competition_readiness_v01.csv"
REPORT_OUT = PACKET / "w_env_obs_systematics_competition_v01.md"

GUARDRAIL = "systematics_competition_no_attribution_no_velocity_endpoint"


def metric_value(path: Path, metric: str) -> str:
    for row in read_csv(path):
        if row["Metric"] == metric:
            return row["Value"]
    raise KeyError(metric)


def optional_metric_value(path: Path, metric: str) -> str:
    if not path.exists():
        return ""
    return metric_value(path, metric)


def optional_decision_status(path: Path, decision_id: str) -> str:
    if not path.exists():
        return ""
    for row in read_csv(path):
        if row["DecisionID"] == decision_id:
            return row["Status"]
    return ""


def joined_count(rows: list[dict[str, str]], w_names: set[str]) -> int:
    return sum(1 for row in rows if row["GalaxyName"] in w_names)


def classes(rows: list[dict[str, str]]) -> str:
    values = sorted(
        {
            row.get("ClassAuditOnly", row.get("Class", ""))
            for row in rows
            if row.get("ClassAuditOnly", row.get("Class", ""))
        }
    )
    return ";".join(values)


def sanitize_things_harmonic() -> list[dict[str, str]]:
    fields = [
        "GalaxyName",
        "PublishedName",
        "ClassAuditOnly",
        "NResidualPoints",
        "MedianNonCircularAmplitudeKms",
        "MedianNonCircularAmplitudeInner1KpcKms",
        "NonCircularAmplitudeOverVmaxPercent",
        "MedianAbsResidualVelocityAfterHarmonicKms",
        "RmaxArcsec",
        "SourceArxiv",
    ]
    rows = []
    for row in read_csv(THINGS_HARMONIC_SRC):
        out = {field: row.get(field, "") for field in fields}
        out["ControlUse"] = "published_harmonic_non_circular_control_only"
        out["InterpretationGuardrail"] = GUARDRAIL
        rows.append(out)
    write_csv(THINGS_HARMONIC_OUT, rows, fields + ["ControlUse", "InterpretationGuardrail"])
    return rows


def sanitize_little_pressure() -> list[dict[str, str]]:
    fields = [
        "GalaxyName",
        "ClassAuditOnly",
        "NJoinedPoints",
        "MedianSigmaOverVc",
        "MedianInnerSigmaOverVc",
        "P80SigmaOverVc",
        "MedianPressureProxyKms",
        "ReadoutStatus",
    ]
    rows = []
    for row in read_csv(LITTLE_PRESSURE_SRC):
        out = {field: row.get(field, "") for field in fields}
        out["ControlUse"] = "dwarf_pressure_support_control_only"
        out["InterpretationGuardrail"] = GUARDRAIL
        rows.append(out)
    write_csv(LITTLE_PRESSURE_OUT, rows, fields + ["ControlUse", "InterpretationGuardrail"])
    return rows


def sanitize_halogas() -> list[dict[str, str]]:
    fields = [
        "GalaxyName",
        "ClassAuditOnly",
        "NJoinedPoints",
        "MeanRadiusFractionDelta",
        "MedianNormalizedLinewidthStress",
        "ReadoutStatus",
    ]
    rows = []
    for row in read_csv(HALOGAS_SRC):
        out = {field: row.get(field, "") for field in fields}
        out["ControlUse"] = "external_linewidth_stress_control_only"
        out["InterpretationGuardrail"] = GUARDRAIL
        rows.append(out)
    write_csv(HALOGAS_OUT, rows, fields + ["ControlUse", "InterpretationGuardrail"])
    return rows


def sanitize_inclination() -> list[dict[str, str]]:
    fields = ["InclinationBinDeg", "Class", "N", "MedianRmsLog"]
    rows = []
    for row in read_csv(INCLINATION_SRC):
        out = {field: row.get(field, "") for field in fields}
        out["ControlUse"] = "inclination_observability_control_summary_only"
        out["InterpretationGuardrail"] = GUARDRAIL
        rows.append(out)
    write_csv(INCLINATION_OUT, rows, fields + ["ControlUse", "InterpretationGuardrail"])
    return rows


def build_matrix() -> list[dict[str, str]]:
    p01_auc = metric_value(P01_METRICS, "auc_high_vs_low_score")
    p07_auc = metric_value(P07_METRICS, "auc_high_vs_low_whisp_burden")
    p07_pearson = metric_value(P07_METRICS, "pearson_whisp_burden_vs_w_tau_score")
    p05_pearson = optional_metric_value(P05_METRICS, "pearson_p05_burden_vs_w_tau_score")
    p05_auc = optional_metric_value(P05_METRICS, "auc_high_vs_low_p05_burden")
    p05_status = optional_decision_status(P05_DECISIONS, "P05D01")
    p09_status = optional_decision_status(P09_DECISIONS, "P09D01")
    p09_recon_auc = optional_metric_value(P09_METRICS, "auc_high_vs_low_reconstruction_risk")
    p09_geometry_auc = optional_metric_value(P09_METRICS, "auc_high_vs_low_observer_geometry")
    if p05_pearson and p05_auc:
        p05_readout = f"Pearson={p05_pearson};AUC={p05_auc};Status={p05_status}"
        p05_decision = "does_not_absorb_direction_in_small_overlap"
        p05_required = "proceed_to_P09_observability_join_keep_P05_as_control"
    else:
        p05_readout = "published_harmonic_columns_available_no_regression"
        p05_decision = "must_control_before_velocity_formula"
        p05_required = "join_P05_to_W_tau_eff_on_overlap_without_using_residual_columns"
    if p09_recon_auc and p09_geometry_auc:
        p09_readout = (
            f"ReconstructionRiskAUC={p09_recon_auc};"
            f"ObserverGeometryAUC={p09_geometry_auc};Status={p09_status}"
        )
        p09_decision = "ordinary_observability_risk_competes_with_signal"
        p09_required = "distance_resolution_environment_join_before_formula"
    else:
        p09_readout = "binned_summary_available_not_galaxy_level_competition"
        p09_decision = "blocks_attribution_until_galaxy_level_join"
        p09_required = "galaxy_level_inclination_resolution_distance_join"
    return [
        {
            "ControlID": "S01",
            "ProxyID": "P05",
            "ControlFamily": "THINGS_published_harmonic_non_circular",
            "CoverageType": "small_overlap_galaxy_level",
            "CoverageN": "7",
            "CompetitionRole": "direct_non_circular_motion_control",
            "CanCompeteNow": "partial_small_overlap",
            "MainThreat": "non_circular_motion_can_mimic_signed_residual_drift",
            "CurrentReadout": p05_readout,
            "Decision": p05_decision,
            "RequiredNextControl": p05_required,
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ControlID": "S02",
            "ProxyID": "P06",
            "ControlFamily": "LITTLE_THINGS_pressure_support",
            "CoverageType": "very_small_dwarf_overlap",
            "CoverageN": "3",
            "CompetitionRole": "pressure_support_and_baryonic_dwarf_control",
            "CanCompeteNow": "insufficient_overlap",
            "MainThreat": "pressure_support_can_shift_low_velocity_dwarf_rotation_curves",
            "CurrentReadout": "pressure_summary_available_control_only",
            "Decision": "control_only_until_more_overlap",
            "RequiredNextControl": "expand_dwarf_overlap_before_formula_claim",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ControlID": "S03",
            "ProxyID": "P08",
            "ControlFamily": "HALOGAS_LR_cube_linewidth_stress",
            "CoverageType": "small_external_family_overlap",
            "CoverageN": "5",
            "CompetitionRole": "external_linewidth_stress_control",
            "CanCompeteNow": "weak_small_overlap",
            "MainThreat": "linewidth_stress_or_resolution_can_absorb_candidate_weight_signal",
            "CurrentReadout": "weak_external_family_control_available",
            "Decision": "retain_as_negative_or_weak_control",
            "RequiredNextControl": "do_not_promote_without_larger_overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ControlID": "S04",
            "ProxyID": "P09",
            "ControlFamily": "inclination_systematics",
            "CoverageType": "binned_summary",
            "CoverageN": "7_summary_rows",
            "CompetitionRole": "mandatory_observability_control",
            "CanCompeteNow": "summary_only",
            "MainThreat": "deprojection_edge_on_and_observability_bias_can_drive_apparent_disturbance",
            "CurrentReadout": p09_readout,
            "Decision": p09_decision,
            "RequiredNextControl": p09_required,
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ControlID": "S05",
            "ProxyID": "P01",
            "ControlFamily": "paper1_external_evidence_type",
            "CoverageType": "broad_prior_joined_to_W_tau_eff",
            "CoverageN": "45",
            "CompetitionRole": "positive_source_side_direction_readout",
            "CanCompeteNow": "yes_as_direction_not_attribution",
            "MainThreat": "positive_direction_could_be_observability_or_non_circular_motion",
            "CurrentReadout": f"AUC={p01_auc}",
            "Decision": "positive_candidate_direction_not_formula",
            "RequiredNextControl": "compare_against_P05_and_P09_controls",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ControlID": "S06",
            "ProxyID": "P07",
            "ControlFamily": "WHISP_lopsidedness_asymmetry",
            "CoverageType": "source_family_holdout_overlap",
            "CoverageN": "10",
            "CompetitionRole": "positive_source_family_holdout",
            "CanCompeteNow": "yes_small_overlap",
            "MainThreat": "HI_asymmetry_can_trace_disturbance_without_unique_tau_core_attribution",
            "CurrentReadout": f"AUC={p07_auc};Pearson={p07_pearson}",
            "Decision": "positive_holdout_but_small_sample",
            "RequiredNextControl": "replicate_with_THINGS_controls_and_larger_external_sample",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def build_coverage(
    things_rows: list[dict[str, str]],
    little_rows: list[dict[str, str]],
    halogas_rows: list[dict[str, str]],
    inclination_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    w_names = {row["GalaxyName"] for row in read_csv(W_TAU)}
    p01_joined = metric_value(P01_METRICS, "coverage_joined")
    p07_joined = metric_value(P07_METRICS, "coverage_joined")
    return [
        {
            "Family": "P01_paper1_external_evidence",
            "SourceFile": "external_evidence_table.csv",
            "Rows": "73",
            "JoinedWithWTauEff": p01_joined,
            "Classes": "A;B;C",
            "UsableFor": "broad_direction_readout",
            "Limitation": "coarse_literature_label_prior",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Family": "P07_WHISP_lopsidedness",
            "SourceFile": "whisp_vaneymeren2011_overlap.csv",
            "Rows": "14",
            "JoinedWithWTauEff": p07_joined,
            "Classes": "B;C",
            "UsableFor": "small_source_family_holdout",
            "Limitation": "small_and_class_imbalanced_overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Family": "P05_THINGS_harmonic_non_circular",
            "SourceFile": THINGS_HARMONIC_OUT.name,
            "Rows": str(len(things_rows)),
            "JoinedWithWTauEff": str(joined_count(things_rows, w_names)),
            "Classes": classes(things_rows),
            "UsableFor": "non_circular_motion_control",
            "Limitation": "small_overlap_and_galaxy_level_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Family": "P06_LITTLE_THINGS_pressure",
            "SourceFile": LITTLE_PRESSURE_OUT.name,
            "Rows": str(len(little_rows)),
            "JoinedWithWTauEff": str(joined_count(little_rows, w_names)),
            "Classes": classes(little_rows),
            "UsableFor": "dwarf_pressure_support_control",
            "Limitation": "very_small_overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Family": "P08_HALOGAS_linewidth",
            "SourceFile": HALOGAS_OUT.name,
            "Rows": str(len(halogas_rows)),
            "JoinedWithWTauEff": str(joined_count(halogas_rows, w_names)),
            "Classes": classes(halogas_rows),
            "UsableFor": "external_linewidth_stress_control",
            "Limitation": "weak_small_overlap_control",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Family": "P09_inclination_systematics",
            "SourceFile": INCLINATION_OUT.name,
            "Rows": str(len(inclination_rows)),
            "JoinedWithWTauEff": "binned_summary",
            "Classes": classes(inclination_rows),
            "UsableFor": "observability_control",
            "Limitation": "not_yet_galaxy_level_in_public_packet",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def build_readiness() -> list[dict[str, str]]:
    p05_status = optional_decision_status(P05_DECISIONS, "P05D01")
    p05_complete = p05_status == "does_not_absorb_direction_in_small_overlap"
    p09_status = optional_decision_status(P09_DECISIONS, "P09D01")
    p09_complete = p09_status == "ordinary_observability_risk_competes_with_signal"
    return [
        {
            "DecisionID": "D01",
            "Decision": "positive_source_side_direction_exists",
            "Status": "supported_but_not_attributed",
            "Rationale": "P01 AUC=0.774159664 and P07 AUC=0.760000000 both point in the expected direction.",
            "Blocks": "tau_core_attribution;velocity_formula",
            "NextAction": "compete_positive_direction_against_P05_non_circular_and_P09_inclination_controls",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "D02",
            "Decision": "systematics_competition",
            "Status": (
                "open_blocker_for_formula"
                if not p05_complete
                else "ordinary_observability_risk_now_primary_blocker"
                if p09_complete
                else "partially_reduced_blocker"
            ),
            "Rationale": (
                "Non-circular motion, pressure support, linewidth stress, and inclination/observability are not yet defeated at galaxy level."
                if not p05_complete
                else "P05 does not absorb the direction in the seven-galaxy overlap, but inclination/observability remains unresolved."
                if not p09_complete
                else "P05 does not absorb the direction, but P09 shows ordinary reconstruction/observability risk competes with the score."
            ),
            "Blocks": "S_tau_full_formula_freeze;field_map_attribution",
            "NextAction": (
                "run_P05_non_circular_overlap_control_before_any_velocity_endpoint"
                if not p05_complete
                else "run_P09_galaxy_level_inclination_observability_join"
                if not p09_complete
                else "run_distance_resolution_environment_join_before_formula"
            ),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "D03",
            "Decision": "velocity_endpoint_with_S_tau_full",
            "Status": "blocked",
            "Rationale": "A positive W_tau_eff proxy direction cannot be promoted to a fitted velocity formula before controls compete.",
            "Blocks": "velocity_readout;coefficient_selection",
            "NextAction": "keep_velocity_endpoint_closed_until_control_matrix_has_a_pass_condition",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "D04",
            "Decision": "next_paper2_gate",
            "Status": "ready",
            "Rationale": (
                "The safest next gate is a small but explicit P05 overlap control using only published harmonic non-circular columns."
                if not p05_complete
                else "The P05 overlap control is complete; the remaining key gate is galaxy-level observability/inclination."
                if not p09_complete
                else "P09 galaxy-level observability decomposition is complete; distance, resolution, and environment must be joined before any formula endpoint."
            ),
            "Blocks": "none_for_control_gate",
            "NextAction": (
                "P05_non_circular_overlap_control_before_S_tau_formula"
                if not p05_complete
                else "P09_galaxy_level_inclination_observability_join"
                if not p09_complete
                else "distance_resolution_environment_join_before_formula"
            ),
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(
    matrix: list[dict[str, str]],
    coverage: list[dict[str, str]],
    readiness: list[dict[str, str]],
) -> None:
    p01 = next(row for row in matrix if row["ControlID"] == "S05")
    p07 = next(row for row in matrix if row["ControlID"] == "S06")
    p05 = next(row for row in matrix if row["ControlID"] == "S01")
    p09 = next(row for row in matrix if row["ControlID"] == "S04")
    lines = [
        "# W_env_obs Systematics Competition v0.1",
        "",
        "This gate asks whether the current source-side `W_tau_eff` direction can survive obvious competing explanations. It is a control matrix, not a new positive endpoint.",
        "",
        "## Positive Direction Still Present",
        "",
        f"- P01 broad external-evidence direction: `{p01['CurrentReadout']}`.",
        f"- P07 WHISP source-family holdout: `{p07['CurrentReadout']}`.",
        "",
        "These are useful candidate signals, but they do not attribute the residual-inferred weight to Tau Core.",
        "",
        "## Main Open Competitors",
        "",
        f"- P05 non-circular motion control: `{p05['Decision']}`.",
        "- P06 pressure-support control: control-only until overlap expands.",
        "- P08 HALOGAS linewidth stress: retain as a weak or negative control.",
        f"- P09 inclination/observability: `{p09['Decision']}`.",
        "",
        "## Decision",
        "",
        "The branch is positive as a proxy-direction result and still blocked as a physical attribution result. The next allowed gate is `P05_non_circular_overlap_control_before_S_tau_formula`. The velocity endpoint remains closed.",
        "",
        "## Generated Files",
        "",
        "- `w_env_obs_systematics_competition_matrix_v01.csv`",
        "- `w_env_obs_systematics_competition_coverage_v01.csv`",
        "- `w_env_obs_systematics_competition_readiness_v01.csv`",
        "- `systematics_control_things_harmonic_summary_v01.csv`",
        "- `systematics_control_littlethings_pressure_summary_v01.csv`",
        "- `systematics_control_halogas_linewidth_summary_v01.csv`",
        "- `systematics_control_inclination_summary_v01.csv`",
        "",
        "## Guardrail",
        "",
        f"`{GUARDRAIL}`",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [
        THINGS_HARMONIC_OUT,
        LITTLE_PRESSURE_OUT,
        HALOGAS_OUT,
        INCLINATION_OUT,
        MATRIX_OUT,
        COVERAGE_OUT,
        READINESS_OUT,
        REPORT_OUT,
    ]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["w_env_obs_systematics_competition_status"] = (
        "systematics_competition_matrix_complete_no_attribution"
    )
    if P09_DECISIONS.exists():
        next_gate = "distance_resolution_environment_join_before_formula"
    elif P05_DECISIONS.exists():
        next_gate = "P09_galaxy_level_inclination_observability_join"
    else:
        next_gate = "P05_non_circular_overlap_control_before_S_tau_formula"
    manifest["paper2_next_gate"] = next_gate
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    things_rows = sanitize_things_harmonic()
    little_rows = sanitize_little_pressure()
    halogas_rows = sanitize_halogas()
    inclination_rows = sanitize_inclination()

    matrix = build_matrix()
    coverage = build_coverage(things_rows, little_rows, halogas_rows, inclination_rows)
    readiness = build_readiness()

    matrix_fields = [
        "ControlID",
        "ProxyID",
        "ControlFamily",
        "CoverageType",
        "CoverageN",
        "CompetitionRole",
        "CanCompeteNow",
        "MainThreat",
        "CurrentReadout",
        "Decision",
        "RequiredNextControl",
        "InterpretationGuardrail",
    ]
    coverage_fields = [
        "Family",
        "SourceFile",
        "Rows",
        "JoinedWithWTauEff",
        "Classes",
        "UsableFor",
        "Limitation",
        "InterpretationGuardrail",
    ]
    readiness_fields = [
        "DecisionID",
        "Decision",
        "Status",
        "Rationale",
        "Blocks",
        "NextAction",
        "InterpretationGuardrail",
    ]
    write_csv(MATRIX_OUT, matrix, matrix_fields)
    write_csv(COVERAGE_OUT, coverage, coverage_fields)
    write_csv(READINESS_OUT, readiness, readiness_fields)
    write_report(matrix, coverage, readiness)
    update_manifest()


if __name__ == "__main__":
    main()
