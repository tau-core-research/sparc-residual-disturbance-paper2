#!/usr/bin/env python3
"""Generate the Paper 2 v0.2 manuscript skeleton and cautious draft."""

from __future__ import annotations

import json

from make_packet_v01_seed import PACKET, write_csv


SKELETON = PACKET / "paper2_manuscript_skeleton_v02.md"
DRAFT = PACKET / "paper2_manuscript_draft_v02.md"
ABSTRACT = PACKET / "paper2_abstract_v02.md"
SECTION_PLAN = PACKET / "paper2_section_plan_v02.csv"
GATE = PACKET / "paper2_manuscript_v02_gate.csv"

GUARDRAIL = "paper2_manuscript_v02_diagnostic_audit_no_tau_validation"


def section_rows() -> list[dict[str, str]]:
    return [
        {
            "Section": "Abstract",
            "Purpose": "State diagnostic residual-inference result and mixed external-proxy context.",
            "RequiredContent": "CORE AUC; WHISP support caveat; route2 closure; no Tau validation",
            "ForbiddenContent": "Tau Core validation; independent external validation claim",
            "Guardrail": GUARDRAIL,
        },
        {
            "Section": "1. Introduction",
            "Purpose": "Frame residual-shape inference as a diagnostic audit.",
            "RequiredContent": "disturbance/non-circular motivation; not a gravity proof",
            "ForbiddenContent": "TOE framing",
            "Guardrail": GUARDRAIL,
        },
        {
            "Section": "2. Data and Frozen Inputs",
            "Purpose": "Document SPARC labels, residual features, and external packet inheritance.",
            "RequiredContent": "45 A/C galaxies; B policy; Paper 1 source packet",
            "ForbiddenContent": "residuals replace external labels",
            "Guardrail": GUARDRAIL,
        },
        {
            "Section": "3. Internal Diagnostic Result",
            "Purpose": "Report primary LOOGO/null/bootstrap result.",
            "RequiredContent": "Projection_RMS AUC=0.771008403; p=0.002; CI",
            "ForbiddenContent": "physical proof",
            "Guardrail": GUARDRAIL,
        },
        {
            "Section": "4. Baseline Families",
            "Purpose": "Compare projection, MOND/RAR, and Newtonian controls.",
            "RequiredContent": "low-acceleration family interpretation; no uniqueness",
            "ForbiddenContent": "projection formula uniquely explains labels",
            "Guardrail": GUARDRAIL,
        },
        {
            "Section": "5. External Proxy Readouts",
            "Purpose": "Summarize WHISP, Reynolds/LVHIS, ALFALFA, HALOGAS.",
            "RequiredContent": "WHISP strongest but small; non-WHISP mixed/underpowered",
            "ForbiddenContent": "external validation broadly confirmed",
            "Guardrail": GUARDRAIL,
        },
        {
            "Section": "6. Negative Audit: THINGS Route2",
            "Purpose": "Show audit discipline and why route2 is not positive evidence.",
            "RequiredContent": "closed not score-ready; N15 not reached; no synthetic mass models",
            "ForbiddenContent": "THINGS N>=15",
            "Guardrail": GUARDRAIL,
        },
        {
            "Section": "7. Limitations and Phase II",
            "Purpose": "Define exact upgrades needed for paper-grade validation.",
            "RequiredContent": "independent N>=15 source family; frozen evidence rule; no endpoint tuning",
            "ForbiddenContent": "current result is final validation",
            "Guardrail": GUARDRAIL,
        },
    ]


def abstract_text() -> str:
    return """# Paper 2 Abstract v0.2

We test whether fixed rotation-curve residual-shape features can recover externally reviewed structural-disturbance labels in the SPARC sample and whether the resulting residual-inferred weight candidate is supported by independent disturbance proxies. The primary internal diagnostic is `Projection_RMS`, evaluated with leave-one-galaxy-out thresholding, shuffled-label null tests, bootstrap uncertainty, baseline-family comparisons, and observability stress checks. In the frozen A/C sample, `Projection_RMS` reaches LOOGO AUC=0.771008403 with empirical shuffled-label p=0.002000000; MOND-like and empirical RAR-like low-acceleration residual scores also separate A/C systems, while a Newtonian baryonic RMS control is near chance. External proxy readouts are mixed: WHISP resolved-HI asymmetry is directionally aligned in a small overlap, WHISP morphology is weaker, Reynolds/LVHIS velocity-field asymmetry is promising but below the frozen minimum sample size, and ALFALFA/HALOGAS readouts are weak or control-like. A THINGS missing-galaxy expansion route was explicitly audited and closed as not score-ready after published machine columns were not recovered and photometry/solver validation failed before scoring. The result is therefore a reproducible diagnostic and external-proxy audit, not a Tau Core validation claim, not a gravity-model selection result, and not independent paper-grade external validation.
"""


