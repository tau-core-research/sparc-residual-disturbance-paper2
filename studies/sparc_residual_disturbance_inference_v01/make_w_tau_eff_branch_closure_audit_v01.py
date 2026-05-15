#!/usr/bin/env python3
"""Create the final closure audit for the W_tau_eff residual-weight branch."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from make_packet_v01_seed import PACKET


CLAIMS_OUT = PACKET / "w_tau_eff_branch_claim_boundary_v01.csv"
FAILURE_OUT = PACKET / "w_tau_eff_branch_failure_modes_v01.csv"
NEXT_GATE_OUT = PACKET / "w_tau_eff_branch_next_gate_v01.csv"
REPORT = PACKET / "w_tau_eff_branch_closure_audit_v01.md"

GUARDRAIL = "w_tau_eff_branch_closed_not_map_not_tau_core_proof"


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def claim_rows() -> list[dict[str, str]]:
    return [
        {
            "ClaimID": "C01",
            "Status": "supported",
            "Claim": "TPG can be treated operationally as an effective local Tau Core weight baseline for this branch.",
            "Evidence": "The fixed TPG/projection prescription is the baseline used by all residual, drift, and history readouts.",
            "Boundary": "This is a working decomposition, not a first-principles derivation of the local weights.",
            "Guardrail": GUARDRAIL,
        },
        {
            "ClaimID": "C02",
            "Status": "supported",
            "Claim": "The TPG residual is structured enough to be a candidate carrier of missing environment/observer-dependent weights.",
            "Evidence": "Candidate score AUC(C higher)=0.774159664; signed-drift and history-improvement features are strongly related.",
            "Boundary": "Candidate carrier does not mean attribution to Tau Core.",
            "Guardrail": GUARDRAIL,
        },
        {
            "ClaimID": "C03",
            "Status": "supported",
            "Claim": "A history-dependent residual state improves the velocity readout relative to S_tau=1.",
            "Evidence": "History rule median delta RMS=-0.016862038; fraction galaxies improved=0.933333333; C fraction improved=1.000000000.",
            "Boundary": "This is not an external prediction because it uses inner observed residuals of the same galaxy.",
            "Guardrail": GUARDRAIL,
        },
        {
            "ClaimID": "C04",
            "Status": "not_established",
            "Claim": "W_tau_eff is the Tau Core field.",
            "Evidence": "No direct field reconstruction, no sky/distance/environment join, and no external source-side predictor are present yet.",
            "Boundary": "Use only residual-inferred effective tau-weight seed terminology.",
            "Guardrail": GUARDRAIL,
        },
        {
            "ClaimID": "C05",
            "Status": "not_established",
            "Claim": "The residual structure is unique to Tau Core rather than observability or galaxy dynamics.",
            "Evidence": "The branch has not yet controlled RA/Dec, distance, inclination, beam smearing, or environment in a mapping framework.",
            "Boundary": "Systematics and non-circular-motion alternatives remain live.",
            "Guardrail": GUARDRAIL,
        },
    ]


def failure_rows() -> list[dict[str, str]]:
    return [
        {
            "FailureModeID": "F01",
            "AlternativeExplanation": "Non-circular or non-equilibrium gas motions",
            "HowItCouldMimicW_tau_eff": "Creates persistent signed residuals and same-sign radial runs.",
            "RequiredControl": "kinematic-quality flags, approaching/receding asymmetry, velocity-field disturbance indicators",
            "StatusBeforeMapping": "open",
            "Guardrail": GUARDRAIL,
        },
        {
            "FailureModeID": "F02",
            "AlternativeExplanation": "Observability and resolution bias",
            "HowItCouldMimicW_tau_eff": "Nearby or better-resolved galaxies reveal more structure and residual drift.",
            "RequiredControl": "distance, angular resolution, beam-smearing proxy, radius-coverage controls",
            "StatusBeforeMapping": "open",
            "Guardrail": GUARDRAIL,
        },
        {
            "FailureModeID": "F03",
            "AlternativeExplanation": "Inclination and deprojection uncertainty",
            "HowItCouldMimicW_tau_eff": "Systematic velocity scaling errors produce coherent signed residuals.",
            "RequiredControl": "inclination, inclination uncertainty, edge-on/face-on stress tests",
            "StatusBeforeMapping": "open",
            "Guardrail": GUARDRAIL,
        },
        {
            "FailureModeID": "F04",
            "AlternativeExplanation": "Baryonic mass-model mismatch",
            "HowItCouldMimicW_tau_eff": "Incorrect disk, bulge, or gas contribution shifts Vbar and leaves integrated residuals.",
            "RequiredControl": "mass-to-light sensitivity, gas/disk/bulge component checks, stellar-mass proxy",
            "StatusBeforeMapping": "open",
            "Guardrail": GUARDRAIL,
        },
        {
            "FailureModeID": "F05",
            "AlternativeExplanation": "Environmental galaxy dynamics rather than observer-weight field",
            "HowItCouldMimicW_tau_eff": "Interactions, tides, or ram pressure create spatially correlated residual structure.",
            "RequiredControl": "environment/LSS proxy, group membership, nearest-neighbor and cluster/filament indicators",
            "StatusBeforeMapping": "open_but_scientifically_relevant",
            "Guardrail": GUARDRAIL,
        },
    ]


def next_gate_rows() -> list[dict[str, str]]:
    return [
        {
            "GateID": "G01",
            "Gate": "coordinate_distance_join",
            "Purpose": "Make W_tau_eff map-testable.",
            "RequiredInputs": "RA;Dec;distance;distance_uncertainty",
            "PassCondition": "All 45 seed galaxies have join status or documented missingness.",
            "DoNotProceedIf": "coordinates or distances are silently imputed without provenance",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "G02",
            "Gate": "systematics_join",
            "Purpose": "Prevent false attribution of residual drift to Tau Core weights.",
            "RequiredInputs": "inclination;beam/resolution proxy;radius coverage;quality flags",
            "PassCondition": "At least distance, inclination, and radius-coverage controls are available.",
            "DoNotProceedIf": "map signal is interpreted before basic observability controls",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "G03",
            "Gate": "environment_join",
            "Purpose": "Separate galaxy environment from observer-dependent weight candidates.",
            "RequiredInputs": "group/cluster/filament or nearest-neighbor proxy",
            "PassCondition": "Environment proxy is present or explicitly marked unavailable.",
            "DoNotProceedIf": "spatial clustering is called observer-field evidence without environment controls",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "G04",
            "Gate": "map_null_tests",
            "Purpose": "Test whether W_tau_eff spatial structure exceeds shuffled or distance-only nulls.",
            "RequiredInputs": "W_tau_eff seed plus coordinate/distance/systematics joins",
            "PassCondition": "predeclared angular, distance, and environment null tests are reported",
            "DoNotProceedIf": "visual sky maps are treated as evidence without null tests",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report() -> None:
    lines = [
        "# W_tau_eff Branch Closure Audit v0.1",
        "",
        "This audit closes the residual-weight branch before any field-map construction. It records what has been established, what remains explicitly unproven, and which controls are mandatory before a map can be interpreted.",
        "",
        "## Branch Status",
        "",
        "Closed for definition and seed generation. Not closed for Tau Core attribution or field mapping.",
        "",
        "## Stable Working Decomposition",
        "",
        "- `TPG`: effective baseline carrying local Tau Core weights.",
        "- `W_tau_eff`: residual-inferred candidate for missing environment- and observer-dependent Tau Core weights.",
        "- `W_tau_eff` is a map-ready seed, not the Tau Core field itself.",
        "",
        "## What Is Established",
        "",
        "- The residual branch has a reproducible galaxy-level `W_tau_eff` seed for 45 galaxies.",
        "- TPG residuals show signed, cumulative, and history-dependent structure.",
        "- A causal inner-history readout improves over `S_tau=1`, but is not an external prediction.",
        "",
        "## What Is Not Established",
        "",
        "- No Tau Core field map has been built.",
        "- No residual structure has been uniquely attributed to Tau Core.",
        "- Observability, inclination, beam smearing, baryonic modelling, and non-circular motion alternatives remain open.",
        "",
        "## Closure Decision",
        "",
        "The branch may proceed to map preparation only after this audit. The next branch must begin with coordinate, distance, systematics, and environment joins, not with interpretive sky maps.",
        "",
        "## Generated Files",
        "",
        "- `w_tau_eff_branch_claim_boundary_v01.csv`",
        "- `w_tau_eff_branch_failure_modes_v01.csv`",
        "- `w_tau_eff_branch_next_gate_v01.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "w_tau_eff_branch_closure_audit_v01.md",
            "w_tau_eff_branch_claim_boundary_v01.csv",
            "w_tau_eff_branch_failure_modes_v01.csv",
            "w_tau_eff_branch_next_gate_v01.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["w_tau_eff_branch_closure_status"] = "closed_for_definition_seed_not_for_attribution"
    manifest["paper2_next_gate"] = "coordinate_distance_systematics_environment_join_before_mapping"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_csv(
        CLAIMS_OUT,
        claim_rows(),
        ["ClaimID", "Status", "Claim", "Evidence", "Boundary", "Guardrail"],
    )
    write_csv(
        FAILURE_OUT,
        failure_rows(),
        [
            "FailureModeID",
            "AlternativeExplanation",
            "HowItCouldMimicW_tau_eff",
            "RequiredControl",
            "StatusBeforeMapping",
            "Guardrail",
        ],
    )
    write_csv(
        NEXT_GATE_OUT,
        next_gate_rows(),
        [
            "GateID",
            "Gate",
            "Purpose",
            "RequiredInputs",
            "PassCondition",
            "DoNotProceedIf",
            "Guardrail",
        ],
    )
    write_report()
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
