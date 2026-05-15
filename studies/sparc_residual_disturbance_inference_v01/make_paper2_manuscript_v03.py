#!/usr/bin/env python3
"""Generate the Paper 2 v0.3 publication-style draft and summary tables."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from make_packet_v01_seed import PACKET, write_csv


DRAFT = PACKET / "paper2_manuscript_draft_v03.md"
ABSTRACT = PACKET / "paper2_abstract_v03.md"
SUMMARY_TABLE = PACKET / "paper2_results_summary_v03.csv"
EXTERNAL_TABLE = PACKET / "paper2_external_proxy_summary_v03.csv"
GATE = PACKET / "paper2_manuscript_v03_gate.csv"

GUARDRAIL = "paper2_v03_publication_draft_diagnostic_audit_no_tau_validation"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def result_summary_rows() -> list[dict[str, str]]:
    metrics = {row["Metric"]: row for row in read_csv(PACKET / "paper2_final_metric_table.csv")}
    return [
        {
            "ResultID": "R1",
            "Quantity": "Projection_RMS LOOGO AUC",
            "Value": metrics["Projection_RMS_LOOGO"]["Value"],
            "Interpretation": "primary internal residual-shape diagnostic",
            "ClaimBoundary": "SPARC-internal class recovery, not external validation",
            "Guardrail": GUARDRAIL,
        },
        {
            "ResultID": "R2",
            "Quantity": "Projection_RMS shuffled-label p",
            "Value": metrics["Projection_RMS_shuffle_null_p"]["Value"],
            "Interpretation": "unlikely under random A/C labels in this packet",
            "ClaimBoundary": "null test only, not independent replication",
            "Guardrail": GUARDRAIL,
        },
        {
            "ResultID": "R3",
            "Quantity": "MOND-simple RMS LOOGO AUC",
            "Value": metrics["MOND_RMS_LOOGO_AUC"]["Value"],
            "Interpretation": "low-acceleration residual-family support",
            "ClaimBoundary": "reduces projection uniqueness claim",
            "Guardrail": GUARDRAIL,
        },
        {
            "ResultID": "R4",
            "Quantity": "RAR-like RMS LOOGO AUC",
            "Value": metrics["RAR_RMS_LOOGO_AUC"]["Value"],
            "Interpretation": "low-acceleration residual-family support",
            "ClaimBoundary": "not gravity-model selection",
            "Guardrail": GUARDRAIL,
        },
        {
            "ResultID": "R5",
            "Quantity": "Newtonian baryonic RMS LOOGO AUC",
            "Value": metrics["Newtonian_Baryonic_RMS_LOOGO_AUC"]["Value"],
            "Interpretation": "near-chance control",
            "ClaimBoundary": "does not prove low-acceleration physics by itself",
            "Guardrail": GUARDRAIL,
        },
    ]


def external_summary_rows() -> list[dict[str, str]]:
    rows = read_csv(PACKET / "paper2_external_validation_status_board_v02.csv")
    keep = ["WHISP_RESOLVED", "WHISP_MORPH", "REYNOLDS_LVH", "ALFALFA", "HALOGAS", "THINGS_ROUTE2"]
    output = []
    for row in rows:
        if row["FamilyID"] not in keep:
            continue
        output.append(
            {
                "FamilyID": row["FamilyID"],
                "JoinedN": row["JoinedN"],
                "PrimaryMetric": row["PrimaryMetric"],
                "Status": row["Status"],
                "ManuscriptRole": row["PaperRole"],
                "AllowedClaim": row["AllowedClaim"],
                "ForbiddenClaim": row["ForbiddenClaim"],
                "Guardrail": GUARDRAIL,
            }
        )
    return output


def abstract_text() -> str:
    return """# Paper 2 Abstract v0.3

