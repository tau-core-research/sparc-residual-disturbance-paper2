#!/usr/bin/env python3
"""Close the THINGS route 2 expansion as not score-ready."""

from __future__ import annotations

import json

from make_packet_v01_seed import PACKET, write_csv


CLOSURE_OUT = PACKET / "things_route2_expansion_closure_v01.md"
DECISION_OUT = PACKET / "things_route2_expansion_closure_decision_v01.csv"
EVIDENCE_OUT = PACKET / "things_route2_expansion_closure_evidence_v01.csv"
BOUNDARY_OUT = PACKET / "things_route2_expansion_claim_boundary_v01.csv"

GUARDRAIL = "route2_expansion_closed_not_score_ready_no_synthetic_mass_models"


def evidence_rows() -> list[dict[str, str]]:
    return [
        {
            "EvidenceID": "R2CLOSE01",
            "Evidence": "source_inputs_staged_for_NGC925_NGC3031",
            "Status": "useful_but_not_score_ready",
            "Finding": "THINGS MOM0/MOM1 and SINGS IRAC1 products are staged outside git with checksum manifests.",
            "Blocks": "does_not_provide_R_Vobs_eVobs_Vgas_Vdisk_Vbul",
            "Guardrail": GUARDRAIL,
        },
        {
            "EvidenceID": "R2CLOSE02",
            "Evidence": "solver_validation_inputs_and_profiles",
            "Status": "useful_negative_control",
            "Finding": "Validation galaxies produced native and surface-density proxy profiles, but this does not validate velocity components.",
            "Blocks": "velocity_solver_not_validated_against_SPARC_component_curves",
            "Guardrail": GUARDRAIL,
        },
        {
            "EvidenceID": "R2CLOSE03",
            "Evidence": "surface_profile_reference_check",
            "Status": "failed",
            "Finding": "Derived IRAC profiles do not reproduce SPARC SBdisk at the frozen threshold.",
            "Blocks": "stellar_component_reconstruction_not_validated",
            "Guardrail": GUARDRAIL,
        },
        {
            "EvidenceID": "R2CLOSE04",
            "Evidence": "background_only_photometry_policy",
            "Status": "failed",
            "Finding": "Outer-annulus background subtraction does not unblock SPARC SBdisk agreement.",
            "Blocks": "simple_sky_offset_not_sufficient",
            "Guardrail": GUARDRAIL,
        },
        {
            "EvidenceID": "R2CLOSE05",
            "Evidence": "published_machine_mass_model_recovery",
            "Status": "failed",
            "Finding": "Official SPARC and de Blok machine/source checks do not expose score-ready per-radius columns for the missing five.",
            "Blocks": "THINGS_N15_expansion",
            "Guardrail": GUARDRAIL,
        },
    ]


def decision_rows() -> list[dict[str, str]]:
    return [
        {
            "DecisionID": "R2CLOSED01",
            "Decision": "close_route2_expansion",
            "Status": "closed_not_score_ready",
            "Scope": "NGC925;NGC3031;NGC3621;NGC3627;NGC4736",
            "AllowedUse": "audit_trail_future_reactivation_if_citable_machine_columns_are_obtained",
            "ForbiddenUse": "score_missing_THINGS_galaxies_from_route2_outputs",
            "NextAction": "return_to_non_route2_paper2_roadmap_or_external_validation_sources",
            "Guardrail": GUARDRAIL,
        },
        {
            "DecisionID": "R2CLOSED02",
            "Decision": "THINGS_N15_status",
            "Status": "not_reached",
            "Scope": "expanded_THINGS_W_tau_eff_control",
            "AllowedUse": "retain_existing_N13_or_below_threshold_THINGS_controls_as_caveated_support",
            "ForbiddenUse": "claim_THINGS_N15_or_paper_grade_external_validation_from_route2",
            "NextAction": "do_not_include_route2_as_positive_evidence_in_manuscript",
            "Guardrail": GUARDRAIL,
        },
    ]


