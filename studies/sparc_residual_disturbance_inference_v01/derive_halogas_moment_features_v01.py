#!/usr/bin/env python3
"""Derive small HALOGAS moment-map features from local verified FITS files."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from astropy.io import fits

from make_packet_v01_seed import PACKET, read_csv, write_csv


ROOT = Path(__file__).resolve().parents[2]
DOWNLOADS = PACKET / "halogas_candidate_moment_downloads_v01.csv"
W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
FEATURE_OUT = PACKET / "halogas_moment_feature_summary_v01.csv"
JOIN_OUT = PACKET / "halogas_moment_w_tau_eff_join_v01.csv"
REPORT = PACKET / "halogas_moment_features_v01.md"

GUARDRAIL = "halogas_moment_features_external_proxy_only_no_velocity_endpoint"


def fmt(value: float) -> str:
    if value is None or math.isnan(value) or math.isinf(value):
        return ""
    return f"{value:.9f}"


def parse_product(filename: str) -> tuple[str, str]:
    if "-HR_" in filename:
        resolution = "HR"
    elif "-LR_" in filename:
        resolution = "LR"
    else:
        resolution = "unknown"
    lower = filename.lower()
    if "coldens" in lower:
        product = "coldens"
    elif "mom0" in lower:
        product = "mom0"
    elif "mom1" in lower:
        product = "mom1"
    else:
        product = "other"
    return resolution, product


def finite_data(path: Path) -> np.ndarray:
    with fits.open(path, memmap=True) as hdul:
        data = np.asarray(hdul[0].data, dtype=float)
    return data[np.isfinite(data)]


def image_features(values: np.ndarray) -> dict[str, float]:
    if values.size == 0:
        return {
            "FinitePixels": 0,
            "PositivePixels": 0,
            "PositiveFraction": math.nan,
            "Mean": math.nan,
            "Median": math.nan,
            "P90": math.nan,
            "P10": math.nan,
            "RobustSpread": math.nan,
            "SumPositive": math.nan,
        }
    positive = values[values > 0]
    p90 = float(np.nanpercentile(values, 90))
    p10 = float(np.nanpercentile(values, 10))
    return {
        "FinitePixels": float(values.size),
        "PositivePixels": float(positive.size),
        "PositiveFraction": float(positive.size / values.size),
        "Mean": float(np.nanmean(values)),
        "Median": float(np.nanmedian(values)),
        "P90": p90,
        "P10": p10,
        "RobustSpread": p90 - p10,
        "SumPositive": float(np.nansum(positive)) if positive.size else 0.0,
    }


def feature_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in read_csv(DOWNLOADS):
        if row["Status"] != "downloaded_verified":
            continue
        resolution, product = parse_product(row["FileName"])
        path = ROOT / row["LocalRawPath"]
        features = image_features(finite_data(path))
        rows.append(
            {
                "GalaxyName": row["GalaxyName"],
                "Resolution": resolution,
                "Product": product,
                "FileName": row["FileName"],
                "FinitePixels": str(int(features["FinitePixels"])),
                "PositivePixels": str(int(features["PositivePixels"])),
                "PositiveFraction": fmt(features["PositiveFraction"]),
                "Mean": fmt(features["Mean"]),
                "Median": fmt(features["Median"]),
                "P90": fmt(features["P90"]),
                "P10": fmt(features["P10"]),
                "RobustSpread": fmt(features["RobustSpread"]),
                "SumPositive": fmt(features["SumPositive"]),
                "AllowedUse": "external_halogas_moment_proxy_only",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def safe_float(value: str) -> float:
    return float(value) if value != "" else math.nan


def product_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, str]]:
    return {(row["GalaxyName"], row["Resolution"], row["Product"]): row for row in rows}


def ratio(num: float, den: float) -> float:
    if den == 0 or math.isnan(num) or math.isnan(den):
        return math.nan
    return num / den


def galaxy_join_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    w_tau = {row["GalaxyName"]: row for row in read_csv(W_TAU)}
    lookup = product_lookup(rows)
    galaxies = sorted({row["GalaxyName"] for row in rows})
    outputs: list[dict[str, str]] = []
    for galaxy in galaxies:
        target = w_tau[galaxy]
        hr_mom0 = lookup.get((galaxy, "HR", "mom0"), {})
        lr_mom0 = lookup.get((galaxy, "LR", "mom0"), {})
        hr_mom1 = lookup.get((galaxy, "HR", "mom1"), {})
        lr_mom1 = lookup.get((galaxy, "LR", "mom1"), {})
        hr_coldens = lookup.get((galaxy, "HR", "coldens"), {})
        lr_coldens = lookup.get((galaxy, "LR", "coldens"), {})
        hr_mom0_pf = safe_float(hr_mom0.get("PositiveFraction", ""))
        lr_mom0_pf = safe_float(lr_mom0.get("PositiveFraction", ""))
        hr_mom1_spread = safe_float(hr_mom1.get("RobustSpread", ""))
        lr_mom1_spread = safe_float(lr_mom1.get("RobustSpread", ""))
        hr_coldens_sum = safe_float(hr_coldens.get("SumPositive", ""))
        lr_coldens_sum = safe_float(lr_coldens.get("SumPositive", ""))
        stress_proxy = np.nanmean(
            [
                hr_mom1_spread,
                lr_mom1_spread,
                ratio(hr_mom0_pf, lr_mom0_pf),
            ]
        )
        outputs.append(
            {
                "GalaxyName": galaxy,
                "Class": target["Class"],
                "W_tau_eff_candidate_score_v01": target["W_tau_eff_candidate_score_v01"],
                "CandidateConfidenceTier": target["CandidateConfidenceTier"],
                "HALOGAS_HR_mom0_positive_fraction": fmt(hr_mom0_pf),
                "HALOGAS_LR_mom0_positive_fraction": fmt(lr_mom0_pf),
                "HALOGAS_HR_LR_mom0_positive_fraction_ratio": fmt(
                    ratio(hr_mom0_pf, lr_mom0_pf)
                ),
                "HALOGAS_HR_mom1_robust_spread": fmt(hr_mom1_spread),
                "HALOGAS_LR_mom1_robust_spread": fmt(lr_mom1_spread),
                "HALOGAS_HR_LR_coldens_sum_ratio": fmt(
                    ratio(hr_coldens_sum, lr_coldens_sum)
                ),
                "HALOGAS_moment_stress_proxy_v01": fmt(float(stress_proxy)),
                "ReadoutUse": "HALOGAS_moment_proxy_no_velocity_endpoint",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return outputs


def write_report(feature_rows_: list[dict[str, str]], join_rows_: list[dict[str, str]]) -> None:
    products = sorted({row["Product"] for row in feature_rows_})
    galaxies = sorted({row["GalaxyName"] for row in join_rows_})
    lines = [
        "# HALOGAS Moment Features v0.1",
        "",
        "This packet derives small external HALOGAS moment-map proxy features from locally verified FITS products. It does not use SPARC velocity residuals as predictors, does not fit a Tau Core formula, and does not open a velocity endpoint.",
        "",
        "## Summary",
        "",
        f"- Feature rows: {len(feature_rows_)}",
        f"- Joined galaxies: {len(join_rows_)} ({';'.join(galaxies)})",
        f"- Products: {';'.join(products)}",
        "",
        "## Generated Files",
        "",
        "- `halogas_moment_feature_summary_v01.csv`",
        "- `halogas_moment_w_tau_eff_join_v01.csv`",
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
    for path in [FEATURE_OUT, JOIN_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["halogas_moment_features_status"] = (
        "derived_external_proxy_features_complete_no_velocity_endpoint"
    )
    manifest["paper2_next_gate"] = "halogas_moment_proxy_vs_w_tau_eff_readout"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    features = feature_rows()
    joined = galaxy_join_rows(features)
    feature_fields = [
        "GalaxyName",
        "Resolution",
        "Product",
        "FileName",
        "FinitePixels",
        "PositivePixels",
        "PositiveFraction",
        "Mean",
        "Median",
        "P90",
        "P10",
        "RobustSpread",
        "SumPositive",
        "AllowedUse",
        "InterpretationGuardrail",
    ]
    join_fields = [
        "GalaxyName",
        "Class",
        "W_tau_eff_candidate_score_v01",
        "CandidateConfidenceTier",
        "HALOGAS_HR_mom0_positive_fraction",
        "HALOGAS_LR_mom0_positive_fraction",
        "HALOGAS_HR_LR_mom0_positive_fraction_ratio",
        "HALOGAS_HR_mom1_robust_spread",
        "HALOGAS_LR_mom1_robust_spread",
        "HALOGAS_HR_LR_coldens_sum_ratio",
        "HALOGAS_moment_stress_proxy_v01",
        "ReadoutUse",
        "InterpretationGuardrail",
    ]
    write_csv(FEATURE_OUT, features, feature_fields)
    write_csv(JOIN_OUT, joined, join_fields)
    write_report(features, joined)
    update_manifest()


if __name__ == "__main__":
    main()
