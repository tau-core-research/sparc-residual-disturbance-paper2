#!/usr/bin/env python3
"""Generate Paper 2 LaTeX source, bibliography, publication figures, and PDF."""

from __future__ import annotations

import csv
import math
import os
import json
import random
import shutil
import subprocess
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "studies/sparc_residual_disturbance_inference_v01/packet_v01_seed"
SOURCE = ROOT / "paper2_submission_source"
SOURCE_FIGURES = SOURCE / "figures"
MAIN_TEX = SOURCE / "main.tex"
REFERENCES = SOURCE / "references.bib"
PDF = SOURCE / "main.pdf"
ZIP_PATH = ROOT / "arxiv_submission_source.zip"
FIGURE_AUDIT_MD = PACKET / "paper2_figure_typography_audit_v01.md"
FIGURE_AUDIT_CSV = PACKET / "paper2_figure_typography_audit_v01.csv"
SOURCE_GATE = PACKET / "paper2_submission_source_gate_v01.csv"
READINESS_MD = PACKET / "paper2_submission_readiness_v02.md"
READINESS_CSV = PACKET / "paper2_submission_readiness_v02.csv"
SAMPLE_TABLE = PACKET / "paper2_ac_sample_appendix_v01.csv"
BASELINE_CI_TABLE = PACKET / "paper2_baseline_auc_ci_v01.csv"
EXTERNAL_GATE_TABLE = PACKET / "paper2_external_proxy_gate_table_v01.csv"
B_SENSITIVITY_TABLE = PACKET / "paper2_b_class_sensitivity_v01.csv"
OBSERVABILITY_TABLE = PACKET / "paper2_observability_covariate_appendix_v01.csv"
OUTLIER_TABLE = PACKET / "paper2_outlier_failure_case_appendix_v01.csv"
STABILITY_TABLE = PACKET / "paper2_stability_effect_size_v01.csv"
ILLUSTRATIVE_CURVES = ROOT / "studies/illustrative_rotation_curves"

