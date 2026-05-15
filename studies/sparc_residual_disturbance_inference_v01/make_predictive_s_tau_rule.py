#!/usr/bin/env python3
"""Freeze a source-side S_tau rule without Vobs or residual target leakage."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET, ROOT


EVIDENCE = (
    ROOT
    / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/external_evidence_table.csv"
)
S_TAU_EFF = PACKET / "s_tau_eff_galaxy_summary.csv"
RULE_CSV = PACKET / "predictive_s_tau_rule_v01.csv"
PREDICTIONS_CSV = PACKET / "predictive_s_tau_by_galaxy_v01.csv"
READOUT_CSV = PACKET / "predictive_s_tau_readout_v01.csv"
REPORT = PACKET / "predictive_s_tau_rule_v01.md"


BASE_RULE = {
    "regular_kinematics": 1.05,
    "low_asymmetry": 1.05,
    "disturbed_hi": 0.85,
    "warp": 0.85,
    "interaction": 0.75,
    "tidal": 0.75,
    "mixed": 0.90,
    "other": 0.95,
    "no_data": 0.95,
}

CONFIDENCE_ADJUST = {
    "High": 0.025,
    "Medium": 0.0,
    "Low": -0.025,
}

COHERENT_TYPES = {"regular_kinematics", "low_asymmetry"}
DISTURBED_TYPES = {"disturbed_hi", "warp", "interaction", "tidal"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.9f}"


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def median(values: list[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    n = len(ordered)
    if n % 2:
        return ordered[n // 2]
    return (ordered[n // 2 - 1] + ordered[n // 2]) / 2


def rmse(values: list[float]) -> float:
    return math.sqrt(mean([value * value for value in values])) if values else math.nan


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return math.nan
    mx = mean(xs)
    my = mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denom = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    if denom == 0:
        return math.nan
    return sum(x * y for x, y in zip(dx, dy)) / denom


def source_side_s_tau(evidence_type: str, confidence: str) -> tuple[float, str]:
    base = BASE_RULE.get(evidence_type, 0.95)
    adjust = CONFIDENCE_ADJUST.get(confidence, 0.0)
    if evidence_type in COHERENT_TYPES:
        value = base + max(0.0, adjust)
    elif evidence_type in DISTURBED_TYPES:
        value = base - max(0.0, adjust)
    else:
        value = base + adjust
    value = min(1.10, max(0.70, value))
    return value, "source_evidence_type_confidence_no_vobs_no_residuals"


def rule_rows() -> list[dict[str, str]]:
    rows = []
    for evidence_type, base in BASE_RULE.items():
        rows.append(
            {
                "RuleID": "S_tau_source_v01",
                "EvidenceType": evidence_type,
                "BaseS_tau": fmt(base),
                "HighConfidencePolicy": (
                    "raise_coherent_or_lower_disturbed_by_0p025"
                    if evidence_type in COHERENT_TYPES | DISTURBED_TYPES
                    else "add_plus_0p025"
                ),
                "MediumConfidencePolicy": "no_adjustment",
                "LowConfidencePolicy": (
                    "lower_uncertain_by_0p025"
                    if evidence_type not in COHERENT_TYPES | DISTURBED_TYPES
                    else "no_extra_directional_adjustment"
                ),
                "AllowedInputs": "EvidenceType;Confidence",
                "ForbiddenInputs": "Vobs;Vbar;Projection_RMS;residuals;S_tau_eff;Class",
                "InterpretationGuardrail": "frozen_source_side_rule_not_fit_to_s_tau_eff",
            }
        )
    return rows


def prediction_rows() -> list[dict[str, str]]:
    rows = []
    for evidence in read_csv(EVIDENCE):
        value, rule = source_side_s_tau(evidence["EvidenceType"], evidence["Confidence"])
        rows.append(
            {
                "GalaxyName": evidence["GalaxyName"],
                "ExternalClassAuditOnly": evidence["Class"],
                "EvidenceType": evidence["EvidenceType"],
                "Confidence": evidence["Confidence"],
                "Predicted_S_tau_source_v01": fmt(value),
                "PredictionRule": rule,
                "InterpretationGuardrail": "prediction_uses_external_source_metadata_only",
            }
        )
    return rows


def readout_rows(predictions: list[dict[str, str]]) -> list[dict[str, str]]:
    s_eff = {row["GalaxyName"]: row for row in read_csv(S_TAU_EFF)}
    rows = []
    for prediction in predictions:
        galaxy = prediction["GalaxyName"]
        if galaxy not in s_eff:
            continue
        target = float(s_eff[galaxy]["Median_S_tau_eff_clipped"])
        predicted = float(prediction["Predicted_S_tau_source_v01"])
        rows.append(
            {
                **prediction,
                "Median_S_tau_eff_clipped_ReadoutOnly": fmt(target),
                "PredictionMinusReadout": fmt(predicted - target),
                "AbsPredictionError": fmt(abs(predicted - target)),
                "BaselineS_tau1AbsError": fmt(abs(1.0 - target)),
                "ReadoutUse": "post_freeze_diagnostic_only_not_rule_training",
            }
        )
    return rows


def summary_metrics(rows: list[dict[str, str]]) -> dict[str, float]:
    pred = [float(row["Predicted_S_tau_source_v01"]) for row in rows]
    target = [float(row["Median_S_tau_eff_clipped_ReadoutOnly"]) for row in rows]
    errors = [float(row["PredictionMinusReadout"]) for row in rows]
    abs_errors = [float(row["AbsPredictionError"]) for row in rows]
    baseline_abs = [float(row["BaselineS_tau1AbsError"]) for row in rows]
    return {
        "N": float(len(rows)),
        "Pearson_predicted_vs_eff": pearson(pred, target),
        "MAE_source_rule": mean(abs_errors),
        "MAE_constant_1": mean(baseline_abs),
        "RMSE_source_rule": rmse(errors),
        "RMSE_constant_1": rmse([1.0 - value for value in target]),
        "MedianError_source_rule": median(errors),
    }


def write_report(rows: list[dict[str, str]], metrics: dict[str, float]) -> None:
    class_groups: dict[str, list[float]] = {"A": [], "C": []}
    for row in rows:
        klass = row["ExternalClassAuditOnly"]
        if klass in class_groups:
            class_groups[klass].append(float(row["Predicted_S_tau_source_v01"]))
    lines = [
        "# Predictive S_tau Rule v0.1",
        "",
        "This gate freezes a source-side `S_tau` rule before looking at the `S_tau_eff` readout. The rule uses only external evidence metadata: `EvidenceType` and `Confidence`.",
        "",
        "## Frozen Rule",
        "",
        "- regular or low-asymmetry evidence maps near `S_tau > 1`",
        "- disturbed HI, warp, interaction, and tidal evidence map below `S_tau = 1`",
        "- mixed, other, and no-data evidence remain close to neutral",
        "- confidence applies only a small directional adjustment",
        "",
        "Forbidden inputs: `Vobs`, `Vbar`, residuals, `Projection_RMS`, `S_tau_eff`, and the A/C class label.",
        "",
        "## Post-Freeze Readout",
        "",
        f"- Galaxies with `S_tau_eff` readout: {int(metrics['N'])}",
        f"- Pearson(predicted source S_tau, empirical S_tau_eff): {fmt(metrics['Pearson_predicted_vs_eff'])}",
        f"- MAE source rule: {fmt(metrics['MAE_source_rule'])}",
        f"- MAE constant S_tau=1 baseline: {fmt(metrics['MAE_constant_1'])}",
        f"- RMSE source rule: {fmt(metrics['RMSE_source_rule'])}",
        f"- RMSE constant S_tau=1 baseline: {fmt(metrics['RMSE_constant_1'])}",
        f"- Median predicted S_tau for A: {fmt(median(class_groups['A']))}",
        f"- Median predicted S_tau for C: {fmt(median(class_groups['C']))}",
        "",
        "## Interpretation",
        "",
        "This is the first leakage-controlled `S_tau` predictor. It is still not a physical derivation, and it is not a fitted improvement over TPG. Its role is to define a simple predeclared source-side mapping that can be stress-tested against the empirical `S_tau_eff` diagnostic and later replaced by kinematic or radial source rules.",
        "",
        "## Next Gate",
        "",
        "Evaluate whether the source-side rule improves velocity residuals relative to `S_tau=1` without refitting any coefficients.",
        "",
        "## Generated Files",
        "",
        "- `predictive_s_tau_rule_v01.csv`",
        "- `predictive_s_tau_by_galaxy_v01.csv`",
        "- `predictive_s_tau_readout_v01.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "predictive_s_tau_rule_v01.csv",
            "predictive_s_tau_by_galaxy_v01.csv",
            "predictive_s_tau_readout_v01.csv",
            "predictive_s_tau_rule_v01.md",
        }
    )
    manifest["files"] = sorted(files)
    manifest["predictive_s_tau_rule_status"] = (
        "source_side_rule_frozen_no_vobs_no_residual_inputs"
    )
    manifest["paper2_next_gate"] = "evaluate_frozen_s_tau_rule_against_tpg_s_tau_equals_1"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rules = rule_rows()
    predictions = prediction_rows()
    readout = readout_rows(predictions)
    metrics = summary_metrics(readout)
    write_csv(
        RULE_CSV,
        rules,
        [
            "RuleID",
            "EvidenceType",
            "BaseS_tau",
            "HighConfidencePolicy",
            "MediumConfidencePolicy",
            "LowConfidencePolicy",
            "AllowedInputs",
            "ForbiddenInputs",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        PREDICTIONS_CSV,
        predictions,
        [
            "GalaxyName",
            "ExternalClassAuditOnly",
            "EvidenceType",
            "Confidence",
            "Predicted_S_tau_source_v01",
            "PredictionRule",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        READOUT_CSV,
        readout,
        [
            "GalaxyName",
            "ExternalClassAuditOnly",
            "EvidenceType",
            "Confidence",
            "Predicted_S_tau_source_v01",
            "PredictionRule",
            "InterpretationGuardrail",
            "Median_S_tau_eff_clipped_ReadoutOnly",
            "PredictionMinusReadout",
            "AbsPredictionError",
            "BaselineS_tau1AbsError",
            "ReadoutUse",
        ],
    )
    write_report(readout, metrics)
    update_manifest()
    print(REPORT)
    print(f"predictive_s_tau_readout={len(readout)}")


if __name__ == "__main__":
    main()
