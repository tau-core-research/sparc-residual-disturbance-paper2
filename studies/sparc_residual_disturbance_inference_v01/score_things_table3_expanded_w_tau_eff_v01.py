#!/usr/bin/env python3
"""Expand THINGS Table 3 W_tau_eff scores using frozen calibration."""

from __future__ import annotations

import json
from pathlib import Path

from make_packet_v01_seed import PACKET, ROOT, read_csv, write_csv
from score_yu2022_alfalfa_expanded_w_tau_eff_v01 import (
    GUARDRAIL as SCORE_GUARDRAIL,
    add_candidate_score,
    candidate_components,
    frozen_calibration,
)


TABLE3 = PACKET / "things_trachternach2008_table3_v01.csv"
W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
EXPANDED_YU = PACKET / "yu2022_alfalfa_expanded_w_tau_eff_scores_v01.csv"
ROTMOD_DIR = Path("/Users/jolcsak/Projects/tau-core/data/sparc/Rotmod_LTG")

POINT_OUT = PACKET / "things_table3_expanded_w_tau_eff_point_trace_v01.csv"
SCORE_OUT = PACKET / "things_table3_expanded_w_tau_eff_scores_v01.csv"
SUMMARY_OUT = PACKET / "things_table3_expanded_w_tau_eff_summary_v01.csv"
DECISION_OUT = PACKET / "things_table3_expanded_w_tau_eff_decision_v01.csv"
REPORT = PACKET / "things_table3_expanded_w_tau_eff_v01.md"

GUARDRAIL = "things_table3_expanded_w_tau_eff_no_endpoint_refit"
MIN_VALID_POINTS = 8


def score_index() -> dict[str, dict[str, str]]:
    scores: dict[str, dict[str, str]] = {}
    for row in read_csv(W_TAU):
        scores[row["GalaxyName"]] = {
            "GalaxyName": row["GalaxyName"],
            "ScoreSource": "frozen_original_w_tau_eff_seed",
            "ScoringStatus": "existing_score_retained",
            "NPoints": "",
            "W_tau_eff_score_resolved_v01": row["W_tau_eff_candidate_score_v01"],
            "W_tau_eff_abs_v01": row["W_tau_eff_abs_v01"],
            "W_tau_eff_signed_v01": row["W_tau_eff_signed_v01"],
            "CandidateConfidenceTier": row["CandidateConfidenceTier"],
        }
    for row in read_csv(EXPANDED_YU):
        if row["W_tau_eff_readout_score_v01"] == "":
            continue
        scores.setdefault(
            row["GalaxyName"],
            {
                "GalaxyName": row["GalaxyName"],
                "ScoreSource": row["ScoreSource"],
                "ScoringStatus": "existing_expanded_score_retained",
                "NPoints": row["NPoints"],
                "W_tau_eff_score_resolved_v01": row["W_tau_eff_readout_score_v01"],
                "W_tau_eff_abs_v01": row["W_tau_eff_abs_v01"],
                "W_tau_eff_signed_v01": row["W_tau_eff_signed_v01"],
                "CandidateConfidenceTier": row["CandidateConfidenceTier"],
            },
        )
    return scores


def table3_rows() -> list[dict[str, str]]:
    return read_csv(TABLE3)