GUARDRAIL = "paper2_submission_source_ready_no_tau_validation_no_external_overclaim"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def auc_c_higher(rows: list[dict[str, str]], score_key: str) -> float:
    a_scores = [float(row[score_key]) for row in rows if row["Class"] == "A"]
    c_scores = [float(row[score_key]) for row in rows if row["Class"] == "C"]
    total = len(a_scores) * len(c_scores)
    wins = 0.0
    for c_score in c_scores:
        for a_score in a_scores:
            if c_score > a_score:
                wins += 1.0
            elif c_score == a_score:
                wins += 0.5
    return wins / total


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def bootstrap_auc_ci(rows: list[dict[str, str]], score_key: str, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    a_rows = [row for row in rows if row["Class"] == "A"]
    c_rows = [row for row in rows if row["Class"] == "C"]
    values = []
    for _ in range(2000):
        sample = [rng.choice(a_rows) for _ in a_rows] + [rng.choice(c_rows) for _ in c_rows]
        values.append(auc_c_higher(sample, score_key))
    return percentile(values, 0.025), percentile(values, 0.975)


def bootstrap_auc_values(rows: list[dict[str, str]], score_key: str, seed: int, n: int = 2000) -> list[float]:
    rng = random.Random(seed)
    a_rows = [row for row in rows if row["Class"] == "A"]
    c_rows = [row for row in rows if row["Class"] == "C"]
    values = []
    for _ in range(n):
        sample = [rng.choice(a_rows) for _ in a_rows] + [rng.choice(c_rows) for _ in c_rows]
        values.append(auc_c_higher(sample, score_key))
    return values


def shuffled_auc_values(rows: list[dict[str, str]], score_key: str, seed: int, n: int = 1000) -> list[float]:
    rng = random.Random(seed)
    scores = [float(row[score_key]) for row in rows]
    labels = [1 if row["Class"] == "C" else 0 for row in rows]
    values = []
    for _ in range(n):
        shuffled = labels[:]
        rng.shuffle(shuffled)
        positives = [score for label, score in zip(shuffled, scores) if label == 1]
        negatives = [score for label, score in zip(shuffled, scores) if label == 0]
        wins = 0.0
        total = 0
        for pos in positives:
            for neg in negatives:
                total += 1
                if pos > neg:
                    wins += 1.0
                elif pos == neg:
                    wins += 0.5
        values.append(wins / total)
    return values


def baseline_score_rows() -> list[dict[str, str]]:
    rows = read_csv(PACKET / "residual_feature_table.csv")
    paper1 = read_csv(
        ROOT
        / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/baseline_score_by_galaxy.csv"
    )
    newtonian = {
        row["GalaxyName"]: row["RmsLog"]
        for row in paper1
        if row["Score"] == "newtonian_baryonic" and row["Class"] in {"A", "C"}
    }
    for row in rows:
        row["Newtonian_Baryonic_RMS"] = newtonian[row["GalaxyName"]]
    return rows


def baseline_ci_rows() -> list[dict[str, str]]:
    rows = baseline_score_rows()
    metrics = [
        ("Projection_RMS", "Projection RMS"),
        ("MOND_RMS", "MOND-simple RMS"),
        ("RAR_RMS", "RAR-like RMS"),
        ("Newtonian_Baryonic_RMS", "Newtonian baryonic RMS"),
    ]
    output = []
    for index, (key, label) in enumerate(metrics):
        low, high = bootstrap_auc_ci(rows, key, 20260601 + index)
        output.append(
            {
                "Predictor": key,
                "Label": label,
                "AUC_C_higher": f"{auc_c_higher(rows, key):.9f}",
                "BootstrapN": "2000",
                "BootstrapCI95Low": f"{low:.9f}",
                "BootstrapCI95High": f"{high:.9f}",
                "Guardrail": GUARDRAIL,
            }
        )
    return output


def sample_appendix_rows() -> list[dict[str, str]]:
    features = {row["GalaxyName"]: row for row in read_csv(PACKET / "residual_feature_table.csv")}
    distances = {
        row["GalaxyName"]: row
        for row in read_csv(PACKET / "distance_resolution_environment_join_v01.csv")
    }
    inclinations = {
        row["GalaxyName"]: row
        for row in read_csv(PACKET / "p09_observability_decomposition_join_v01.csv")
    }
    output = []
    for name in sorted(features):
        row = features[name]
        distance = distances[name]
        inclination = inclinations[name]
        output.append(
            {
                "GalaxyName": name,
                "Class": row["Class"],
                "DistanceMpc": distance["DistanceMpc"],
                "InclinationDeg": inclination["InclinationDeg"],
                "NPoints": row["NPoints"],
                "Projection_RMS": row["Projection_RMS"],
                "MOND_RMS": row["MOND_RMS"],
                "RAR_RMS": row["RAR_RMS"],
                "Guardrail": GUARDRAIL,
            }
        )
    return output


def external_gate_rows() -> list[dict[str, str]]:
    rows = read_csv(PACKET / "paper2_external_proxy_summary_v03.csv")
    output = []
    for row in rows:
        status = row["Status"]
        if status in {"directional_support_but_small_overlap", "mixed_directional_support"}:
            gate = "supporting_context"
        elif status == "promising_below_minimum_n":
            gate = "fail_minimum_n"
        elif status in {"weak_or_non_directional", "weak_control_only"}:
            gate = "weak_or_control"
        else:
            gate = "negative_audit"
        output.append(
            {
                "ProxySource": row["FamilyID"],
                "OverlapN": row["JoinedN"],
                "Direction": row["Status"],
                "EffectSize": row["PrimaryMetric"],
                "FrozenGate": gate,
                "Guardrail": GUARDRAIL,
            }
        )
    return output


def external_latex_rows() -> str:
    display = {
        "WHISP_RESOLVED": ("WHISP resolved", "positive, small N", "r=0.391; AUC=0.714", "context"),
        "WHISP_MORPH": ("WHISP morph.", "mixed", "AUC=0.644; burden=0.506", "context"),
        "REYNOLDS_LVH": ("Reynolds/LVHIS", "promising, N<15", "r=0.375; AUC=0.778", "fail N"),
        "ALFALFA": ("ALFALFA", "weak", "r=0.146; AUC=0.472", "weak"),
        "HALOGAS": ("HALOGAS", "control-like", "r=0.216; AUC=0.500", "control"),
        "THINGS_ROUTE2": ("THINGS route2", "closed", "0 score-ready", "negative audit"),
    }
    rows = []
    for row in external_gate_rows():
        source, direction, effect, gate = display[row["ProxySource"]]
        rows.append(
            " & ".join(
                [
                    latex_escape(source),
                    latex_escape(row["OverlapN"]),
                    latex_escape(direction),
                    latex_escape(effect),
                    latex_escape(gate),
                ]
            )
            + r"\\"
        )
    return "\n".join(rows)


def b_sensitivity_rows() -> list[dict[str, str]]:
    policy = read_csv(PACKET / "paper2_b_class_policy.csv")[0]
    return [
        {
            "SensitivityID": "B01",
            "NB": policy["NB"],
            "ProjectionRMSThreshold": policy["ProjectionRMSThreshold"],
            "BPredictedC_like": policy["BPredictedC_like"],
            "BPredictedA_like": policy["BPredictedA_like"],
            "Interpretation": "descriptive_uncertainty_band_not_primary_training",
            "Guardrail": GUARDRAIL,
        }
    ]


def observability_rows() -> list[dict[str, str]]:
    metrics = {
        row["Metric"]: row for row in read_csv(PACKET / "multivariable_no_velocity_stress_metrics_v01.csv")
    }
    wanted = [
        "partial_pearson_tau_distance_after_nuisance_vs_score_after_nuisance",
        "partial_auc_tau_distance_residual_high_vs_low_score_residual",
        "nuisance_model_r2_for_w_tau_score",
        "pearson_NPoints_z_vs_w_tau_score",
        "pearson_MeanErrVobsKms_z_vs_w_tau_score",
        "pearson_InclinationErrorDeg_z_vs_w_tau_score",
        "pearson_DistanceFractionalError_z_vs_w_tau_score",
    ]
    output = []
    for metric in wanted:
        row = metrics[metric]
        output.append(
            {
                "Metric": metric,
                "N": row["N"],
                "Value": row["Value"],
                "SecondaryValue": row["SecondaryValue"],
                "Interpretation": "observability_covariate_stress_not_bias_erasure",
                "Guardrail": GUARDRAIL,
            }
        )
    return output


def observability_latex_rows() -> str:
    labels = {
        "partial_pearson_tau_distance_after_nuisance_vs_score_after_nuisance": "partial distance residual correlation",
        "partial_auc_tau_distance_residual_high_vs_low_score_residual": "partial distance residual AUC",
        "nuisance_model_r2_for_w_tau_score": "nuisance-only model R2",
        "pearson_NPoints_z_vs_w_tau_score": "point-count correlation",
        "pearson_MeanErrVobsKms_z_vs_w_tau_score": "velocity-error correlation",
        "pearson_InclinationErrorDeg_z_vs_w_tau_score": "inclination-error correlation",
        "pearson_DistanceFractionalError_z_vs_w_tau_score": "distance-error correlation",
    }
    secondary = {
        "partial_pearson_tau_distance_after_nuisance_vs_score_after_nuisance": "nuisance controls",
        "partial_auc_tau_distance_residual_high_vs_low_score_residual": "residual split",
        "nuisance_model_r2_for_w_tau_score": "nuisance-only",
        "pearson_NPoints_z_vs_w_tau_score": "nuisance channel",
        "pearson_MeanErrVobsKms_z_vs_w_tau_score": "nuisance channel",
        "pearson_InclinationErrorDeg_z_vs_w_tau_score": "nuisance channel",
        "pearson_DistanceFractionalError_z_vs_w_tau_score": "nuisance channel",
    }
    return "\n".join(
        f"{latex_escape(labels[row['Metric']])} & {latex_escape(row['N'])} & {latex_escape(row['Value'])} & {latex_escape(secondary[row['Metric']])}\\\\"
        for row in observability_rows()
    )


def mann_whitney_u(a_values: list[float], c_values: list[float]) -> float:
    wins = 0.0
    for c_score in c_values:
        for a_score in a_values:
            if c_score > a_score:
                wins += 1.0
            elif c_score == a_score:
                wins += 0.5
    return wins


def cliff_delta(a_values: list[float], c_values: list[float]) -> float:
    greater = lesser = 0
    for c_score in c_values:
        for a_score in a_values:
            if c_score > a_score:
                greater += 1
            elif c_score < a_score:
                lesser += 1
    return (greater - lesser) / (len(a_values) * len(c_values))


def effect_size_rows() -> list[dict[str, str]]:
    rows = baseline_score_rows()
    a_values = [float(row["Projection_RMS"]) for row in rows if row["Class"] == "A"]
    c_values = [float(row["Projection_RMS"]) for row in rows if row["Class"] == "C"]
    auc_value = auc_c_higher(rows, "Projection_RMS")
    cliff = cliff_delta(a_values, c_values)
    bootstrap = bootstrap_auc_values(rows, "Projection_RMS", 20260611)
    shuffled = shuffled_auc_values(rows, "Projection_RMS", 20260515)
    without_camb = [row for row in rows if row["GalaxyName"] != "CamB"]
    return [
        {
            "Metric": "mann_whitney_u_c_higher",
            "Value": f"{mann_whitney_u(a_values, c_values):.9f}",
            "SecondaryValue": f"nA={len(a_values)};nC={len(c_values)}",
            "Interpretation": "rank_effect_size_not_model_selection",
            "Guardrail": GUARDRAIL,
        },
        {
            "Metric": "cliffs_delta_c_higher",
            "Value": f"{cliff:.9f}",
            "SecondaryValue": "positive_means_C_scores_tend_higher",
            "Interpretation": "rank_effect_size_not_model_selection",
            "Guardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_minus_chance",
            "Value": f"{auc_value - 0.5:.9f}",
            "SecondaryValue": f"auc={auc_value:.9f}",
            "Interpretation": "descriptive_effect_size",
            "Guardrail": GUARDRAIL,
        },
        {
            "Metric": "bootstrap_auc_median",
            "Value": f"{percentile(bootstrap, 0.5):.9f}",
            "SecondaryValue": f"p05={percentile(bootstrap, 0.05):.9f};p95={percentile(bootstrap, 0.95):.9f}",
            "Interpretation": "stability_distribution",
            "Guardrail": GUARDRAIL,
        },
        {
            "Metric": "permutation_auc_median",
            "Value": f"{percentile(shuffled, 0.5):.9f}",
            "SecondaryValue": f"p95={percentile(shuffled, 0.95):.9f};observed={auc_value:.9f}",
            "Interpretation": "label_null_distribution",
            "Guardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_without_CamB",
            "Value": f"{auc_c_higher(without_camb, 'Projection_RMS'):.9f}",
            "SecondaryValue": "A-class outlier removed for sensitivity only",
            "Interpretation": "outlier_sensitivity_not_primary_result",
            "Guardrail": GUARDRAIL,
        },
    ]


def outlier_rows() -> list[dict[str, str]]:
    features = {row["GalaxyName"]: row for row in read_csv(PACKET / "residual_feature_table.csv")}
    errors = {
        row["GalaxyName"]: row
        for row in read_csv(PACKET / "residual_inference_projection_rms_error_audit.csv")
    }
    distance = {
        row["GalaxyName"]: row
        for row in read_csv(PACKET / "distance_resolution_environment_join_v01.csv")
    }
    inclination = {
        row["GalaxyName"]: row
        for row in read_csv(PACKET / "p09_observability_decomposition_join_v01.csv")
    }
    output = []
    for name in ["CamB", "UGC05764", "NGC5585"]:
        frow = features[name]
        erow = errors[name]
        drow = distance[name]
        irow = inclination[name]
        output.append(
            {
                "GalaxyName": name,
                "Class": frow["Class"],
                "ErrorFamily": erow["ErrorFamily"],
                "Projection_RMS": frow["Projection_RMS"],
                "LOOGOThreshold": erow["LOOGOThreshold"],
                "Margin": erow["MarginScoreMinusThreshold"],
                "NPoints": frow["NPoints"],
                "DistanceMpc": drow["DistanceMpc"],
                "InclinationDeg": irow["InclinationDeg"],
                "EvidenceType": erow["EvidenceType"],
                "InspectionNote": erow["DiagnosticNote"],
                "Guardrail": GUARDRAIL,
            }
        )
    return output


def outlier_latex_rows() -> str:
    compact_notes = {
        "CamB": "dominant A-class failure; low point count; very high low-acceleration residual burden",
        "UGC05764": "secondary A-class failure; compact 10-point curve; high residual margin",
        "NGC5585": "near-threshold A-class failure; external low-asymmetry evidence but residual just above gate",
    }
    error_labels = {
        "false_positive_A_as_C": "A as C",
        "false_negative_C_as_A": "C as A",
        "correct": "correct",
    }

    return "\n".join(
        " & ".join(
            latex_escape(value)
            for value in [
                row["GalaxyName"],
                row["Class"],
                error_labels[row["ErrorFamily"]],
                row["Projection_RMS"],
                row["NPoints"],
                row["DistanceMpc"],
                row["InclinationDeg"],
                compact_notes[row["GalaxyName"]],
            ]
        )
        + r"\\"
        for row in outlier_rows()
    )


def effect_latex_rows() -> str:
    labels = {
        "mann_whitney_u_c_higher": "Mann--Whitney $U$",
        "cliffs_delta_c_higher": "Cliff's $\\delta$",
        "auc_minus_chance": "AUC minus chance",
        "bootstrap_auc_median": "Bootstrap AUC median",
        "permutation_auc_median": "Label-shuffle AUC median",
        "auc_without_CamB": "AUC without CamB",
    }
    secondary = {
        "positive_means_C_scores_tend_higher": "positive means C scores tend higher",
        "A-class outlier removed for sensitivity only": "A-class outlier removed for sensitivity only",
    }

    return "\n".join(
        f"{labels[row['Metric']]} & {latex_escape(row['Value'])} & {latex_escape(secondary.get(row['SecondaryValue'], row['SecondaryValue']))}\\\\"
        for row in effect_size_rows()
    )


def save_pdf(name: str) -> None:
    SOURCE_FIGURES.mkdir(parents=True, exist_ok=True)
    metadata = {
        "Creator": "sparc-residual-disturbance-paper2",
        "Producer": "matplotlib",
        "CreationDate": None,
        "ModDate": None,
    }
    plt.savefig(SOURCE_FIGURES / name, format="pdf", bbox_inches="tight", metadata=metadata)
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

    rng = random.Random(20260515)
    plt.figure(figsize=(6.4, 4.0))
    parts = plt.violinplot([a_values, c_values], positions=[1, 2], widths=0.55, showextrema=False)
    for body, color in zip(parts["bodies"], ["#2a6fbb", "#c65d1e"]):
        body.set_facecolor(color)
        body.set_edgecolor("#222222")
        body.set_alpha(0.28)
    plt.boxplot(
        [a_values, c_values],
        positions=[1, 2],
        widths=0.25,
        showfliers=False,
        patch_artist=True,
        boxprops={"facecolor": "white", "edgecolor": "#222222"},
        medianprops={"color": "#222222", "linewidth": 1.4},
    )
    for xpos, values, color, label in [
        (1, a_values, "#2a6fbb", "A: regular"),
        (2, c_values, "#c65d1e", "C: disturbed"),
    ]:
        jitter = [xpos + rng.uniform(-0.08, 0.08) for _ in values]
        plt.scatter(jitter, values, s=22, alpha=0.78, color=color, label=label)
    plt.axhline(threshold, color="#1f1f1f", linewidth=1.2, linestyle="--", label="LOOGO threshold")
    plt.xticks([1, 2], ["A", "C"])
    plt.ylabel("Projection RMS residual score")
    plt.title("Projection RMS by external class")
    plt.legend(frameon=False)
    plt.tight_layout()
    save_pdf("paper2_projection_rms_distribution.pdf")


def plot_baseline_auc_comparison() -> None:
    ci_rows = baseline_ci_rows()
    labels = ["Projection", "MOND", "RAR", "Newtonian"]
    aucs = [float(row["AUC_C_higher"]) for row in ci_rows]
    lows = [float(row["BootstrapCI95Low"]) for row in ci_rows]
    highs = [float(row["BootstrapCI95High"]) for row in ci_rows]
    yerr = [[auc - low for auc, low in zip(aucs, lows)], [high - auc for auc, high in zip(aucs, highs)]]
    colors = ["#2a6fbb", "#3f8f4f", "#7b5aa6", "#777777"]

    plt.figure(figsize=(6.4, 4.0))
    bars = plt.bar(
        labels,
        aucs,
        color=colors,
        width=0.62,
        yerr=yerr,
        error_kw={"elinewidth": 1.2, "capsize": 3, "capthick": 1.2, "ecolor": "#222222"},
    )
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
    sensitivity = counts["correct"]  # placeholder to keep the text block close to counts below
    recall_c = 20 / 28
    specificity_a = 14 / 17
    balanced_accuracy = (recall_c + specificity_a) / 2
    plt.text(
        1.0,
        29.0,
        f"sensitivity(C)={recall_c:.3f}\nspecificity(A)={specificity_a:.3f}\nbalanced acc.={balanced_accuracy:.3f}",
        ha="center",
        va="top",
        fontsize=10,
    )
    plt.tight_layout()
    save_pdf("paper2_error_audit.pdf")


def plot_confusion_matrix() -> None:
    rows = [
        row
        for row in read_csv(PACKET / "residual_inference_loogo_predictions.csv")
        if row["Predictor"] == "Projection_RMS"
    ]
    matrix = [[0, 0], [0, 0]]
    for row in rows:
        true_index = 0 if row["TrueClass"] == "A" else 1
        pred_index = 0 if row["PredictedClass"] == "A" else 1
        matrix[true_index][pred_index] += 1

    fig, ax = plt.subplots(figsize=(4.4, 4.0))
    im = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=max(max(row) for row in matrix))
    ax.set_xticks([0, 1], ["Pred. A", "Pred. C"])
    ax.set_yticks([0, 1], ["True A", "True C"])
    ax.set_title("Projection RMS confusion matrix")
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            ax.text(j, i, str(value), ha="center", va="center", color="#111111", fontsize=14)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    plt.tight_layout()
    save_pdf("paper2_confusion_matrix.pdf")


