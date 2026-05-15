#!/usr/bin/env python3
"""Freeze route 2 THINGS mass-model reconstruction protocol before scoring."""

from __future__ import annotations

import json
from pathlib import Path

from make_packet_v01_seed import PACKET, write_csv


PROTOCOL = PACKET / "things_route2_mass_model_reconstruction_protocol_v01.md"
INPUTS = PACKET / "things_route2_required_inputs_v01.csv"
RULES = PACKET / "things_route2_frozen_rules_v01.csv"
GATE = PACKET / "things_route2_scoring_gate_v01.csv"

GUARDRAIL = "route2_protocol_frozen_before_any_new_things_score"
MISSING = ["NGC925", "NGC3031", "NGC3621", "NGC3627", "NGC4736"]


def input_rows() -> list[dict[str, str]]:
    return [
        {
            "InputID": "R2I01",
            "Component": "ObservedRotationCurve",
            "RequiredField": "R_kpc;Vobs_kms;eVobs_kms",
            "PrimarySource": "published_THINGS_rotation_curve_or_committed_extraction_from_THINGS_velocity_field",
            "AllowedFallback": "none_without_documented_radius_grid_and_uncertainty_rule",
            "Forbidden": "digitize_final_mass_model_plot_without_error_model",
            "ScoreDependency": "required",
        },
        {
            "InputID": "R2I02",
            "Component": "GasVelocity",
            "RequiredField": "Vgas_kms",
            "PrimarySource": "published_HI_surface_density_profile_or_THINGS_moment0_map",
            "AllowedFallback": "derive_with_single_committed_thin_disk_rule_and_helium_factor",
            "Forbidden": "tune_gas_curve_to_match_Vobs_or_W_tau_eff",
            "ScoreDependency": "required",
        },
        {
            "InputID": "R2I03",
            "Component": "DiskVelocity",
            "RequiredField": "Vdisk_kms",
            "PrimarySource": "published_3p6um_profile_or_SINGS_equivalent_profile",
            "AllowedFallback": "derive_with_fixed_vertical_profile_and_fixed_ML_policy",
            "Forbidden": "fit_disk_ML_to_velocity_residuals",
            "ScoreDependency": "required",
        },
        {
            "InputID": "R2I04",
            "Component": "BulgeVelocity",
            "RequiredField": "Vbul_kms_or_zero_with_documented_no_bulge_policy",
            "PrimarySource": "published_bulge_disk_decomposition_or_protocol_bulge_rule",
            "AllowedFallback": "set_zero_only_if_protocol_classifies_no_required_bulge_component_before_scoring",
            "Forbidden": "toggle_bulge_component_after_viewing_score_direction",
            "ScoreDependency": "required_or_explicit_zero",
        },
        {
            "InputID": "R2I05",
            "Component": "Provenance",
            "RequiredField": "source_url;download_date;file_size_or_checksum;processing_script",
            "PrimarySource": "public_archive_or_literature_table",
            "AllowedFallback": "manual_transcription_only_with_double_entry_check",
            "Forbidden": "untracked_private_notes_or_unversioned_manual_edits",
            "ScoreDependency": "required",
        },
    ]


def frozen_rules() -> list[dict[str, str]]:
    return [
        {
            "RuleID": "R2F01",
            "Rule": "scoring_order",
            "FrozenChoice": "complete_inputs_and_protocol_first_then_score",
            "Reason": "prevents endpoint-driven reconstruction",
            "ForbiddenAfterFreeze": "change_component_rule_after_W_tau_eff_readout",
        },
        {
            "RuleID": "R2F02",
            "Rule": "radius_grid",
            "FrozenChoice": "use_published_rotation_curve_radius_grid_when_available_otherwise_commit_extraction_grid_before_component_calculation",
            "Reason": "keeps Vobs and baryonic components co-registered",
            "ForbiddenAfterFreeze": "interpolate_selectively_to_improve_residuals",
        },
        {
            "RuleID": "R2F03",
            "Rule": "gas_component",
            "FrozenChoice": "thin_disk_HI_component_with_1p4_helium_metals_factor_if_deriving_from_HI_surface_density",
            "Reason": "matches the de_Blok_THINGS_mass_model_description",
            "ForbiddenAfterFreeze": "vary_helium_or_disk_geometry_by_galaxy_to_change_score",
        },
        {
            "RuleID": "R2F04",
            "Rule": "stellar_component",
            "FrozenChoice": "fixed_3p6um_ML_policy_documented_before_scoring",
            "Reason": "prevents stellar_mass_to_light_endpoint_tuning",
            "ForbiddenAfterFreeze": "fit_ML_to_Vobs_or_W_tau_eff",
        },
        {
            "RuleID": "R2F05",
            "Rule": "bulge_policy",
            "FrozenChoice": "document_bulge_needed_before_scoring_from_published_decomposition_or_morphology",
            "Reason": "prevents post_hoc_bulge_switching",
            "ForbiddenAfterFreeze": "add_or_remove_bulge_after_readout",
        },
        {
            "RuleID": "R2F06",
            "Rule": "quality_gate",
            "FrozenChoice": "score_only_galaxies_with_at_least_eight_valid_radial_points_and_all_required_components",
            "Reason": "matches existing expanded_THINGS scoring discipline",
            "ForbiddenAfterFreeze": "lower_point_threshold_to_cross_N15",
        },
        {
            "RuleID": "R2F07",
            "Rule": "claim_boundary",
            "FrozenChoice": "route2_outputs_are_THINGS_control_inputs_not_tau_validation",
            "Reason": "keeps paper2 interpretation conservative",
            "ForbiddenAfterFreeze": "promote_route2_to_primary_tau_core_evidence",
        },
    ]


