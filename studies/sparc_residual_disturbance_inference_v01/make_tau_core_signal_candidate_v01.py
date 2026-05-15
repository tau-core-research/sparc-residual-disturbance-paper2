#!/usr/bin/env python3
"""Summarize the TPG residual as a Tau Core signal-candidate carrier."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET


DRIFT = PACKET / "integrated_tau_drift_galaxy_summary_v01.csv"
HISTORY = PACKET / "history_s_tau_velocity_galaxy_summary.csv"
FEATURES = PACKET / "residual_feature_table.csv"
SIGNAL_OUT = PACKET / "tau_core_signal_candidate_galaxy_summary_v01.csv"
RELATION_OUT = PACKET / "tau_core_signal_candidate_relation_summary_v01.csv"
REPORT = PACKET / "tau_core_signal_candidate_v01.md"

GUARDRAIL = "tau_core_signal_candidate_not_attribution_or_proof"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.9f}"


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def median(values: list[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    n = len(ordered)
    if n % 2:
        return ordered[n // 2]
    return (ordered[n // 2 - 1] + ordered[n // 2]) / 2


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return math.nan
    mx = mean(xs)
    my = mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denom = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    if denom == 0:
        return math.nan
    return sum(x * y for x, y in zip(dx, dy)) / denom


def fractional_ranks(values: list[float]) -> list[float]:
    if len(values) <= 1:
        return [0.0 for _ in values]
    pairs = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0 for _ in values]
    for rank, (_, index) in enumerate(pairs):
        ranks[index] = rank / (len(values) - 1)
    return ranks


def auc_c_higher(rows: list[dict[str, str]], field: str) -> float:
    positives = [float(row[field]) for row in rows if row["Class"] == "C" and row[field] != ""]
    negatives = [float(row[field]) for row in rows if row["Class"] == "A" and row[field] != ""]
    if not positives or not negatives:
        return math.nan
    wins = 0.0
    total = 0
    for pos in positives:
        for neg in negatives:
            total += 1
            if pos > neg:
                wins += 1
            elif pos == neg:
                wins += 0.5
    return wins / total


def indexed(path: Path) -> dict[str, dict[str, str]]:
    return {row["GalaxyName"]: row for row in read_csv(path)}


def signal_rows() -> list[dict[str, str]]:
    drift = indexed(DRIFT)
    history = indexed(HISTORY)
    features = indexed(FEATURES)
    rows: list[dict[str, str]] = []
    galaxies = sorted(set(drift) & set(history) & set(features))
    components = {
        "AbsFinalMeanSignedResidual": [float(drift[g]["AbsFinalMeanSignedResidual"]) for g in galaxies],
        "MaxAbsCumulativeMeanResidual": [
            float(drift[g]["MaxAbsCumulativeMeanResidual"]) for g in galaxies
        ],
        "SignImbalance": [float(drift[g]["SignImbalance"]) for g in galaxies],
        "MaxSameSignRunFraction": [float(drift[g]["MaxSameSignRunFraction"]) for g in galaxies],
        "HistoryImprovement": [-float(history[g]["DeltaRMS_HistoryMinusS1"]) for g in galaxies],
    }
    ranks = {name: fractional_ranks(values) for name, values in components.items()}
    for index, galaxy in enumerate(galaxies):
        signal_score = mean([ranks[name][index] for name in sorted(ranks)])
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": drift[galaxy]["Class"],
                "Projection_RMS": features[galaxy]["Projection_RMS"],
                "AbsFinalMeanSignedResidual": drift[galaxy]["AbsFinalMeanSignedResidual"],
                "MaxAbsCumulativeMeanResidual": drift[galaxy]["MaxAbsCumulativeMeanResidual"],
                "SignImbalance": drift[galaxy]["SignImbalance"],
                "MaxSameSignRunFraction": drift[galaxy]["MaxSameSignRunFraction"],
                "HistoryDeltaRMS_HistoryMinusS1": history[galaxy]["DeltaRMS_HistoryMinusS1"],
                "HistoryImprovement_PositiveIsBetter": fmt(
                    -float(history[galaxy]["DeltaRMS_HistoryMinusS1"])
                ),
                "Median_S_tau_eff_clipped": drift[galaxy]["Median_S_tau_eff_clipped"],
                "TauCoreSignalCandidateScore_v01": fmt(signal_score),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def relation_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    pairs = [
        ("Projection_RMS", "TauCoreSignalCandidateScore_v01"),
        ("AbsFinalMeanSignedResidual", "TauCoreSignalCandidateScore_v01"),
        ("MaxAbsCumulativeMeanResidual", "TauCoreSignalCandidateScore_v01"),
        ("SignImbalance", "TauCoreSignalCandidateScore_v01"),
        ("MaxSameSignRunFraction", "TauCoreSignalCandidateScore_v01"),
        ("HistoryImprovement_PositiveIsBetter", "TauCoreSignalCandidateScore_v01"),
        ("Median_S_tau_eff_clipped", "TauCoreSignalCandidateScore_v01"),
        ("Projection_RMS", "HistoryImprovement_PositiveIsBetter"),
        ("AbsFinalMeanSignedResidual", "HistoryImprovement_PositiveIsBetter"),
        ("SignImbalance", "HistoryImprovement_PositiveIsBetter"),
    ]
    output: list[dict[str, str]] = []
    for left, right in pairs:
        xs = [float(row[left]) for row in rows if row[left] != "" and row[right] != ""]
        ys = [float(row[right]) for row in rows if row[left] != "" and row[right] != ""]
        output.append(
            {
                "Relation": f"{left}__vs__{right}",
                "N": str(len(xs)),
                "Pearson": fmt(pearson(xs, ys)),
                "LeftMedian_A": fmt(median([float(row[left]) for row in rows if row["Class"] == "A"])),
                "LeftMedian_C": fmt(median([float(row[left]) for row in rows if row["Class"] == "C"])),
                "LeftAUC_C_higher": fmt(auc_c_higher(rows, left)),
                "RightAUC_C_higher": fmt(auc_c_higher(rows, right)),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return output


def write_report(rows: list[dict[str, str]], relations: list[dict[str, str]]) -> None:
    rel = {row["Relation"]: row for row in relations}
    score_auc = auc_c_higher(rows, "TauCoreSignalCandidateScore_v01")
    history_auc = auc_c_higher(rows, "HistoryImprovement_PositiveIsBetter")
    projection_auc = auc_c_higher(rows, "Projection_RMS")
    a_score = median(
        [float(row["TauCoreSignalCandidateScore_v01"]) for row in rows if row["Class"] == "A"]
    )
    c_score = median(
        [float(row["TauCoreSignalCandidateScore_v01"]) for row in rows if row["Class"] == "C"]
    )
    lines = [
        "# Tau Core Environment/Observer Weight Candidate v0.1",
        "",
        "This packet formalizes the working hypothesis that the TPG prescription already carries the local Tau Core weights captured by the fixed projection baseline, while the remaining TPG residual is a candidate carrier of environment- and observer-dependent Tau Core weights. It does not identify the residual itself with Tau Core. The residual can also contain ordinary observational, baryonic, and non-circular-motion systematics.",
        "",
        "## Operational Definition",
        "",
        "`TauCoreSignalCandidateScore_v01` is the mean rank of five diagnostics designed to isolate the non-local part left after the TPG local-weight baseline: final signed drift, maximum cumulative drift, sign imbalance, same-sign run fraction, and the improvement obtained by the causal inner-history readout.",
        "",
        "## Main Readout",
        "",
        f"- Galaxies: {len(rows)}",
        f"- Median candidate score, A: {fmt(a_score)}",
        f"- Median candidate score, C: {fmt(c_score)}",
        f"- AUC(C higher), candidate score: {fmt(score_auc)}",
        f"- AUC(C higher), projection RMS: {fmt(projection_auc)}",
        f"- AUC(C higher), history improvement: {fmt(history_auc)}",
        f"- Pearson(projection RMS, candidate score): {rel['Projection_RMS__vs__TauCoreSignalCandidateScore_v01']['Pearson']}",
        f"- Pearson(abs final signed drift, history improvement): {rel['AbsFinalMeanSignedResidual__vs__HistoryImprovement_PositiveIsBetter']['Pearson']}",
        "",
        "## Interpretation",
        "",
        "The residual difference is a plausible carrier of missing environment/observer weights because its signed, cumulative, and history-dependent features are structured rather than random. However, the current evidence supports only a Tau Core weight-candidate framing. Attribution requires external source-side predictors or controls that can explain why this residual structure is not merely disturbance, observability, inclination, beam smearing, or baryonic-model error.",
        "",
        "## Consequence For The Model",
        "",
        "The next useful Tau Core expression should separate local weights already approximated by TPG from environment/observer-dependent weights left in the residual. The current results favor an integrated state variable: a term whose value at radius `R` depends on accumulated inner geometry, environment, viewing geometry, or coherence history.",
        "",
        "## Generated Files",
        "",
        "- `tau_core_signal_candidate_galaxy_summary_v01.csv`",
        "- `tau_core_signal_candidate_relation_summary_v01.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "tau_core_signal_candidate_v01.md",
            "tau_core_signal_candidate_galaxy_summary_v01.csv",
            "tau_core_signal_candidate_relation_summary_v01.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["tau_core_signal_candidate_status"] = "residual_signal_candidate_framing_complete"
    manifest["paper2_next_gate"] = "source_side_proxy_or_systematics_controls_for_tau_core_signal_candidate"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = signal_rows()
    relations = relation_rows(rows)
    write_csv(
        SIGNAL_OUT,
        rows,
        [
            "GalaxyName",
            "Class",
            "Projection_RMS",
            "AbsFinalMeanSignedResidual",
            "MaxAbsCumulativeMeanResidual",
            "SignImbalance",
            "MaxSameSignRunFraction",
            "HistoryDeltaRMS_HistoryMinusS1",
            "HistoryImprovement_PositiveIsBetter",
            "Median_S_tau_eff_clipped",
            "TauCoreSignalCandidateScore_v01",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        RELATION_OUT,
        relations,
        [
            "Relation",
            "N",
            "Pearson",
            "LeftMedian_A",
            "LeftMedian_C",
            "LeftAUC_C_higher",
            "RightAUC_C_higher",
            "InterpretationGuardrail",
        ],
    )
    write_report(rows, relations)
    update_manifest()
    print(REPORT)
    print(f"tau_core_signal_candidate_galaxies={len(rows)}")


if __name__ == "__main__":
    main()