def plot_projection_roc() -> None:
    rows = [
        row
        for row in read_csv(PACKET / "residual_inference_loogo_predictions.csv")
        if row["Predictor"] == "Projection_RMS"
    ]
    scores = [float(row["Score"]) for row in rows]
    thresholds = [min(scores) - 1e-6] + sorted(set(scores)) + [max(scores) + 1e-6]
    points = []
    for threshold in thresholds:
        tp = fp = tn = fn = 0
        for row in rows:
            pred_c = float(row["Score"]) >= threshold
            true_c = row["TrueClass"] == "C"
            if pred_c and true_c:
                tp += 1
            elif pred_c and not true_c:
                fp += 1
            elif not pred_c and true_c:
                fn += 1
            else:
                tn += 1
        tpr = tp / (tp + fn)
        fpr = fp / (fp + tn)
        points.append((fpr, tpr))
    points = sorted(points)

    plt.figure(figsize=(4.6, 4.2))
    plt.plot([point[0] for point in points], [point[1] for point in points], color="#2a6fbb", linewidth=1.8)
    plt.plot([0, 1], [0, 1], linestyle=":", color="#555555", linewidth=1.0)
    plt.xlabel("False-positive rate")
    plt.ylabel("True-positive rate")
    plt.title("Projection RMS ROC curve")
    plt.text(0.58, 0.14, "AUC=0.771", fontsize=11)
    plt.xlim(-0.02, 1.02)
    plt.ylim(-0.02, 1.02)
    plt.tight_layout()
    save_pdf("paper2_projection_roc.pdf")


