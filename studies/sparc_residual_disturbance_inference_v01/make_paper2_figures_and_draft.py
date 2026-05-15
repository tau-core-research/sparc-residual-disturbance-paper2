#!/usr/bin/env python3
"""Generate Paper 2 public figures and a first full manuscript draft."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

from make_packet_v01_seed import PACKET, ROOT


FIGURES = ROOT / "figures"
MANUSCRIPT = PACKET / "paper2_manuscript_draft.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def save_svg(name: str) -> None:
    path = FIGURES / name
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, format="svg", bbox_inches="tight")
    plt.close()


def plot_projection_rms_distribution() -> None:
    rows = read_csv(PACKET / "residual_feature_table.csv")
    calibration = read_csv(PACKET / "paper2_calibration_uncertainty.csv")[0]
    a_values = [float(row["Projection_RMS"]) for row in rows if row["Class"] == "A"]
    c_values = [float(row["Projection_RMS"]) for row in rows if row["Class"] == "C"]
    threshold = float(calibration["Threshold"])

    plt.figure(figsize=(6.8, 4.2))
    bins = [index / 20 for index in range(0, 21)]
    plt.hist(a_values, bins=bins, alpha=0.72, label="A: externally regular", color="#2878b5")
    plt.hist(c_values, bins=bins, alpha=0.62, label="C: externally disturbed", color="#c85200")
    plt.axvline(threshold, color="#222222", linewidth=1.5, linestyle="--", label="A/C threshold")
    plt.xlabel("Projection RMS residual")
    plt.ylabel("Number of galaxies")
    plt.title("A/C separation by fixed Projection RMS residual")
    plt.legend(frameon=False, fontsize=9)
    plt.tight_layout()
    save_svg("paper2_projection_rms_distribution.svg")


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
    colors = ["#2878b5", "#5b8f22", "#7b5aa6", "#777777"]

    plt.figure(figsize=(6.8, 4.2))
    bars = plt.bar(labels, aucs, color=colors)
    plt.axhline(0.5, color="#333333", linewidth=1.0, linestyle=":", label="chance")
    plt.ylim(0.4, 0.85)
    plt.ylabel("LOOGO AUC")
    plt.title("Residual-family A/C recovery")
    for bar, value in zip(bars, aucs):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.012,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    plt.legend(frameon=False, fontsize=9)
    plt.tight_layout()
    save_svg("paper2_baseline_auc_comparison.svg")


def plot_error_audit() -> None:
    rows = read_csv(PACKET / "residual_inference_projection_rms_error_audit.csv")
    counts = {"correct": 0, "false positive A as C": 0, "false negative C as A": 0}
    for row in rows:
        if row["ErrorFamily"] == "correct":
            counts["correct"] += 1
        elif row["ErrorFamily"] == "false_positive_A_as_C":
            counts["false positive A as C"] += 1
        elif row["ErrorFamily"] == "false_negative_C_as_A":
            counts["false negative C as A"] += 1

    plt.figure(figsize=(6.8, 4.2))
    labels = list(counts)
    values = [counts[label] for label in labels]
    bars = plt.bar(labels, values, color=["#2878b5", "#c85200", "#7b5aa6"])
    plt.ylabel("Number of galaxies")
    plt.title("Projection RMS threshold error audit")
    plt.xticks(rotation=18, ha="right")
    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.5,
            str(value),
            ha="center",
            va="bottom",
            fontsize=9,
        )
    plt.tight_layout()
    save_svg("paper2_error_audit.svg")


def plot_distance_stress() -> None:
    rows = read_csv(PACKET / "paper2_observability_stress.csv")
    labels = []
    values = []
    for row in rows:
        if row["MedianPairedDiff_C_minus_A"]:
            label = row["StressTest"].replace("sparc_distance_", "").replace("_matched_pairs", "")
            labels.append(label.replace("_", " "))
            values.append(float(row["MedianPairedDiff_C_minus_A"]))

    plt.figure(figsize=(6.8, 4.2))
    bars = plt.bar(labels, values, color=["#2878b5", "#5b8f22", "#c85200"])
    plt.axhline(0.0, color="#333333", linewidth=1.0)
    plt.ylabel("Median paired C minus A Projection RMS")
    plt.title("Distance-matched observability stress")
    plt.xticks(rotation=15, ha="right")
    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.006,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    plt.tight_layout()
    save_svg("paper2_distance_stress.svg")


def write_manuscript() -> None:
    metrics = {row["Metric"]: row for row in read_csv(PACKET / "paper2_final_metric_table.csv")}
    readiness = {row["Gate"]: row for row in read_csv(PACKET / "paper2_readiness_table.csv")}
    lines = [
        "# Residual-shape inference of structural disturbance in SPARC rotation curves: a diagnostic audit",
        "",
        "## Abstract",
        "",
        "We test whether fixed rotation-curve residual-shape features can recover externally reviewed structural-disturbance labels in the SPARC sample. The analysis reverses the direction of the Paper 1 residual-blind audit: the A/C labels are targets here, while residuals are predictors. The primary frozen diagnostic is `Projection_RMS`, evaluated with leave-one-galaxy-out thresholding, a shuffled-label null, bootstrap uncertainty, baseline-family comparisons, and distance-matched stress checks. `Projection_RMS` reaches a LOOGO AUC of 0.771 with accuracy 0.756; a shuffled-label null gives empirical p=0.002, and the bootstrap 95% AUC interval is [0.601, 0.909]. MOND-like and RAR-like residual scores also separate A/C systems, while a Newtonian baryonic RMS control is near chance. The result is therefore best read as a residual-shape diagnostic association in the low-acceleration residual family, not as a Tau Core validation result, not as a unique projection-model selection result, and not as a replacement for external evidence labels.",
        "",
        "## 1. Introduction",
        "",
        "Rotation-curve residuals are often treated as model failures or nuisance structure. In disturbed galaxies, however, residual morphology can also encode non-equilibrium dynamics, non-circular motion, beam-smearing sensitivity, asymmetric drift corrections, or geometry-dependent observational systematics. This paper asks a deliberately narrower question: can fixed residual-shape features recover externally reviewed A/C disturbance class better than chance?",
        "",
        "The study is a diagnostic audit. It does not attempt to prove a gravitational model. It uses the external labels inherited from the Paper 1 evidence packet as targets and tests whether a small set of residual features can recover those targets under simple, reviewable validation rules.",
        "",
        "## 2. Data and Label Scope",
        "",
        "The working sample contains 45 SPARC galaxies with Paper 1 A/C labels: 17 externally regular A systems and 28 externally disturbed C systems. B-class systems are intentionally excluded from primary training and primary A/C validation because they are uncertain by construction. They are retained only as an uncertainty band and as a possible prioritization set for future external review.",
        "",
        "The residual-feature table is generated from the fixed point map in `taucore_specificity_point_map.csv`. Required derived Paper 1 inputs are included in this repository only where needed to preserve reproducibility paths.",
        "",
        "## 3. Residual Features",
        "",
        "The primary diagnostic is `Projection_RMS`, the galaxy-level RMS of the fixed projection residual. Additional exploratory features include radial residual structure, low-acceleration residual burden, and residual differences between the projection, MOND-simple, and empirical RAR-like baselines. The composite score is not promoted as the primary result because it does not improve the leave-one-galaxy-out baseline.",
        "",
        "## 4. Validation Design",
        "",
        "The primary classifier is intentionally simple: for each held-out galaxy, the A/C threshold is recomputed from the remaining galaxies as the midpoint between the A and C medians, and the held-out galaxy is classified by whether its score lies above or below that threshold. This leave-one-galaxy-out design avoids fitting the threshold on the held-out galaxy while keeping the rule transparent.",
        "",
        "A shuffled-label null preserves class counts and tests whether the observed AUC is typical under random A/C assignment. Bootstrap resampling provides sample-size uncertainty, but it is not treated as independent external validation.",
        "",
        "## 5. Results",
        "",
        f"The primary `Projection_RMS` diagnostic reaches LOOGO AUC={metrics['Projection_RMS_LOOGO']['Value']} with {metrics['Projection_RMS_LOOGO']['SecondaryValue']}. The shuffled-label empirical p-value is {metrics['Projection_RMS_shuffle_null_p']['Value']}, with null 95th-percentile AUC reported as {metrics['Projection_RMS_shuffle_null_p']['SecondaryValue']}. The bootstrap 95% AUC interval is [{metrics['Projection_RMS_bootstrap_auc_ci95']['Value']}, {metrics['Projection_RMS_bootstrap_auc_ci95']['SecondaryValue']}].",
        "",
        "![Projection RMS distribution](../../../figures/paper2_projection_rms_distribution.svg)",
        "",
        "## 6. Baseline-Family Comparison",
        "",
        f"MOND-simple RMS reaches AUC={metrics['MOND_RMS_LOOGO_AUC']['Value']}, and empirical RAR-like RMS reaches AUC={metrics['RAR_RMS_LOOGO_AUC']['Value']}. The Newtonian baryonic RMS control reaches AUC={metrics['Newtonian_Baryonic_RMS_LOOGO_AUC']['Value']}. This pattern argues against a generic residual-amplitude artifact and supports the narrower claim that A/C separation appears mainly in low-acceleration residual-family scores. It does not establish projection-formula uniqueness.",
        "",
        "![Baseline AUC comparison](../../../figures/paper2_baseline_auc_comparison.svg)",
        "",
        "## 7. Error Audit",
        "",
        "The Projection RMS threshold yields 34 correct classifications, 3 false-positive A-as-C systems, and 8 false-negative C-as-A systems. The false negatives are especially important: several externally disturbed systems do not express that disturbance as a large smooth rotation-curve residual burden. This is a useful diagnostic failure mode, not a reason to relabel the galaxies from residuals alone.",
        "",
        "![Projection RMS error audit](../../../figures/paper2_error_audit.svg)",
        "",
        "## 8. Observability Stress",
        "",
        f"Distance matching does not erase the signal, but it does not solve the selection-function problem. The greedy distance-matched C-higher fraction is {metrics['distance_matched_greedy_fraction_c_higher']['Value']} ({metrics['distance_matched_greedy_fraction_c_higher']['SecondaryValue']}), and the strict distance-caliper median C-A difference is {metrics['distance_strict_caliper_median_diff']['Value']} ({metrics['distance_strict_caliper_median_diff']['SecondaryValue']}). The correct interpretation is that observability remains a major caveat.",
        "",
        "![Distance stress](../../../figures/paper2_distance_stress.svg)",
        "",
        "## 9. B-Class Policy",
        "",
        f"Using the frozen Projection RMS A/C threshold, {metrics['B_class_projection_threshold_split']['Value']} of 28 B-class galaxies score C-like ({metrics['B_class_projection_threshold_split']['SecondaryValue']}). This split is descriptive only. B galaxies are not used as primary training labels because that would turn uncertainty into pseudo-ground-truth.",
        "",
        "## 10. Limitations",
        "",
        "The sample is small. The labels are externally reviewed but not immune to source selection or observability bias. Nearby galaxies can reveal structural disturbance more easily than distant galaxies, and beam smearing, inclination, non-circular motion, pressure support, and asymmetric drift corrections can all affect residual morphology. The analysis also lacks independent external validation in a second survey family. HALOGAS H07 is treated only as a weak, non-specific external-family control.",
        "",
        "## 11. Claim Boundary",
        "",
        "Allowed claim: fixed residual-shape features recover externally reviewed A/C disturbance class better than chance in the current SPARC packet, with important observability caveats.",
        "",
        "Forbidden claims: Tau Core validation, projection-model uniqueness, replacement of external evidence labels by residual-only labels, or independent external validation.",
        "",
        "## 12. Phase II",
        "",
        f"The primary diagnostic gate is {readiness['Primary diagnostic']['Status']}; observability is {readiness['Observability']['Status']}; external validation is {readiness['External validation']['Status']}. The next paper-grade step is a held-out external validation sample with a frozen evidence rule and a predeclared residual-feature map.",
        "",
    ]
    MANUSCRIPT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update({"paper2_manuscript_draft.md"})
    manifest["files"] = sorted(files)
    manifest["paper2_figures_and_draft_status"] = "public_figures_and_first_full_draft_ready"
    manifest["paper2_next_gate"] = "figure_review_and_manuscript_polish"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    plot_projection_rms_distribution()
    plot_baseline_auc_comparison()
    plot_error_audit()
    plot_distance_stress()
    write_manuscript()
    update_manifest()
    print(MANUSCRIPT)
    print("paper2_figures=4")


if __name__ == "__main__":
    main()
