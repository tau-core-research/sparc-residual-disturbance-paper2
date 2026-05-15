#!/usr/bin/env python3
"""Score the frozen Yu et al. 2022 ALFALFA W_tau_eff expansion candidates.

The directional Af/Ac readout is intentionally not computed here. Existing
W_tau_eff seed overlaps are retained as anchors and are not refit.
"""

from __future__ import annotations

import bisect
import csv
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv
from make_w_tau_eff_field_seed_v01 import confidence_tier


QUEUE = PACKET / "yu2022_alfalfa_seed_expansion_queue_v01.csv"
FIELD_SEED = PACKET / "w_tau_eff_field_seed_v01.csv"
DRIFT = PACKET / "integrated_tau_drift_galaxy_summary_v01.csv"
HISTORY = PACKET / "history_s_tau_velocity_galaxy_summary.csv"

POINT_OUT = PACKET / "yu2022_alfalfa_expanded_w_tau_eff_point_trace_v01.csv"
SCORE_OUT = PACKET / "yu2022_alfalfa_expanded_w_tau_eff_scores_v01.csv"
SUMMARY_OUT = PACKET / "yu2022_alfalfa_expanded_w_tau_eff_summary_v01.csv"
DECISION_OUT = PACKET / "yu2022_alfalfa_expanded_w_tau_eff_decision_v01.csv"
REPORT = PACKET / "yu2022_alfalfa_expanded_w_tau_eff_scoring_v01.md"

GUARDRAIL = "yu2022_alfalfa_expanded_scoring_no_af_ac_directional_readout"
MIN_VALID_POINTS = 8
ALPHA = 0.360
UDISK = 0.5
UBUL = 0.7
A0_M_S2 = 1.2e-10
KPC_M = 3.0856775814913673e19
HISTORY_GAIN = 0.50
HISTORY_LOW = 0.50
HISTORY_HIGH = 1.50
BREAK_THRESHOLD = 0.15


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


def rms(values: list[float]) -> float:
    return math.sqrt(mean([value * value for value in values])) if values else math.nan


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


def signed_square(value: float) -> float:
    return value * abs(value)


