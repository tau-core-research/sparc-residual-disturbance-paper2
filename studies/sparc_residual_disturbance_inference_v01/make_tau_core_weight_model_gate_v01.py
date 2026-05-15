#!/usr/bin/env python3
"""Freeze the next Tau Core weight-model gate after the residual signal candidate."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from make_packet_v01_seed import PACKET


MODEL_OUT = PACKET / "tau_core_weight_model_gate_v01.csv"
EVIDENCE_OUT = PACKET / "tau_core_weight_model_evidence_matrix_v01.csv"
TEST_OUT = PACKET / "tau_core_weight_model_next_tests_v01.csv"
REPORT = PACKET / "tau_core_weight_model_gate_v01.md"

GUARDRAIL = "model_gate_not_fit_not_tau_core_proof"


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def model_rows() -> list[dict[str, str]]:
    return [
        {
            "ComponentID": "M01",
            "Component": "Local baseline",
            "Symbol": "W_local_TPG(R)",
            "Definition": "The fixed TPG/projection multiplier already carries the local Tau Core weights available to the baseline.",
            "OperationalForm": "V_TPG(R)=Vbar(R)*(1+alpha*ln(1+a0/aN))",
            "AllowedInputs": "Vbar;aN;fixed_alpha",
            "ForbiddenInputs": "residuals;A/C_label;future_points;environment_tuning",
            "Guardrail": GUARDRAIL,
        },
        {
            "ComponentID": "M02",
            "Component": "Environment/observer residual weight",
            "Symbol": "W_env_obs(R)",
            "Definition": "Candidate missing non-local weight left after the local TPG baseline.",
            "OperationalForm": "W_env_obs(R_i)=F(integral/history of inner geometry or inner signed residual proxy up to R_i)",
            "AllowedInputs": "predeclared_history_state_or_external_proxy",
            "ForbiddenInputs": "current_point_residual;future_points;outcome_selected_mapping",
            "Guardrail": GUARDRAIL,
        },
        {
            "ComponentID": "M03",
            "Component": "History-state pilot",
            "Symbol": "H_tau(R_i)",
            "Definition": "Causal pilot state used only to test whether integrated radial information is useful.",
            "OperationalForm": "H_tau(R_i)=mean_{j<i} signed_residual_TPG(R_j)",
            "AllowedInputs": "inner_signed_TPG_residuals_only",
            "ForbiddenInputs": "current_point_residual;future_points;S_tau_eff;A/C_label",
            "Guardrail": GUARDRAIL,
        },
        {
            "ComponentID": "M04",
            "Component": "Next physical model target",
            "Symbol": "S_tau_full(R)",
            "Definition": "A later paper-grade expression should combine local TPG weights with an independently predicted environment/observer state.",
            "OperationalForm": "S_tau_full(R)=1+g(W_env_obs(R)); g must be frozen before velocity readout",
            "AllowedInputs": "external_source_side_proxy_or_predeclared_geometry_state",
            "ForbiddenInputs": "same_endpoint_velocity_residual_fitting",
            "Guardrail": GUARDRAIL,
        },
    ]


def evidence_rows() -> list[dict[str, str]]:
    return [
        {
            "EvidenceID": "E01",
            "Observation": "Candidate residual score separates A/C systems.",
            "Metric": "TauCoreSignalCandidateScore_v01 AUC(C higher)=0.774159664",
            "Supports": "TPG residual carries structured non-local information.",
            "DoesNotProve": "Tau Core attribution or uniqueness.",
            "Guardrail": GUARDRAIL,
        },
        {
            "EvidenceID": "E02",
            "Observation": "Projection RMS remains strong.",
            "Metric": "Projection RMS AUC(C higher)=0.771008403",
            "Supports": "TPG residual amplitude is informative.",
            "DoesNotProve": "Whether amplitude is environment/observer weight rather than ordinary disturbance.",
            "Guardrail": GUARDRAIL,
        },
        {
            "EvidenceID": "E03",
            "Observation": "History improvement is strong.",
            "Metric": "History improvement AUC(C higher)=0.762605042; all-galaxy improvement fraction=0.933333333",
            "Supports": "Integrated radial state carries predictive information for outer points.",
            "DoesNotProve": "External predictability, because the pilot uses inner observed residuals.",
            "Guardrail": GUARDRAIL,
        },
        {
            "EvidenceID": "E04",
            "Observation": "Abs final signed drift and history improvement are tightly coupled.",
            "Metric": "Pearson=0.954744346",
            "Supports": "The useful correction is aligned with cumulative signed drift.",
            "DoesNotProve": "That the drift is not caused by systematics or non-circular motion.",
            "Guardrail": GUARDRAIL,
        },
    ]


def test_rows() -> list[dict[str, str]]:
    return [
        {
            "TestID": "T01",
            "NextTest": "source_side_history_proxy",
            "Question": "Can external geometry/environment proxies predict the history state without using residuals?",
            "PassCondition": "Predeclared proxy improves over S_tau=1 on held-out galaxies or source families.",
            "FailureInterpretation": "Integrated residual state may be descriptive rather than physically predictive.",
            "Guardrail": GUARDRAIL,
        },
        {
            "TestID": "T02",
            "NextTest": "systematics_competition",
            "Question": "Do inclination, resolution, baryonic, or non-circular-motion controls absorb W_env_obs?",
            "PassCondition": "Residual weight candidate remains after predeclared controls.",
            "FailureInterpretation": "Candidate is likely ordinary systematics or disturbed dynamics.",
            "Guardrail": GUARDRAIL,
        },
        {
            "TestID": "T03",
            "NextTest": "map_readiness_join",
            "Question": "Can W_tau_eff be joined to sky, distance, and environment metadata without silent imputation?",
            "PassCondition": "RA, Dec, distance, uncertainty, and environment provenance are available or missingness is explicit.",
            "FailureInterpretation": "Do not attempt field-map interpretation.",
            "Guardrail": GUARDRAIL,
        },
        {
            "TestID": "T04",
            "NextTest": "heldout_formula_freeze",
            "Question": "Can a fixed S_tau_full expression be declared before endpoint readout?",
            "PassCondition": "Formula, coefficients, allowed inputs, and primary endpoint are frozen before evaluation.",
            "FailureInterpretation": "Any improvement remains exploratory and non-paper-grade.",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report() -> None:
    lines = [
        "# Tau Core Weight Model Gate v0.1",
        "",
        "This gate continues the residual signal-candidate branch without jumping to field mapping. It freezes the next model interpretation to test: TPG carries local Tau Core weights, while the remaining residual structure is a candidate for missing environment- and observer-dependent weights.",
        "",
        "## Working Equation",
        "",
        "The branch should treat the current TPG prescription as the local-weight baseline:",
        "",
        "`V_TPG(R)=Vbar(R)*(1+alpha*ln(1+a0/aN))`.",
        "",
        "The missing term is not a new pointwise constant. The evidence favors an integrated state:",
        "",
        "`S_tau_full(R)=1+g(W_env_obs(R))`",
        "",
        "where `W_env_obs(R)` must be predicted from a predeclared history, geometry, environment, or observer-state proxy before any endpoint velocity readout.",
        "",
        "## Why This Gate Exists",
        "",
        "- The residual is structured, signed, cumulative, and history-dependent.",
        "- The history readout improves the TPG baseline, especially in C systems.",
        "- The history readout is not external prediction, so the next model must replace inner residual history with source-side or geometry-side predictors.",
        "",
        "## Claim Boundary",
        "",
        "This gate does not prove Tau Core, does not build a field map, and does not fit a new formula. It freezes the next model target and the tests required to make it paper-grade.",
        "",
        "## Generated Files",
        "",
        "- `tau_core_weight_model_gate_v01.csv`",
        "- `tau_core_weight_model_evidence_matrix_v01.csv`",
        "- `tau_core_weight_model_next_tests_v01.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "tau_core_weight_model_gate_v01.md",
            "tau_core_weight_model_gate_v01.csv",
            "tau_core_weight_model_evidence_matrix_v01.csv",
            "tau_core_weight_model_next_tests_v01.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["tau_core_weight_model_gate_status"] = "local_plus_environment_observer_weight_model_target_frozen"
    manifest["paper2_next_gate"] = "source_side_or_geometry_proxy_for_w_env_obs_before_velocity_endpoint"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_csv(
        MODEL_OUT,
        model_rows(),
        [
            "ComponentID",
            "Component",
            "Symbol",
            "Definition",
            "OperationalForm",
            "AllowedInputs",
            "ForbiddenInputs",
            "Guardrail",
        ],
    )
    write_csv(
        EVIDENCE_OUT,
        evidence_rows(),
        ["EvidenceID", "Observation", "Metric", "Supports", "DoesNotProve", "Guardrail"],
    )
    write_csv(
        TEST_OUT,
        test_rows(),
        ["TestID", "NextTest", "Question", "PassCondition", "FailureInterpretation", "Guardrail"],
    )
    write_report()
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