def skeleton_text() -> str:
    return """# Paper 2 Manuscript Skeleton v0.2

Working title: Residual-shape inference and external-proxy audit of structural disturbance in SPARC rotation curves

## Paper Identity

Paper 2 is a diagnostic residual-inference and external-proxy audit. It is not a Tau Core validation paper. It is not a gravity proof. It is not an independent external-validation paper yet.

## Core Internal Result

- Primary feature: `Projection_RMS`
- LOOGO AUC: 0.771008403
- Accuracy: 0.755555556
- Shuffled-label empirical p: 0.002000000
- Bootstrap 95% AUC interval: [0.600802469, 0.909100262]

## Baseline Family Interpretation

- MOND-simple RMS AUC: 0.720588235
- RAR-like RMS AUC: 0.731092437
- Newtonian baryonic RMS AUC: 0.506302521

Interpretation: A/C separation is a low-acceleration residual-family phenomenon in this packet, not projection-formula uniqueness.

## External Proxy Status

- WHISP resolved-HI: directional support, small overlap.
- WHISP morphology: mixed weak support.
- Reynolds/LVHIS: promising velocity-field asymmetry, below frozen N>=15 gate.
- ALFALFA: weak/non-directional profile-asymmetry readout.
- HALOGAS: weak small-overlap control.
- THINGS route2: closed not score-ready; negative audit appendix only.

## Claim Boundary

Allowed: fixed residual-shape features carry reproducible external-label information inside SPARC, with cautious supporting external-proxy readouts.

Forbidden: Tau Core validation, TOE evidence, gravity proof, projection uniqueness, broad independent external validation, THINGS N>=15, or route2 positive evidence.

## Proposed Sections

1. Introduction: diagnostic residual-shape inference.
2. Data and frozen inputs.
3. Internal SPARC residual diagnostic.
4. Baseline-family comparison.
5. External proxy readouts.
6. Negative audit: THINGS route2 closure.
7. Limitations and Phase II validation plan.

## Next Gate

Convert this skeleton into a concise manuscript draft and update figures/tables around v0.2 claims.
"""


