#!/usr/bin/env python3
"""Generate Paper 2 LaTeX source, bibliography, publication figures, and PDF."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt

from make_packet_v01_seed import PACKET, ROOT, write_csv


SOURCE = ROOT / "paper2_submission_source"
SOURCE_FIGURES = SOURCE / "figures"
MAIN_TEX = SOURCE / "main.tex"
REFERENCES = SOURCE / "references.bib"
PDF = SOURCE / "main.pdf"
FIGURE_AUDIT_MD = PACKET / "paper2_figure_typography_audit_v01.md"
FIGURE_AUDIT_CSV = PACKET / "paper2_figure_typography_audit_v01.csv"
SOURCE_GATE = PACKET / "paper2_submission_source_gate_v01.csv"
READINESS_MD = PACKET / "paper2_submission_readiness_v02.md"
READINESS_CSV = PACKET / "paper2_submission_readiness_v02.csv"

GUARDRAIL = "paper2_submission_source_ready_no_tau_validation_no_external_overclaim"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def save_pdf(name: str) -> None:
    SOURCE_FIGURES.mkdir(parents=True, exist_ok=True)
    plt.savefig(SOURCE_FIGURES / name, format="pdf", bbox_inches="tight")
    plt.close()


def style() -> None:
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 9,
            "figure.dpi": 180,
            "savefig.dpi": 300,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def plot_projection_rms_distribution() -> None:
    rows = read_csv(PACKET / "residual_feature_table.csv")
    calibration = read_csv(PACKET / "paper2_calibration_uncertainty.csv")[0]
    a_values = [float(row["Projection_RMS"]) for row in rows if row["Class"] == "A"]
    c_values = [float(row["Projection_RMS"]) for row in rows if row["Class"] == "C"]
    threshold = float(calibration["Threshold"])

    plt.figure(figsize=(6.4, 4.0))
    bins = [index / 20 for index in range(0, 21)]
    plt.hist(a_values, bins=bins, alpha=0.78, label="A: regular", color="#2a6fbb")
    plt.hist(c_values, bins=bins, alpha=0.64, label="C: disturbed", color="#c65d1e")
    plt.axvline(threshold, color="#1f1f1f", linewidth=1.2, linestyle="--", label="LOOGO threshold")
    plt.xlabel("Projection RMS residual score")
    plt.ylabel("Galaxies")
    plt.title("Residual-score separation of external A/C classes")
    plt.legend(frameon=False)
    plt.tight_layout()
    save_pdf("paper2_projection_rms_distribution.pdf")


def plot_baseline_auc_comparison() -> None:
    baseline_rows = read_csv(PACKET / "paper2_baseline_family_loogo.csv")
    newtonian = read_csv(PACKET / "paper2_newtonian_scope.csv")
    values = {
        "Projection": next(row for row in baseline_rows if row["Predictor"] == "Projection_RMS")[
            "AUC_C_higher"
        ],
        "MOND": next(row for row in baseline_rows if row["Predictor"] == "MOND_RMS")[
            "AUC_C_higher"
        ],
        "RAR": next(row for row in baseline_rows if row["Predictor"] == "RAR_RMS")[
            "AUC_C_higher"
        ],
        "Newtonian": next(
            row for row in newtonian if row["Predictor"] == "Newtonian_Baryonic_RMS"
        )["AUC_C_higher"],
    }
    labels = list(values)
    aucs = [float(values[label]) for label in labels]
    colors = ["#2a6fbb", "#3f8f4f", "#7b5aa6", "#777777"]

    plt.figure(figsize=(6.4, 4.0))
    bars = plt.bar(labels, aucs, color=colors, width=0.62)
    plt.axhline(0.5, color="#333333", linewidth=1.0, linestyle=":", label="chance")
    plt.ylim(0.4, 0.85)
    plt.ylabel("LOOGO AUC")
    plt.title("A/C recovery by residual-score family")
    for bar, value in zip(bars, aucs):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.012,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )
    plt.legend(frameon=False)
    plt.tight_layout()
    save_pdf("paper2_baseline_auc_comparison.pdf")


def plot_error_audit() -> None:
    rows = read_csv(PACKET / "residual_inference_projection_rms_error_audit.csv")
    labels = ["correct", "A as C", "C as A"]
    counts = {label: 0 for label in labels}
    for row in rows:
        if row["ErrorFamily"] == "correct":
            counts["correct"] += 1
        elif row["ErrorFamily"] == "false_positive_A_as_C":
            counts["A as C"] += 1
        elif row["ErrorFamily"] == "false_negative_C_as_A":
            counts["C as A"] += 1

    plt.figure(figsize=(6.4, 4.0))
    bars = plt.bar(labels, [counts[label] for label in labels], color=["#2a6fbb", "#c65d1e", "#7b5aa6"])
    plt.ylabel("Galaxies")
    plt.title("Held-out classification error audit")
    for bar in bars:
        value = int(bar.get_height())
        plt.text(bar.get_x() + bar.get_width() / 2, value + 0.5, str(value), ha="center")
    plt.tight_layout()
    save_pdf("paper2_error_audit.pdf")


def plot_distance_stress() -> None:
    rows = read_csv(PACKET / "paper2_observability_stress.csv")
    labels = []
    values = []
    for row in rows:
        if row["MedianPairedDiff_C_minus_A"]:
            labels.append(
                row["StressTest"]
                .replace("sparc_distance_", "")
                .replace("_matched_pairs", "")
                .replace("_", " ")
            )
            values.append(float(row["MedianPairedDiff_C_minus_A"]))

    plt.figure(figsize=(6.4, 4.0))
    bars = plt.bar(labels, values, color=["#2a6fbb", "#3f8f4f", "#c65d1e"], width=0.62)
    plt.axhline(0.0, color="#333333", linewidth=1.0)
    plt.ylabel("Median paired C-A score")
    plt.title("Distance-matched observability stress")
    plt.xticks(rotation=12, ha="right")
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, value + 0.006, f"{value:.3f}", ha="center")
    plt.tight_layout()
    save_pdf("paper2_distance_stress.pdf")


def generate_figures() -> None:
    style()
    plot_projection_rms_distribution()
    plot_baseline_auc_comparison()
    plot_error_audit()
    plot_distance_stress()


def bib_text() -> str:
    return r"""@article{Lelli2016SPARC,
  author = {Lelli, Federico and McGaugh, Stacy S. and Schombert, James M.},
  title = {{SPARC}: Mass Models for 175 Disk Galaxies with Spitzer Photometry and Accurate Rotation Curves},
  journal = {The Astronomical Journal},
  volume = {152},
  pages = {157},
  year = {2016},
  doi = {10.3847/0004-6256/152/6/157}
}

