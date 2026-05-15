#!/usr/bin/env python3
"""Parse Reynolds et al. 2020 VizieR asymmetry tables and crossmatch W_tau_eff."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/external_validation_sources_v01/reynolds2020_vizier"
W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"

DOWNLOAD_OUT = PACKET / "reynolds2020_vizier_download_manifest_v01.csv"
CATALOG_OUT = PACKET / "reynolds2020_asymmetry_catalog_v01.csv"
CROSSMATCH_OUT = PACKET / "reynolds2020_asymmetry_w_tau_eff_crossmatch_v01.csv"
METRIC_OUT = PACKET / "reynolds2020_asymmetry_crossmatch_metrics_v01.csv"
DECISION_OUT = PACKET / "reynolds2020_asymmetry_crossmatch_decision_v01.csv"
REPORT = PACKET / "reynolds2020_asymmetry_crossmatch_v01.md"

GUARDRAIL = "reynolds2020_asymmetry_crossmatch_no_velocity_endpoint"


TABLES = [
    ("LVHIS", "tablea1.dat", (8, 14, 19, 22, 25, 31, 36, 41, 46, 51, 56, 62)),
    ("VIVA", "tablea2.dat", (7, 13, 18, 21, 24, 30, 35, 40, 45, 50, 55, 61)),
    ("HALOGAS", "tablea3.dat", (7, 13, 18, 21, 24, 30, 35, 40, 45, 50, 55, 61)),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_slice(line: str, start: int, end: int) -> str:
    return line[start:end].strip()


def parse_float(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    return f"{float(value):.9f}"


def parse_int(value: str) -> str:
    value = value.strip()
    return str(int(value)) if value else ""


def download_rows() -> list[dict[str, str]]:
    outputs = []
    for filename in ["ReadMe.txt", "tablea1.dat", "tablea2.dat", "tablea3.dat"]:
        path = RAW / filename
        outputs.append(
            {
                "FileName": filename,
                "LocalRawPath": str(path.relative_to(ROOT)),
                "Status": "downloaded" if path.exists() else "missing",
                "Bytes": str(path.stat().st_size) if path.exists() else "0",
                "SHA256": sha256(path) if path.exists() else "",
                "SourceURL": f"https://cdsarc.cds.unistra.fr/ftp/J/MNRAS/493/5089/{filename if filename != 'ReadMe.txt' else 'ReadMe'}",
                "PublicPacketUse": "derived_catalog_and_crossmatch_only",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return outputs


def catalog_rows() -> list[dict[str, str]]:
    rows = []
    for survey, filename, widths in TABLES:
        path = RAW / filename
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            name_end = widths[0]
            name = line[:name_end].strip()
            offsets = [0, *widths]
            # fixed byte ranges from CDS are 1-indexed; these slices match the
            # readme columns after the name field for both table layouts.
            values = {
                "logrho": parse_float(text_slice(line, name_end + 1, widths[1])),
                "logMass": parse_float(text_slice(line, widths[1] + 1, widths[2])),
                "DVsys": parse_int(text_slice(line, widths[2] + 1, widths[3])),
                "DVsysopt": parse_int(text_slice(line, widths[3] + 1, widths[4])),
                "Aspec": parse_float(text_slice(line, widths[4] + 1, widths[5])),
                "Aflux": parse_float(text_slice(line, widths[5] + 1, widths[6])),
                "Apeak": parse_float(text_slice(line, widths[6] + 1, widths[7])),
                "Amap": parse_float(text_slice(line, widths[7] + 1, widths[8])),
                "A1_inner": parse_float(text_slice(line, widths[8] + 1, widths[9])),
                "A2_outer": parse_float(text_slice(line, widths[9] + 1, widths[10])),
                "Avel": parse_float(text_slice(line, widths[10] + 1, widths[11])),
            }
            rows.append(
                {
                    "Survey": survey,
                    "ExternalName": name,
                    **values,
                    "Source": "Reynolds_etal_2020_VizieR_J_MNRAS_493_5089",
                    "AllowedUse": "published_resolved_HI_asymmetry_proxy_only",
                    "InterpretationGuardrail": GUARDRAIL,
                }
            )
    return rows


def crossmatch_rows(catalog: list[dict[str, str]]) -> list[dict[str, str]]:
    w_tau = {row["GalaxyName"]: row for row in read_csv(W_TAU)}
    outputs = []
    for row in catalog:
        canonical = row["ExternalName"]
        target = w_tau.get(canonical)
        if not target:
            continue
        outputs.append(
            {
                **row,
                "CanonicalSPARCName": canonical,
                "Class": target["Class"],
                "W_tau_eff_candidate_score_v01": target[
                    "W_tau_eff_candidate_score_v01"
                ],
                "CandidateConfidenceTier": target["CandidateConfidenceTier"],
                "CrossmatchMode": "exact_name_match",
                "ReadoutUse": "non_WHISP_resolved_HI_asymmetry_crossmatch_no_velocity_endpoint",
            }
        )
    return outputs


def safe_float(value: str) -> float:
    return float(value) if value else math.nan


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def pearson(xs: list[float], ys: list[float]) -> float:
    pairs = [(x, y) for x, y in zip(xs, ys) if not math.isnan(x) and not math.isnan(y)]
    if len(pairs) < 2:
        return math.nan
    xs2, ys2 = zip(*pairs)
    mx = mean(list(xs2))
    my = mean(list(ys2))
    dx = [x - mx for x in xs2]
    dy = [y - my for y in ys2]
    denom = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    if denom == 0:
        return math.nan
    return sum(x * y for x, y in zip(dx, dy)) / denom


def fmt(value: float) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.9f}"


def metric_rows(catalog: list[dict[str, str]], cross: list[dict[str, str]]) -> list[dict[str, str]]:
    score = [safe_float(row["W_tau_eff_candidate_score_v01"]) for row in cross]
    amap = [safe_float(row["Amap"]) for row in cross]
    avel = [safe_float(row["Avel"]) for row in cross]
    surveys = ";".join(sorted({row["Survey"] for row in cross}))
    return [
        {
            "Metric": "reynolds2020_catalog_rows",
            "N": str(len(catalog)),
            "Value": str(len(catalog)),
            "SecondaryValue": "LVHIS;VIVA;HALOGAS",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "exact_w_tau_eff_crossmatch_rows",
            "N": str(len(cross)),
            "Value": str(len(cross)),
            "SecondaryValue": surveys,
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_amap_vs_w_tau_score",
            "N": str(len(cross)),
            "Value": fmt(pearson(amap, score)),
            "SecondaryValue": "bias-corrected moment-0 map asymmetry",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_avel_vs_w_tau_score",
            "N": str(len(cross)),
            "Value": fmt(pearson(avel, score)),
            "SecondaryValue": "velocity-field asymmetry",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "minimum_non_whisp_asymmetry_gate",
            "N": str(len(cross)),
            "Value": "not_met",
            "SecondaryValue": "requires N>=15 from frozen target plan",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def decision_rows(metrics: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in metrics}
    return [
        {
            "DecisionID": "R20D01",
            "Decision": "Reynolds2020_non_WHISP_asymmetry_crossmatch",
            "Status": "catalog_ingested_but_exact_overlap_below_minimum_n",
            "Rationale": (
                "VizieR rows="
                + lookup["reynolds2020_catalog_rows"]["Value"]
                + "; exact W_tau_eff overlap="
                + lookup["exact_w_tau_eff_crossmatch_rows"]["Value"]
                + "; frozen minimum N=15."
            ),
            "Blocks": "paper_grade_non_WHISP_asymmetry_validation_claim",
            "NextAction": "resolve_LVHIS_aliases_or_expand_W_tau_eff_seed_before_directional_claim",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "R20D02",
            "Decision": "velocity_endpoint_status",
            "Status": "closed",
            "Rationale": "Published asymmetry parameters are external proxies only.",
            "Blocks": "S_tau_full_velocity_formula",
            "NextAction": "do_not_fit_coefficients_on_Reynolds2020_overlap",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    lines = [
        "# Reynolds 2020 Asymmetry Crossmatch v0.1",
        "",
        "This packet parses the VizieR machine-readable tables for Reynolds et al. (2020), `J/MNRAS/493/5089`, and exact-name crossmatches the resolved H I asymmetry parameters to the current `W_tau_eff` seed. It is an external-proxy crossmatch only and does not open a velocity endpoint.",
        "",
        "## Metrics",
        "",
        f"- Catalog rows: {lookup['reynolds2020_catalog_rows']['Value']}",
        f"- Exact `W_tau_eff` overlap: {lookup['exact_w_tau_eff_crossmatch_rows']['Value']} ({lookup['exact_w_tau_eff_crossmatch_rows']['SecondaryValue']})",
        f"- Pearson Amap vs W_tau_eff: {lookup['pearson_amap_vs_w_tau_score']['Value']}",
        f"- Pearson Avel vs W_tau_eff: {lookup['pearson_avel_vs_w_tau_score']['Value']}",
        f"- Minimum N gate: {lookup['minimum_non_whisp_asymmetry_gate']['Value']}",
        "",
        "## Decision",
        "",
        f"`{decisions[0]['Status']}`",
        "",
        decisions[0]["Rationale"],
        "",
        "The exact-name overlap is currently HALOGAS-only. LVHIS uses survey IDs rather than common galaxy names, so LVHIS alias resolution is the next step before treating this as a non-WHISP validation family.",
        "",
        "## Generated Files",
        "",
        "- `reynolds2020_vizier_download_manifest_v01.csv`",
        "- `reynolds2020_asymmetry_catalog_v01.csv`",
        "- `reynolds2020_asymmetry_w_tau_eff_crossmatch_v01.csv`",
        "- `reynolds2020_asymmetry_crossmatch_metrics_v01.csv`",
        "- `reynolds2020_asymmetry_crossmatch_decision_v01.csv`",
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
    for path in [
        DOWNLOAD_OUT,
        CATALOG_OUT,
        CROSSMATCH_OUT,
        METRIC_OUT,
        DECISION_OUT,
        REPORT,
    ]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["reynolds2020_asymmetry_crossmatch_status"] = (
        "vizier_catalog_ingested_exact_overlap_below_minimum_n"
    )
    manifest["paper2_next_gate"] = "LVHIS_alias_resolution_or_expand_W_tau_eff_seed"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    downloads = download_rows()
    catalog = catalog_rows()
    cross = crossmatch_rows(catalog)
    metrics = metric_rows(catalog, cross)
    decisions = decision_rows(metrics)
    write_csv(
        DOWNLOAD_OUT,
        downloads,
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
    catalog_fields = [
        "Survey",
        "ExternalName",
        "logrho",
        "logMass",
        "DVsys",
        "DVsysopt",
        "Aspec",
        "Aflux",
        "Apeak",
        "Amap",
        "A1_inner",
        "A2_outer",
        "Avel",
        "Source",
        "AllowedUse",
        "InterpretationGuardrail",
    ]
    write_csv(CATALOG_OUT, catalog, catalog_fields)
    cross_fields = catalog_fields + [
        "CanonicalSPARCName",
        "Class",
        "W_tau_eff_candidate_score_v01",
        "CandidateConfidenceTier",
        "CrossmatchMode",
        "ReadoutUse",
    ]
    write_csv(CROSSMATCH_OUT, cross, cross_fields)
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
            "Rationale",
            "Blocks",
            "NextAction",
            "InterpretationGuardrail",
        ],
    )
    write_report(metrics, decisions)
    update_manifest()


if __name__ == "__main__":
    main()
