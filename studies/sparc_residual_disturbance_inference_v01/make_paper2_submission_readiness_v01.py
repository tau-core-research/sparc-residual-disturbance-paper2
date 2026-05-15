#!/usr/bin/env python3
"""Create a submission-readiness audit for the Paper 2 v0.3 packet."""

from __future__ import annotations

import json

from make_packet_v01_seed import PACKET, write_csv


README = PACKET / "paper2_submission_readiness_v01.md"
READINESS = PACKET / "paper2_submission_readiness_v01.csv"
NEXT_ACTIONS = PACKET / "paper2_submission_next_actions_v01.csv"

GUARDRAIL = "paper2_submission_readiness_no_tau_validation_no_external_validation_overclaim"


def readiness_rows() -> list[dict[str, str]]:
    return [
        {
            "Area": "Manuscript identity",
            "Status": "ready_as_diagnostic_audit_draft",
            "Evidence": "paper2_manuscript_draft_v03.md;paper2_abstract_v03.md",
            "BlockingIssue": "",
            "RequiredBeforeSubmission": "polish wording and convert to target journal format",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "Primary internal result",
            "Status": "ready_with_caveats",
            "Evidence": "Projection_RMS AUC=0.771008403;p=0.002000000",
            "BlockingIssue": "",
            "RequiredBeforeSubmission": "keep as SPARC-internal diagnostic result",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "Baseline comparison",
            "Status": "ready",
            "Evidence": "MOND/RAR separate A/C; Newtonian near chance",
            "BlockingIssue": "",
            "RequiredBeforeSubmission": "avoid projection-uniqueness language",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "External proxy support",
            "Status": "supporting_context_only",
            "Evidence": "WHISP small positive; non-WHISP mixed or underpowered",
            "BlockingIssue": "no independent N>=15 source-family validation",
            "RequiredBeforeSubmission": "describe as proxy audit, not validation",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "THINGS route2",
            "Status": "closed_negative_audit",
            "Evidence": "missing machine mass-model columns; failed photometry/solver gate",
            "BlockingIssue": "not score-ready",
            "RequiredBeforeSubmission": "retain as limitation or appendix only",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "Figures",
            "Status": "draft_figures_exist",
            "Evidence": "four SVG figures in figures/",
            "BlockingIssue": "journal typography and caption polish not yet audited",
            "RequiredBeforeSubmission": "final figure typography/caption review",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "Bibliography",
            "Status": "not_ready",
            "Evidence": "related work notes exist but no final .bib/LaTeX references",
            "BlockingIssue": "citation package missing",
            "RequiredBeforeSubmission": "create target bibliography and cite external proxy sources",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "Submission source",
            "Status": "not_ready",
            "Evidence": "Markdown packet exists",
            "BlockingIssue": "no LaTeX source/PDF candidate for Paper 2",
            "RequiredBeforeSubmission": "generate LaTeX source, compile PDF, visually inspect equations/figures",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "Reproducibility",
            "Status": "ready",
            "Evidence": "pytest packet checks pass; raw data not tracked",
            "BlockingIssue": "",
            "RequiredBeforeSubmission": "update README command list to include latest v03/readiness scripts",
            "Guardrail": GUARDRAIL,
        },
    ]


def next_action_rows() -> list[dict[str, str]]:
    return [
        {
            "StepID": "P2SUB01",
            "Action": "polish_v03_manuscript_language",
            "Why": "remove packet-like wording and prepare a journal-style narrative",
            "BlocksSubmission": "yes",
            "CanClaimTauValidation": "no",
            "Guardrail": GUARDRAIL,
        },
        {
            "StepID": "P2SUB02",
            "Action": "create_latex_source_and_bibliography",
            "Why": "arXiv/journal submission requires source and references",
            "BlocksSubmission": "yes",
            "CanClaimTauValidation": "no",
            "Guardrail": GUARDRAIL,
        },
        {
            "StepID": "P2SUB03",
            "Action": "figure_typography_and_caption_audit",
            "Why": "current SVGs are reproducible but still draft presentation figures",
            "BlocksSubmission": "yes",
            "CanClaimTauValidation": "no",
            "Guardrail": GUARDRAIL,
        },
        {
            "StepID": "P2SUB04",
            "Action": "keep_phase_ii_as_future_validation",
            "Why": "current external readouts are mixed and do not establish independent validation",
            "BlocksSubmission": "no",
            "CanClaimTauValidation": "no",
            "Guardrail": GUARDRAIL,
        },
    ]


def markdown_text() -> str:
    rows = readiness_rows()
    actions = next_action_rows()
    ready = [row for row in rows if row["Status"] in {"ready", "ready_with_caveats", "ready_as_diagnostic_audit_draft"}]
    blockers = [row for row in rows if row["Status"] == "not_ready"]
    caveats = [row for row in rows if row["Status"] in {"supporting_context_only", "closed_negative_audit", "draft_figures_exist"}]
    lines = [
        "# Paper 2 Submission Readiness v0.1",
        "",
        "Verdict: the Paper 2 packet is ready as a cautious diagnostic-audit draft, but it is not yet submission-ready.",
        "",
        "The remaining blockers are presentation and source-package blockers, not signal-discovery blockers.",
        "",
        "## Ready Items",
        "",
    ]
    for row in ready:
        lines.append(f"- {row['Area']}: {row['Status']} ({row['Evidence']}).")
    lines.extend(["", "## Caveated Items", ""])
    for row in caveats:
        lines.append(
            f"- {row['Area']}: {row['Status']}. Required before submission: {row['RequiredBeforeSubmission']}."
        )
    lines.extend(["", "## Blocking Items", ""])
    for row in blockers:
        lines.append(f"- {row['Area']}: {row['BlockingIssue']}.")
    lines.extend(
        [
            "",
            "## Next Actions",
            "",
        ]
    )
    for row in actions:
        lines.append(f"- {row['StepID']}: {row['Action']} ({row['Why']}).")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Allowed: Paper 2 can be developed as a SPARC residual-shape diagnostic and external-proxy audit.",
            "",
            "Forbidden: Tau Core validation, gravity-model selection, broad independent external validation, or THINGS route2 positive evidence.",
            "",
            f"Guardrail: `{GUARDRAIL}`",
            "",
        ]
    )
    return "\n".join(lines)


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [README, READINESS, NEXT_ACTIONS]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["paper2_submission_readiness_v01_status"] = (
        "diagnostic_draft_ready_submission_source_and_bibliography_not_ready"
    )
    manifest["paper2_next_gate"] = "paper2_latex_source_bibliography_and_figure_polish"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    README.write_text(markdown_text(), encoding="utf-8")
    write_csv(
        READINESS,
        readiness_rows(),
        [
            "Area",
            "Status",
            "Evidence",
            "BlockingIssue",
            "RequiredBeforeSubmission",
            "Guardrail",
        ],
    )
    write_csv(
        NEXT_ACTIONS,
        next_action_rows(),
        ["StepID", "Action", "Why", "BlocksSubmission", "CanClaimTauValidation", "Guardrail"],
    )
    update_manifest()
    print(README)


if __name__ == "__main__":
    main()
