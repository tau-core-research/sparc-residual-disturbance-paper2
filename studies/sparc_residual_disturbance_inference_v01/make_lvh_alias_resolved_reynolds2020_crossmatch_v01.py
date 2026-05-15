#!/usr/bin/env python3
"""Resolve LVHIS IDs in Reynolds et al. 2020 and re-crossmatch W_tau_eff."""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
from urllib.request import urlopen

from make_packet_v01_seed import PACKET, read_csv, write_csv


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/external_validation_sources_v01/lvhis"
LVHIS_URL = "https://www.narrabri.atnf.csiro.au/research/LVHIS/LVHIS-database.html"
LVHIS_HTML = RAW / "LVHIS-database.html"

CATALOG = PACKET / "reynolds2020_asymmetry_catalog_v01.csv"
W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"

MANIFEST_OUT = PACKET / "lvhis_database_download_manifest_v01.csv"
ALIAS_OUT = PACKET / "lvhis_alias_resolution_v01.csv"
CROSSMATCH_OUT = PACKET / "reynolds2020_lvh_alias_resolved_w_tau_eff_crossmatch_v01.csv"
METRIC_OUT = PACKET / "reynolds2020_lvh_alias_resolved_metrics_v01.csv"
DECISION_OUT = PACKET / "reynolds2020_lvh_alias_resolved_decision_v01.csv"
REPORT = PACKET / "reynolds2020_lvh_alias_resolved_crossmatch_v01.md"

GUARDRAIL = "lvhis_alias_resolved_reynolds2020_no_velocity_endpoint"


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_cell = False
        self.buffer = ""
        self.row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self.row = []
        if tag in {"td", "th"}:
            self.in_cell = True
            self.buffer = ""

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.buffer += data

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self.in_cell:
            self.row.append(" ".join(self.buffer.split()))
            self.in_cell = False
        if tag == "tr" and self.row:
            self.rows.append(self.row)


def ensure_lvhis_html() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    if LVHIS_HTML.exists():
        return
    with urlopen(LVHIS_URL, timeout=60) as response:
        LVHIS_HTML.write_bytes(response.read())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_name(name: str) -> str:
    clean = name.upper().replace("?", "").replace(" GALAXY", "").strip()
    patterns = [
        (r"NGC\s*(\d+)$", lambda m: "NGC" + m.group(1).zfill(4)),
        (r"IC\s*(\d+)$", lambda m: "IC" + m.group(1).zfill(4)),
        (
            r"ESO\s*(\d+)\s*-\s*G\s*(\d+)$",
            lambda m: "ESO" + m.group(1).zfill(3) + "-G" + m.group(2).zfill(3),
        ),
        (r"UGCA\s*(\d+)$", lambda m: "UGCA" + m.group(1).zfill(3)),
    ]
    for pattern, formatter in patterns:
        match = re.match(pattern, clean)
        if match:
            return formatter(match)
    return clean.replace(" ", "")


def lvh_rows() -> list[dict[str, str]]:
    parser = TableParser()
    parser.feed(LVHIS_HTML.read_text(encoding="iso-8859-1", errors="ignore"))
    rows = []
    for row in parser.rows:
        if len(row) < 2:
            continue
        match = re.match(r"LVHIS\s+(\d+)$", row[0])
        if not match:
            continue
        rows.append(
            {
                "ExternalName": "LVHIS" + match.group(1).zfill(3),
                "LVHIS_ID_Display": row[0],
                "OpticalID": row[1],
                "CanonicalSPARCNameCandidate": canonical_name(row[1]),
                "HIPASS_ID": row[7] if len(row) > 7 else "",
                "Source": "ATNF_LVHIS_database_Koribalski_etal_2018",
                "SourceURL": LVHIS_URL,
                "AllowedUse": "alias_resolution_only",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


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


def auc(pos: list[float], neg: list[float]) -> float:
    pairs = [(p, n) for p in pos for n in neg if not math.isnan(p) and not math.isnan(n)]
    if not pairs:
        return math.nan
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p, n in pairs)
    return wins / len(pairs)


def fmt(value: float) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.9f}"


