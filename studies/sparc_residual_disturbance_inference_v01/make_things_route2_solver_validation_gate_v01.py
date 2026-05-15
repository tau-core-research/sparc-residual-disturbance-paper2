#!/usr/bin/env python3
"""Define the route 2 solver validation gate before missing-galaxy scoring."""

from __future__ import annotations

import csv
import json

from make_packet_v01_seed import PACKET, write_csv


SOURCE_SUMMARY = PACKET / "things_source_s_tau_velocity_galaxy_summary.csv"
TABLE3_SCORES = PACKET / "things_table3_expanded_w_tau_eff_scores_v01.csv"

VALIDATION_TARGETS = PACKET / "things_route2_solver_validation_targets_v01.csv"
VALIDATION_REQUIREMENTS = PACKET / "things_route2_solver_validation_requirements_v01.csv"
VALIDATION_GATE = PACKET / "things_route2_solver_validation_gate_v01.csv"
REPORT = PACKET / "things_route2_solver_validation_gate_v01.md"

GUARDRAIL = "route2_solver_validation_before_missing_galaxy_scores"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def source_overlap() -> dict[str, dict[str, str]]:
    rows = read_csv(SOURCE_SUMMARY)
    return {row["GalaxyName"]: row for row in rows}


def table3_scores() -> dict[str, dict[str, str]]:
    rows = read_csv(TABLE3_SCORES)
    return {row["GalaxyName"]: row for row in rows}


def validation_target_rows() -> list[dict[str, str]]:
    source = source_overlap()
    table3 = table3_scores()
    candidates = [
        ("DDO154", "anchor_low_mass_high_quality_overlap"),
        ("NGC2366", "anchor_disturbed_c_overlap"),
        ("NGC2403", "anchor_high_point_count_a_overlap"),
        ("NGC2976", "anchor_c_overlap"),
        ("NGC3198", "anchor_regular_disk_overlap"),
        ("NGC5055", "anchor_c_overlap_with_existing_improvement"),
        ("NGC7331", "anchor_massive_disk_overlap"),
    ]
    rows = []
    for galaxy, role in candidates:
        src = source[galaxy]
        score = table3[galaxy]
        rows.append(
            {
                "GalaxyName": galaxy,
                "ValidationRole": role,
                "Class": src["Class"],
                "ExistingSparcReference": "yes",
                "ExistingWtauEffSeed": "yes",
                "ExistingPointCount": src["NPoints"],
                "THINGSNonCircularTable3": "yes",
                "LocalRotmodReferencePath": score["LocalRotmodPath"],
                "RequiredRawInputsForValidation": "THINGS_MOM0;SINGS_IRAC1;fixed_geometry",
                "ValidationUse": "solver_reconstruction_accuracy_only_not_tau_endpoint",
                "ForbiddenUse": "choose_solver_or_tolerance_by_W_tau_eff_direction",
                "CanScoreMissingGalaxiesNow": "no",
                "Guardrail": GUARDRAIL,
            }
        )
    return rows


def requirement_rows() -> list[dict[str, str]]:
    return [
        {
            "RequirementID": "R2VAL01",
            "Requirement": "stage_validation_raw_inputs",
            "PassCondition": "at_least_three_validation_galaxies_have_THINGS_MOM0_and_SINGS_IRAC1_products_staged_outside_git",
            "FailureAction": "do_not_apply_solver_to_NGC925_NGC3031",
            "CanScoreMissingGalaxiesNow": "no",
            "Guardrail": GUARDRAIL,
        },
        {
            "RequirementID": "R2VAL02",
            "Requirement": "derive_component_profiles_without_endpoint_feedback",
            "PassCondition": "Vgas_Vdisk_Vbul_profiles_are_derived_from_source_images_using_frozen_geometry_conversion_solver_policy",
            "FailureAction": "do_not_apply_solver_to_NGC925_NGC3031",
            "CanScoreMissingGalaxiesNow": "no",
            "Guardrail": GUARDRAIL,
        },
        {
            "RequirementID": "R2VAL03",
            "Requirement": "compare_to_existing_SPARC_component_curves",
            "PassCondition": "median_absolute_fractional_component_error_le_0p15_for_at_least_three_validation_galaxies",
            "FailureAction": "revise_solver_only_before_any_missing_score_and_restart_validation",
            "CanScoreMissingGalaxiesNow": "no",
            "Guardrail": GUARDRAIL,
        },
        {
            "RequirementID": "R2VAL04",
            "Requirement": "freeze_validation_report_before_missing_scores",
            "PassCondition": "report_contains_per_component_errors_failures_and_no_W_tau_eff_endpoint_tuning",
            "FailureAction": "keep_route2_as_not_score_ready",
            "CanScoreMissingGalaxiesNow": "no",
            "Guardrail": GUARDRAIL,
        },
    ]