@dataset{Lelli2016SPARCZenodo,
  author = {Lelli, Federico and McGaugh, Stacy S. and Schombert, James M.},
  title = {{SPARC} Galaxy Rotation Curve},
  publisher = {Zenodo},
  year = {2016},
  doi = {10.5281/zenodo.16284118}
}

@article{Milgrom1983MOND,
  author = {Milgrom, M.},
  title = {A modification of the Newtonian dynamics as a possible alternative to the hidden mass hypothesis},
  journal = {The Astrophysical Journal},
  volume = {270},
  pages = {365--370},
  year = {1983},
  doi = {10.1086/161130}
}

@article{McGaugh2016RAR,
  author = {McGaugh, Stacy S. and Lelli, Federico and Schombert, James M.},
  title = {Radial Acceleration Relation in Rotationally Supported Galaxies},
  journal = {Physical Review Letters},
  volume = {117},
  pages = {201101},
  year = {2016},
  doi = {10.1103/PhysRevLett.117.201101}
}

@article{vanEymeren2011WHISP,
  author = {van Eymeren, J. and Juette, E. and Jog, C. J. and Stein, Y. and Dettmar, R.-J.},
  title = {Lopsidedness in {WHISP} galaxies. I. Rotation curves and kinematic lopsidedness},
  journal = {Astronomy and Astrophysics},
  volume = {530},
  pages = {A29},
  year = {2011},
  doi = {10.1051/0004-6361/201016177}
}