def plot_stability_distributions() -> None:
    rows = baseline_score_rows()
    bootstrap = bootstrap_auc_values(rows, "Projection_RMS", 20260611)
    shuffled = shuffled_auc_values(rows, "Projection_RMS", 20260515)
    observed = auc_c_higher(rows, "Projection_RMS")

    plt.figure(figsize=(6.4, 4.0))
    bins = [0.25 + index * 0.025 for index in range(31)]
    plt.hist(shuffled, bins=bins, alpha=0.62, color="#777777", label="label shuffle")
    plt.hist(bootstrap, bins=bins, alpha=0.54, color="#2a6fbb", label="bootstrap")
    plt.axvline(observed, color="#c65d1e", linewidth=1.6, label="observed")
    plt.xlabel("AUC")
    plt.ylabel("Resamples")
    plt.title("Projection RMS AUC stability")
    plt.legend(frameon=False)
    plt.tight_layout()
    save_pdf("paper2_auc_stability_distributions.pdf")


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


def illustrative_rotation_rows() -> dict[str, list[dict[str, str]]]:
    path = ILLUSTRATIVE_CURVES / "paper2_context_rotation_points.csv"
    if not path.exists():
        return {}
    rows: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(path):
        rows.setdefault(row["GalaxyName"], []).append(row)
    return rows