def gate_rows(targets: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "GateID": "R2VALG01",
            "Status": "validation_targets_defined_from_existing_THINGS_SPARC_overlap",
            "Evidence": f"N_targets={len(targets)}",
            "CanApplySolverToMissingGalaxies": "no",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "stage_validation_raw_inputs_for_at_least_three_targets",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2VALG02",
            "Status": "validation_raw_inputs_not_yet_staged",
            "Evidence": "no_validation_MOM0_IRAC_stack_manifest_yet",
            "CanApplySolverToMissingGalaxies": "no",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "download_or_stage_source_products_outside_public_repo",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2VALG03",
            "Status": "solver_not_yet_accuracy_validated",
            "Evidence": "no_component_error_table_yet",
            "CanApplySolverToMissingGalaxies": "no",
            "CanScoreMissingGalaxiesNow": "no",
            "NextAction": "derive_blind_component_profiles_and_compare_to_SPARC_reference",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report(targets: list[dict[str, str]], gates: list[dict[str, str]]) -> None:
    names = ", ".join(row["GalaxyName"] for row in targets)
    lines = [
        "# THINGS Route 2 Solver Validation Gate v0.1",
        "",
        "This gate defines the validation path for the route 2 component-derivation solver before any missing THINGS galaxy is scored.",
        "",
        "## Validation Targets",
        "",
        f"Frozen validation targets: {names}.",
        "",
        "These galaxies already have SPARC-compatible component curves in the local reference workflow and THINGS non-circular-motion context. They are therefore suitable for validating the reconstruction solver against known component curves without using the missing-galaxy endpoint.",
        "",
        "## Pass Standard",
        "",
        "At least three validation galaxies must have source products staged outside git, blind component profiles derived under the frozen route 2 policy, and median absolute fractional component error <= 0.15 against existing SPARC component curves.",
        "",
        "## Current Decision",
        "",
    ]
    for gate in gates:
        lines.append(f"- `{gate['GateID']}`: {gate['Status']}; score={gate['CanScoreMissingGalaxiesNow']}.")
    lines.extend(
        [
            "",
            "No missing-galaxy score may be computed from route 2 until this validation gate passes.",
            "No solver or tolerance may be selected using `W_tau_eff` direction.",
            "",
            f"Guardrail: `{GUARDRAIL}`",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [VALIDATION_TARGETS, VALIDATION_REQUIREMENTS, VALIDATION_GATE, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_route2_solver_validation_status"] = (
        "validation_targets_and_pass_conditions_frozen_inputs_not_yet_staged"
    )
    manifest["paper2_next_gate"] = (
        "route2_stage_solver_validation_inputs_for_at_least_three_overlap_galaxies"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    targets = validation_target_rows()
    requirements = requirement_rows()
    gates = gate_rows(targets)
    write_csv(
        VALIDATION_TARGETS,
        targets,
        [
            "GalaxyName",
            "ValidationRole",
            "Class",
            "ExistingSparcReference",
            "ExistingWtauEffSeed",
            "ExistingPointCount",
            "THINGSNonCircularTable3",
            "LocalRotmodReferencePath",
            "RequiredRawInputsForValidation",
            "ValidationUse",
            "ForbiddenUse",
            "CanScoreMissingGalaxiesNow",
            "Guardrail",
        ],
    )
    write_csv(
        VALIDATION_REQUIREMENTS,
        requirements,
        [
            "RequirementID",
            "Requirement",
            "PassCondition",
            "FailureAction",
            "CanScoreMissingGalaxiesNow",
            "Guardrail",
        ],
    )
    write_csv(
        VALIDATION_GATE,
        gates,
        [
            "GateID",
            "Status",
            "Evidence",
            "CanApplySolverToMissingGalaxies",
            "CanScoreMissingGalaxiesNow",
            "NextAction",
            "Guardrail",
        ],
    )
    write_report(targets, gates)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