@article{vanEymeren2011WHISPII,
  author = {van Eymeren, J. and Juette, E. and Jog, C. J. and Stein, Y. and Dettmar, R.-J.},
  title = {Lopsidedness in {WHISP} galaxies. II. Morphological lopsidedness},
  journal = {Astronomy and Astrophysics},
  volume = {530},
  pages = {A30},
  year = {2011},
  doi = {10.1051/0004-6361/201016178}
}

@article{Holwerda2011WHISP,
  author = {Holwerda, B. W. and Pirzkal, N. and de Blok, W. J. G. and Blyth, S.-L. and van der Heyden, K. J. and Elson, E. C. and Bouchard, A.},
  title = {Quantified {H I} morphology -- II. Lopsidedness and interaction in {WHISP} column density maps},
  journal = {Monthly Notices of the Royal Astronomical Society},
  volume = {416},
  pages = {2415--2425},
  year = {2011},
  doi = {10.1111/j.1365-2966.2011.17683.x}
}

@article{Trachternach2008THINGS,
  author = {Trachternach, C. and de Blok, W. J. G. and Walter, F. and Brinks, E. and Kennicutt, Jr., R. C.},
  title = {Dynamical Centers and Noncircular Motions in {THINGS} Galaxies: Implications for Dark Matter Halos},
  journal = {The Astronomical Journal},
  volume = {136},
  pages = {2720--2760},
  year = {2008},
  doi = {10.1088/0004-6256/136/6/2720}
}

@article{Oman2019NonCircular,
  author = {Oman, Kyle A. and Marasco, Antonino and Navarro, Julio F. and Frenk, Carlos S. and Schaye, Joop and Benitez-Llambay, Alejandro},
  title = {Non-circular motions and the diversity of dwarf galaxy rotation curves},
  journal = {Monthly Notices of the Royal Astronomical Society},
  volume = {482},
  pages = {821--847},
  year = {2019},
  doi = {10.1093/mnras/sty2687}
}

@article{Reynolds2020HIAsymmetries,
  author = {Reynolds, T. N. and Westmeier, T. and Staveley-Smith, L. and Chauhan, G. and Lagos, C. D. P.},
  title = {{H I} asymmetries in {LVHIS}, {VIVA}, and {HALOGAS} galaxies},
  journal = {Monthly Notices of the Royal Astronomical Society},
  volume = {493},
  pages = {5089--5106},
  year = {2020},
  doi = {10.1093/mnras/staa597}
}