def parse_rotmod(path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        radius = float(parts[0])
        vobs = float(parts[1])
        vgas = float(parts[3])
        vdisk = float(parts[4])
        vbul = float(parts[5])
        vbar2 = signed_square(vgas) + UDISK * vdisk * vdisk + UBUL * vbul * vbul
        if radius <= 0 or vobs <= 0 or vbar2 <= 0:
            continue
        a_n = vbar2 * 1.0e6 / (radius * KPC_M)
        a_n_over_a0 = a_n / A0_M_S2
        if a_n_over_a0 <= 0:
            continue
        kernel = ALPHA * math.log1p(1.0 / a_n_over_a0)
        model = math.sqrt(vbar2) * (1.0 + kernel)
        if model <= 0 or not math.isfinite(kernel):
            continue
        rows.append(
            {
                "RadiusKpc": radius,
                "Vobs": vobs,
                "Vbar": math.sqrt(vbar2),
                "aN_over_a0": a_n_over_a0,
                "LogKernelAlphaLn": kernel,
                "SignedLogResidual_TPG": math.log(vobs / model),
            }
        )
    max_radius = max([row["RadiusKpc"] for row in rows], default=math.nan)
    for row in rows:
        row["RadiusFraction"] = row["RadiusKpc"] / max_radius if max_radius > 0 else math.nan
    return sorted(rows, key=lambda row: row["RadiusKpc"])


def max_same_sign_run(values: list[float]) -> int:
    best = 0
    current = 0
    last_sign = 0
    for value in values:
        sign = 1 if value > 0 else -1 if value < 0 else 0
        if sign == 0:
            current = 0
            last_sign = 0
            continue
        if sign == last_sign:
            current += 1
        else:
            current = 1
            last_sign = sign
        best = max(best, current)
    return best


def candidate_components(row: dict[str, str]) -> tuple[list[dict[str, str]], dict[str, str]]:
    galaxy = row["CanonicalSPARCNameCandidate"]
    rotmod = parse_rotmod(Path(row["LocalRotmodPath"]))
    point_rows: list[dict[str, str]] = []
    signed_values: list[float] = []
    cumulative_values: list[float] = []
    previous_signed: list[float] = []
    first_break = math.nan
    cumulative = 0.0
    abs_history_s1: list[float] = []
    abs_history_rule: list[float] = []
    delta_abs_history: list[float] = []
    for index, point in enumerate(rotmod, start=1):
        residual = point["SignedLogResidual_TPG"]
        signed_values.append(residual)
        cumulative += residual
        cumulative_mean = cumulative / len(signed_values)
        cumulative_values.append(cumulative_mean)
        if math.isnan(first_break) and abs(cumulative_mean) >= BREAK_THRESHOLD:
            first_break = point["RadiusFraction"]
        history_state = mean(previous_signed) if previous_signed else 0.0
        s_history = min(HISTORY_HIGH, max(HISTORY_LOW, 1.0 + HISTORY_GAIN * history_state))
        model_history = point["Vbar"] * (1.0 + s_history * point["LogKernelAlphaLn"])
        residual_history = math.log(point["Vobs"] / model_history)
        abs_history_s1.append(abs(residual))
        abs_history_rule.append(abs(residual_history))
        delta_abs_history.append(abs(residual_history) - abs(residual))
        point_rows.append(
            {
                "GalaxyName": galaxy,
                "AGC": row["AGC"],
                "FreezeRole": row["FreezeRole"],
                "PointIndex": str(index),
                "RadiusKpc": fmt(point["RadiusKpc"]),
                "RadiusFraction": fmt(point["RadiusFraction"]),
                "aN_over_a0": fmt(point["aN_over_a0"]),
                "VobsKms": fmt(point["Vobs"]),
                "VbarKms": fmt(point["Vbar"]),
                "LogKernelAlphaLn": fmt(point["LogKernelAlphaLn"]),
                "SignedLogResidual_TPG": fmt(residual),
                "CumulativeMeanSignedResidual": fmt(cumulative_mean),
                "HistoryStatePriorMeanSignedResidual": fmt(history_state),
                "Predicted_S_tau_history_v01": fmt(s_history),
                "SignedLogResidual_HistoryRule": fmt(residual_history),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
        previous_signed.append(residual)
    if len(signed_values) < MIN_VALID_POINTS:
        return point_rows, {
            "GalaxyName": galaxy,
            "AGC": row["AGC"],
            "ScoreSource": "not_scored_minimum_radial_points_not_met",
            "ScoringStatus": "excluded",
            "NPoints": str(len(signed_values)),
            "InterpretationGuardrail": GUARDRAIL,
        }
    positive_fraction = sum(value > 0 for value in signed_values) / len(signed_values)
    components = {
        "GalaxyName": galaxy,
        "AGC": row["AGC"],
        "ScoreSource": "expanded_yu2022_rotmod_scoring_frozen_w_tau_eff_calibration",
        "ScoringStatus": "scored",
        "NPoints": str(len(signed_values)),
        "W_tau_eff_signed_v01": fmt(mean(signed_values)),
        "W_tau_eff_abs_v01": fmt(abs(mean(signed_values))),
        "AbsFinalMeanSignedResidual": fmt(abs(mean(signed_values))),
        "MaxAbsCumulativeMeanResidual": fmt(max([abs(value) for value in cumulative_values])),
        "SignImbalance": fmt(abs(positive_fraction - 0.5) * 2.0),
        "MaxSameSignRunFraction": fmt(max_same_sign_run(signed_values) / len(signed_values)),
        "FirstBreakRadiusFraction_abs0p15": fmt(first_break),
        "CumulativeDriftRadiusPearson": fmt(
            pearson([point["RadiusFraction"] for point in rotmod], cumulative_values)
        ),
        "RMSLogResidual_S_tau1": fmt(rms(abs_history_s1)),
        "RMSLogResidual_HistoryRule": fmt(rms(abs_history_rule)),
        "DeltaRMS_HistoryMinusS1": fmt(rms(abs_history_rule) - rms(abs_history_s1)),
        "HistoryImprovement_PositiveIsBetter": fmt(
            -(rms(abs_history_rule) - rms(abs_history_s1))
        ),
        "MedianDeltaAbsLogResidual_HistoryMinusS1": fmt(median(delta_abs_history)),
        "FractionPointsImproved": fmt(
            sum(delta < 0 for delta in delta_abs_history) / len(delta_abs_history)
        ),
        "InterpretationGuardrail": GUARDRAIL,
    }
    return point_rows, components


def indexed(path: Path) -> dict[str, dict[str, str]]:
    return {row["GalaxyName"]: row for row in read_csv(path)}


def frozen_calibration() -> dict[str, list[float]]:
    drift = indexed(DRIFT)
    history = indexed(HISTORY)
    galaxies = sorted(set(drift) & set(history))
    components = {
        "AbsFinalMeanSignedResidual": [
            float(drift[galaxy]["AbsFinalMeanSignedResidual"]) for galaxy in galaxies
        ],
        "MaxAbsCumulativeMeanResidual": [
            float(drift[galaxy]["MaxAbsCumulativeMeanResidual"]) for galaxy in galaxies
        ],
        "SignImbalance": [float(drift[galaxy]["SignImbalance"]) for galaxy in galaxies],
        "MaxSameSignRunFraction": [
            float(drift[galaxy]["MaxSameSignRunFraction"]) for galaxy in galaxies
        ],
        "HistoryImprovement": [
            -float(history[galaxy]["DeltaRMS_HistoryMinusS1"]) for galaxy in galaxies
        ],
    }
    return {name: sorted(values) for name, values in components.items()}


def percentile(value: float, calibration_values: list[float]) -> float:
    if not calibration_values:
        return math.nan
    if len(calibration_values) == 1:
        return 0.0
    rank = bisect.bisect_left(calibration_values, value)
    return min(1.0, max(0.0, rank / (len(calibration_values) - 1)))


def add_candidate_score(row: dict[str, str], calibration: dict[str, list[float]]) -> dict[str, str]:
    if row["ScoringStatus"] != "scored":
        row.update(
            {
                "W_tau_eff_readout_score_v01": "",
                "CandidateConfidenceTier": "not_scored",
                "AnchorPolicy": "",
            }
        )
        return row
    ranks = {
        "RankAbsFinalMeanSignedResidual": percentile(
            float(row["AbsFinalMeanSignedResidual"]),
            calibration["AbsFinalMeanSignedResidual"],
        ),
        "RankMaxAbsCumulativeMeanResidual": percentile(
            float(row["MaxAbsCumulativeMeanResidual"]),
            calibration["MaxAbsCumulativeMeanResidual"],
        ),
        "RankSignImbalance": percentile(float(row["SignImbalance"]), calibration["SignImbalance"]),
        "RankMaxSameSignRunFraction": percentile(
            float(row["MaxSameSignRunFraction"]),
            calibration["MaxSameSignRunFraction"],
        ),
        "RankHistoryImprovement": percentile(
            float(row["HistoryImprovement_PositiveIsBetter"]),
            calibration["HistoryImprovement"],
        ),
    }
    score = mean(list(ranks.values()))
    row.update({name: fmt(value) for name, value in ranks.items()})
    row["W_tau_eff_readout_score_v01"] = fmt(score)
    row["CandidateConfidenceTier"] = confidence_tier(
        score,
        float(row["HistoryImprovement_PositiveIsBetter"]),
        float(row["W_tau_eff_abs_v01"]),
    )
    row["AnchorPolicy"] = ""
    return row


def anchor_score_rows(queue_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seed = indexed(FIELD_SEED)
    output: list[dict[str, str]] = []
    for queue in queue_rows:
        galaxy = queue["CanonicalSPARCNameCandidate"]
        source = seed[galaxy]
        output.append(
            {
                "GalaxyName": galaxy,
                "AGC": queue["AGC"],
                "FreezeRole": queue["FreezeRole"],
                "ScoreSource": "frozen_original_w_tau_eff_seed",
                "ScoringStatus": "anchor_not_refit",
                "NPoints": "",
                "W_tau_eff_signed_v01": source["W_tau_eff_signed_v01"],
                "W_tau_eff_abs_v01": source["W_tau_eff_abs_v01"],
                "AbsFinalMeanSignedResidual": source["W_tau_eff_abs_v01"],
                "MaxAbsCumulativeMeanResidual": source["MaxAbsCumulativeMeanResidual"],
                "SignImbalance": source["SignImbalance"],
                "MaxSameSignRunFraction": source["MaxSameSignRunFraction"],
                "FirstBreakRadiusFraction_abs0p15": source["FirstBreakRadiusFraction_abs0p15"],
                "CumulativeDriftRadiusPearson": "",
                "RMSLogResidual_S_tau1": "",
                "RMSLogResidual_HistoryRule": "",
                "DeltaRMS_HistoryMinusS1": "",
                "HistoryImprovement_PositiveIsBetter": source["HistoryImprovement_PositiveIsBetter"],
                "MedianDeltaAbsLogResidual_HistoryMinusS1": "",
                "FractionPointsImproved": "",
                "RankAbsFinalMeanSignedResidual": "",
                "RankMaxAbsCumulativeMeanResidual": "",
                "RankSignImbalance": "",
                "RankMaxSameSignRunFraction": "",
                "RankHistoryImprovement": "",
                "W_tau_eff_readout_score_v01": source["W_tau_eff_candidate_score_v01"],
                "CandidateConfidenceTier": source["CandidateConfidenceTier"],
                "AnchorPolicy": "retained_without_refit",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return output


def score_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    queue = read_csv(QUEUE)
    anchors = [row for row in queue if row["FreezeRole"] == "anchor_existing_seed"]
    candidates = [
        row
        for row in queue
        if row["ScoringPermission"] == "allowed_after_expanded_scoring_script_committed"
    ]
    calibration = frozen_calibration()
    points: list[dict[str, str]] = []
    scores = anchor_score_rows(anchors)
    for candidate in candidates:
        point_rows, component_row = candidate_components(candidate)
        points.extend(point_rows)
        component_row["FreezeRole"] = candidate["FreezeRole"]
        scores.append(add_candidate_score(component_row, calibration))
    return points, sorted(scores, key=lambda row: row["GalaxyName"])


def summary_rows(scores: list[dict[str, str]]) -> list[dict[str, str]]:
    scored_candidates = [
        row
        for row in scores
        if row["FreezeRole"] == "predeclared_expansion_candidate"
        and row["ScoringStatus"] == "scored"
    ]
    excluded_candidates = [
        row
        for row in scores
        if row["FreezeRole"] == "predeclared_expansion_candidate"
        and row["ScoringStatus"] == "excluded"
    ]
    anchors = [row for row in scores if row["FreezeRole"] == "anchor_existing_seed"]
    readout = [
        float(row["W_tau_eff_readout_score_v01"])
        for row in scores
        if row["W_tau_eff_readout_score_v01"] != ""
    ]
    candidate_scores = [
        float(row["W_tau_eff_readout_score_v01"])
        for row in scored_candidates
        if row["W_tau_eff_readout_score_v01"] != ""
    ]
    return [
        {
            "Subset": "anchors",
            "NGalaxies": str(len(anchors)),
            "Median_W_tau_eff_readout_score_v01": fmt(
                median([float(row["W_tau_eff_readout_score_v01"]) for row in anchors])
            ),
            "NHighCandidate": str(
                sum(row["CandidateConfidenceTier"] == "high_candidate" for row in anchors)
            ),
            "NMediumCandidate": str(
                sum(row["CandidateConfidenceTier"] == "medium_candidate" for row in anchors)
            ),
            "NLowOrControlCandidate": str(
                sum(row["CandidateConfidenceTier"] == "low_or_control_candidate" for row in anchors)
            ),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Subset": "scored_expansion_candidates",
            "NGalaxies": str(len(scored_candidates)),
            "Median_W_tau_eff_readout_score_v01": fmt(median(candidate_scores)),
            "NHighCandidate": str(
                sum(row["CandidateConfidenceTier"] == "high_candidate" for row in scored_candidates)
            ),
            "NMediumCandidate": str(
                sum(row["CandidateConfidenceTier"] == "medium_candidate" for row in scored_candidates)
            ),
            "NLowOrControlCandidate": str(
                sum(
                    row["CandidateConfidenceTier"] == "low_or_control_candidate"
                    for row in scored_candidates
                )
            ),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Subset": "excluded_expansion_candidates",
            "NGalaxies": str(len(excluded_candidates)),
            "Median_W_tau_eff_readout_score_v01": "",
            "NHighCandidate": "0",
            "NMediumCandidate": "0",
            "NLowOrControlCandidate": "0",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Subset": "directional_readout_ready_rows",
            "NGalaxies": str(len(readout)),
            "Median_W_tau_eff_readout_score_v01": fmt(median(readout)),
            "NHighCandidate": str(
                sum(
                    row["CandidateConfidenceTier"] == "high_candidate"
                    for row in scores
                    if row["W_tau_eff_readout_score_v01"] != ""
                )
            ),
            "NMediumCandidate": str(
                sum(
                    row["CandidateConfidenceTier"] == "medium_candidate"
                    for row in scores
                    if row["W_tau_eff_readout_score_v01"] != ""
                )
            ),
            "NLowOrControlCandidate": str(
                sum(
                    row["CandidateConfidenceTier"] == "low_or_control_candidate"
                    for row in scores
                    if row["W_tau_eff_readout_score_v01"] != ""
                )
            ),
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def decision_rows(scores: list[dict[str, str]]) -> list[dict[str, str]]:
    scored_candidates = [
        row
        for row in scores
        if row["FreezeRole"] == "predeclared_expansion_candidate"
        and row["ScoringStatus"] == "scored"
    ]
    readout_ready = [row for row in scores if row["W_tau_eff_readout_score_v01"] != ""]
    return [
        {
            "DecisionID": "YU22S01",
            "Decision": "expanded_scoring_status",
            "Status": "met" if len(scored_candidates) >= 15 else "not_met",
            "N": str(len(scored_candidates)),
            "PassCondition": "at least 15 predeclared expansion candidates receive frozen-calibration W_tau_eff scores",
            "NextAction": "commit_expanded_scores_before_directional_readout",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "YU22S02",
            "Decision": "directional_readout_gate",
            "Status": "ready_after_commit" if len(readout_ready) >= 15 else "not_ready",
            "N": str(len(readout_ready)),
            "PassCondition": "anchors plus scored candidates reach N>=15",
            "NextAction": "separate_script_may_join_Af_Ac_after_this_packet_is_committed",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "YU22S03",
            "Decision": "anchor_refit_policy",
            "Status": "satisfied",
            "N": str(sum(row["AnchorPolicy"] == "retained_without_refit" for row in scores)),
            "PassCondition": "all existing W_tau_eff anchors retain original seed scores",
            "NextAction": "do_not_replace_original_w_tau_eff_seed",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(scores: list[dict[str, str]], summary: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    by_subset = {row["Subset"]: row for row in summary}
    by_decision = {row["DecisionID"]: row for row in decisions}
    excluded = [
        row["GalaxyName"]
        for row in scores
        if row["FreezeRole"] == "predeclared_expansion_candidate"
        and row["ScoringStatus"] == "excluded"
    ]
    lines = [
        "# Yu 2022 ALFALFA Expanded W_tau_eff Scoring v0.1",
        "",
        "This packet computes frozen-calibration `W_tau_eff` scores for the predeclared Yu et al. (2022) ALFALFA expansion candidates. It does not compute the Af/Ac directional readout.",
        "",
        "## Scoring Policy",
        "",
        "Existing `W_tau_eff` seed overlaps are retained as anchors without refit. New candidates are scored from SPARC rotmod residual-shape diagnostics and calibrated against the frozen original `W_tau_eff` component distributions.",
        "",
        f"The first scoring pass requires at least {MIN_VALID_POINTS} valid radial rotmod points.",
        "",
        "## Counts",
        "",
        f"- Anchors retained without refit: {by_subset['anchors']['NGalaxies']}",
        f"- Scored expansion candidates: {by_subset['scored_expansion_candidates']['NGalaxies']}",
        f"- Excluded expansion candidates: {by_subset['excluded_expansion_candidates']['NGalaxies']}",
        f"- Directional-readout-ready rows: {by_subset['directional_readout_ready_rows']['NGalaxies']}",
        f"- Expanded scoring gate: {by_decision['YU22S01']['Status']}",
        f"- Directional readout gate: {by_decision['YU22S02']['Status']}",
        "",
        "## Exclusions",
        "",
        "The following predeclared candidates remain documented but are not scored in this first pass because they have fewer than eight valid radial points:",
        "",
        ", ".join(excluded) if excluded else "None.",
        "",
        "## Endpoint Boundary",
        "",
        "Af and Ac are not used in this script. A separate directional-readout script may join the committed score table to Af/Ac after this packet is committed.",
        "",
        "## Generated Files",
        "",
        "- `yu2022_alfalfa_expanded_w_tau_eff_point_trace_v01.csv`",
        "- `yu2022_alfalfa_expanded_w_tau_eff_scores_v01.csv`",
        "- `yu2022_alfalfa_expanded_w_tau_eff_summary_v01.csv`",
        "- `yu2022_alfalfa_expanded_w_tau_eff_decision_v01.csv`",
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
    manifest["yu2022_alfalfa_expanded_w_tau_eff_scoring_status"] = (
        "expanded_scores_committed_directional_readout_ready_after_commit"
    )
    manifest["paper2_next_gate"] = "yu2022_alfalfa_af_ac_directional_readout"
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
            "AGC",
            "FreezeRole",
            "ScoreSource",
            "ScoringStatus",
            "NPoints",
            "W_tau_eff_signed_v01",
            "W_tau_eff_abs_v01",
            "AbsFinalMeanSignedResidual",
            "MaxAbsCumulativeMeanResidual",
            "SignImbalance",
            "MaxSameSignRunFraction",
            "FirstBreakRadiusFraction_abs0p15",
            "CumulativeDriftRadiusPearson",
            "RMSLogResidual_S_tau1",
            "RMSLogResidual_HistoryRule",
            "DeltaRMS_HistoryMinusS1",
            "HistoryImprovement_PositiveIsBetter",
            "MedianDeltaAbsLogResidual_HistoryMinusS1",
            "FractionPointsImproved",
            "RankAbsFinalMeanSignedResidual",
            "RankMaxAbsCumulativeMeanResidual",
            "RankSignImbalance",
            "RankMaxSameSignRunFraction",
            "RankHistoryImprovement",
            "W_tau_eff_readout_score_v01",
            "CandidateConfidenceTier",
            "AnchorPolicy",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        SUMMARY_OUT,
        summary,
        [
            "Subset",
            "NGalaxies",
            "Median_W_tau_eff_readout_score_v01",
            "NHighCandidate",
            "NMediumCandidate",
            "NLowOrControlCandidate",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        DECISION_OUT,
        decisions,
        [
            "DecisionID",
            "Decision",
            "Status",
            "N",
            "PassCondition",
            "NextAction",
            "InterpretationGuardrail",
        ],
    )
    write_report(scores, summary, decisions)
    update_manifest()
    print(REPORT)
    print(f"yu2022_scored_expansion_candidates={summary[1]['NGalaxies']}")
    print(f"yu2022_directional_readout_ready_rows={summary[3]['NGalaxies']}")


if __name__ == "__main__":
    main()
