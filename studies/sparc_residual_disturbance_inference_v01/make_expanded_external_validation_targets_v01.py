#!/usr/bin/env python3
"""Freeze expanded non-WHISP external validation targets for Paper 2."""

from __future__ import annotations

import json

from make_packet_v01_seed import PACKET, write_csv


TARGET_OUT = PACKET / "expanded_external_validation_targets_v01.csv"
PASS_FAIL_OUT = PACKET / "expanded_external_validation_pass_fail_v01.csv"
REPORT = PACKET / "expanded_external_validation_targets_v01.md"

GUARDRAIL = "expanded_external_validation_targets_no_velocity_endpoint_no_formula_fit"


def target_rows() -> list[dict[str, str]]:
    return [
        {
            "TargetID": "EVT01",
            "SourceFamily": "THINGS harmonic velocity-field controls",
            "PrimaryObservable": "published non-circular motion amplitudes and harmonic residual terms",
            "CurrentOverlapN": "7",
            "MinimumDirectionalN": "12",
            "MinimumBalancedClasses": "at_least_4_A_and_4_C",
            "Endpoint": "W_tau_eff_direction_only",
            "PassCondition": (
                "same-sign Pearson or Spearman versus W_tau_eff and AUC>=0.60 "
                "without using Vobs residuals as predictors"
            ),
            "FailureCondition": (
                "direction reverses or becomes null after class/observability checks"
            ),
            "RoleIfPasses": "required_non_circular_motion_competitor_or_supporting_control",
            "RoleIfFails": "do_not_use_THINGS_as_positive_external_validation",
            "Priority": "high",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "TargetID": "EVT02",
            "SourceFamily": "LITTLE THINGS dwarf pressure-support controls",
            "PrimaryObservable": "sigma_over_vc or pressure-support proxy from HI kinematic summaries",
            "CurrentOverlapN": "2",
            "MinimumDirectionalN": "10",
            "MinimumBalancedClasses": "at_least_3_A_or_regular_and_3_C_or_disturbed",
            "Endpoint": "dwarf_pressure_systematics_only",
            "PassCondition": (
                "pressure proxy either explains W_tau_eff variance or is shown not to absorb "
                "the W_tau_eff direction"
            ),
            "FailureCondition": "coverage remains too small for directional inference",
            "RoleIfPasses": "dwarf_specific_systematics_control",
            "RoleIfFails": "exclude_from_primary_external_validation_claim",
            "Priority": "medium",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "TargetID": "EVT03",
            "SourceFamily": "HALOGAS linewidth or cube-derived stress",
            "PrimaryObservable": "linewidth stress, outer-disk HI disturbance, or matched cube proxy",
            "CurrentOverlapN": "5",
            "MinimumDirectionalN": "10",
            "MinimumBalancedClasses": "at_least_3_A_and_3_C",
            "Endpoint": "linewidth_stress_control_only",
            "PassCondition": (
                "linewidth/stress proxy has a predeclared monotonic relation to W_tau_eff "
                "with AUC>=0.60 or documents a null control"
            ),
            "FailureCondition": "proxy remains weak, noisy, or too sparse",
            "RoleIfPasses": "independent_HI_cube_family_control",
            "RoleIfFails": "retain_as_weak_control_only",
            "Priority": "medium",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "TargetID": "EVT04",
            "SourceFamily": "Non-WHISP resolved HI asymmetry catalogues",
            "PrimaryObservable": "resolved HI lopsidedness, asymmetry, warp, or disturbance flags",
            "CurrentOverlapN": "0",
            "MinimumDirectionalN": "15",
            "MinimumBalancedClasses": "at_least_5_A_and_5_C",
            "Endpoint": "external_asymmetry_direction_replication",
            "PassCondition": (
                "positive W_tau_eff direction repeats outside WHISP under the same frozen "
                "sign convention"
            ),
            "FailureCondition": "non-WHISP asymmetry family does not reproduce the WHISP direction",
            "RoleIfPasses": "strongest_near_term_external_validation_candidate",
            "RoleIfFails": "treat_WHISP_positive_result_as_source_family_specific",
            "Priority": "high",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "TargetID": "EVT05",
            "SourceFamily": "Observer-distance and resolution matched external sample",
            "PrimaryObservable": "distance, angular size, resolution, inclination, and source-family disturbance",
            "CurrentOverlapN": "10",
            "MinimumDirectionalN": "20",
            "MinimumBalancedClasses": "distance_matched_A_C_or_source_family_matched_split",
            "Endpoint": "observer_distance_hypothesis_stress_only",
            "PassCondition": (
                "observer-distance partial relation remains positive after source-family, "
                "distance, angular-size, and inclination controls"
            ),
            "FailureCondition": "partial observer-distance relation remains null or reversed",
            "RoleIfPasses": "observer_distance_hypothesis_can_be_reopened_as_interpretation",
            "RoleIfFails": "park_observer_distance_interpretation",
            "Priority": "high",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def pass_fail_rows() -> list[dict[str, str]]:
    return [
        {
            "GateID": "EVG01",
            "Gate": "minimum_coverage",
            "PassRule": "at least one non-WHISP family reaches MinimumDirectionalN",
            "FailRule": "all non-WHISP families remain below MinimumDirectionalN",
            "CurrentStatus": "not_yet_met",
            "Blocks": "paper_grade_external_validation_claim",
            "NextAction": "expand_THINGS_or_non_WHISP_HI_asymmetry_overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "GateID": "EVG02",
            "Gate": "class_or_source_balance",
            "PassRule": "validation family includes both regular and disturbed systems or an explicit matched split",
            "FailRule": "validation family is single-class or only source-biased",
            "CurrentStatus": "not_yet_met",
            "Blocks": "observer_distance_claim",
            "NextAction": "require_balanced_or_matched_external_family",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "GateID": "EVG03",
            "Gate": "direction_replication",
            "PassRule": "predeclared external proxy direction reproduces W_tau_eff with AUC>=0.60",
            "FailRule": "direction reverses, collapses, or only appears after post-hoc tuning",
            "CurrentStatus": "open",
            "Blocks": "strong_W_tau_eff_external_validation_claim",
            "NextAction": "run_only_after_target_family_is_expanded",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "GateID": "EVG04",
            "Gate": "velocity_endpoint",
            "PassRule": "not allowed in this target-plan phase",
            "FailRule": "any coefficient fit or Vobs-residual-selected mapping is attempted",
            "CurrentStatus": "closed",
            "Blocks": "S_tau_full_velocity_formula",
            "NextAction": "keep_velocity_endpoint_closed",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(targets: list[dict[str, str]], gates: list[dict[str, str]]) -> None:
    lines = [
        "# Expanded External Validation Targets v0.1",
        "",
        "This packet freezes the next non-WHISP external validation targets after the WHISP observer-distance stress test. It is a target plan only: it does not add a velocity endpoint, does not fit a formula, and does not promote the observer-distance interpretation.",
        "",
        "## Target Order",
        "",
    ]
    for row in targets:
        lines.append(
            f"- {row['TargetID']} ({row['SourceFamily']}): priority={row['Priority']}; "
            f"minimum N={row['MinimumDirectionalN']}; endpoint={row['Endpoint']}."
        )
    lines.extend(
        [
            "",
            "## Pass/Fail Gates",
            "",
        ]
    )
    for row in gates:
        lines.append(f"- {row['GateID']} ({row['Gate']}): {row['CurrentStatus']}.")
    lines.extend(
        [
            "",
            "## Current Decision",
            "",
            "The next useful work is not another in-sample Tau Core interpretation. It is targeted external-data expansion. The highest-value path is either a larger non-WHISP resolved-HI asymmetry family or an expanded THINGS-like kinematic-control family with enough overlap for a predeclared directional readout.",
            "",
            "## Generated Files",
            "",
            "- `expanded_external_validation_targets_v01.csv`",
            "- `expanded_external_validation_pass_fail_v01.csv`",
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
    for path in [TARGET_OUT, PASS_FAIL_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["expanded_external_validation_targets_status"] = (
        "target_plan_frozen_no_velocity_endpoint"
    )
    manifest["paper2_next_gate"] = "expand_non_whisp_external_overlap"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    targets = target_rows()
    gates = pass_fail_rows()
    target_fields = [
        "TargetID",
        "SourceFamily",
        "PrimaryObservable",
        "CurrentOverlapN",
        "MinimumDirectionalN",
        "MinimumBalancedClasses",
        "Endpoint",
        "PassCondition",
        "FailureCondition",
        "RoleIfPasses",
        "RoleIfFails",
        "Priority",
        "InterpretationGuardrail",
    ]
    gate_fields = [
        "GateID",
        "Gate",
        "PassRule",
        "FailRule",
        "CurrentStatus",
        "Blocks",
        "NextAction",
        "InterpretationGuardrail",
    ]
    write_csv(TARGET_OUT, targets, target_fields)
    write_csv(PASS_FAIL_OUT, gates, gate_fields)
    write_report(targets, gates)
    update_manifest()


if __name__ == "__main__":
    main()