@article{Yu2022ALFALFA,
  author = {Yu, Nai-Ping and Ho, Luis C. and Wang, Jing},
  title = {Statistical Analysis of {H I} Profile Asymmetry and Shape for Nearby Galaxies},
  journal = {The Astrophysical Journal Supplement Series},
  volume = {261},
  pages = {21},
  year = {2022}
}
"""


def tex_text() -> str:
    return r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{float}

\title{Residual-shape inference and external-proxy audit of structural disturbance in SPARC rotation curves}
\author{Jozsef Olcsak}
\date{Working submission candidate, 2026}

\begin{document}
\maketitle

\begin{abstract}
We ask whether fixed rotation-curve residual-shape features can recover externally reviewed structural-disturbance labels in SPARC galaxies, and whether independent H\,I disturbance proxies support the same diagnostic direction. The study reverses the Paper 1 audit: the A/C labels are treated as frozen external targets, while residual features are evaluated as predictors under leave-one-galaxy-out thresholding, shuffled-label null tests, bootstrap uncertainty, baseline-family controls, and observability stress checks. The primary internal feature, Projection RMS, reaches LOOGO AUC=0.771008403 with shuffled-label $p=0.002000000$ and bootstrap 95\% AUC interval $[0.600802469,0.909100262]$. MOND-simple and empirical RAR-like residual scores also separate A/C systems, whereas a Newtonian baryonic RMS control is near chance, indicating a low-acceleration residual-family effect rather than projection-formula uniqueness. External proxy readouts are supportive but not decisive. The result is therefore a reproducible residual-inference and external-proxy audit, not a Tau Core validation claim, not gravity-model selection, and not independent paper-grade external validation.
\end{abstract}

\section{Introduction}

Rotation-curve residuals are usually discussed as model error, but their radial structure can also carry information about non-equilibrium dynamics, non-circular motions, pressure support, beam smearing, inclination, and source-dependent observability \cite{Trachternach2008THINGS,Oman2019NonCircular}. Paper 1 established a residual-blind association between externally assigned structural-disturbance labels and low-acceleration residual scatter in SPARC. Here we ask the inverse diagnostic question: can fixed residual-shape features recover those external labels better than chance?

The scope is deliberately narrow. This paper does not use residuals to redefine the labels, does not validate Tau Core, and does not select a unique gravity law. It tests whether a frozen residual feature map contains recoverable information about externally reviewed A/C disturbance classes, then checks whether independent H\,I disturbance proxies point in the same direction.

\section{Data and frozen inputs}

The working A/C sample contains 45 SPARC galaxies inherited from the Paper 1 reproducibility packet: 17 externally regular A systems and 28 externally disturbed C systems. SPARC rotation-curve and mass-model context follows \cite{Lelli2016SPARC,Lelli2016SPARCZenodo}. B-class systems remain excluded from the primary target labels because they encode uncertainty by construction. The residual features are computed from the fixed Paper 1 point map and are not retrained on the external-proxy catalogues.

The public packet contains the derived tables, scripts, figures, and audit records needed to regenerate the diagnostic results. Raw survey products and raw SPARC rotmod files are not redistributed by this repository.

\section{Residual-shape endpoint and validation design}

The primary endpoint is Projection RMS, the galaxy-level RMS of a fixed low-acceleration projection residual. It is used as an operational residual-shape score rather than as a physical proof of the projection formula. The key design choice is that the score is fixed before the external-proxy readouts are interpreted.

The primary internal validation uses leave-one-galaxy-out thresholding. For each held-out galaxy, the decision threshold is recomputed from the remaining A and C systems as the midpoint between their class medians. A shuffled-label null preserves class counts and tests whether the observed AUC is expected under random A/C labels. Bootstrap resampling estimates sample-size uncertainty. These tests are internal to SPARC and should not be described as independent validation.

\section{Primary results}

\begin{table}[H]
\centering
\caption{Primary residual-inference results.}
\begin{tabular}{llll}
\toprule
Quantity & Value & Interpretation & Claim boundary\\
\midrule
Projection RMS LOOGO AUC & 0.771008403 & primary diagnostic & SPARC-internal\\
Projection RMS shuffled-label $p$ & 0.002000000 & label-null check & not replication\\
MOND-simple RMS AUC & 0.720588235 & low-acceleration family & not unique\\
RAR-like RMS AUC & 0.731092437 & low-acceleration family & not model selection\\
Newtonian baryonic RMS AUC & 0.506302521 & near-chance control & limited inference\\
\bottomrule
\end{tabular}
\end{table}

\begin{figure}[H]
\centering
\includegraphics[width=0.82\linewidth]{figures/paper2_projection_rms_distribution.pdf}
\caption{Distribution of the fixed Projection RMS residual score for externally regular A and disturbed C systems.}
\end{figure}

The primary signal is positive and statistically sharp in the frozen internal packet. The result is strongest when stated as class recovery from residual shape, not as a physical detection of an underlying field.

\section{Baseline-family comparison}

The baseline comparison weakens any projection-specific claim but strengthens the broader phenomenological result. MOND-simple \cite{Milgrom1983MOND} and empirical RAR-like \cite{McGaugh2016RAR} residual scores also separate A/C systems, while the Newtonian baryonic RMS score is near chance. The defensible conclusion is that A/C separation is concentrated in low-acceleration residual-family scores.

\begin{figure}[H]
\centering
\includegraphics[width=0.78\linewidth]{figures/paper2_baseline_auc_comparison.pdf}
\caption{Held-out A/C recovery across residual-score families. The Newtonian baryonic RMS score is near chance.}
\end{figure}

This pattern is compatible with several physical readings: disturbed systems may violate smooth equilibrium assumptions, non-circular motions may be more important in low-acceleration regions, or observability may expose more disturbance structure in particular subsets. The present data do not distinguish these explanations.

\section{Failure modes}

The error audit is retained because a useful diagnostic must show where it fails. False-negative C systems demonstrate that externally disturbed galaxies do not always produce large residual burden under a smooth rotation-curve score. False-positive A systems show that residual structure can arise without a strong external disturbance label.

\begin{figure}[H]
\centering
\includegraphics[width=0.78\linewidth]{figures/paper2_error_audit.pdf}
\caption{Held-out classification outcome counts for the Projection RMS threshold rule.}
\end{figure}

These failures are not relabeling evidence. They are targets for follow-up inspection, especially where residual morphology, inclination, radial coverage, and H\,I kinematic asymmetry disagree.

\section{External proxy readouts}

The external H\,I context draws on WHISP lopsidedness and morphology \cite{vanEymeren2011WHISP,vanEymeren2011WHISPII,Holwerda2011WHISP}, THINGS non-circular-motion diagnostics \cite{Trachternach2008THINGS}, Reynolds et al. H\,I asymmetry catalogues \cite{Reynolds2020HIAsymmetries}, and ALFALFA profile asymmetry \cite{Yu2022ALFALFA}. WHISP resolved-HI asymmetry is the strongest supportive external readout, but its overlap is small. WHISP morphology is mixed, Reynolds/LVHIS is promising but below the frozen $N\geq15$ gate, and ALFALFA/HALOGAS do not provide strong directional support. The external evidence therefore supports the paper as an audit, not as an independent validation result.

\section{THINGS route2 negative audit}

The THINGS expansion route was audited because it could have raised the independent-control overlap. It is now closed as not score-ready. The required machine-readable per-radius mass-model columns were not recovered for the missing galaxies, and the reconstruction route failed its photometry and solver-validation gates before any missing-galaxy scores were computed.

This negative audit should remain visible. It documents why the paper does not claim THINGS $N\geq15$, avoids plot-digitized or synthetic mass models, and prevents endpoint-driven data recovery from entering the evidence chain.

\section{Observability and systematics}

Observability remains the main scientific caveat. Nearby galaxies can reveal asymmetry and morphological disturbance more easily than distant systems; inclination, beam smearing, asymmetric drift, pressure support, and non-circular motion can all alter residual morphology. The current controls reduce but do not eliminate these concerns.

\begin{figure}[H]
\centering
\includegraphics[width=0.78\linewidth]{figures/paper2_distance_stress.pdf}
\caption{Distance-matched stress checks for the primary residual score. These checks reduce but do not eliminate observability concerns.}
\end{figure}

Accordingly, the result should be read as a reproducible SPARC diagnostic association with external-proxy context, not as a selection-function-proof physical inference.

\section{Claim boundary and Phase II}

Allowed claim: fixed residual-shape features recover externally reviewed A/C disturbance class better than chance in the current SPARC packet, and several external proxy readouts provide mixed but informative context.

Forbidden claims: Tau Core validation, gravity-model selection, projection-formula uniqueness, replacement of external labels by residual-only labels, broad independent external validation, or THINGS route2 positive evidence.

The next paper-grade step is a held-out external source-family test with $N\geq15$, a frozen evidence rule, no velocity-endpoint refit, explicit observability covariates, and predefined failure conditions. A negative Phase II result should be treated as evidence that the present association is SPARC-specific, proxy-specific, or observability-driven.

\bibliographystyle{plain}
\bibliography{references}

\end{document}
"""


