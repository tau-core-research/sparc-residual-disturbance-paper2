#!/usr/bin/env python3
"""Freeze the primary source-side W_env_obs proxy design before endpoint tests."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from make_packet_v01_seed import PACKET


DESIGN_OUT = PACKET / "w_env_obs_proxy_design_v01.csv"
RULE_OUT = PACKET / "w_env_obs_proxy_rule_freeze_v01.csv"
ENDPOINT_OUT = PACKET / "w_env_obs_proxy_endpoint_plan_v01.csv"
REPORT = PACKET / "w_env_obs_proxy_design_v01.md"

GUARDRAIL = "proxy_design_frozen_no_endpoint_readout_no_rule_fitting"


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def design_rows() -> list[dict[str, str]]:
    return [
        {
            "DesignID": "D01",
            "Role": "primary_broad_prior",
            "ProxyID": "P01",
            "ProxyFamily": "paper1_external_evidence_type",
            "Purpose": "Provide the first galaxy-level source-side prior for W_env_obs without residual inputs.",
            "AllowedInputs": "EvidenceType;Confidence;ResidualBlind flag",
            "ForbiddenInputs": "Vobs;Vbar;TPG_residual;S_tau_eff;history_state;endpoint_velocity;Class as numeric input",
            "CoverageExpectation": "73 galaxies before quality intersection",
            "UseInNextEndpoint": "yes_primary_prior",
            "Guardrail": GUARDRAIL,
        },
        {
            "DesignID": "D02",
            "Role": "source_family_holdout",
            "ProxyID": "P07",
            "ProxyFamily": "WHISP_lopsidedness_asymmetry",
            "Purpose": "Act as the first independent source-family check for environment/disturbance proxy direction.",
            "AllowedInputs": "published HI lopsidedness;tidal parameter;epsilon_kin",
            "ForbiddenInputs": "TPG_residual;S_tau_eff;endpoint_velocity",
            "CoverageExpectation": "14 galaxies in current overlap",
            "UseInNextEndpoint": "holdout_or_secondary_readout",
            "Guardrail": GUARDRAIL,
        },
        {
            "DesignID": "D03",
            "Role": "small_overlap_sanity_check",
            "ProxyID": "P03",
            "ProxyFamily": "THINGS_moment_map_kinematic_stress",
            "Purpose": "Check whether radial HI stress proxies align with the frozen W_env_obs direction.",
            "AllowedInputs": "HI moment-map stress;dispersion/asymmetry proxy;ring profiles",
            "ForbiddenInputs": "TPG_residual;current_point_residual;S_tau_eff",
            "CoverageExpectation": "8 galaxies in current overlap",
            "UseInNextEndpoint": "small_overlap_sanity_only",
            "Guardrail": GUARDRAIL,
        },
        {
            "DesignID": "D04",
            "Role": "geometry_sanity_check",
            "ProxyID": "P04",
            "ProxyFamily": "THINGS_global_geometry_stress",
            "Purpose": "Check if global viewing geometry and annular stress add information beyond the broad prior.",
            "AllowedInputs": "global PA/inclination elliptical annuli stress",
            "ForbiddenInputs": "TPG_residual;S_tau_eff;endpoint_velocity",
            "CoverageExpectation": "8 galaxies in current overlap",
            "UseInNextEndpoint": "small_overlap_sanity_only",
            "Guardrail": GUARDRAIL,
        },
        {
            "DesignID": "D05",
            "Role": "mandatory_systematics_control",
            "ProxyID": "P09",
            "ProxyFamily": "inclination_systematics",
            "Purpose": "Prevent interpreting inclination/deprojection effects as W_env_obs.",
            "AllowedInputs": "inclination bins;class counts;median residual stress summary",
            "ForbiddenInputs": "use_as_positive_tau_proxy",
            "CoverageExpectation": "summary-level current packet",
            "UseInNextEndpoint": "control_required_before_interpretation",
            "Guardrail": GUARDRAIL,
        },
    ]


def rule_rows() -> list[dict[str, str]]:
    return [
        {
            "RuleStep": "R01",
            "Name": "primary_proxy_inputs",
            "Definition": "Use P01 EvidenceType and Confidence only as the first broad W_env_obs prior.",
            "FrozenChoice": "P01_primary",
            "Reason": "Largest coverage and residual-blind provenance.",
            "Guardrail": GUARDRAIL,
        },
        {
            "RuleStep": "R02",
            "Name": "directional_prior",
            "Definition": "Regular/low-asymmetry evidence is treated as lower W_env_obs burden; disturbed HI, tidal, interaction, and warp evidence as higher burden.",
            "FrozenChoice": "direction_only_no_coefficients",
            "Reason": "Matches the signal-candidate interpretation without fitting endpoint amplitudes.",
            "Guardrail": GUARDRAIL,
        },
        {
            "RuleStep": "R03",
            "Name": "holdout_family",
            "Definition": "Use P07 WHISP lopsidedness/asymmetry only after the P01 direction is frozen.",
            "FrozenChoice": "P07_holdout",
            "Reason": "Independent source family and direct HI asymmetry relevance.",
            "Guardrail": GUARDRAIL,
        },
        {
            "RuleStep": "R04",
            "Name": "small_overlap_families",
            "Definition": "Use P03/P04 only as small-overlap sanity checks, not as primary training or coefficient selection.",
            "FrozenChoice": "P03_P04_sanity_only",
            "Reason": "THINGS proxies are radial but coverage is too small and prior direct stress mapping was too crude.",
            "Guardrail": GUARDRAIL,
        },
        {
            "RuleStep": "R05",
            "Name": "blocked_endpoint_actions",
            "Definition": "No velocity endpoint readout and no S_tau_full coefficient selection in this design freeze.",
            "FrozenChoice": "endpoint_blocked",
            "Reason": "Avoid outcome selection before proxy rule formalization.",
            "Guardrail": GUARDRAIL,
        },
    ]


def endpoint_rows() -> list[dict[str, str]]:
    return [
        {
            "EndpointGate": "E01",
            "Endpoint": "proxy_direction_vs_W_tau_eff_candidate_score",
            "AllowedAfterThisDesign": "yes_next",
            "PrimaryQuestion": "Does the frozen P01 direction separate W_tau_eff candidate burden without using velocity residual inputs as predictors?",
            "PassCondition": "predeclared direction has positive association with W_tau_eff candidate score",
            "FailureCondition": "P01 direction is null or reversed",
            "Guardrail": GUARDRAIL,
        },
        {
            "EndpointGate": "E02",
            "Endpoint": "P07_source_family_holdout",
            "AllowedAfterThisDesign": "yes_after_E01",
            "PrimaryQuestion": "Does WHISP lopsidedness/asymmetry support the same direction in its overlap?",
            "PassCondition": "WHISP burden aligns with P01/W_tau_eff direction",
            "FailureCondition": "WHISP does not align or is dominated by class imbalance",
            "Guardrail": GUARDRAIL,
        },
        {
            "EndpointGate": "E03",
            "Endpoint": "velocity_readout_with_S_tau_full",
            "AllowedAfterThisDesign": "no",
            "PrimaryQuestion": "Does a full S_tau formula improve velocity residuals?",
            "PassCondition": "not applicable at this gate",
            "FailureCondition": "attempted before formula and coefficients are frozen",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report() -> None:
    lines = [
        "# W_env_obs Proxy Design v0.1",
        "",
        "This gate freezes the first source-side design for predicting the environment/observer weight candidate `W_env_obs`. It intentionally does not evaluate a velocity endpoint and does not select coefficients.",
        "",
        "## Frozen Design",
        "",
        "- Primary broad prior: `P01` Paper 1 external evidence type.",
        "- Source-family holdout: `P07` WHISP lopsidedness/asymmetry.",
        "- Small-overlap sanity checks: `P03/P04` THINGS stress and geometry proxies.",
        "- Mandatory control: `P09` inclination/systematics.",
        "",
        "## Frozen Direction",
        "",
        "Regular or low-asymmetry external evidence is treated as lower `W_env_obs` burden. Disturbed HI, tidal, interaction, and warp evidence is treated as higher `W_env_obs` burden. This is directional only; no amplitude or velocity coefficient is fitted here.",
        "",
        "## Blocked Actions",
        "",
        "- No `S_tau_full` coefficient selection.",
        "- No velocity endpoint readout.",
        "- No use of current-point residuals, empirical `S_tau_eff`, or history-state targets as proxy inputs.",
        "",
        "## Next Gate",
        "",
        "The next allowed gate is `proxy_direction_vs_W_tau_eff_candidate_score`: test the frozen P01 direction against the already-defined `W_tau_eff` candidate score, then use P07 as a source-family holdout.",
        "",
        "## Generated Files",
        "",
        "- `w_env_obs_proxy_design_v01.csv`",
        "- `w_env_obs_proxy_rule_freeze_v01.csv`",
        "- `w_env_obs_proxy_endpoint_plan_v01.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "w_env_obs_proxy_design_v01.md",
            "w_env_obs_proxy_design_v01.csv",
            "w_env_obs_proxy_rule_freeze_v01.csv",
            "w_env_obs_proxy_endpoint_plan_v01.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["w_env_obs_proxy_design_status"] = "primary_source_side_proxy_design_frozen_no_endpoint"
    manifest["paper2_next_gate"] = "proxy_direction_vs_w_tau_eff_candidate_score"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_csv(
        DESIGN_OUT,
        design_rows(),
        [
            "DesignID",
            "Role",
            "ProxyID",
            "ProxyFamily",
            "Purpose",
            "AllowedInputs",
            "ForbiddenInputs",
            "CoverageExpectation",
            "UseInNextEndpoint",
            "Guardrail",
        ],
    )
    write_csv(
        RULE_OUT,
        rule_rows(),
        ["RuleStep", "Name", "Definition", "FrozenChoice", "Reason", "Guardrail"],
    )
    write_csv(
        ENDPOINT_OUT,
        endpoint_rows(),
        [
            "EndpointGate",
            "Endpoint",
            "AllowedAfterThisDesign",
            "PrimaryQuestion",
            "PassCondition",
            "FailureCondition",
            "Guardrail",
        ],
    )
    write_report()
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
