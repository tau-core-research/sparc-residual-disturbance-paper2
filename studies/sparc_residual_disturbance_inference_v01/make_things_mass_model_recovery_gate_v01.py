#!/usr/bin/env python3
"""Close route 1 and open route 2 for missing THINGS mass models."""

from __future__ import annotations

import json
from pathlib import Path

from make_packet_v01_seed import PACKET, write_csv


RECOVERY_OUT = PACKET / "things_mass_model_recovery_gate_v01.csv"
ROUTE2_OUT = PACKET / "things_mass_model_route2_reconstruction_plan_v01.csv"
DECISION_OUT = PACKET / "things_mass_model_recovery_gate_decision_v01.csv"
REPORT = PACKET / "things_mass_model_recovery_gate_v01.md"

MISSING = ["NGC925", "NGC3031", "NGC3621", "NGC3627", "NGC4736"]
GUARDRAIL = "route1_then_route2_no_score_from_plots_no_target_refit"


def recovery_rows() -> list[dict[str, str]]:
    rows = []
    for galaxy in MISSING:
        rows.append(
            {
                "GalaxyName": galaxy,
                "Route1Question": "public_per_radius_mass_model_columns_available",
                "SPARCRotmodStatus": "absent_from_public_SPARC_LTG_rotmod",
                "SPARCMassModelTableStatus": "absent_from_public_SPARC_Table2",
                "DeblokArxivSourceStatus": "method_and_global_fit_tables_present_per_radius_columns_not_exposed",
                "THINGSHIStatus": "HI_FITS_products_available",
                "ScoreReadyColumnsFound": "no",
                "RequiredColumns": "Vobs;Vgas;Vdisk;Vbul_or_frozen_equivalent",
                "Route1Conclusion": "not_score_ready_from_direct_public_tables",
                "Guardrail": GUARDRAIL,
            }
        )
    return rows


def route2_rows() -> list[dict[str, str]]:
    return [
        {
            "StepID": "R2-01",
            "Step": "freeze_reconstruction_scope",
            "Input": "THINGS_HI_FITS_plus_public_stellar_photometry_or_published_profiles",
            "Allowed": "write_rule_before_any_W_tau_eff_scoring",
            "Forbidden": "choose_rule_after_viewing_score_direction",
            "MinimumDeliverable": "route2_protocol_md_with_units_radius_grid_ML_policy_and_exclusions",
        },
        {
            "StepID": "R2-02",
            "Step": "recover_or_compute_gas_component",
            "Input": "THINGS_moment0_maps_or_published_HI_surface_density_profiles",
            "Allowed": "derive_Vgas_with_single_committed_disk_assumption",
            "Forbidden": "tune_gas_component_to_reduce_residuals",
            "MinimumDeliverable": "per_galaxy_Vgas_trace_with_source_and_assumption_log",
        },
        {
            "StepID": "R2-03",
            "Step": "recover_or_compute_stellar_component",
            "Input": "SINGS_or_equivalent_3p6um_profiles",
            "Allowed": "apply_fixed_ML_policy_and_document_bulge_disk_handling",
            "Forbidden": "fit_ML_to_W_tau_eff_or_Vobs_endpoint",
            "MinimumDeliverable": "per_galaxy_Vdisk_Vbul_trace_with_fixed_ML_policy",
        },
        {
            "StepID": "R2-04",
            "Step": "score_only_after_freeze",
            "Input": "two_or_more_completed_missing_galaxy_mass_models",
            "Allowed": "compute_W_tau_eff_after_protocol_commit",
            "Forbidden": "claim_THINGS_N15_before_two_score_ready_rows",
            "MinimumDeliverable": "N_ge_15_THINGS_control_readout_or_documented_failure",
        },
    ]


def decision_rows() -> list[dict[str, str]]:
    return [
        {
            "DecisionID": "TMRG01",
            "Status": "route1_direct_table_recovery_not_score_ready",
            "Meaning": "published sources confirm relevant THINGS analysis exists but do not expose the required per-radius baryonic velocity columns in the checked public machine-readable paths",
            "NextGate": "route2_frozen_reconstruction_protocol",
        },
        {
            "DecisionID": "TMRG02",
            "Status": "route2_allowed_but_not_yet_scored",
            "Meaning": "THINGS HI FITS products can be future inputs, but scoring remains blocked until the reconstruction rule is frozen and at least two missing galaxies are completed",
            "NextGate": "write_route2_protocol_before_data_ingestion",
        },
    ]


def write_report(
    recovery: list[dict[str, str]],
    route2: list[dict[str, str]],
    decisions: list[dict[str, str]],
) -> None:
    missing = ", ".join(row["GalaxyName"] for row in recovery)
    lines = [
        "# THINGS Mass-Model Recovery Gate v0.1",
        "",
        "This gate implements the requested order: first attempt direct recovery of public, compatible mass-model columns; if that does not work, move to a frozen reconstruction protocol.",
        "",
        "## Route 1 Result",
        "",
        f"Checked missing galaxies: {missing}.",
        "",
        "Direct score-ready public tables were not recovered for the missing five. The public SPARC LTG rotmod archive and SPARC machine-readable mass-model table do not include these rows, while the de Blok et al. source package documents the mass-model analysis without exposing SPARC-style per-radius `Vobs`, `Vgas`, `Vdisk`, and `Vbul` columns for these objects.",
        "",
        "This closes route 1 for immediate scoring. It does not mean the galaxies are unusable; it means the current public-table path is not enough.",
        "",
        "## Route 2 Opened",
        "",
        "Route 2 is allowed only as a pre-registered reconstruction protocol. The protocol must be committed before any new `W_tau_eff` score is computed, and it must not tune gas, stellar, or mass-to-light choices to improve the endpoint.",
        "",
        "## Route 2 Minimum",
        "",
        "To cross the THINGS N>=15 gate, at least two of the five missing galaxies must receive frozen, source-documented per-radius baryonic components.",
        "",
        "## Generated Files",
        "",
        "- `things_mass_model_recovery_gate_v01.csv`",
        "- `things_mass_model_route2_reconstruction_plan_v01.csv`",
        "- `things_mass_model_recovery_gate_decision_v01.csv`",
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
    for path in [RECOVERY_OUT, ROUTE2_OUT, DECISION_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_mass_model_recovery_gate_status"] = (
        "route1_not_score_ready_route2_protocol_required"
    )
    manifest["paper2_next_gate"] = "write_route2_frozen_THINGS_mass_model_protocol"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    recovery = recovery_rows()
    route2 = route2_rows()
    decisions = decision_rows()
    write_csv(
        RECOVERY_OUT,
        recovery,
        [
            "GalaxyName",
            "Route1Question",
            "SPARCRotmodStatus",
            "SPARCMassModelTableStatus",
            "DeblokArxivSourceStatus",
            "THINGSHIStatus",
            "ScoreReadyColumnsFound",
            "RequiredColumns",
            "Route1Conclusion",
            "Guardrail",
        ],
    )
    write_csv(
        ROUTE2_OUT,
        route2,
        [
            "StepID",
            "Step",
            "Input",
            "Allowed",
            "Forbidden",
            "MinimumDeliverable",
        ],
    )
    write_csv(
        DECISION_OUT,
        decisions,
        [
            "DecisionID",
            "Status",
            "Meaning",
            "NextGate",
        ],
    )
    write_report(recovery, route2, decisions)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