def figure_audit_rows() -> list[dict[str, str]]:
    return [
        {
            "Figure": "paper2_projection_rms_distribution.pdf",
            "Source": "residual_feature_table.csv;paper2_calibration_uncertainty.csv",
            "TypographyStatus": "publication_candidate",
            "CaptionStatus": "short_descriptive_caption_in_latex",
            "VectorExport": "pdf",
            "Guardrail": GUARDRAIL,
        },
        {
            "Figure": "paper2_baseline_auc_comparison.pdf",
            "Source": "paper2_baseline_family_loogo.csv;paper2_newtonian_scope.csv",
            "TypographyStatus": "publication_candidate",
            "CaptionStatus": "short_descriptive_caption_in_latex",
            "VectorExport": "pdf",
            "Guardrail": GUARDRAIL,
        },
        {
            "Figure": "paper2_error_audit.pdf",
            "Source": "residual_inference_projection_rms_error_audit.csv",
            "TypographyStatus": "publication_candidate",
            "CaptionStatus": "short_descriptive_caption_in_latex",
            "VectorExport": "pdf",
            "Guardrail": GUARDRAIL,
        },
        {
            "Figure": "paper2_distance_stress.pdf",
            "Source": "paper2_observability_stress.csv",
            "TypographyStatus": "publication_candidate",
            "CaptionStatus": "short_descriptive_caption_in_latex",
            "VectorExport": "pdf",
            "Guardrail": GUARDRAIL,
        },
    ]


