# Paper 2 Submission Readiness v0.1

Verdict: the Paper 2 packet is ready as a cautious diagnostic-audit draft, but it is not yet submission-ready.

The remaining blockers are presentation and source-package blockers, not signal-discovery blockers.

## Ready Items

- Manuscript identity: ready_as_diagnostic_audit_draft (paper2_manuscript_draft_v03.md;paper2_abstract_v03.md).
- Primary internal result: ready_with_caveats (Projection_RMS AUC=0.771008403;p=0.002000000).
- Baseline comparison: ready (MOND/RAR separate A/C; Newtonian near chance).
- Reproducibility: ready (pytest packet checks pass; raw data not tracked).

## Caveated Items

- External proxy support: supporting_context_only. Required before submission: describe as proxy audit, not validation.
- THINGS route2: closed_negative_audit. Required before submission: retain as limitation or appendix only.
- Figures: draft_figures_exist. Required before submission: final figure typography/caption review.

## Blocking Items

- Bibliography: citation package missing.
- Submission source: no LaTeX source/PDF candidate for Paper 2.

## Next Actions

- P2SUB01: polish_v03_manuscript_language (remove packet-like wording and prepare a journal-style narrative).
- P2SUB02: create_latex_source_and_bibliography (arXiv/journal submission requires source and references).
- P2SUB03: figure_typography_and_caption_audit (current SVGs are reproducible but still draft presentation figures).
- P2SUB04: keep_phase_ii_as_future_validation (current external readouts are mixed and do not establish independent validation).

## Claim Boundary

Allowed: Paper 2 can be developed as a SPARC residual-shape diagnostic and external-proxy audit.

Forbidden: Tau Core validation, gravity-model selection, broad independent external validation, or THINGS route2 positive evidence.

Guardrail: `paper2_submission_readiness_no_tau_validation_no_external_validation_overclaim`