def boundary_rows() -> list[dict[str, str]]:
    return [
        {
            "ClaimID": "R2CLAIM01",
            "Claim": "Route2 produced score-ready missing THINGS galaxies.",
            "Status": "forbidden",
            "Replacement": "Route2 produced a reproducible negative audit and remains not score-ready.",
            "Guardrail": GUARDRAIL,
        },
        {
            "ClaimID": "R2CLAIM02",
            "Claim": "The velocity solver was validated.",
            "Status": "forbidden",
            "Replacement": "Velocity-solver validation was blocked before solver execution by failed stellar surface-profile checks.",
            "Guardrail": GUARDRAIL,
        },
        {
            "ClaimID": "R2CLAIM03",
            "Claim": "THINGS was expanded to N>=15.",
            "Status": "forbidden",
            "Replacement": "THINGS remains below the frozen N>=15 external-validation gate.",
            "Guardrail": GUARDRAIL,
        },
        {
            "ClaimID": "R2CLAIM04",
            "Claim": "Route2 disproves the broader W_tau_eff direction.",
            "Status": "forbidden",
            "Replacement": "Route2 only shows that this reconstruction path is not validated for missing THINGS mass-model recovery.",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report(
    evidence: list[dict[str, str]],
    decisions: list[dict[str, str]],
    boundaries: list[dict[str, str]],
) -> None:
    lines = [
        "# THINGS Route 2 Expansion Closure v0.1",
        "",
        "Route 2 is closed as not score-ready. The closure is methodological, not a negative Tau claim: the staged source products and validation audits remain useful, but they do not justify scoring the missing THINGS galaxies.",
        "",
        "## Evidence",
        "",
    ]
    for row in evidence:
        lines.append(f"- `{row['EvidenceID']}`: {row['Status']} - {row['Finding']}")
    lines.extend(["", "## Decisions", ""])
    for row in decisions:
        lines.append(
            f"- `{row['DecisionID']}`: {row['Status']}; forbidden={row['ForbiddenUse']}."
        )
    lines.extend(["", "## Claim Boundary", ""])
    for row in boundaries:
        lines.append(
            f"- `{row['ClaimID']}`: {row['Status']} - replace with: {row['Replacement']}"
        )
    lines.extend(
        [
            "",
            "## Reopening Condition",
            "",
            "Route 2 may be reopened only if citable, machine-readable per-radius mass-model columns are obtained for at least two missing THINGS galaxies, or if a complete photometry/decomposition plus velocity-solver pipeline is pre-registered and validates against existing SPARC component curves before missing-galaxy scoring.",
            "",
            "No route2 `W_tau_eff` score is computed here.",
            "No synthetic mass-model columns are created here.",
            "",
            f"Guardrail: `{GUARDRAIL}`",
            "",
        ]
    )
    CLOSURE_OUT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [CLOSURE_OUT, DECISION_OUT, EVIDENCE_OUT, BOUNDARY_OUT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_route2_expansion_status"] = (
        "closed_not_score_ready_no_synthetic_mass_models_no_scores"
    )
    manifest["paper2_next_gate"] = (
        "return_to_non_route2_paper2_roadmap_or_external_validation_sources"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    evidence = evidence_rows()
    decisions = decision_rows()
    boundaries = boundary_rows()
    write_csv(
        EVIDENCE_OUT,
        evidence,
        ["EvidenceID", "Evidence", "Status", "Finding", "Blocks", "Guardrail"],
    )
    write_csv(
        DECISION_OUT,
        decisions,
        [
            "DecisionID",
            "Decision",
            "Status",
            "Scope",
            "AllowedUse",
            "ForbiddenUse",
            "NextAction",
            "Guardrail",
        ],
    )
    write_csv(
        BOUNDARY_OUT,
        boundaries,
        ["ClaimID", "Claim", "Status", "Replacement", "Guardrail"],
    )
    write_report(evidence, decisions, boundaries)
    update_manifest()
    print(CLOSURE_OUT)


if __name__ == "__main__":
    main()
