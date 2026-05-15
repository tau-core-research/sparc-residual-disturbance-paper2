#!/usr/bin/env python3
"""Audit Projection_RMS classifier errors for residual-disturbance inference."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "studies/sparc_residual_disturbance_inference_v01/packet_v01_seed"
PAPER1_PACKET = ROOT / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced"
PREDICTIONS = PACKET / "residual_inference_loogo_predictions.csv"
FEATURES = PACKET / "residual_feature_table.csv"
EVIDENCE = PAPER1_PACKET / "external_evidence_table.csv"
ERROR_CSV = PACKET / "residual_inference_projection_rms_error_audit.csv"
SUMMARY_CSV = PACKET / "residual_inference_projection_rms_error_summary.csv"
REPORT = PACKET / "residual_inference_projection_rms_error_audit.md"

PRIMARY_PREDICTOR = "Projection_RMS"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["GalaxyName"]: row for row in rows}


def error_family(true_class: str, predicted: str) -> str:
    if true_class == predicted:
        return "correct"
    if true_class == "A" and predicted == "C":
        return "false_positive_A_as_C"
    return "false_negative_C_as_A"


def diagnostic_note(row: dict[str, str], feature: dict[str, str], evidence: dict[str, str]) -> str:
    family = error_family(row["TrueClass"], row["PredictedClass"])
    evidence_type = evidence.get("EvidenceType", "")
    confidence = evidence.get("Confidence", "")
    score = float(row["Score"])
    threshold = float(row["LOOGOThreshold"])
    margin = score - threshold
    if family == "correct":
        return "projection_rms_agrees_with_external_class"
    if family == "false_positive_A_as_C":
        return (
            "residual_high_for_external_A; candidate hidden systematics, underestimated observational uncertainty, "
            "or externally regular but dynamically hard case"
        )
    return (
        "residual_low_for_external_C; candidate disturbance not expressed in smooth rotation-curve residuals, "
        f"or label evidence type {evidence_type} with confidence {confidence} traces morphology more than residual burden; "
        f"margin={margin:.6f}"
    )


def build_error_rows() -> list[dict[str, str]]:
    features = index(read_csv(FEATURES))
    evidence = index(read_csv(EVIDENCE))
    rows: list[dict[str, str]] = []
    for prediction in read_csv(PREDICTIONS):
        if prediction["Predictor"] != PRIMARY_PREDICTOR:
            continue
        galaxy = prediction["GalaxyName"]
        feature = features[galaxy]
        ev = evidence.get(galaxy, {})
        margin = float(prediction["Score"]) - float(prediction["LOOGOThreshold"])
        family = error_family(prediction["TrueClass"], prediction["PredictedClass"])
        rows.append(
            {
                "GalaxyName": galaxy,
                "TrueClass": prediction["TrueClass"],
                "PredictedClass": prediction["PredictedClass"],
                "ErrorFamily": family,
                "ProjectionRMS": prediction["Score"],
                "LOOGOThreshold": prediction["LOOGOThreshold"],
                "MarginScoreMinusThreshold": f"{margin:.9f}",
                "NPoints": feature["NPoints"],
                "ProjectionLowAccelerationMean": feature["Projection_LowAccelerationMean"],
                "ProjectionRadiusPearson": feature["Projection_RadiusPearson"],
                "EvidenceType": ev.get("EvidenceType", ""),
                "Confidence": ev.get("Confidence", ""),
                "EvidenceSummary": ev.get("EvidenceSummary", ""),
                "DiagnosticNote": diagnostic_note(prediction, feature, ev),
            }
        )
    return rows


def build_summary_rows(error_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    family_counts = Counter(row["ErrorFamily"] for row in error_rows)
    evidence_counts = Counter(
        row["EvidenceType"] for row in error_rows if row["ErrorFamily"] != "correct"
    )
    rows = [
        {
            "SummaryID": "projection_rms_confusion",
            "N": str(len(error_rows)),
            "Correct": str(family_counts["correct"]),
            "FalsePositiveAasC": str(family_counts["false_positive_A_as_C"]),
            "FalseNegativeCasA": str(family_counts["false_negative_C_as_A"]),
            "DominantErrorFamily": "false_negative_C_as_A",
            "Interpretation": "Projection_RMS is conservative for C: most errors are externally disturbed galaxies with low residual burden.",
        }
    ]
    for evidence_type, count in sorted(evidence_counts.items()):
        rows.append(
            {
                "SummaryID": f"error_evidence_type_{evidence_type}",
                "N": str(count),
                "Correct": "",
                "FalsePositiveAasC": "",
                "FalseNegativeCasA": "",
                "DominantErrorFamily": "",
                "Interpretation": "Evidence type represented among Projection_RMS errors.",
            }
        )
    return rows


def write_report(error_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    false_pos = [row for row in error_rows if row["ErrorFamily"] == "false_positive_A_as_C"]
    false_neg = [row for row in error_rows if row["ErrorFamily"] == "false_negative_C_as_A"]
    lines = [
        "# Projection RMS Error Audit v0.1",
        "",
        "This packet audits where the frozen `Projection_RMS` residual-disturbance baseline fails under leave-one-galaxy-out validation.",
        "",
        "## Error Counts",
        "",
        f"- Correct: {summary_rows[0]['Correct']}",
        f"- False positive A-as-C: {summary_rows[0]['FalsePositiveAasC']}",
        f"- False negative C-as-A: {summary_rows[0]['FalseNegativeCasA']}",
        "",
        "## False Positives",
        "",
        ", ".join(row["GalaxyName"] for row in false_pos) if false_pos else "none",
        "",
        "These are externally regular/calmer galaxies whose residual burden is C-like. They are the most interesting candidates for hidden systematics or a physically hard regular disk.",
        "",
        "## False Negatives",
        "",
        ", ".join(row["GalaxyName"] for row in false_neg) if false_neg else "none",
        "",
        "These are externally disturbed galaxies whose projection residual burden is low. They show that external disturbance is not guaranteed to appear as high residual RMS.",
        "",
        "## Interpretation",
        "",
        "The error pattern is scientifically useful: the baseline is fairly precise for C predictions, but misses several C-labeled systems. This supports using residuals as a diagnostic screen, not as a replacement for external evidence.",
        "",
        "## Next Gate",
        "",
        "Use this audit to define candidate follow-up categories: hidden-systematics A-as-C, quiet-disturbance C-as-A, and robust C-like residual cases. Do not relabel galaxies from residuals alone.",
        "",
        "## Generated Files",
        "",
        "- `residual_inference_projection_rms_error_audit.csv`",
        "- `residual_inference_projection_rms_error_summary.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    files.update(
        {
            "residual_inference_projection_rms_error_audit.md",
            "residual_inference_projection_rms_error_audit.csv",
            "residual_inference_projection_rms_error_summary.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["projection_rms_error_audit_status"] = "error_taxonomy_complete_no_residual_relabeling"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    error_rows = build_error_rows()
    summary_rows = build_summary_rows(error_rows)
    write_csv(
        ERROR_CSV,
        error_rows,
        [
            "GalaxyName",
            "TrueClass",
            "PredictedClass",
            "ErrorFamily",
            "ProjectionRMS",
            "LOOGOThreshold",
            "MarginScoreMinusThreshold",
            "NPoints",
            "ProjectionLowAccelerationMean",
            "ProjectionRadiusPearson",
            "EvidenceType",
            "Confidence",
            "EvidenceSummary",
            "DiagnosticNote",
        ],
    )
    write_csv(
        SUMMARY_CSV,
        summary_rows,
        [
            "SummaryID",
            "N",
            "Correct",
            "FalsePositiveAasC",
            "FalseNegativeCasA",
            "DominantErrorFamily",
            "Interpretation",
        ],
    )
    write_report(error_rows, summary_rows)
    update_manifest()
    print(REPORT)
    print(f"projection_rms_error_rows={len(error_rows)}")


if __name__ == "__main__":
    main()