def score_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    existing = score_index()
    calibration = frozen_calibration()
    scores: list[dict[str, str]] = []
    points: list[dict[str, str]] = []
    for row in table3_rows():
        galaxy = row["GalaxyName"]
        rotmod_path = ROTMOD_DIR / f"{galaxy}_rotmod.dat"
        base = {
            "GalaxyName": galaxy,
            "PublishedName": row["PublishedName"],
            "MedianNonCircularAmplitudeKms": row["MedianNonCircularAmplitudeKms"],
            "NonCircularAmplitudeOverVmaxPercent": row["NonCircularAmplitudeOverVmaxPercent"],
            "MedianAbsResidualVelocityAfterHarmonicKms": row[
                "MedianAbsResidualVelocityAfterHarmonicKms"
            ],
            "HasLocalSparcRotmod": "yes" if rotmod_path.exists() else "no",
            "LocalRotmodPath": str(rotmod_path) if rotmod_path.exists() else "",
            "InterpretationGuardrail": GUARDRAIL,
        }
        if galaxy in existing:
            scores.append({**base, **existing[galaxy]})
            continue
        if not rotmod_path.exists():
            scores.append(
                {
                    **base,
                    "ScoreSource": "not_scored_no_local_sparc_rotmod",
                    "ScoringStatus": "excluded_no_rotmod",
                    "NPoints": "0",
                    "W_tau_eff_score_resolved_v01": "",
                    "W_tau_eff_abs_v01": "",
                    "W_tau_eff_signed_v01": "",
                    "CandidateConfidenceTier": "not_scored",
                }
            )
            continue
        pseudo_queue = {
            "CanonicalSPARCNameCandidate": galaxy,
            "AGC": "",
            "FreezeRole": "things_table3_predeclared_expansion_candidate",
            "LocalRotmodPath": str(rotmod_path),
        }
        point_rows, component = candidate_components(pseudo_queue)
        points.extend(point_rows)
        n_points = int(component["NPoints"])
        if component["ScoringStatus"] != "scored" or n_points < MIN_VALID_POINTS:
            scores.append(
                {
                    **base,
                    "ScoreSource": "not_scored_minimum_radial_points_not_met",
                    "ScoringStatus": "excluded_minimum_points",
                    "NPoints": str(n_points),
                    "W_tau_eff_score_resolved_v01": "",
                    "W_tau_eff_abs_v01": "",
                    "W_tau_eff_signed_v01": "",
                    "CandidateConfidenceTier": "not_scored",
                }
            )
            continue
        component["FreezeRole"] = "things_table3_predeclared_expansion_candidate"
        scored = add_candidate_score(component, calibration)
        scores.append(
            {
                **base,
                "ScoreSource": "expanded_things_table3_rotmod_scoring_frozen_w_tau_eff_calibration",
                "ScoringStatus": "newly_scored_from_rotmod",
                "NPoints": scored["NPoints"],
                "W_tau_eff_score_resolved_v01": scored["W_tau_eff_readout_score_v01"],
                "W_tau_eff_abs_v01": scored["W_tau_eff_abs_v01"],
                "W_tau_eff_signed_v01": scored["W_tau_eff_signed_v01"],
                "CandidateConfidenceTier": scored["CandidateConfidenceTier"],
            }
        )
    return points, scores