We ask whether fixed rotation-curve residual-shape features can recover externally reviewed structural-disturbance labels in SPARC galaxies, and whether independent H I disturbance proxies support the same diagnostic direction. The study reverses the Paper 1 audit: the A/C labels are treated as frozen external targets, while residual features are evaluated as predictors under leave-one-galaxy-out thresholding, shuffled-label null tests, bootstrap uncertainty, baseline-family controls, and observability stress checks. The primary internal feature, `Projection_RMS`, reaches LOOGO AUC=0.771008403 with shuffled-label p=0.002000000 and bootstrap 95% AUC interval [0.600802469, 0.909100262]. MOND-simple and empirical RAR-like residual scores also separate A/C systems, whereas a Newtonian baryonic RMS control is near chance, indicating a low-acceleration residual-family effect rather than projection-formula uniqueness. External proxy readouts are supportive but not decisive: WHISP resolved-HI asymmetry is directionally aligned in a small overlap, WHISP morphology is mixed, Reynolds/LVHIS is promising but underpowered, and ALFALFA/HALOGAS are weak or control-like. A THINGS expansion route was closed as not score-ready after required machine-readable mass-model columns were not recovered. The result is therefore a reproducible residual-inference and external-proxy audit, not a Tau Core validation claim, not gravity-model selection, and not independent paper-grade external validation.
"""


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[column] for column in columns) + " |")
    return lines


def draft_text() -> str:
    summary = result_summary_rows()
    external = external_summary_rows()
    return "\n".join(
        [
            "# Residual-shape inference and external-proxy audit of structural disturbance in SPARC rotation curves",
            "",
            "## Abstract",
            "",
            abstract_text().split("\n\n", 1)[1].strip(),
            "",
            "## 1. Introduction",
            "",
            "Rotation-curve residuals are usually discussed as model error, but their radial structure can also carry information about non-equilibrium dynamics, non-circular motions, pressure support, beam smearing, inclination, and source-dependent observability. Paper 1 established a residual-blind association between externally assigned structural-disturbance labels and low-acceleration residual scatter in SPARC. Here we ask the inverse diagnostic question: can fixed residual-shape features recover those external labels better than chance?",
            "",
            "The scope is deliberately narrow. This paper does not use residuals to redefine the labels, does not validate Tau Core, and does not select a unique gravity law. It tests whether a frozen residual feature map contains recoverable information about externally reviewed A/C disturbance classes, then checks whether independent H I disturbance proxies point in the same direction.",
            "",
            "## 2. Data and Frozen Inputs",
            "",
            "The working A/C sample contains 45 SPARC galaxies inherited from the Paper 1 reproducibility packet: 17 externally regular A systems and 28 externally disturbed C systems. B-class systems remain excluded from the primary target labels because they encode uncertainty by construction. The residual features are computed from the fixed Paper 1 point map and are not retrained on the external-proxy catalogs.",
            "",
            "The public packet contains the derived tables, scripts, figures, and audit records needed to regenerate the diagnostic results. Raw survey products and raw SPARC rotmod files are not redistributed by this repository.",
            "",
            "## 3. Residual-Shape Endpoint",
            "",
            "The primary endpoint is `Projection_RMS`, the galaxy-level RMS of a fixed low-acceleration projection residual. It is used as an operational residual-shape score rather than as a physical proof of the projection formula. The key design choice is that the score is fixed before the external-proxy readouts are interpreted.",
            "",
            "## 4. Validation Design",
            "",
            "The primary internal validation uses leave-one-galaxy-out thresholding. For each held-out galaxy, the decision threshold is recomputed from the remaining A and C systems as the midpoint between their class medians. A shuffled-label null preserves class counts and tests whether the observed AUC is expected under random A/C labels. Bootstrap resampling estimates sample-size uncertainty. These tests are internal to SPARC and should not be described as independent validation.",
            "",
            "## 5. Primary Results",
            "",
            *markdown_table(
                summary,
                ["ResultID", "Quantity", "Value", "Interpretation", "ClaimBoundary"],
            ),
            "",
            "![Projection RMS distribution](../../../figures/paper2_projection_rms_distribution.svg)",
            "",
            "The primary signal is positive and statistically sharp in the frozen internal packet. The result is strongest when stated as class recovery from residual shape, not as a physical detection of an underlying field.",
            "",
            "## 6. Baseline-Family Comparison",
            "",
            "The baseline comparison weakens any projection-specific claim but strengthens the broader phenomenological result. MOND-simple and empirical RAR-like residual scores also separate A/C systems, while the Newtonian baryonic RMS score is near chance. The defensible conclusion is that A/C separation is concentrated in low-acceleration residual-family scores.",
            "",
            "![Baseline AUC comparison](../../../figures/paper2_baseline_auc_comparison.svg)",
            "",
            "This pattern is compatible with several physical readings: disturbed systems may violate smooth equilibrium assumptions, non-circular motions may be more important in low-acceleration regions, or observability may expose more disturbance structure in particular subsets. The present data do not distinguish these explanations.",
            "",
            "## 7. Failure Modes",
            "",
            "The error audit is retained because a useful diagnostic must show where it fails. False-negative C systems demonstrate that externally disturbed galaxies do not always produce large residual burden under a smooth rotation-curve score. False-positive A systems show that residual structure can arise without a strong external disturbance label.",
            "",
            "![Projection RMS error audit](../../../figures/paper2_error_audit.svg)",
            "",
            "These failures are not relabeling evidence. They are targets for follow-up inspection, especially where residual morphology, inclination, radial coverage, and H I kinematic asymmetry disagree.",
            "",
            "## 8. External Proxy Readouts",
            "",
            *markdown_table(
                external,
                ["FamilyID", "JoinedN", "PrimaryMetric", "Status", "ManuscriptRole"],
            ),
            "",
            "WHISP resolved-HI asymmetry is the strongest supportive external readout, but its overlap is small. WHISP morphology is mixed, Reynolds/LVHIS is promising but below the frozen N>=15 gate, and ALFALFA/HALOGAS do not provide strong directional support. The external evidence therefore supports the paper as an audit, not as an independent validation result.",
            "",
            "## 9. THINGS Route2 Negative Audit",
            "",
            "The THINGS expansion route was audited because it could have raised the independent-control overlap. It is now closed as not score-ready. The required machine-readable per-radius mass-model columns were not recovered for the missing galaxies, and the reconstruction route failed its photometry and solver-validation gates before any missing-galaxy scores were computed.",
            "",
            "This negative audit should remain visible. It documents why the paper does not claim THINGS N>=15, avoids plot-digitized or synthetic mass models, and prevents endpoint-driven data recovery from entering the evidence chain.",
            "",
            "## 10. Observability and Systematics",
            "",
            "Observability remains the main scientific caveat. Nearby galaxies can reveal asymmetry and morphological disturbance more easily than distant systems; inclination, beam smearing, asymmetric drift, pressure support, and non-circular motion can all alter residual morphology. The current controls reduce but do not eliminate these concerns.",
            "",
            "![Distance stress](../../../figures/paper2_distance_stress.svg)",
            "",
            "Accordingly, the result should be read as a reproducible SPARC diagnostic association with external-proxy context, not as a selection-function-proof physical inference.",
            "",
            "## 11. Claim Boundary",
            "",
            "Allowed claim: fixed residual-shape features recover externally reviewed A/C disturbance class better than chance in the current SPARC packet, and several external proxy readouts provide mixed but informative context.",
            "",
            "Forbidden claims: Tau Core validation, gravity-model selection, projection-formula uniqueness, replacement of external labels by residual-only labels, broad independent external validation, or THINGS route2 positive evidence.",
            "",
            "## 12. Phase II",
            "",
            "The next paper-grade step is a held-out external source-family test with N>=15, a frozen evidence rule, no velocity-endpoint refit, explicit observability covariates, and predefined failure conditions. A negative Phase II result should be treated as evidence that the present association is SPARC-specific, proxy-specific, or observability-driven.",
            "",
        ]
    )


def gate_rows() -> list[dict[str, str]]:
    return [
        {
            "GateID": "P2MSV03G01",
            "Status": "publication_style_draft_generated",
            "Evidence": "paper2_manuscript_draft_v03.md;paper2_abstract_v03.md",
            "CanClaimTauValidation": "no",
            "NextAction": "review_wording_and_prepare_latex_candidate",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "P2MSV03G02",
            "Status": "external_proxy_table_integrated_with_caveats",
            "Evidence": "paper2_external_proxy_summary_v03.csv",
            "CanClaimTauValidation": "no",
            "NextAction": "keep_external_readouts_as_context_not_validation",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "P2MSV03G03",
            "Status": "negative_things_route2_audit_retained",
            "Evidence": "things_route2_expansion_closure_v01.md",
            "CanClaimTauValidation": "no",
            "NextAction": "do_not_reopen_route2_without_citable_machine_columns",
            "Guardrail": GUARDRAIL,
        },
    ]


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [DRAFT, ABSTRACT, SUMMARY_TABLE, EXTERNAL_TABLE, GATE]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["paper2_manuscript_v03_status"] = (
        "publication_style_draft_generated_external_proxy_caveats_integrated"
    )
    manifest["paper2_next_gate"] = "review_paper2_v03_wording_and_prepare_latex_candidate"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    DRAFT.write_text(draft_text(), encoding="utf-8")
    ABSTRACT.write_text(abstract_text(), encoding="utf-8")
    write_csv(
        SUMMARY_TABLE,
        result_summary_rows(),
        ["ResultID", "Quantity", "Value", "Interpretation", "ClaimBoundary", "Guardrail"],
    )
    write_csv(
        EXTERNAL_TABLE,
        external_summary_rows(),
        [
            "FamilyID",
            "JoinedN",
            "PrimaryMetric",
            "Status",
            "ManuscriptRole",
            "AllowedClaim",
            "ForbiddenClaim",
            "Guardrail",
        ],
    )
    write_csv(
        GATE,
        gate_rows(),
        ["GateID", "Status", "Evidence", "CanClaimTauValidation", "NextAction", "Guardrail"],
    )
    update_manifest()
    print(DRAFT)


if __name__ == "__main__":
    main()
