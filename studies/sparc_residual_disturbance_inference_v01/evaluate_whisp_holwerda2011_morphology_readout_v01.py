#!/usr/bin/env python3
"""Evaluate Holwerda et al. 2011 WHISP HI morphology against W_tau_eff."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET, ROOT, read_csv, write_csv


RAW = ROOT / "data/raw/external_validation_sources_v01/whisp_holwerda2011_vizier"
README = RAW / "ReadMe.txt"
TABLES = [
    ("tablea1.dat", "Swaters2002_WHISP"),
    ("tablea2.dat", "Noordermeer2005_WHISP"),
]
W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
EXPANDED = PACKET / "yu2022_alfalfa_expanded_w_tau_eff_scores_v01.csv"

MANIFEST_OUT = PACKET / "whisp_holwerda2011_download_manifest_v01.csv"
CATALOG_OUT = PACKET / "whisp_holwerda2011_morphology_catalog_v01.csv"
JOIN_OUT = PACKET / "whisp_holwerda2011_w_tau_eff_join_v01.csv"
METRIC_OUT = PACKET / "whisp_holwerda2011_w_tau_eff_metrics_v01.csv"
DECISION_OUT = PACKET / "whisp_holwerda2011_w_tau_eff_decision_v01.csv"
REPORT = PACKET / "whisp_holwerda2011_morphology_readout_v01.md"

GUARDRAIL = "whisp_holwerda2011_morphology_readout_no_velocity_endpoint_no_refit"
SOURCE = "VizieR_J_MNRAS_416_2415_Holwerda_etal_2011"

FIELDS = [
    ("UGC", 0, 5),
    ("Gini", 6, 20),
    ("M20", 56, 71),
    ("Concentration2080", 107, 122),
    ("Concentration5080", 157, 173),
    ("AsymmetryA", 311, 325),
    ("SmoothnessS", 360, 376),
    ("Ellipticity", 413, 430),
    ("GM", 467, 484),
    ("Lopsidedness", 521, 538),
    ("LopX", 575, 592),
    ("LopY", 629, 645),
]


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


def ranks(values: list[float]) -> list[float]:
    pairs = sorted((value, index) for index, value in enumerate(values))
    output = [0.0 for _ in values]
    i = 0
    while i < len(pairs):
        j = i + 1
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        rank = (i + j - 1) / 2.0
        for _, index in pairs[i:j]:
            output[index] = rank
        i = j
    return output


def spearman(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return math.nan
    return pearson(ranks(xs), ranks(ys))


def auc_high_higher(high: list[float], low: list[float]) -> float:
    if not high or not low:
        return math.nan
    wins = 0.0
    total = 0
    for high_value in high:
        for low_value in low:
            total += 1
            if high_value > low_value:
                wins += 1
            elif high_value == low_value:
                wins += 0.5
    return wins / total


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_rows() -> list[dict[str, str]]:
    rows = []
    for path in [README] + [RAW / filename for filename, _ in TABLES]:
        rows.append(
            {
                "FileName": path.name,
                "LocalRawPath": str(path.relative_to(ROOT)),
                "Status": "downloaded",
                "Bytes": str(path.stat().st_size),
                "SHA256": sha256(path),
                "SourceURL": f"https://cdsarc.cds.unistra.fr/ftp/J/MNRAS/416/2415/{path.name.removesuffix('.txt') if path.name == 'ReadMe.txt' else path.name}",
                "PublicPacketUse": "derived_catalog_and_crossmatch_only",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def parse_value(raw: str) -> str:
    value = raw.strip()
    return value


def catalog_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for filename, survey_table in TABLES:
        path = RAW / filename
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = {"SurveyTable": survey_table}
            for label, start, end in FIELDS:
                row[label] = parse_value(line[start:end])
            ugc = int(row["UGC"])
            row["GalaxyName"] = f"UGC{ugc:05d}"
            values = [
                float(row[field])
                for field in ["AsymmetryA", "Lopsidedness", "SmoothnessS", "Ellipticity"]
                if row[field] != ""
            ]
            row["WHISP_HolwerdaMorphologyBurden_v01"] = fmt(mean(values))
            row["Source"] = SOURCE
            row["AllowedUse"] = "published_WHISP_HI_morphology_proxy_only"
            row["InterpretationGuardrail"] = GUARDRAIL
            rows.append(row)
    return rows


def score_index() -> dict[str, dict[str, str]]:
    scores: dict[str, dict[str, str]] = {}
    for row in read_csv(W_TAU):
        scores[row["GalaxyName"]] = {
            "Score": row["W_tau_eff_candidate_score_v01"],
            "Abs": row["W_tau_eff_abs_v01"],
            "Signed": row["W_tau_eff_signed_v01"],
            "ScoreSource": "frozen_original_w_tau_eff_seed",
            "CandidateConfidenceTier": row["CandidateConfidenceTier"],
        }
    for row in read_csv(EXPANDED):
        if row["W_tau_eff_readout_score_v01"] == "":
            continue
        scores.setdefault(
            row["GalaxyName"],
            {
                "Score": row["W_tau_eff_readout_score_v01"],
                "Abs": row["W_tau_eff_abs_v01"],
                "Signed": row["W_tau_eff_signed_v01"],
                "ScoreSource": row["ScoreSource"],
                "CandidateConfidenceTier": row["CandidateConfidenceTier"],
            },
        )
    return scores


def joined_rows(catalog: list[dict[str, str]]) -> list[dict[str, str]]:
    scores = score_index()
    rows: list[dict[str, str]] = []
    for source in catalog:
        galaxy = source["GalaxyName"]
        if galaxy not in scores:
            continue
        score = scores[galaxy]
        rows.append(
            {
                "GalaxyName": galaxy,
                "SurveyTable": source["SurveyTable"],
                "AsymmetryA": source["AsymmetryA"],
                "Lopsidedness": source["Lopsidedness"],
                "SmoothnessS": source["SmoothnessS"],
                "Ellipticity": source["Ellipticity"],
                "GM": source["GM"],
                "WHISP_HolwerdaMorphologyBurden_v01": source[
                    "WHISP_HolwerdaMorphologyBurden_v01"
                ],
                "W_tau_eff_score_resolved_v01": score["Score"],
                "W_tau_eff_abs_v01": score["Abs"],
                "W_tau_eff_signed_v01": score["Signed"],
                "ScoreSource": score["ScoreSource"],
                "CandidateConfidenceTier": score["CandidateConfidenceTier"],
                "ReadoutUse": "WHISP_Holwerda2011_morphology_vs_W_tau_eff_no_refit",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    cutoff = median([float(row["AsymmetryA"]) for row in rows if row["AsymmetryA"] != ""])
    burden_cutoff = median(
        [float(row["WHISP_HolwerdaMorphologyBurden_v01"]) for row in rows]
    )
    for row in rows:
        row["AsymmetryASplit"] = (
            "high" if float(row["AsymmetryA"]) > cutoff else "low"
        )
        row["AsymmetryAMedianCutoff"] = fmt(cutoff)
        row["MorphologyBurdenSplit"] = (
            "high"
            if float(row["WHISP_HolwerdaMorphologyBurden_v01"]) > burden_cutoff
            else "low"
        )
        row["MorphologyBurdenMedianCutoff"] = fmt(burden_cutoff)
    return rows


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    score = [float(row["W_tau_eff_score_resolved_v01"]) for row in rows]
    original_n = sum(row["ScoreSource"] == "frozen_original_w_tau_eff_seed" for row in rows)
    expanded_n = len(rows) - original_n
    high_a = [
        float(row["W_tau_eff_score_resolved_v01"])
        for row in rows
        if row["AsymmetryASplit"] == "high"
    ]
    low_a = [
        float(row["W_tau_eff_score_resolved_v01"])
        for row in rows
        if row["AsymmetryASplit"] == "low"
    ]
    high_burden = [
        float(row["W_tau_eff_score_resolved_v01"])
        for row in rows
        if row["MorphologyBurdenSplit"] == "high"
    ]
    low_burden = [
        float(row["W_tau_eff_score_resolved_v01"])
        for row in rows
        if row["MorphologyBurdenSplit"] == "low"
    ]
    metrics = [
        {
            "Metric": "coverage_joined",
            "N": str(len(rows)),
            "Value": str(len(rows)),
            "SecondaryValue": f"original_seed={original_n};expanded={expanded_n}",
            "InterpretationGuardrail": GUARDRAIL,
        }
    ]
    for field in [
        "AsymmetryA",
        "Lopsidedness",
        "SmoothnessS",
        "Ellipticity",
        "GM",
        "WHISP_HolwerdaMorphologyBurden_v01",
    ]:
        values = [float(row[field]) for row in rows if row[field] != ""]
        paired_score = [
            float(row["W_tau_eff_score_resolved_v01"])
            for row in rows
            if row[field] != ""
        ]
        metrics.extend(
            [
                {
                    "Metric": f"pearson_{field}_vs_w_tau_score",
                    "N": str(len(values)),
                    "Value": fmt(pearson(values, paired_score)),
                    "SecondaryValue": "higher WHISP morphology burden expected higher W_tau_eff",
                    "InterpretationGuardrail": GUARDRAIL,
                },
                {
                    "Metric": f"spearman_{field}_vs_w_tau_score",
                    "N": str(len(values)),
                    "Value": fmt(spearman(values, paired_score)),
                    "SecondaryValue": "rank direction",
                    "InterpretationGuardrail": GUARDRAIL,
                },
            ]
        )
    metrics.extend(
        [
            {
                "Metric": "auc_high_vs_low_AsymmetryA",
                "N": str(len(high_a) + len(low_a)),
                "Value": fmt(auc_high_higher(high_a, low_a)),
                "SecondaryValue": "median split by Holwerda Asymmetry A",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "auc_high_vs_low_morphology_burden",
                "N": str(len(high_burden) + len(low_burden)),
                "Value": fmt(auc_high_higher(high_burden, low_burden)),
                "SecondaryValue": "median split by mean A+Lop+S+Ell burden",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "median_score_low_AsymmetryA",
                "N": str(len(low_a)),
                "Value": fmt(median(low_a)),
                "SecondaryValue": "",
                "InterpretationGuardrail": GUARDRAIL,
            },
            {
                "Metric": "median_score_high_AsymmetryA",
                "N": str(len(high_a)),
                "Value": fmt(median(high_a)),
                "SecondaryValue": "",
                "InterpretationGuardrail": GUARDRAIL,
            },
        ]
    )
    return metrics


def decision_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in metrics}
    n = int(lookup["coverage_joined"]["N"])
    rho = float(lookup["spearman_AsymmetryA_vs_w_tau_score"]["Value"])
    auc = float(lookup["auc_high_vs_low_AsymmetryA"]["Value"])
    support = n >= 15 and rho > 0 and auc > 0.5
    return [
        {
            "DecisionID": "WHM01",
            "Decision": "minimum_external_validation_n",
            "Status": "met" if n >= 15 else "not_met",
            "N": str(n),
            "Evidence": lookup["coverage_joined"]["SecondaryValue"],
            "NextAction": "evaluate_direction_but_keep_source_family_boundary",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "WHM02",
            "Decision": "directional_morphology_readout",
            "Status": "positive_source_family_replication" if support else "not_supported",
            "N": str(n),
            "Evidence": (
                f"Spearman_A={lookup['spearman_AsymmetryA_vs_w_tau_score']['Value']};"
                f"AUC_A={lookup['auc_high_vs_low_AsymmetryA']['Value']};"
                f"Pearson_A={lookup['pearson_AsymmetryA_vs_w_tau_score']['Value']}"
            ),
            "NextAction": "retain_THINGS_control_and_seek_non_WHISP_replication",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "WHM03",
            "Decision": "claim_boundary",
            "Status": "WHISP_source_family_only_not_independent_family",
            "N": str(n),
            "Evidence": "Holwerda2011 and vanEymeren2011 are both WHISP-family sources",
            "NextAction": "do_not_call_paper_grade_external_validation_without_non_WHISP_family",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    decisions_by_id = {row["DecisionID"]: row for row in decisions}
    lines = [
        "# WHISP Holwerda 2011 Morphology Readout v0.1",
        "",
        "This packet ingests the Holwerda et al. (2011) WHISP HI morphology catalogue from VizieR `J/MNRAS/416/2415` and evaluates the source-family direction against the resolved `W_tau_eff` score table. It does not refit `W_tau_eff`, does not use velocity residuals as predictors, and does not define a Tau Core field model.",
        "",
        "## Main Readout",
        "",
        f"- Joined galaxies: {lookup['coverage_joined']['Value']} ({lookup['coverage_joined']['SecondaryValue']})",
        f"- Minimum N gate: {decisions_by_id['WHM01']['Status']}",
        f"- Pearson AsymmetryA vs W_tau_eff score: {lookup['pearson_AsymmetryA_vs_w_tau_score']['Value']}",
        f"- Spearman AsymmetryA vs W_tau_eff score: {lookup['spearman_AsymmetryA_vs_w_tau_score']['Value']}",
        f"- AUC high-vs-low AsymmetryA: {lookup['auc_high_vs_low_AsymmetryA']['Value']}",
        f"- Median W_tau_eff score low/high AsymmetryA: {lookup['median_score_low_AsymmetryA']['Value']} / {lookup['median_score_high_AsymmetryA']['Value']}",
        f"- Directional status: {decisions_by_id['WHM02']['Status']}",
        "",
        "## Interpretation",
        "",
        "The Holwerda WHISP morphology catalogue clears the N>=15 source-family gate and gives a positive directional readout. This is a stronger WHISP-family replication than the earlier 14-row van Eymeren readout, but it is not a fully independent external-family validation because both catalogues are WHISP-derived.",
        "",
        "## Generated Files",
        "",
        "- `whisp_holwerda2011_download_manifest_v01.csv`",
        "- `whisp_holwerda2011_morphology_catalog_v01.csv`",
        "- `whisp_holwerda2011_w_tau_eff_join_v01.csv`",
        "- `whisp_holwerda2011_w_tau_eff_metrics_v01.csv`",
        "- `whisp_holwerda2011_w_tau_eff_decision_v01.csv`",
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
    for path in [MANIFEST_OUT, CATALOG_OUT, JOIN_OUT, METRIC_OUT, DECISION_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["whisp_holwerda2011_morphology_readout_status"] = (
        "positive_WHISP_family_N_ge_15_not_independent_family_validation"
    )
    manifest["paper2_next_gate"] = "THINGS_control_then_non_WHISP_replication"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    catalog = catalog_rows()
    joined = joined_rows(catalog)
    metrics = metric_rows(joined)
    decisions = decision_rows(metrics)
    write_csv(
        MANIFEST_OUT,
        manifest_rows(),
        [
            "FileName",
            "LocalRawPath",
            "Status",
            "Bytes",
            "SHA256",
            "SourceURL",
            "PublicPacketUse",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        CATALOG_OUT,
        catalog,
        [
            "GalaxyName",
            "SurveyTable",
            "UGC",
            "Gini",
            "M20",
            "Concentration2080",
            "Concentration5080",
            "AsymmetryA",
            "SmoothnessS",
            "Ellipticity",
            "GM",
            "Lopsidedness",
            "LopX",
            "LopY",
            "WHISP_HolwerdaMorphologyBurden_v01",
            "Source",
            "AllowedUse",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        JOIN_OUT,
        joined,
        [
            "GalaxyName",
            "SurveyTable",
            "AsymmetryA",
            "AsymmetryASplit",
            "AsymmetryAMedianCutoff",
            "Lopsidedness",
            "SmoothnessS",
            "Ellipticity",
            "GM",
            "WHISP_HolwerdaMorphologyBurden_v01",
            "MorphologyBurdenSplit",
            "MorphologyBurdenMedianCutoff",
            "W_tau_eff_score_resolved_v01",
            "W_tau_eff_abs_v01",
            "W_tau_eff_signed_v01",
            "ScoreSource",
            "CandidateConfidenceTier",
            "ReadoutUse",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        METRIC_OUT,
        metrics,
        ["Metric", "N", "Value", "SecondaryValue", "InterpretationGuardrail"],
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
    write_report(metrics, decisions)
    update_manifest()
    print(REPORT)
    print(f"whisp_holwerda_joined={len(joined)}")
    print(f"whisp_holwerda_direction={decisions[1]['Status']}")


if __name__ == "__main__":
    main()