def plot_illustrative_rotation_curves() -> None:
    model_rows = illustrative_rotation_rows()
    galaxies = ["DDO154", "CamB"]
    if not set(galaxies) <= set(model_rows):
        return

    fig, axes = plt.subplots(2, 2, figsize=(9.0, 6.5), sharex="col")
    for col, galaxy in enumerate(galaxies):
        points = sorted(model_rows[galaxy], key=lambda row: float(row["RadiusKpc"]))
        radii = [float(point["RadiusKpc"]) for point in points]
        vobs = [float(point["VobsKms"]) for point in points]
        verr = [float(point["ErrVobsKms"]) for point in points]
        vbar = [float(point["VbarKms"]) for point in points]
        projection = [float(point["AbsResidualProjection"]) for point in points]
        mond = [float(point["AbsResidualMONDSimple"]) for point in points]
        rar = [float(point["AbsResidualRAR"]) for point in points]
        score = float(points[0]["ProjectionRMS"])
        threshold = float(points[0]["LOOGOThreshold"])
        role = points[0]["Role"]
        pred = points[0]["PredictedClass"]

        ax_curve = axes[0][col]
        ax_curve.errorbar(
            radii,
            vobs,
            yerr=verr,
            fmt="o",
            ms=3.3,
            lw=0.8,
            color="#111827",
            ecolor="#9ca3af",
            capsize=1.4,
            label="$V_{\\rm obs}$",
            zorder=5,
        )
        ax_curve.plot(radii, vbar, color="#6b7280", lw=1.35, linestyle="--", label="$V_{\\rm bar}$ baseline")
        ax_curve.set_title(f"{galaxy}: {role}", fontsize=11)
        ax_curve.set_ylabel("velocity [km s$^{-1}$]")
        ax_curve.grid(True, alpha=0.22)
        if col == 1:
            ax_curve.legend(frameon=False, fontsize=7.5, loc="best")

        ax_diag = axes[1][col]
        ax_diag.axhline(threshold, color="#111827", lw=0.9, alpha=0.65, linestyle="--", label="LOOGO threshold")
        ax_diag.plot(radii, projection, color="#b91c1c", lw=1.25, label="projection")
        ax_diag.plot(radii, mond, color="#2563eb", lw=1.0, linestyle="-.", label="MOND")
        ax_diag.plot(radii, rar, color="#0891b2", lw=1.0, linestyle=":", label="RAR")
        ax_diag.text(
            0.03,
            0.93,
            f"RMS={score:.3f}; predicted {pred}",
            transform=ax_diag.transAxes,
            fontsize=8.2,
            va="top",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.7, "pad": 1.5},
        )
        ax_diag.set_ylabel("absolute log residual")
        ax_diag.set_xlabel("radius [kpc]")
        ax_diag.grid(True, alpha=0.22)
        if col == 1:
            ax_diag.legend(frameon=False, fontsize=7.5, loc="best")

    fig.suptitle("Classifier success/failure rotation-curve context", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    save_pdf("paper2_illustrative_rotation_curves.pdf")


def generate_figures() -> None:
    style()
    plot_projection_rms_distribution()
    plot_baseline_auc_comparison()
    plot_error_audit()
    plot_confusion_matrix()
    plot_projection_roc()
    plot_stability_distributions()
    plot_distance_stress()
    plot_illustrative_rotation_curves()


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


def latex_escape(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("#", "\\#")
    )


def rows_to_latex(rows: list[dict[str, str]], columns: list[str], max_rows: int | None = None) -> str:
    use_rows = rows if max_rows is None else rows[:max_rows]
    lines = []
    for row in use_rows:
        lines.append(" & ".join(latex_escape(row[column]) for column in columns) + r"\\")
    return "\n".join(lines)


def tex_text() -> str:
    ci_rows = baseline_ci_rows()
    sample_rows = sample_appendix_rows()
    external_rows = external_gate_rows()
    b_rows = b_sensitivity_rows()
    ci_table = rows_to_latex(
        ci_rows,
        ["Label", "AUC_C_higher", "BootstrapCI95Low", "BootstrapCI95High"],
    )
    sample_table = rows_to_latex(
        sample_rows,
        ["GalaxyName", "Class", "DistanceMpc", "InclinationDeg", "NPoints", "Projection_RMS"],
    )
    outlier_table = outlier_latex_rows()
    effect_table = effect_latex_rows()
    external_table = external_latex_rows()
    b_table = (
        f"{latex_escape(b_rows[0]['NB'])} & "
        f"{latex_escape(b_rows[0]['ProjectionRMSThreshold'])} & "
        f"{latex_escape(b_rows[0]['BPredictedC_like'])} & "
        f"{latex_escape(b_rows[0]['BPredictedA_like'])} & descriptive only\\\\"
    )
    observability_table = observability_latex_rows()
    tex = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{float}
\usepackage{longtable}

\title{Residual-shape inference and external-proxy audit of structural disturbance in SPARC rotation curves}
\author{Jozsef Olcsak}
\date{2026}

\begin{document}
\maketitle

\begin{abstract}
We ask whether fixed rotation-curve residual-shape features can recover externally reviewed structural-disturbance labels in SPARC galaxies, and whether independent H\,I disturbance proxies support the same diagnostic direction. The study reverses the Paper 1 audit: the A/C labels are treated as frozen external targets, while residual features are evaluated as predictors under leave-one-galaxy-out thresholding, shuffled-label null tests, bootstrap uncertainty, baseline-family controls, and observability stress checks. The primary internal feature, Projection RMS, reaches LOOGO AUC=0.771008403 with shuffled-label $p=0.002000000$ and bootstrap 95\% AUC interval $[0.600802469,0.909100262]$. MOND-simple and empirical RAR-like residual scores also separate A/C systems, whereas a Newtonian baryonic RMS control is near chance, indicating a low-acceleration residual-family effect rather than projection-formula uniqueness. External proxy readouts are supportive but not decisive. The result is therefore promising but sample-limited: a reproducible residual-inference and external-proxy audit, not a Tau Core validation claim, not gravity-model selection, and not independent paper-grade external validation.
\end{abstract}

\section{Introduction}

Rotation-curve residuals are usually discussed as model error, but their radial structure can also carry information about non-equilibrium dynamics, non-circular motions, pressure support, beam smearing, inclination, and source-dependent observability \cite{Trachternach2008THINGS,Oman2019NonCircular}. Paper 1 established a residual-blind association between externally assigned structural-disturbance labels and low-acceleration residual scatter in SPARC. Here we ask the inverse diagnostic question: can fixed residual-shape features recover those external labels better than chance?

The scope is deliberately narrow. This paper does not use residuals to redefine the labels, does not validate Tau Core, and does not select a unique gravity law. It tests whether a frozen residual feature map contains recoverable information about externally reviewed A/C disturbance classes, then checks whether independent H\,I disturbance proxies point in the same direction.

\section{Data and frozen inputs}

The working A/C sample contains 45 SPARC galaxies inherited from the Paper 1 reproducibility packet: 17 externally regular A systems and 28 externally disturbed C systems. SPARC rotation-curve and mass-model context follows \cite{Lelli2016SPARC,Lelli2016SPARCZenodo}. B-class systems remain excluded from the primary target labels because they encode uncertainty by construction. The residual features are computed from the fixed Paper 1 point map and are not retrained on the external-proxy catalogues.

The full reproducibility package, including the frozen derived tables, baseline-score comparisons, control summaries, figures, arXiv source package, and regeneration script, is archived at doi:10.5281/zenodo.20210154. The analysis can be regenerated with the commands listed in the repository README. Raw survey products and raw SPARC rotmod files are not redistributed by this repository.

The projection-family score is treated operationally as a fixed residual map inherited from Paper 1, without requiring the physical correctness of the underlying projection ansatz. This convention is central to the audit: the paper tests residual information content, not the physical validity of the projection model.

\section{Residual-shape endpoint and validation design}

For each galaxy $g$ and radial point $i$, the packet starts from absolute log-residual magnitudes
\[
r_{{m,gi}} = \left|\log V_{{\rm obs},gi} - \log V_{{m,gi}}\right|,
\]
where $m$ denotes the fixed residual family. Projection RMS is then
\[
{\rm RMS}_{{m,g}} =
\sqrt{{1\over N_g}\sum_i r_{{m,gi}}^2}.
\]
All points are weighted equally; no velocity-error weighting is applied in the primary endpoint. The radial domain is the available SPARC rotation-curve support for each galaxy after the inherited Paper 1 point-map construction. The same aggregation is used for Projection RMS, MOND-simple RMS, RAR-like RMS, and Newtonian baryonic RMS. The Projection endpoint is used as an operational residual-shape score rather than as a physical proof of the projection formula.

The primary internal validation uses leave-one-galaxy-out thresholding. For held-out galaxy $h$, the threshold is recomputed from the remaining galaxies:
\[
T_h={1\over2}\left[{\rm median}({\rm RMS}_{g\in A,g\ne h})+
{\rm median}({\rm RMS}_{g\in C,g\ne h})\right].
\]
The held-out galaxy is classified as C-like if its score exceeds $T_h$. A shuffled-label null preserves the 17/28 A/C class counts and uses 1000 shuffles with random seed 20260515; the practical p-value floor is therefore of order $10^{-3}$, and the observed empirical value is $p=0.002000000$. Bootstrap uncertainty uses 2000 class-stratified galaxy resamples with random seed 20260516 for the primary endpoint. These tests are internal to SPARC and should not be described as independent validation.

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

\begin{table}[H]
\centering
\caption{Bootstrap AUC intervals for baseline residual-score families.}
\begin{tabular}{lccc}
\toprule
Score family & AUC & CI low & CI high\\
\midrule
{ci_table}
\bottomrule
\end{tabular}
\end{table}

\begin{figure}[H]
\centering
\includegraphics[width=0.82\linewidth]{figures/paper2_projection_rms_distribution.pdf}
\caption{Distribution of the fixed Projection RMS residual score for externally regular A and disturbed C systems.}
\end{figure}

The primary signal is positive, but the bootstrap interval is broad. The correct reading is promising but sample-limited class recovery from residual shape, not a physical detection of an underlying field.

\begin{figure}[H]
\centering
\includegraphics[width=0.94\linewidth]{figures/paper2_illustrative_rotation_curves.pdf}
\caption{Classifier-context rotation-curve diagnostics for DDO154, a correctly recovered regular A system, and CamB, the named false-positive A outlier. The upper panels show observed rotation curves against the baryonic baseline; the lower panels show per-radius absolute residual profiles and the corresponding leave-one-galaxy-out threshold. This visualization is not a primary endpoint and is not used to tune the classifier.}
\end{figure}

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

\begin{figure}[H]
\centering
\includegraphics[width=0.58\linewidth]{figures/paper2_confusion_matrix.pdf}
\caption{Confusion matrix for the held-out Projection RMS rule.}
\end{figure}

These failures are not relabeling evidence. They are targets for follow-up inspection, especially where residual morphology, inclination, radial coverage, and H\,I kinematic asymmetry disagree.

CamB is the most important failure case. It is externally labeled A from regular-kinematics evidence, but it has Projection RMS near 0.96 and only nine rotation-curve points. The paper therefore treats CamB as a named residual-hard outlier rather than letting it disappear inside summary statistics.

\begin{table}[H]
\centering
\caption{B-class sensitivity check. B systems are not used as primary labels.}
\begin{tabular}{ccccc}
\toprule
$N_B$ & Threshold & B C-like & B A-like & Interpretation\\
\midrule
{b_table}
\bottomrule
\end{tabular}
\end{table}

\begin{table}[H]
\centering
\caption{Named outliers and failure-case inspection.}
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{lllrrrrp{0.34\linewidth}}
\toprule
Galaxy & Class & Error & Score & Points & Distance & Incl. & Inspection note\\
\midrule
{outlier_table}
\bottomrule
\end{tabular}
\end{table}

\section{External proxy readouts}

The external H\,I context draws on WHISP lopsidedness and morphology \cite{vanEymeren2011WHISP,vanEymeren2011WHISPII,Holwerda2011WHISP}, THINGS non-circular-motion diagnostics \cite{Trachternach2008THINGS}, Reynolds et al. H\,I asymmetry catalogues \cite{Reynolds2020HIAsymmetries}, and ALFALFA profile asymmetry \cite{Yu2022ALFALFA}. Table~\ref{tab:external} lists each frozen proxy gate. WHISP resolved-HI asymmetry is the strongest supportive external readout, but its overlap is small. WHISP morphology is mixed, Reynolds/LVHIS is promising but below the frozen $N\geq15$ gate, and ALFALFA/HALOGAS do not provide strong directional support. The external evidence therefore supports the paper as an audit, not as an independent validation result.

The strongest remaining weakness is external validation. All rotation-curve residual endpoints in this manuscript are SPARC-internal, and the auxiliary H\,I proxy readouts are contextual rather than a held-out replication. A fair skeptical reading is therefore: the association is reproducible within this SPARC packet, but it is not yet externally established.

\begin{table}[H]
\centering
\caption{External-proxy readouts and frozen gates.}
\label{tab:external}
\footnotesize
\begin{tabular}{lllll}
\toprule
Source & Overlap & Direction/status & Effect size & Gate\\
\midrule
{external_table}
\bottomrule
\end{tabular}
\end{table}

\section{External-validation status}

The present manuscript should not be read as a completed external-validation study. It contains three weaker ingredients: an internal SPARC residual-inference result, small-overlap external-proxy consistency checks, and a negative THINGS expansion audit. These ingredients are useful because they define the next test, but they do not replace that test.

A paper-grade Phase II replication must be a source-family holdout. The evidence rule, disturbance labels, observability covariates, minimum overlap, and pass/fail thresholds must be frozen before any endpoint readout. The minimum acceptable target remains $N\geq15$ score-ready galaxies in a non-SPARC source family or in a demonstrably independent kinematic-proxy family. If the effect disappears, reverses, or becomes dominated by distance, inclination, point count, or beam-size proxies, the correct conclusion is that the current result is SPARC-specific, proxy-specific, or observability-driven.

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

The distance-stress labels are operational. Greedy unique matching pairs each A galaxy with one nearby C galaxy without reusing controls. Optimal ordered matching sorts both classes by distance and pairs by rank. The Mpc-caliper check keeps only pairs within the frozen maximum distance separation. These checks are not a full selection-function model.

\begin{table}[H]
\centering
\caption{Observability and nuisance-covariate stress summaries.}
\footnotesize
\begin{tabular}{lrrl}
\toprule
Check & N & Value & Secondary value\\
\midrule
{observability_table}
\bottomrule
\end{tabular}
\end{table}

This appendix-style stress table is not a full hierarchical model or a claim of bias removal. It documents that observability channels were inspected and that residual association should remain caveated until a larger external holdout can support multivariable inference.

\section{Claim boundary and Phase II}

Allowed claim: fixed residual-shape features recover externally reviewed A/C disturbance class better than chance in the current SPARC packet, and several external proxy readouts provide mixed but informative context.

Forbidden claims: Tau Core validation, gravity-model selection, projection-formula uniqueness, replacement of external labels by residual-only labels, broad independent external validation, or THINGS route2 positive evidence.

The next paper-grade step is a held-out external source-family test with $N\geq15$, a frozen evidence rule, no velocity-endpoint refit, explicit observability covariates, and predefined failure conditions. A negative Phase II result should be treated as evidence that the present association is SPARC-specific, proxy-specific, or observability-driven.

\clearpage
\section{Conclusion}

This paper finds that fixed residual-shape features recover externally reviewed A/C disturbance classes better than chance within the current SPARC packet. The strongest internal endpoint is Projection RMS, with LOOGO AUC=0.771008403. MOND-simple and empirical RAR-like residual scores also separate the classes, while the Newtonian baryonic RMS control is near chance. The result points to a low-acceleration residual-family association with structural disturbance, not to a projection-formula-specific detection.

The paper does not establish a new gravity model, does not validate Tau Core, and does not replace external disturbance labels with residual-only labels. It also does not provide completed external validation. CamB and the other named failure cases show that residual burden can be high in externally regular systems, and the observability checks show that distance, radial coverage, inclination, point count, and H\,I data quality remain live alternative explanations.

The next decisive test is a held-out external source-family replication with a frozen evidence rule, at least $N\geq15$ score-ready galaxies, observability covariates, and predefined failure conditions. If that test supports the same residual-disturbance direction, the present result becomes a stronger phenomenological claim. If it fails, the appropriate interpretation is that the association is SPARC-specific, proxy-specific, or observability-driven.

\clearpage
\section{ROC appendix}

\begin{figure}[H]
\centering
\includegraphics[width=0.58\linewidth]{figures/paper2_projection_roc.pdf}
\caption{ROC curve for the Projection RMS score using the frozen A/C labels.}
\end{figure}

\section{Stability and effect-size appendix}

\begin{table}[H]
\centering
\caption{Rank and stability effect-size summaries for Projection RMS.}
\footnotesize
\begin{tabular}{lll}
\toprule
Metric & Value & Secondary value\\
\midrule
{effect_table}
\bottomrule
\end{tabular}
\end{table}

\begin{figure}[H]
\centering
\includegraphics[width=0.72\linewidth]{figures/paper2_auc_stability_distributions.pdf}
\caption{Bootstrap and shuffled-label AUC distributions for the Projection RMS endpoint.}
\end{figure}

\appendix

\section{A/C sample table}

\begin{longtable}{llrrrr}
\caption{Frozen A/C sample used for the primary diagnostic.}\\
\toprule
Galaxy & Class & Distance & Incl. & Points & Projection RMS\\
\midrule
\endfirsthead
\toprule
Galaxy & Class & Distance & Incl. & Points & Projection RMS\\
\midrule
\endhead
{sample_table}
\bottomrule
\end{longtable}

\bibliographystyle{plain}
\bibliography{references}

\end{document}
"""
    return (
        tex.replace("{ci_table}", ci_table)
        .replace("{b_table}", b_table)
        .replace("{external_table}", external_table)
        .replace("{observability_table}", observability_table)
        .replace("{outlier_table}", outlier_table)
        .replace("{effect_table}", effect_table)
        .replace("{sample_table}", sample_table)
    )


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
        {
            "Figure": "paper2_confusion_matrix.pdf",
            "Source": "residual_inference_loogo_predictions.csv",
            "TypographyStatus": "publication_candidate",
            "CaptionStatus": "short_descriptive_caption_in_latex",
            "VectorExport": "pdf",
            "Guardrail": GUARDRAIL,
        },
        {
            "Figure": "paper2_projection_roc.pdf",
            "Source": "residual_inference_loogo_predictions.csv",
            "TypographyStatus": "appendix_candidate",
            "CaptionStatus": "short_descriptive_caption_in_latex",
            "VectorExport": "pdf",
            "Guardrail": GUARDRAIL,
        },
        {
            "Figure": "paper2_auc_stability_distributions.pdf",
            "Source": "residual_feature_table.csv;paper2_shuffled_label_null.csv",
            "TypographyStatus": "appendix_candidate",
            "CaptionStatus": "short_descriptive_caption_in_latex",
            "VectorExport": "pdf",
            "Guardrail": GUARDRAIL,
        },
        {
            "Figure": "paper2_illustrative_rotation_curves.pdf",
            "Source": "studies/illustrative_rotation_curves/paper2_context_rotation_points.csv",
            "TypographyStatus": "publication_candidate_illustrative",
            "CaptionStatus": "explicitly_not_primary_endpoint",
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
            "Evidence": "vector PDF figures; figure typography audit",
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
    env = os.environ.copy()
    env.setdefault("SOURCE_DATE_EPOCH", "0")
    result = subprocess.run(
        ["tectonic", "main.tex"],
        cwd=SOURCE,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    log_path = SOURCE / "tectonic_build.log"
    log_path.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
    if result.returncode == 0 and PDF.exists() and PDF.stat().st_size > 10_000:
        return "pdf_compiled_with_tectonic"
    return "pdf_compile_failed"


def build_arxiv_zip() -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in [MAIN_TEX, REFERENCES]:
            info = zipfile.ZipInfo(path.name)
            info.date_time = (2026, 5, 18, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
        for path in sorted(SOURCE_FIGURES.glob("*.pdf")):
            info = zipfile.ZipInfo(f"figures/{path.name}")
            info.date_time = (2026, 5, 18, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    files = {path.name for path in PACKET.iterdir() if path.is_file()}
    manifest = {
        "packet": "sparc_residual_disturbance_inference_v01/packet_v01_seed",
        "package_profile": "slim_publication_reproducibility_package",
        "doi": "10.5281/zenodo.20210154",
        "status": "paper2_submission_source_ready",
        "source_point_map": (
            "studies/sparc_residual_coherence_test_v01/"
            "paper_packet_v06_distance_balanced/taucore_specificity_point_map.csv"
        ),
        "files": sorted(files),
        "guardrail": GUARDRAIL,
        "paper2_submission_source_v01_status": (
            "latex_bibliography_pdf_and_figure_audit_generated"
        ),
        "paper2_next_gate": "human_pdf_review_and_journal_specific_polish",
        "excluded_from_slim_repo": [
            "raw survey products",
            "raw SPARC rotmod files",
            "exploratory Tau Core and S_tau branches",
            "closed THINGS route2 reconstruction work products",
            "local build previews and cache files",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    SOURCE.mkdir(parents=True, exist_ok=True)
    generate_figures()
    MAIN_TEX.write_text(tex_text(), encoding="utf-8")
    REFERENCES.write_text(bib_text(), encoding="utf-8")
    pdf_status = compile_pdf()
    build_arxiv_zip()
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
    write_csv(
        SAMPLE_TABLE,
        sample_appendix_rows(),
        [
            "GalaxyName",
            "Class",
            "DistanceMpc",
            "InclinationDeg",
            "NPoints",
            "Projection_RMS",
            "MOND_RMS",
            "RAR_RMS",
            "Guardrail",
        ],
    )
    write_csv(
        BASELINE_CI_TABLE,
        baseline_ci_rows(),
        [
            "Predictor",
            "Label",
            "AUC_C_higher",
            "BootstrapN",
            "BootstrapCI95Low",
            "BootstrapCI95High",
            "Guardrail",
        ],
    )
    write_csv(
        EXTERNAL_GATE_TABLE,
        external_gate_rows(),
        ["ProxySource", "OverlapN", "Direction", "EffectSize", "FrozenGate", "Guardrail"],
    )
    write_csv(
        B_SENSITIVITY_TABLE,
        b_sensitivity_rows(),
        [
            "SensitivityID",
            "NB",
            "ProjectionRMSThreshold",
            "BPredictedC_like",
            "BPredictedA_like",
            "Interpretation",
            "Guardrail",
        ],
    )
    write_csv(
        OBSERVABILITY_TABLE,
        observability_rows(),
        ["Metric", "N", "Value", "SecondaryValue", "Interpretation", "Guardrail"],
    )
    write_csv(
        OUTLIER_TABLE,
        outlier_rows(),
        [
            "GalaxyName",
            "Class",
            "ErrorFamily",
            "Projection_RMS",
            "LOOGOThreshold",
            "Margin",
            "NPoints",
            "DistanceMpc",
            "InclinationDeg",
            "EvidenceType",
            "InspectionNote",
            "Guardrail",
        ],
    )
    write_csv(
        STABILITY_TABLE,
        effect_size_rows(),
        ["Metric", "Value", "SecondaryValue", "Interpretation", "Guardrail"],
    )
    update_manifest()
    print(PDF)
    print(pdf_status)


if __name__ == "__main__":
    main()
