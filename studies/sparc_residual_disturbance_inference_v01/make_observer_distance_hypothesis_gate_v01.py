#!/usr/bin/env python3
"""Freeze the observer-distance hypothesis gate without opening a formula endpoint."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


METRICS = PACKET / "multivariable_no_velocity_stress_metrics_v01.csv"
DECISIONS = PACKET / "multivariable_no_velocity_stress_decision_v01.csv"

CLAIMS_OUT = PACKET / "observer_distance_hypothesis_claim_boundary_v01.csv"
VALIDATION_OUT = PACKET / "observer_distance_hypothesis_validation_plan_v01.csv"
READINESS_OUT = PACKET / "observer_distance_hypothesis_readiness_v01.csv"
REPORT = PACKET / "observer_distance_hypothesis_gate_v01.md"

GUARDRAIL = "observer_distance_hypothesis_only_no_formula_no_tau_core_proof"


def metric(metric_name: str) -> str:
    for row in read_csv(METRICS):
        if row["Metric"] == metric_name:
            return row["Value"]
    raise KeyError(metric_name)


def decision_status(decision_id: str) -> str:
    for row in read_csv(DECISIONS):
        if row["DecisionID"] == decision_id:
            return row["Status"]
    raise KeyError(decision_id)


def claim_rows() -> list[dict[str, str]]:
    raw_p = metric("pearson_tau_distance_raw_vs_w_tau_score")
    raw_auc = metric("auc_nearer_vs_farther_tau_distance_raw")
    partial_p = metric(
        "partial_pearson_tau_distance_after_nuisance_vs_score_after_nuisance"
    )
    partial_auc = metric("partial_auc_tau_distance_residual_high_vs_low_score_residual")
    nuisance_r2 = metric("nuisance_model_r2_for_w_tau_score")
    return [
        {
            "ClaimID": "ODC01",
            "Claim": "A nearer-higher observer-distance candidate channel is positively associated with W_tau_eff candidate score in the SPARC A/C packet.",
            "Status": "supported_as_in_sample_hypothesis",
            "Evidence": f"raw Pearson={raw_p}; raw AUC={raw_auc}",
            "AllowedWording": "observer-distance candidate channel",
            "ForbiddenWording": "Tau Core field;gravity proof;velocity formula",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ClaimID": "ODC02",
            "Claim": "The observer-distance candidate remains positive after simple angular-size, sampling, velocity-error, inclination-error, fractional-distance-error, and physical-radius nuisance controls.",
            "Status": "supported_as_stress_survival",
            "Evidence": f"partial Pearson={partial_p}; partial AUC={partial_auc}; nuisance-only R2={nuisance_r2}",
            "AllowedWording": "survives the no-velocity nuisance stress",
            "ForbiddenWording": "independent validation;causal observer field",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ClaimID": "ODC03",
            "Claim": "The result distinguishes a Tau Core observer effect from ordinary observability bias.",
            "Status": "not_established",
            "Evidence": "Requires external validation and stronger resolution/environment controls.",
            "AllowedWording": "compatible with an observer-centered Tau Core hypothesis",
            "ForbiddenWording": "rules out observability bias;proves observer effect",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ClaimID": "ODC04",
            "Claim": "The result permits opening an S_tau_full velocity formula endpoint.",
            "Status": "blocked",
            "Evidence": "All current readouts are covariate/score stress tests, not velocity endpoints.",
            "AllowedWording": "hypothesis gate",
            "ForbiddenWording": "formula validation;coefficient selection;velocity endpoint",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def validation_rows() -> list[dict[str, str]]:
    return [
        {
            "ValidationID": "ODV01",
            "Target": "WHISP overlap",
            "RequiredInput": "published HI asymmetry/lopsidedness plus independent distance metadata",
            "PassCondition": "nearer-higher distance channel remains positive after asymmetry and angular-size controls",
            "FailCondition": "distance channel vanishes or reverses after source-family controls",
            "EndpointPermission": "no_velocity_endpoint",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ValidationID": "ODV02",
            "Target": "THINGS/LITTLE_THINGS/HALOGAS small overlaps",
            "RequiredInput": "published geometry, distance, cube/ring sampling, and non-circular/pressure/linewidth controls",
            "PassCondition": "distance-like residual score trend is not explained by angular-size, sampling, or non-circular controls",
            "FailCondition": "trend is absorbed by resolution or kinematic systematics",
            "EndpointPermission": "no_velocity_endpoint",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ValidationID": "ODV03",
            "Target": "external environment coverage",
            "RequiredInput": "residual-blind group/tidal/large-scale-environment proxies with distance coverage",
            "PassCondition": "observer-distance trend and environment trend can be separated in a predeclared stress test",
            "FailCondition": "distance channel is a proxy for environment catalogue incompleteness",
            "EndpointPermission": "no_velocity_endpoint",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ValidationID": "ODV04",
            "Target": "future velocity formula gate",
            "RequiredInput": "at least one external source-family pass and one observability-control pass",
            "PassCondition": "predeclared source-side channel predicts W_tau_eff without target residual leakage",
            "FailCondition": "only in-sample W_tau_eff score associations are available",
            "EndpointPermission": "blocked_until_external_validation",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def readiness_rows(claims: list[dict[str, str]]) -> list[dict[str, str]]:
    supported = [row for row in claims if row["Status"].startswith("supported")]
    blocked = [row for row in claims if row["Status"] in {"blocked", "not_established"}]
    return [
        {
            "ReadinessID": "ODR01",
            "Question": "Can this be written as a Paper 2 hypothesis result?",
            "Status": "yes_with_guardrails",
            "Rationale": f"{len(supported)} supported hypothesis claims; {len(blocked)} blocked or not-established claims.",
            "NextAction": "write_as_observer_distance_hypothesis_not_as_tau_core_proof",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ReadinessID": "ODR02",
            "Question": "Can this open a velocity formula endpoint?",
            "Status": "no",
            "Rationale": decision_status("MV02"),
            "NextAction": "external_validation_before_velocity_endpoint",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "ReadinessID": "ODR03",
            "Question": "What is the next gate?",
            "Status": "ready",
            "Rationale": "The hypothesis is frozen; the next scientific step is external source-family validation.",
            "NextAction": "observer_distance_external_validation_readout",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(
    claims: list[dict[str, str]],
    validation: list[dict[str, str]],
    readiness: list[dict[str, str]],
) -> None:
    lines = [
        "# Observer-Distance Hypothesis Gate v0.1",
        "",
        "This gate freezes the observer-distance result as a hypothesis-level result only. It does not open an `S_tau_full` velocity endpoint and does not claim a Tau Core field detection.",
        "",
        "## Frozen Hypothesis",
        "",
        "`H_tau_distance`: a nearer-higher observer-distance candidate channel remains associated with the residual-inferred `W_tau_eff` candidate score after simple angular-size, sampling, velocity-error, inclination-error, distance-fractional-error, and physical-radius nuisance controls.",
        "",
        "## Current Evidence",
        "",
        f"- Raw Pearson: {metric('pearson_tau_distance_raw_vs_w_tau_score')}",
        f"- Raw AUC: {metric('auc_nearer_vs_farther_tau_distance_raw')}",
        f"- Partial Pearson after nuisance controls: {metric('partial_pearson_tau_distance_after_nuisance_vs_score_after_nuisance')}",
        f"- Partial residual AUC: {metric('partial_auc_tau_distance_residual_high_vs_low_score_residual')}",
        f"- Nuisance-only score R2: {metric('nuisance_model_r2_for_w_tau_score')}",
        "",
        "## Interpretation",
        "",
        "The result supports carrying an observer-distance channel forward as a predeclared hypothesis. It remains compatible with Tau Core's observer-centered framing, but it is not a proof of Tau Core and not a velocity formula validation.",
        "",
        "## Required External Validation",
        "",
        "At least one external source-family validation must reproduce the direction under predeclared controls before any formula endpoint can be considered.",
        "",
        "## Generated Files",
        "",
        "- `observer_distance_hypothesis_claim_boundary_v01.csv`",
        "- `observer_distance_hypothesis_validation_plan_v01.csv`",
        "- `observer_distance_hypothesis_readiness_v01.csv`",
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
    for path in [CLAIMS_OUT, VALIDATION_OUT, READINESS_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["observer_distance_hypothesis_gate_status"] = (
        "hypothesis_frozen_external_validation_required"
    )
    manifest["paper2_next_gate"] = "observer_distance_external_validation_readout"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    claims = claim_rows()
    validation = validation_rows()
    readiness = readiness_rows(claims)
    claim_fields = [
        "ClaimID",
        "Claim",
        "Status",
        "Evidence",
        "AllowedWording",
        "ForbiddenWording",
        "InterpretationGuardrail",
    ]
    validation_fields = [
        "ValidationID",
        "Target",
        "RequiredInput",
        "PassCondition",
        "FailCondition",
        "EndpointPermission",
        "InterpretationGuardrail",
    ]
    readiness_fields = [
        "ReadinessID",
        "Question",
        "Status",
        "Rationale",
        "NextAction",
        "InterpretationGuardrail",
    ]
    write_csv(CLAIMS_OUT, claims, claim_fields)
    write_csv(VALIDATION_OUT, validation, validation_fields)
    write_csv(READINESS_OUT, readiness, readiness_fields)
    write_report(claims, validation, readiness)
    update_manifest()


if __name__ == "__main__":
    main()