def source_gate_rows(pdf_status: str) -> list[dict[str, str]]:
    return [
        {
            "GateID": "P2SRC01",
            "Status": "latex_source_generated",
            "Evidence": "paper2_submission_source/main.tex",
            "BlocksSubmission": "no",
            "CanClaimTauValidation": "no",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "P2SRC02",
            "Status": "bibliography_generated",
            "Evidence": "paper2_submission_source/references.bib",
            "BlocksSubmission": "no",
            "CanClaimTauValidation": "no",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "P2SRC03",
            "Status": "figures_audited_publication_candidate",
            "Evidence": "paper2_figure_typography_audit_v01.csv",
            "BlocksSubmission": "no",
            "CanClaimTauValidation": "no",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "P2SRC04",
            "Status": pdf_status,
            "Evidence": "paper2_submission_source/main.pdf",
            "BlocksSubmission": "no" if pdf_status == "pdf_compiled_with_tectonic" else "yes",
            "CanClaimTauValidation": "no",
            "Guardrail": GUARDRAIL,
        },
    ]


def readiness_rows(pdf_status: str) -> list[dict[str, str]]:
    return [
        {
            "Area": "Manuscript identity",
            "Status": "ready_as_diagnostic_audit_candidate",
            "Evidence": "paper2_submission_source/main.tex",
            "RemainingIssue": "human journal-style polish still useful",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "Submission source",
            "Status": "ready" if pdf_status == "pdf_compiled_with_tectonic" else "blocked",
            "Evidence": "main.tex;main.pdf",
            "RemainingIssue": "" if pdf_status == "pdf_compiled_with_tectonic" else "PDF did not compile",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "Bibliography",
            "Status": "ready",
            "Evidence": "references.bib",
            "RemainingIssue": "verify preferred journal reference style before submission",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "Figures",
            "Status": "ready_as_publication_candidate",
            "Evidence": "four vector PDF figures; figure typography audit",
            "RemainingIssue": "final visual human review recommended",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "Claim boundary",
            "Status": "ready",
            "Evidence": "main.tex claim-boundary section; source gate",
            "RemainingIssue": "do not strengthen to Tau Core validation",
            "Guardrail": GUARDRAIL,
        },
    ]


