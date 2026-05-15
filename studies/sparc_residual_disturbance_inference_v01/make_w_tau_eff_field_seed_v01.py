#!/usr/bin/env python3
"""Close the residual-weight branch with a W_tau_eff field seed table."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET


SIGNAL = PACKET / "tau_core_signal_candidate_galaxy_summary_v01.csv"
DRIFT = PACKET / "integrated_tau_drift_galaxy_summary_v01.csv"
HISTORY = PACKET / "history_s_tau_velocity_galaxy_summary.csv"
FIELD_OUT = PACKET / "w_tau_eff_field_seed_v01.csv"
SUMMARY_OUT = PACKET / "w_tau_eff_field_seed_summary_v01.csv"
REPORT = PACKET / "w_tau_eff_field_seed_v01.md"

GUARDRAIL = "w_tau_eff_residual_inferred_seed_not_tau_core_field_map"


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


def indexed(path: Path) -> dict[str, dict[str, str]]:
    return {row["GalaxyName"]: row for row in read_csv(path)}


def confidence_tier(score: float, history_improvement: float, drift_abs: float) -> str:
    if score >= 0.70 and history_improvement > 0 and drift_abs >= 0.15:
        return "high_candidate"
    if score >= 0.45 and history_improvement > 0:
        return "medium_candidate"
    return "low_or_control_candidate"


def field_rows() -> list[dict[str, str]]:
    signal = indexed(SIGNAL)
    drift = indexed(DRIFT)
    history = indexed(HISTORY)
    rows: list[dict[str, str]] = []
    for galaxy in sorted(set(signal) & set(drift) & set(history)):
        signed = float(drift[galaxy]["FinalMeanSignedResidual"])
        abs_signed = abs(signed)
        score = float(signal[galaxy]["TauCoreSignalCandidateScore_v01"])
        history_improvement = float(signal[galaxy]["HistoryImprovement_PositiveIsBetter"])
        rows.append(
            {
                "GalaxyName": galaxy,
                "Class": signal[galaxy]["Class"],
                "W_tau_eff_signed_v01": fmt(signed),
                "W_tau_eff_abs_v01": fmt(abs_signed),
                "W_tau_eff_candidate_score_v01": fmt(score),
                "HistoryImprovement_PositiveIsBetter": fmt(history_improvement),
                "MaxAbsCumulativeMeanResidual": drift[galaxy]["MaxAbsCumulativeMeanResidual"],
                "SignImbalance": drift[galaxy]["SignImbalance"],
                "MaxSameSignRunFraction": drift[galaxy]["MaxSameSignRunFraction"],
                "FirstBreakRadiusFraction_abs0p15": drift[galaxy]["FirstBreakRadiusFraction_abs0p15"],
                "Median_S_tau_eff_clipped": drift[galaxy]["Median_S_tau_eff_clipped"],
                "MapReadiness": "needs_ra_dec_distance_environment_join",
                "CandidateConfidenceTier": confidence_tier(score, history_improvement, abs_signed),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def summary_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for group in ["all", "A", "C"]:
        subset = rows if group == "all" else [row for row in rows if row["Class"] == group]
        scores = [float(row["W_tau_eff_candidate_score_v01"]) for row in subset]
        signed = [float(row["W_tau_eff_signed_v01"]) for row in subset]
        abs_values = [float(row["W_tau_eff_abs_v01"]) for row in subset]
        output.append(
            {
                "Group": group,
                "NGalaxies": str(len(subset)),
                "Median_W_tau_eff_candidate_score_v01": fmt(median(scores)),
                "Mean_W_tau_eff_candidate_score_v01": fmt(mean(scores)),
                "Median_W_tau_eff_signed_v01": fmt(median(signed)),
                "Median_W_tau_eff_abs_v01": fmt(median(abs_values)),
                "NHighCandidate": str(
                    sum(row["CandidateConfidenceTier"] == "high_candidate" for row in subset)
                ),
                "NMediumCandidate": str(
                    sum(row["CandidateConfidenceTier"] == "medium_candidate" for row in subset)
                ),
                "NLowOrControlCandidate": str(
                    sum(row["CandidateConfidenceTier"] == "low_or_control_candidate" for row in subset)
                ),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return output


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    by_group = {row["Group"]: row for row in summary}
    lines = [
        "# W_tau_eff Field Seed v0.1",
        "",
        "This closing packet defines a map-ready residual-inferred effective tau-weight seed. It is the bridge from the residual/history branch to later sky or distance mapping.",
        "",
        "## Definition",
        "",
        "The working decomposition is:",
        "",
        "- `TPG`: effective baseline carrying local Tau Core weights.",
        "- `W_tau_eff`: residual-inferred candidate for the missing environment- and observer-dependent Tau Core weights.",
        "",
        "`W_tau_eff_signed_v01` is the final mean signed TPG log residual. `W_tau_eff_candidate_score_v01` is the previously defined rank-composite score using signed drift, cumulative drift, sign persistence, and history-rule improvement.",
        "",
        "## Main Summary",
        "",
        f"- Galaxies: {by_group['all']['NGalaxies']}",
        f"- Median candidate score, all: {by_group['all']['Median_W_tau_eff_candidate_score_v01']}",
        f"- Median candidate score, A: {by_group['A']['Median_W_tau_eff_candidate_score_v01']}",
        f"- Median candidate score, C: {by_group['C']['Median_W_tau_eff_candidate_score_v01']}",
        f"- High-candidate galaxies, all/A/C: {by_group['all']['NHighCandidate']} / {by_group['A']['NHighCandidate']} / {by_group['C']['NHighCandidate']}",
        "",
        "## Not A Map Yet",
        "",
        "This packet intentionally does not claim a Tau Core field map. The public packet does not yet include the sky-position, distance, and environment columns required for mapping. The next stage must join RA, Dec, distance, distance uncertainty, and environment/LSS proxies before testing angular or radial structure.",
        "",
        "## Required Next Inputs",
        "",
        "- RA and Dec",
        "- distance and distance uncertainty",
        "- inclination/systematics controls",
        "- environment or large-scale-structure proxy",
        "- source-family provenance for held-out validation",
        "",
        "## Generated Files",
        "",
        "- `w_tau_eff_field_seed_v01.csv`",
        "- `w_tau_eff_field_seed_summary_v01.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "w_tau_eff_field_seed_v01.md",
            "w_tau_eff_field_seed_v01.csv",
            "w_tau_eff_field_seed_summary_v01.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["w_tau_eff_field_seed_status"] = "residual_inferred_effective_weight_seed_complete"
    manifest["paper2_next_gate"] = "join_coordinates_distances_environment_for_w_tau_eff_mapping"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = field_rows()
    summary = summary_rows(rows)
    write_csv(
        FIELD_OUT,
        rows,
        [
            "GalaxyName",
            "Class",
            "W_tau_eff_signed_v01",
            "W_tau_eff_abs_v01",
            "W_tau_eff_candidate_score_v01",
            "HistoryImprovement_PositiveIsBetter",
            "MaxAbsCumulativeMeanResidual",
            "SignImbalance",
            "MaxSameSignRunFraction",
            "FirstBreakRadiusFraction_abs0p15",
            "Median_S_tau_eff_clipped",
            "MapReadiness",
            "CandidateConfidenceTier",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        SUMMARY_OUT,
        summary,
        [
            "Group",
            "NGalaxies",
            "Median_W_tau_eff_candidate_score_v01",
            "Mean_W_tau_eff_candidate_score_v01",
            "Median_W_tau_eff_signed_v01",
            "Median_W_tau_eff_abs_v01",
            "NHighCandidate",
            "NMediumCandidate",
            "NLowOrControlCandidate",
            "InterpretationGuardrail",
        ],
    )
    write_report(rows, summary)
    update_manifest()
    print(REPORT)
    print(f"w_tau_eff_field_seed_galaxies={len(rows)}")


if __name__ == "__main__":
    main()