def scoring_gate_rows() -> list[dict[str, str]]:
    return [
        {
            "GateID": "R2G01",
            "Gate": "ProtocolFreeze",
            "PassCondition": "protocol_and_required_input_tables_committed_before_new_scores",
            "CurrentStatus": "passed_protocol_only_no_scores",
            "NextAction": "download_or_recover_source_inputs_with_manifest",
        },
        {
            "GateID": "R2G02",
            "Gate": "InputCompleteness",
            "PassCondition": "at_least_two_missing_galaxies_have_R_Vobs_eVobs_Vgas_Vdisk_Vbul_or_zero_bulge_with_provenance",
            "CurrentStatus": "not_started",
            "NextAction": "build_per_galaxy_input_inventory",
        },
        {
            "GateID": "R2G03",
            "Gate": "NoEndpointLeakage",
            "PassCondition": "component_rules_not_modified_after_any_W_tau_eff_readout",
            "CurrentStatus": "active_guardrail",
            "NextAction": "record_git_commit_hash_before_scoring",
        },
        {
            "GateID": "R2G04",
            "Gate": "THINGSN15",
            "PassCondition": "N_resolved_THINGS_scores_ge_15_after_two_or_more_completed_missing_rows",
            "CurrentStatus": "blocked_until_inputs_complete",
            "NextAction": "do_not_claim_N15_until_gate_passes",
        },
    ]


def write_protocol() -> None:
    lines = [
        "# THINGS Route 2 Mass-Model Reconstruction Protocol v0.1",
        "",
        "This protocol freezes the second route for completing at least two of the five unresolved THINGS Table 3 galaxies. It is intentionally a protocol only: no new `W_tau_eff` score is computed here.",
        "",
        "## Scope",
        "",
        "Route 2 is allowed because direct public-table recovery did not expose score-ready per-radius baryonic velocity columns for NGC925, NGC3031, NGC3621, NGC3627, or NGC4736. The goal is to reconstruct or recover compatible mass-model inputs without tuning any choice to the final residual score.",
        "",
        "## Required Components",
        "",
        "A galaxy becomes score-ready only when the packet contains radius-matched `R`, `Vobs`, `eVobs`, `Vgas`, `Vdisk`, and `Vbul` columns, or a documented zero-bulge policy fixed before scoring.",
        "",
        "## Frozen Choices",
        "",
        "- Use the published rotation-curve radius grid when available.",
        "- If the gas component is derived from HI surface density, use a single thin-disk rule and a 1.4 helium/metals factor.",
        "- Fix the 3.6 micron stellar mass-to-light policy before scoring.",
        "- Decide bulge handling before scoring from published decomposition or morphology, not from the score direction.",
        "- Require at least eight valid radial points, matching the existing expanded THINGS scoring discipline.",
        "",
        "## Forbidden Actions",
        "",
        "- Do not digitize final model plots as score-ready data unless a separate uncertainty and double-entry protocol is committed.",
        "- Do not tune gas geometry, M/L, interpolation, bulge inclusion, or radius cuts after viewing `W_tau_eff`.",
        "- Do not claim THINGS N>=15 until at least two missing galaxies pass the complete input gate.",
        "- Do not promote route 2 output to Tau Core validation; it remains a THINGS control expansion.",
        "",
        "## Next Step",
        "",
        "Build a per-galaxy input inventory for the five missing objects and download or recover only the source products needed for the required components.",
        "",
        "## Guardrail",
        "",
        f"`{GUARDRAIL}`",
        "",
    ]
    PROTOCOL.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [PROTOCOL, INPUTS, RULES, GATE]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_route2_mass_model_protocol_status"] = (
        "frozen_protocol_only_no_new_scores"
    )
    manifest["paper2_next_gate"] = "route2_per_galaxy_input_inventory_before_downloads"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_csv(
        INPUTS,
        input_rows(),
        [
            "InputID",
            "Component",
            "RequiredField",
            "PrimarySource",
            "AllowedFallback",
            "Forbidden",
            "ScoreDependency",
        ],
    )
    write_csv(
        RULES,
        frozen_rules(),
        ["RuleID", "Rule", "FrozenChoice", "Reason", "ForbiddenAfterFreeze"],
    )
    write_csv(
        GATE,
        scoring_gate_rows(),
        ["GateID", "Gate", "PassCondition", "CurrentStatus", "NextAction"],
    )
    write_protocol()
    update_manifest()
    print(PROTOCOL)


if __name__ == "__main__":
    main()