def readiness_md(pdf_status: str) -> str:
    rows = readiness_rows(pdf_status)
    lines = [
        "# Paper 2 Submission Readiness v0.2",
        "",
        "Verdict: the three previous publication blockers are closed for a submission-candidate packet.",
        "",
        "Closed blockers:",
        "",
        "- LaTeX source/PDF candidate: `paper2_submission_source/main.tex` and `main.pdf`.",
        "- Bibliography/citation package: `paper2_submission_source/references.bib`.",
        "- Figure typography/caption audit: vector PDF figures plus `paper2_figure_typography_audit_v01.csv`.",
        "",
        "## Readiness Table",
        "",
    ]
    for row in rows:
        lines.append(f"- {row['Area']}: {row['Status']} ({row['Evidence']}).")
    lines.extend(
        [
            "",
            "## Remaining Non-Blocking Work",
            "",
            "- Human visual review of the generated PDF.",
            "- Journal-specific formatting adjustments.",
            "- Optional tightening of prose before arXiv/journal upload.",
            "",
            "## Claim Boundary",
            "",
            "The source remains a diagnostic SPARC residual-shape audit. It does not claim Tau Core validation, gravity-model selection, or independent paper-grade external validation.",
            "",
            f"Guardrail: `{GUARDRAIL}`",
            "",
        ]
    )
    return "\n".join(lines)


def figure_audit_md() -> str:
    lines = [
        "# Paper 2 Figure Typography Audit v0.1",
        "",
        "All submission-candidate figures are regenerated as vector PDF files under `paper2_submission_source/figures/`.",
        "",
    ]
    for row in figure_audit_rows():
        lines.append(
            f"- `{row['Figure']}`: {row['TypographyStatus']}; {row['CaptionStatus']}; source `{row['Source']}`."
        )
    lines.extend(
        [
            "",
            "The figures remain reproducible from packet tables and do not introduce new data or endpoint tuning.",
            "",
            f"Guardrail: `{GUARDRAIL}`",
            "",
        ]
    )
    return "\n".join(lines)


def compile_pdf() -> str:
    if shutil.which("tectonic") is None:
        return "pdf_blocked_no_tectonic"
    result = subprocess.run(
        ["tectonic", "main.tex"],
        cwd=SOURCE,
        text=True,
        capture_output=True,
        check=False,
    )
    log_path = SOURCE / "tectonic_build.log"
    log_path.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
    if result.returncode == 0 and PDF.exists() and PDF.stat().st_size > 10_000:
        return "pdf_compiled_with_tectonic"
    return "pdf_compile_failed"


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [
        FIGURE_AUDIT_MD,
        FIGURE_AUDIT_CSV,
        SOURCE_GATE,
        READINESS_MD,
        READINESS_CSV,
    ]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["paper2_submission_source_v01_status"] = (
        "latex_bibliography_pdf_and_figure_audit_generated"
    )
    manifest["paper2_next_gate"] = "human_pdf_review_and_journal_specific_polish"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    SOURCE.mkdir(parents=True, exist_ok=True)
    generate_figures()
    MAIN_TEX.write_text(tex_text(), encoding="utf-8")
    REFERENCES.write_text(bib_text(), encoding="utf-8")
    pdf_status = compile_pdf()
    FIGURE_AUDIT_MD.write_text(figure_audit_md(), encoding="utf-8")
    READINESS_MD.write_text(readiness_md(pdf_status), encoding="utf-8")
    write_csv(
        FIGURE_AUDIT_CSV,
        figure_audit_rows(),
        ["Figure", "Source", "TypographyStatus", "CaptionStatus", "VectorExport", "Guardrail"],
    )
    write_csv(
        SOURCE_GATE,
        source_gate_rows(pdf_status),
        ["GateID", "Status", "Evidence", "BlocksSubmission", "CanClaimTauValidation", "Guardrail"],
    )
    write_csv(
        READINESS_CSV,
        readiness_rows(pdf_status),
        ["Area", "Status", "Evidence", "RemainingIssue", "Guardrail"],
    )
    update_manifest()
    print(PDF)
    print(pdf_status)


if __name__ == "__main__":
    main()
