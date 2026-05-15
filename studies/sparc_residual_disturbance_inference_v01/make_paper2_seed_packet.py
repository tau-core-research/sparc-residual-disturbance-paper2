#!/usr/bin/env python3
"""Create Paper 2 seed documents for the residual-disturbance inference branch."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from make_packet_v01_seed import PACKET


RELATED_WORK = PACKET / "paper2_related_work.md"
OUTLINE = PACKET / "paper2_cautious_outline.md"
CLAIM_BOUNDARY = PACKET / "paper2_claim_boundary.csv"


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_related_work() -> None:
    lines = [
        "# Paper 2 Related Work Positioning",
        "",
        "This note positions the residual-disturbance inference branch against nearby galaxy-dynamics literature.",
        "",
        "## Closest Literature Families",
        "",
        "1. HI kinematic lopsidedness and receding/approaching rotation-curve asymmetry.",
        "   van Eymeren et al. (2011) classify WHISP galaxies using differences between receding and approaching rotation curves and quantify kinematic lopsidedness.",
        "",
        "2. Harmonic decomposition and non-circular motions in HI velocity fields.",
        "   Trachternach et al. (2008) use THINGS velocity fields to quantify non-circular motions and dark-halo potential elongations.",
        "",
        "3. Rotation-curve diversity caused by non-circular motions and viewing geometry.",
        "   Oman et al. (2019) show in mock HI observations that non-circular gas motions and line-of-sight orientation can strongly bias recovered rotation curves.",
        "",
        "4. HI morphology, asymmetry, and environment diagnostics.",
        "   Work on WHISP, LVHIS, VIVA, and HALOGAS connects HI asymmetry and kinematic disturbance to environment and interaction state.",
        "",
        "## Paper 2 Niche",
        "",
        "Paper 2 should not claim that disturbed galaxies have unusual kinematics; that is established. The narrower contribution is a residual-space diagnostic audit:",
        "",
        "> Can fixed SPARC rotation-curve residual-shape features recover externally reviewed disturbance class better than chance, while Projection, MOND/RAR, and Newtonian residual families remain visible side-by-side?",
        "",
        "The novelty is therefore the direction of inference and the input space: external A/C class is predicted from fixed residual features, not from HI velocity fields, images, or receding/approaching rotation curves.",
        "",
        "## References To Track",
        "",
        "- van Eymeren et al. 2011, A&A 530 A29, `Lopsidedness in WHISP galaxies I: Rotation curves and kinematic lopsidedness`, https://doi.org/10.1051/0004-6361/201016177",
        "- Trachternach et al. 2008, AJ 136 2720, `Dynamical Centers and Noncircular Motions in THINGS Galaxies`, https://doi.org/10.1088/0004-6256/136/6/2720",
        "- Oman et al. 2019, MNRAS 482 821, `Non-circular motions and the diversity of dwarf galaxy rotation curves`, https://arxiv.org/abs/1706.07478",
        "- Reynolds et al. 2020, MNRAS 493 5089, `HI asymmetries in LVHIS, VIVA, and HALOGAS galaxies`, https://doi.org/10.1093/mnras/staa597",
        "",
        "## Guardrail",
        "",
        "Do not present Paper 2 as a Tau Core proof. Present it as a diagnostic audit of whether residual-shape information carries recoverable disturbance information under held-out validation.",
    ]
    RELATED_WORK.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outline() -> None:
    lines = [
        "# Paper 2 Cautious Outline",
        "",
        "Working title:",
        "",
        "`Residual-shape inference of structural disturbance in SPARC rotation curves: a diagnostic audit`",
        "",
        "## Central Question",
        "",
        "Can residual-shape features from fixed rotation-curve baseline scores recover externally assigned A/C disturbance class better than chance?",
        "",
        "## Primary Claim Candidate",
        "",
        "A simple residual-amplitude feature, `Projection_RMS`, recovers A/C class in a leave-one-galaxy-out sanity check with AUC 0.771 and accuracy 0.756. This is a diagnostic result, not a physical proof or model-selection result.",
        "",
        "## Required Framing",
        "",
        "- Paper 1 direction: external labels -> residual scatter.",
        "- Paper 2 direction: residual shape -> external disturbance class.",
        "- The labels are targets here, not residual-blind evidence.",
        "- Projection/MOND/RAR/Newton residual families must remain side-by-side.",
        "- B-class galaxies stay outside the primary A/C classifier unless a separate uncertainty analysis is frozen.",
        "",
        "## Proposed Sections",
        "",
        "1. Introduction: residuals as diagnostic fingerprints, not theory confirmation.",
        "2. Related work: HI lopsidedness, harmonic decomposition, non-circular motions, rotation-curve diversity.",
        "3. Data: Paper 1 residual point map and frozen A/C evidence labels.",
        "4. Features: residual amplitude, radial structure, low-acceleration burden, comparator differences.",
        "5. Validation: leave-one-galaxy-out threshold classifier and shuffled-label null.",
        "6. Results: Projection_RMS primary baseline; composite score demoted.",
        "7. Error audit: false-positive A-as-C and false-negative C-as-A families.",
        "8. Controls: distance/radius/mass/observability sensitivity and baseline-family comparison.",
        "9. Limitations: small sample, label subjectivity, residual target leakage risk, no Tau-specific claim.",
        "10. Discussion: how residual-shape inference can prioritize future external A/C review.",
        "",
        "## Paper-Grade Missing Pieces",
        "",
        "- Add shuffled-label null distribution for the LOOGO primary baseline.",
        "- Add distance/radius/mass observability stress tests for the classifier score.",
        "- Add baseline-family comparison table for Projection, MOND-simple, RAR, and Newtonian features.",
        "- Freeze whether B-class galaxies are excluded, held out, or used only as an uncertainty set.",
        "- Report calibration and uncertainty, not only AUC/accuracy.",
        "",
        "## HALOGAS H07 Role",
        "",
        "HALOGAS H07 should be mentioned only as an external-family weak control: a simple LR cube linewidth-stress proxy did not produce a strong or Tau-specific residual association. It should not be used as Paper 2 primary evidence.",
    ]
    OUTLINE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_claim_boundary() -> None:
    rows = [
        {
            "ClaimID": "P2_C01_primary_diagnostic",
            "AllowedClaim": "fixed_residual_shape_features_can_recover_external_ac_class_better_than_chance_if_null_tests_hold",
            "CurrentEvidence": "Projection_RMS_LOOGO_AUC_0.771_accuracy_0.756",
            "RequiredUpgrade": "shuffled_label_null_and_observability_stress_tests",
            "ForbiddenClaim": "tau_core_validation_or_physical_proof",
            "Status": "candidate_after_missing_controls",
        },
        {
            "ClaimID": "P2_C02_model_specificity",
            "AllowedClaim": "baseline_families_can_be_compared_side_by_side",
            "CurrentEvidence": "projection_rms_primary_baseline_only",
            "RequiredUpgrade": "mond_rar_newton_feature_family_loogo_metrics",
            "ForbiddenClaim": "projection_formula_uniquely_explains_disturbance",
            "Status": "not_established",
        },
        {
            "ClaimID": "P2_C03_classifier_use",
            "AllowedClaim": "classifier_can_prioritize_future_external_review_candidates",
            "CurrentEvidence": "error_audit_identifies_false_positive_and_false_negative_families",
            "RequiredUpgrade": "calibration_uncertainty_and_b_class_policy",
            "ForbiddenClaim": "residuals_can_replace_external_evidence_labels",
            "Status": "diagnostic_only",
        },
        {
            "ClaimID": "P2_C04_halogas_role",
            "AllowedClaim": "halogas_h07_is_a_weak_external_family_control",
            "CurrentEvidence": "h07f_projection_r_0.009_mond_0.024_rar_0.027",
            "RequiredUpgrade": "none_for_closeout_reference",
            "ForbiddenClaim": "halogas_h07_supports_tau_specific_validation",
            "Status": "closed_control",
        },
    ]
    write_csv(
        CLAIM_BOUNDARY,
        rows,
        [
            "ClaimID",
            "AllowedClaim",
            "CurrentEvidence",
            "RequiredUpgrade",
            "ForbiddenClaim",
            "Status",
        ],
    )


def update_readme() -> None:
    readme = PACKET / "README.md"
    text = readme.read_text(encoding="utf-8")
    marker = "\n"
    addition = """
## Paper 2 Seed

This packet is now the seed for a cautious Paper 2 direction: residual-shape
inference of externally reviewed disturbance class. The current strongest
baseline is `Projection_RMS` under leave-one-galaxy-out validation, but the
paper-grade claim remains blocked until shuffled-label null tests,
observability stress tests, and baseline-family comparisons are added.

Paper 2 must be framed as a diagnostic audit, not as Tau Core validation.
"""
    if "## Paper 2 Seed" not in text:
        readme.write_text(text.rstrip() + addition + marker, encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "paper2_related_work.md",
            "paper2_cautious_outline.md",
            "paper2_claim_boundary.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["paper2_seed_status"] = "cautious_diagnostic_paper_seed_not_tau_validation"
    manifest["paper2_next_gate"] = (
        "shuffled_label_null_observability_stress_baseline_family_comparison"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_related_work()
    write_outline()
    write_claim_boundary()
    update_readme()
    update_manifest()
    print(OUTLINE)
    print("paper2_seed_files=3")


if __name__ == "__main__":
    main()