def summary_rows(scores: list[dict[str, str]]) -> list[dict[str, str]]:
    counts: dict[str, int] = {}
    for row in scores:
        counts[row["ScoringStatus"]] = counts.get(row["ScoringStatus"], 0) + 1
    usable = [row for row in scores if row["W_tau_eff_score_resolved_v01"] != ""]
    return [
        {
            "Metric": "things_table3_total_rows",
            "Value": str(len(scores)),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "things_table3_resolved_w_tau_eff_rows",
            "Value": str(len(usable)),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "newly_scored_from_rotmod",
            "Value": str(counts.get("newly_scored_from_rotmod", 0)),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "excluded_no_rotmod",
            "Value": str(counts.get("excluded_no_rotmod", 0)),
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def decision_rows(scores: list[dict[str, str]]) -> list[dict[str, str]]:
    usable = [row for row in scores if row["W_tau_eff_score_resolved_v01"] != ""]
    return [
        {
            "DecisionID": "T3X01",
            "Decision": "expanded_THINGS_score_coverage",
            "Status": "expanded_but_still_below_N15" if len(usable) < 15 else "N15_met",
            "N": str(len(usable)),
            "Evidence": "all THINGS Table 3 rows with local SPARC rotmods and N>=8 were scored",
            "NextAction": "run_expanded_THINGS_control_readout",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "T3X02",
            "Decision": "endpoint_boundary",
            "Status": "no_refit_no_velocity_formula",
            "N": str(len(usable)),
            "Evidence": "scores use the frozen original W_tau_eff component calibration",
            "NextAction": "use_as_external_control_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(summary: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row["Value"] for row in summary}
    lines = [
        "# THINGS Table 3 Expanded W_tau_eff Scores v0.1",
        "",
        "This packet expands THINGS Table 3 control coverage by scoring every published Table 3 galaxy that has a local SPARC rotmod and at least eight valid radial points. Existing original or Yu-expanded scores are retained without refit.",
        "",
        "## Summary",
        "",
        f"- THINGS Table 3 rows: {lookup['things_table3_total_rows']}",
        f"- Resolved W_tau_eff rows: {lookup['things_table3_resolved_w_tau_eff_rows']}",
        f"- Newly scored from rotmod: {lookup['newly_scored_from_rotmod']}",
        f"- Excluded without local rotmod: {lookup['excluded_no_rotmod']}",
        f"- Coverage decision: {decisions[0]['Status']}",
        "",
        "## Boundary",
        "",
        "This is a control expansion only. It does not refit `W_tau_eff`, does not use THINGS metrics to tune the score, and does not open a velocity endpoint.",
        "",
        "## Generated Files",
        "",
        "- `things_table3_expanded_w_tau_eff_point_trace_v01.csv`",
        "- `things_table3_expanded_w_tau_eff_scores_v01.csv`",
        "- `things_table3_expanded_w_tau_eff_summary_v01.csv`",
        "- `things_table3_expanded_w_tau_eff_decision_v01.csv`",
        "",
        "## Guardrail",
        "",
        f"`{GUARDRAIL}`",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [POINT_OUT, SCORE_OUT, SUMMARY_OUT, DECISION_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_table3_expanded_w_tau_eff_status"] = (
        "expanded_to_all_local_rotmod_THINGS_rows_below_N15"
    )
    manifest["paper2_next_gate"] = "expanded_THINGS_control_readout"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    points, scores = score_rows()
    summary = summary_rows(scores)
    decisions = decision_rows(scores)
    write_csv(
        POINT_OUT,
        points,
        [
            "GalaxyName",
            "AGC",
            "FreezeRole",
            "PointIndex",
            "RadiusKpc",
            "RadiusFraction",
            "aN_over_a0",
            "VobsKms",
            "VbarKms",
            "LogKernelAlphaLn",
            "SignedLogResidual_TPG",
            "CumulativeMeanSignedResidual",
            "HistoryStatePriorMeanSignedResidual",
            "Predicted_S_tau_history_v01",
            "SignedLogResidual_HistoryRule",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        SCORE_OUT,
        scores,
        [
            "GalaxyName",
            "PublishedName",
            "MedianNonCircularAmplitudeKms",
            "NonCircularAmplitudeOverVmaxPercent",
            "MedianAbsResidualVelocityAfterHarmonicKms",
            "HasLocalSparcRotmod",
            "LocalRotmodPath",
            "ScoreSource",
            "ScoringStatus",
            "NPoints",
            "W_tau_eff_score_resolved_v01",
            "W_tau_eff_abs_v01",
            "W_tau_eff_signed_v01",
            "CandidateConfidenceTier",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        SUMMARY_OUT,
        summary,
        ["Metric", "Value", "InterpretationGuardrail"],
    )
    write_csv(
        DECISION_OUT,
        decisions,
        [
            "DecisionID",
            "Decision",
            "Status",
            "N",
            "Evidence",
            "NextAction",
            "InterpretationGuardrail",
        ],
    )
    write_report(summary, decisions)
    update_manifest()
    print(REPORT)
    print(f"things_expanded_resolved_rows={decisions[0]['N']}")
    print(f"things_expanded_status={decisions[0]['Status']}")


if __name__ == "__main__":
    main()
