#!/usr/bin/env python3
"""Freeze the next classifier gate after LOOGO validation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "studies/sparc_residual_disturbance_inference_v01/packet_v01_seed"
LOOGO_METRICS = PACKET / "residual_inference_loogo_metric_summary.csv"
GATE_CSV = PACKET / "residual_inference_classifier_gate_v01.csv"
REPORT = PACKET / "residual_inference_classifier_gate_v01.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def metric_by_predictor() -> dict[str, dict[str, str]]:
    return {row["Predictor"]: row for row in read_csv(LOOGO_METRICS)}


def build_gate_rows() -> list[dict[str, str]]:
    metrics = metric_by_predictor()
    rms = metrics["Projection_RMS"]
    low_acc = metrics["Projection_LowAccelerationMean"]
    composite = metrics["ResidualDisturbanceScore_v01"]
    return [
        {
            "GateID": "RDI_G01_primary_baseline",
            "Priority": "1",
            "Decision": "freeze_projection_rms_as_primary_baseline",
            "Rationale": (
                f"Projection_RMS has the strongest LOOGO AUC={rms['AUC_C_higher']} "
                f"and accuracy={rms['Accuracy']} with simple physical meaning."
            ),
            "AllowedNextAction": "report_projection_rms_as_primary_residual_diagnostic_baseline",
            "BlockedAction": "do_not_replace_with_multifeature_score_unless_nested_validation_beats_baseline",
            "Status": "primary_baseline_frozen",
        },
        {
            "GateID": "RDI_G02_secondary_baseline",
            "Priority": "2",
            "Decision": "keep_low_acceleration_mean_as_secondary_sanity_check",
            "Rationale": (
                f"Projection_LowAccelerationMean has similar LOOGO accuracy={low_acc['Accuracy']} "
                f"and AUC={low_acc['AUC_C_higher']} but is less general than full Projection_RMS."
            ),
            "AllowedNextAction": "report_as_supporting_low_acceleration_readout",
            "BlockedAction": "do_not_claim_low_acceleration_feature_is_unique_without_comparator_holdout",
            "Status": "secondary_supporting_baseline",
        },
        {
            "GateID": "RDI_G03_composite_score",
            "Priority": "3",
            "Decision": "demote_residual_disturbance_score_v01_to_exploratory",
            "Rationale": (
                f"The first composite score underperforms: LOOGO accuracy={composite['Accuracy']} "
                f"and AUC={composite['AUC_C_higher']}."
            ),
            "AllowedNextAction": "redesign_only_under_predeclared_nested_validation",
            "BlockedAction": "do_not_use_current_composite_as_primary_classifier",
            "Status": "demoted_exploratory",
        },
        {
            "GateID": "RDI_G04_next_validation",
            "Priority": "4",
            "Decision": "require_nested_or_source_family_validation_before_paper_claim",
            "Rationale": "LOOGO is a useful first sanity check but still reuses the same Paper 1 label set and source context.",
            "AllowedNextAction": "freeze_nested_validation_or_external_source_family_holdout",
            "BlockedAction": "do_not_present_current_results_as_paper_grade_classifier",
            "Status": "open_required_upgrade",
        },
    ]


def write_report(rows: list[dict[str, str]]) -> None:
    lines = [
        "# Residual-Disturbance Classifier Gate v0.1",
        "",
        "This packet freezes the second-stage decision boundary after the first leave-one-galaxy-out validation.",
        "",
        "## Decision",
        "",
        "`Projection_RMS` becomes the primary baseline. It is simple, physically interpretable, and currently stronger than the first multifeature residual-disturbance score.",
        "",
        "The current composite score is demoted to exploratory. Adding features is not automatically an improvement.",
        "",
        "## Gates",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"### {row['GateID']}",
                "",
                f"- Priority: {row['Priority']}",
                f"- Decision: `{row['Decision']}`",
                f"- Rationale: {row['Rationale']}",
                f"- Allowed next action: {row['AllowedNextAction']}",
                f"- Blocked action: {row['BlockedAction']}",
                f"- Status: `{row['Status']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Guardrail",
            "",
            "Do not optimize feature sets on the same A/C labels and then report the result as validated. Any richer classifier must beat the `Projection_RMS` baseline under nested validation or an external source-family holdout.",
            "",
            "## Generated File",
            "",
            "- `residual_inference_classifier_gate_v01.csv`",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    files.update({"residual_inference_classifier_gate_v01.md", "residual_inference_classifier_gate_v01.csv"})
    manifest["files"] = sorted(files)
    manifest["classifier_gate_status"] = "projection_rms_primary_baseline_frozen"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_gate_rows()
    write_csv(
        GATE_CSV,
        rows,
        ["GateID", "Priority", "Decision", "Rationale", "AllowedNextAction", "BlockedAction", "Status"],
    )
    write_report(rows)
    update_manifest()
    print(REPORT)
    print(f"classifier_gate_rows={len(rows)}")


if __name__ == "__main__":
    main()