def draft_text() -> str:
    return """# Residual-shape inference and external-proxy audit of structural disturbance in SPARC rotation curves

## Abstract

We test whether fixed rotation-curve residual-shape features can recover externally reviewed structural-disturbance labels in the SPARC sample and whether the resulting residual-inferred weight candidate is supported by independent disturbance proxies. The primary internal diagnostic is `Projection_RMS`, evaluated with leave-one-galaxy-out thresholding, shuffled-label null tests, bootstrap uncertainty, baseline-family comparisons, and observability stress checks. In the frozen A/C sample, `Projection_RMS` reaches LOOGO AUC=0.771008403 with empirical shuffled-label p=0.002000000; MOND-like and empirical RAR-like low-acceleration residual scores also separate A/C systems, while a Newtonian baryonic RMS control is near chance. External proxy readouts are mixed: WHISP resolved-HI asymmetry is directionally aligned in a small overlap, WHISP morphology is weaker, Reynolds/LVHIS velocity-field asymmetry is promising but below the frozen minimum sample size, and ALFALFA/HALOGAS readouts are weak or control-like. A THINGS missing-galaxy expansion route was explicitly audited and closed as not score-ready after published machine columns were not recovered and photometry/solver validation failed before scoring. The result is therefore a reproducible diagnostic and external-proxy audit, not a Tau Core validation claim, not a gravity-model selection result, and not independent paper-grade external validation.

## 1. Introduction

Rotation-curve residuals are often treated as model failures, but residual structure can also encode non-equilibrium dynamics, non-circular motions, observational resolution limits, pressure support, deprojection uncertainty, and morphology-dependent systematics. This paper asks a narrower diagnostic question: do fixed residual-shape features carry information about externally reviewed structural disturbance classes?

The answer is useful only if the claim is kept narrow. This paper does not validate Tau Core, does not select a unique gravity model, and does not replace external labels with residual-only labels. It audits whether residual-shape information and independent disturbance proxies point in a consistent direction, and where they fail.

## 2. Data and Frozen Inputs

The internal diagnostic uses the frozen SPARC A/C packet inherited from the residual-blind Paper 1 workflow. B-class systems remain excluded from primary truth labels because they are uncertain by construction. Residual features are derived from the fixed point map and are evaluated under predeclared rules.

The primary internal endpoint is `Projection_RMS`. External catalog readouts are treated as proxy checks, not as training data and not as endpoints for refitting.

## 3. Internal SPARC Residual Diagnostic

The primary classifier is intentionally simple: leave one galaxy out, recompute the A/C threshold from the remaining galaxies, and classify the held-out system by whether its residual score is above or below the frozen direction. `Projection_RMS` reaches LOOGO AUC=0.771008403 and accuracy=0.755555556. A shuffled-label null gives empirical p=0.002000000, and the bootstrap 95% AUC interval is [0.600802469, 0.909100262].

This is the strongest current Paper 2 result. It shows that residual-shape features recover external A/C information better than chance in the current SPARC packet. It does not show that the residual score is physically unique or that the underlying projection formula is validated.

## 4. Baseline-Family Comparison

The baseline-family comparison is important because it prevents over-branding the result. MOND-simple RMS reaches AUC=0.720588235, and empirical RAR-like RMS reaches AUC=0.731092437. The Newtonian baryonic RMS control is near chance at AUC=0.506302521.

The clean interpretation is that A/C separation appears mainly in low-acceleration residual-family scores. Projection-specific uniqueness is not established.

## 5. External Proxy Readouts

The external readouts are informative but not yet paper-grade validation. WHISP resolved-HI asymmetry is the strongest positive external context, with N=14, Pearson=0.391218683, and AUC=0.714285714. WHISP morphology is weaker and mixed: the Asymmetry A split is directionally suggestive, while the composite morphology burden is close to neutral.

Non-WHISP sources remain underpowered or mixed. Reynolds/LVHIS velocity-field asymmetry is promising after alias resolution, but N=6 is below the frozen N>=15 gate. ALFALFA profile asymmetry has larger overlap but weak directionality. HALOGAS is retained as a small-overlap control, not as positive validation.

## 6. Negative Audit: THINGS Route2 Closure

The THINGS route2 expansion was tested because adding missing THINGS galaxies could have strengthened the external validation story. That path is now closed as not score-ready. Official machine-readable SPARC and de Blok sources did not expose per-radius `R,Vobs,eVobs,Vgas,Vdisk,Vbul` columns for the missing galaxies. A reconstruction route was explored, but photometry and solver validation failed before missing-galaxy scoring.

This closure is a strength of the audit. It prevents synthetic mass models, plot digitization, or endpoint-driven reconstruction from entering the evidence chain. THINGS route2 is therefore a negative audit appendix, not positive evidence.

## 7. Limitations and Phase II

The current result is meaningful but bounded. The internal SPARC diagnostic is positive; external proxy support is mixed; observability and source-family selection remain important limitations. The work should be presented as a residual-inference audit with cautious external-proxy context.

The next paper-grade validation step is not more opportunistic data chasing. It is a frozen external source-family test with enough overlap, a predeclared evidence rule, no velocity endpoint refit, and explicit failure conditions.
"""


def gate_rows() -> list[dict[str, str]]:
    return [
        {
            "GateID": "P2MSV02G01",
            "Status": "v02_skeleton_and_abstract_generated",
            "Evidence": "paper2_manuscript_skeleton_v02.md;paper2_abstract_v02.md",
            "CanClaimTauValidation": "no",
            "NextAction": "edit_v02_draft_into_publication_style_and_update_figures",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "P2MSV02G02",
            "Status": "route2_demoted_to_negative_audit_appendix",
            "Evidence": "things_route2_expansion_closure_v01.md",
            "CanClaimTauValidation": "no",
            "NextAction": "do_not_use_route2_as_positive_evidence",
            "Guardrail": GUARDRAIL,
        },
    ]


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [SKELETON, DRAFT, ABSTRACT, SECTION_PLAN, GATE]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["paper2_manuscript_v02_status"] = (
        "skeleton_abstract_draft_generated_diagnostic_audit_no_tau_validation"
    )
    manifest["paper2_next_gate"] = "edit_paper2_v02_publication_style_and_update_figures"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    SKELETON.write_text(skeleton_text(), encoding="utf-8")
    DRAFT.write_text(draft_text(), encoding="utf-8")
    ABSTRACT.write_text(abstract_text(), encoding="utf-8")
    write_csv(
        SECTION_PLAN,
        section_rows(),
        ["Section", "Purpose", "RequiredContent", "ForbiddenContent", "Guardrail"],
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