def crossmatch_rows(alias_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    aliases = {row["ExternalName"]: row for row in alias_rows}
    w_tau = {row["GalaxyName"]: row for row in read_csv(W_TAU)}
    outputs = []
    for row in read_csv(CATALOG):
        alias = aliases.get(row["ExternalName"])
        canonical = row["ExternalName"] if row["ExternalName"] in w_tau else ""
        mode = "exact_name_match" if canonical else ""
        if not canonical and alias:
            candidate = alias["CanonicalSPARCNameCandidate"]
            if candidate in w_tau:
                canonical = candidate
                mode = "lvhis_database_optical_id_alias"
        if not canonical:
            continue
        target = w_tau[canonical]
        outputs.append(
            {
                **row,
                "CanonicalSPARCName": canonical,
                "Class": target["Class"],
                "W_tau_eff_candidate_score_v01": target[
                    "W_tau_eff_candidate_score_v01"
                ],
                "CandidateConfidenceTier": target["CandidateConfidenceTier"],
                "CrossmatchMode": mode,
                "AliasSource": alias["Source"] if alias else "exact_name",
                "ReadoutUse": "non_WHISP_resolved_HI_asymmetry_alias_resolved_no_velocity_endpoint",
            }
        )
    return outputs


def manifest_rows() -> list[dict[str, str]]:
    return [
        {
            "FileName": LVHIS_HTML.name,
            "LocalRawPath": str(LVHIS_HTML.relative_to(ROOT)),
            "Status": "downloaded" if LVHIS_HTML.exists() else "missing",
            "Bytes": str(LVHIS_HTML.stat().st_size) if LVHIS_HTML.exists() else "0",
            "SHA256": sha256(LVHIS_HTML) if LVHIS_HTML.exists() else "",
            "SourceURL": LVHIS_URL,
            "PublicPacketUse": "derived_alias_table_only",
            "InterpretationGuardrail": GUARDRAIL,
        }
    ]


def metric_rows(alias_rows: list[dict[str, str]], cross: list[dict[str, str]]) -> list[dict[str, str]]:
    score = [safe_float(row["W_tau_eff_candidate_score_v01"]) for row in cross]
    amap = [safe_float(row["Amap"]) for row in cross]
    avel = [safe_float(row["Avel"]) for row in cross]
    c_amap = [safe_float(row["Amap"]) for row in cross if row["Class"] == "C"]
    a_amap = [safe_float(row["Amap"]) for row in cross if row["Class"] == "A"]
    c_avel = [safe_float(row["Avel"]) for row in cross if row["Class"] == "C"]
    a_avel = [safe_float(row["Avel"]) for row in cross if row["Class"] == "A"]
    alias_resolved = [
        row for row in cross if row["CrossmatchMode"] == "lvhis_database_optical_id_alias"
    ]
    return [
        {
            "Metric": "lvhis_alias_rows",
            "N": str(len(alias_rows)),
            "Value": str(len(alias_rows)),
            "SecondaryValue": "ATNF_LVHIS_database",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "alias_resolved_w_tau_eff_crossmatch_rows",
            "N": str(len(cross)),
            "Value": str(len(cross)),
            "SecondaryValue": ";".join(sorted({row["Survey"] for row in cross})),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "lvhis_new_alias_matches",
            "N": str(len(alias_resolved)),
            "Value": str(len(alias_resolved)),
            "SecondaryValue": ";".join(row["CanonicalSPARCName"] for row in alias_resolved),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_amap_vs_w_tau_score_alias_resolved",
            "N": str(len(cross)),
            "Value": fmt(pearson(amap, score)),
            "SecondaryValue": "bias-corrected moment-0 map asymmetry",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "pearson_avel_vs_w_tau_score_alias_resolved",
            "N": str(len(cross)),
            "Value": fmt(pearson(avel, score)),
            "SecondaryValue": "velocity-field asymmetry",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_c_higher_amap_alias_resolved",
            "N": str(len(cross)),
            "Value": fmt(auc(c_amap, a_amap)),
            "SecondaryValue": "C higher than A if map asymmetry tracks disturbance",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "auc_c_higher_avel_alias_resolved",
            "N": str(len(cross)),
            "Value": fmt(auc(c_avel, a_avel)),
            "SecondaryValue": "C higher than A if velocity-field asymmetry tracks disturbance",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "minimum_non_whisp_asymmetry_gate_alias_resolved",
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
            "DecisionID": "LVHD01",
            "Decision": "LVHIS_alias_resolved_Reynolds2020_crossmatch",
            "Status": "alias_resolution_improves_overlap_but_below_minimum_n",
            "Rationale": (
                "Alias-resolved overlap="
                + lookup["alias_resolved_w_tau_eff_crossmatch_rows"]["Value"]
                + "; new LVHIS alias matches="
                + lookup["lvhis_new_alias_matches"]["Value"]
                + "; frozen minimum N=15."
            ),
            "Blocks": "paper_grade_non_WHISP_asymmetry_validation_claim",
            "NextAction": "expand_seed_or_add_independent_alias_catalogue_before_directional_claim",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "LVHD02",
            "Decision": "velocity_endpoint_status",
            "Status": "closed",
            "Rationale": "Alias resolution changes join keys only; it does not use velocity residuals or fit coefficients.",
            "Blocks": "S_tau_full_velocity_formula",
            "NextAction": "keep_as_external_proxy_gate_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(metrics: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in metrics}
    lines = [
        "# LVHIS Alias-Resolved Reynolds 2020 Crossmatch v0.1",
        "",
        "This packet resolves LVHIS survey IDs through the public ATNF LVHIS database and re-crossmatches the Reynolds et al. (2020) resolved H I asymmetry catalogue to the frozen `W_tau_eff` seed. It is a join-key and external-proxy audit only.",
        "",
        "## Metrics",
        "",
        f"- LVHIS alias rows: {lookup['lvhis_alias_rows']['Value']}",
        f"- Alias-resolved `W_tau_eff` overlap: {lookup['alias_resolved_w_tau_eff_crossmatch_rows']['Value']} ({lookup['alias_resolved_w_tau_eff_crossmatch_rows']['SecondaryValue']})",
        f"- New LVHIS alias matches: {lookup['lvhis_new_alias_matches']['Value']} ({lookup['lvhis_new_alias_matches']['SecondaryValue']})",
        f"- Pearson Amap vs W_tau_eff: {lookup['pearson_amap_vs_w_tau_score_alias_resolved']['Value']}",
        f"- Pearson Avel vs W_tau_eff: {lookup['pearson_avel_vs_w_tau_score_alias_resolved']['Value']}",
        f"- AUC C higher Amap: {lookup['auc_c_higher_amap_alias_resolved']['Value']}",
        f"- AUC C higher Avel: {lookup['auc_c_higher_avel_alias_resolved']['Value']}",
        f"- Minimum N gate: {lookup['minimum_non_whisp_asymmetry_gate_alias_resolved']['Value']}",
        "",
        "## Decision",
        "",
        f"`{decisions[0]['Status']}`",
        "",
        decisions[0]["Rationale"],
        "",
        "The alias step increases the overlap, but not enough for a directional non-WHISP validation claim. The velocity-field asymmetry readout is recorded as a small-sample hint only; it is not a Tau Core claim and does not open a velocity endpoint.",
        "",
        "## Generated Files",
        "",
        "- `lvhis_database_download_manifest_v01.csv`",
        "- `lvhis_alias_resolution_v01.csv`",
        "- `reynolds2020_lvh_alias_resolved_w_tau_eff_crossmatch_v01.csv`",
        "- `reynolds2020_lvh_alias_resolved_metrics_v01.csv`",
        "- `reynolds2020_lvh_alias_resolved_decision_v01.csv`",
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
    for path in [MANIFEST_OUT, ALIAS_OUT, CROSSMATCH_OUT, METRIC_OUT, DECISION_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["lvhis_alias_resolution_status"] = (
        "resolved_ids_alias_crossmatch_below_minimum_n"
    )
    manifest["paper2_next_gate"] = (
        "expand_seed_or_add_independent_alias_catalogue_before_directional_claim"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    ensure_lvhis_html()
    aliases = lvh_rows()
    cross = crossmatch_rows(aliases)
    metrics = metric_rows(aliases, cross)
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
        ALIAS_OUT,
        aliases,
        [
            "ExternalName",
            "LVHIS_ID_Display",
            "OpticalID",
            "CanonicalSPARCNameCandidate",
            "HIPASS_ID",
            "Source",
            "SourceURL",
            "AllowedUse",
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
    write_csv(
        CROSSMATCH_OUT,
        cross,
        catalog_fields
        + [
            "CanonicalSPARCName",
            "Class",
            "W_tau_eff_candidate_score_v01",
            "CandidateConfidenceTier",
            "CrossmatchMode",
            "AliasSource",
            "ReadoutUse",
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
