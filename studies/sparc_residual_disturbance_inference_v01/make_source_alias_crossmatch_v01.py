#!/usr/bin/env python3
"""Build source alias crossmatch for downloaded external validation sources."""

from __future__ import annotations

import csv
import json

from make_packet_v01_seed import PACKET, read_csv, write_csv


W_TAU = PACKET / "w_tau_eff_field_seed_v01.csv"
HALOGAS_DOWNLOADS = PACKET / "halogas_candidate_moment_downloads_v01.csv"
OUT = PACKET / "source_alias_crossmatch_v01.csv"
REPORT = PACKET / "source_alias_crossmatch_v01.md"

GUARDRAIL = "alias_crossmatch_join_only_no_velocity_endpoint"


def source_galaxies() -> list[tuple[str, str]]:
    pairs = {(row["GalaxyName"], "HALOGAS") for row in read_csv(HALOGAS_DOWNLOADS)}
    pairs.update(
        {
            ("DDO154", "THINGS"),
            ("NGC2366", "THINGS"),
            ("NGC2403", "THINGS"),
            ("NGC2976", "THINGS"),
            ("NGC3198", "THINGS"),
            ("NGC5055", "THINGS"),
            ("NGC7331", "THINGS"),
            ("DDO154", "LITTLE_THINGS"),
            ("DDO168", "LITTLE_THINGS"),
            ("NGC2366", "LITTLE_THINGS"),
        }
    )
    return sorted(pairs)


def rows() -> list[dict[str, str]]:
    w_tau = {row["GalaxyName"]: row for row in read_csv(W_TAU)}
    outputs: list[dict[str, str]] = []
    for name, family in source_galaxies():
        target = w_tau.get(name)
        outputs.append(
            {
                "ExternalName": name,
                "CanonicalSPARCName": name if target else "",
                "SourceFamily": family,
                "InWTauEff": "yes" if target else "no",
                "Class": target["Class"] if target else "",
                "W_tau_eff_candidate_score_v01": (
                    target["W_tau_eff_candidate_score_v01"] if target else ""
                ),
                "CandidateConfidenceTier": target["CandidateConfidenceTier"] if target else "",
                "AliasResolution": "exact_name_match" if target else "unmatched",
                "AllowedUse": "join_key_only",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return outputs


def write_report(output_rows: list[dict[str, str]]) -> None:
    matched = [row for row in output_rows if row["InWTauEff"] == "yes"]
    unmatched = [row for row in output_rows if row["InWTauEff"] != "yes"]
    families = sorted({row["SourceFamily"] for row in output_rows})
    lines = [
        "# Source Alias Crossmatch v0.1",
        "",
        "This table freezes exact-name alias joins for the current external-validation sources. It is a join audit only and does not create a velocity endpoint.",
        "",
        "## Summary",
        "",
        f"- Source families: {';'.join(families)}",
        f"- Unique source-family rows: {len(output_rows)}",
        f"- Matched to `W_tau_eff`: {len(matched)}",
        f"- Unmatched: {len(unmatched)}",
        "",
        "## Generated Files",
        "",
        "- `source_alias_crossmatch_v01.csv`",
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
    for path in [OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["source_alias_crossmatch_status"] = "exact_name_crossmatch_complete"
    manifest["paper2_next_gate"] = "halogas_moment_feature_derivation"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    output_rows = rows()
    fields = [
        "ExternalName",
        "CanonicalSPARCName",
        "SourceFamily",
        "InWTauEff",
        "Class",
        "W_tau_eff_candidate_score_v01",
        "CandidateConfidenceTier",
        "AliasResolution",
        "AllowedUse",
        "InterpretationGuardrail",
    ]
    write_csv(OUT, output_rows, fields)
    write_report(output_rows)
    update_manifest()


if __name__ == "__main__":
    main()
