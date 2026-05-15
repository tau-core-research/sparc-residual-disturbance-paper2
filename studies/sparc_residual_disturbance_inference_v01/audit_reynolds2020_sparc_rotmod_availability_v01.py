#!/usr/bin/env python3
"""Audit SPARC rotmod availability for the frozen Reynolds expansion queue."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from make_packet_v01_seed import PACKET, read_csv, write_csv


ROOT = Path(__file__).resolve().parents[2]
ROT_DIR = Path("/Users/jolcsak/Projects/tau-core/data/sparc/Rotmod_LTG")

QUEUE = PACKET / "reynolds2020_seed_expansion_candidate_queue_v01.csv"
AVAIL_OUT = PACKET / "reynolds2020_sparc_rotmod_availability_v01.csv"
SUMMARY_OUT = PACKET / "reynolds2020_sparc_rotmod_availability_summary_v01.csv"
DECISION_OUT = PACKET / "reynolds2020_sparc_rotmod_availability_decision_v01.csv"
REPORT = PACKET / "reynolds2020_sparc_rotmod_availability_audit_v01.md"

GUARDRAIL = "reynolds2020_sparc_rotmod_availability_no_raw_redistribution"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_rotmod(path: Path) -> tuple[str, int, float, float]:
    distance = ""
    radii = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if stripped.startswith("# Distance"):
            distance = stripped.split("=", 1)[1].replace("Mpc", "").strip()
            continue
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) >= 7:
            radii.append(float(parts[0]))
    if not radii:
        return distance, 0, 0.0, 0.0
    return distance, len(radii), min(radii), max(radii)


def availability_rows() -> list[dict[str, str]]:
    rotmods = {path.stem.replace("_rotmod", ""): path for path in ROT_DIR.glob("*_rotmod.dat")}
    rows = []
    for row in read_csv(QUEUE):
        canonical = row["CanonicalSPARCNameCandidate"]
        is_candidate = (
            row["ExpansionStatus"]
            == "predeclared_candidate_pending_sparc_rotmod_audit"
        )
        path = rotmods.get(canonical)
        available = is_candidate and path is not None
        distance = ""
        n_points = 0
        r_min = 0.0
        r_max = 0.0
        if available:
            distance, n_points, r_min, r_max = parse_rotmod(path)
        passes = available and n_points >= 8
        rows.append(
            {
                "Survey": row["Survey"],
                "ExternalName": row["ExternalName"],
                "CanonicalSPARCNameCandidate": canonical,
                "ExpansionStatus": row["ExpansionStatus"],
                "PreScorePriority": row["PreScorePriority"],
                "RotmodAvailable": "yes" if available else "no",
                "LocalRotmodPath": str(path) if available else "",
                "RotmodSHA256": sha256(path) if available else "",
                "DistanceMpcFromRotmod": distance if available else "",
                "NRotmodPoints": str(n_points) if available else "0",
                "MinRadiusKpc": f"{r_min:.9f}" if available else "",
                "MaxRadiusKpc": f"{r_max:.9f}" if available else "",
                "PassesMinimumRadialPointGate": "yes" if passes else "no",
                "AllowedPublicUse": "derived_availability_manifest_only",
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return rows


def summary_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    candidates = [
        row
        for row in rows
        if row["ExpansionStatus"]
        == "predeclared_candidate_pending_sparc_rotmod_audit"
    ]
    available = [row for row in candidates if row["RotmodAvailable"] == "yes"]
    passed = [row for row in candidates if row["PassesMinimumRadialPointGate"] == "yes"]
    high_passed = [row for row in passed if row["PreScorePriority"] == "high"]
    by_survey = []
    for survey in ["LVHIS", "VIVA", "HALOGAS"]:
        subset = [row for row in candidates if row["Survey"] == survey]
        survey_passed = [
            row for row in subset if row["PassesMinimumRadialPointGate"] == "yes"
        ]
        by_survey.append(
            {
                "Metric": f"{survey.lower()}_candidate_passed_rotmod_gate",
                "N": str(len(subset)),
                "Value": str(len(survey_passed)),
                "SecondaryValue": ";".join(row["CanonicalSPARCNameCandidate"] for row in survey_passed),
                "InterpretationGuardrail": GUARDRAIL,
            }
        )
    return [
        {
            "Metric": "predeclared_expansion_candidates",
            "N": str(len(candidates)),
            "Value": str(len(candidates)),
            "SecondaryValue": "from_frozen_queue",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "rotmod_available_candidates",
            "N": str(len(candidates)),
            "Value": str(len(available)),
            "SecondaryValue": ";".join(row["CanonicalSPARCNameCandidate"] for row in available),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "minimum_radial_point_gate_passed",
            "N": str(len(candidates)),
            "Value": str(len(passed)),
            "SecondaryValue": ";".join(row["CanonicalSPARCNameCandidate"] for row in passed),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "high_priority_avel_passed",
            "N": str(len(candidates)),
            "Value": str(len(high_passed)),
            "SecondaryValue": ";".join(row["CanonicalSPARCNameCandidate"] for row in high_passed),
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "Metric": "expanded_validation_minimum_n_gate",
            "N": str(len(passed)),
            "Value": "not_met",
            "SecondaryValue": "requires_at_least_15_passed_rotmod_candidates",
            "InterpretationGuardrail": GUARDRAIL,
        },
        *by_survey,
    ]


def decision_rows(summary: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {row["Metric"]: row for row in summary}
    return [
        {
            "DecisionID": "R20A01",
            "Decision": "Reynolds2020_expansion_rotmod_availability",
            "Status": "current_local_sparc_rotmod_overlap_below_minimum_n",
            "Rationale": (
                "Predeclared candidates="
                + lookup["predeclared_expansion_candidates"]["Value"]
                + "; rotmod gate passed="
                + lookup["minimum_radial_point_gate_passed"]["Value"]
                + "; frozen minimum N=15."
            ),
            "Blocks": "expanded_Reynolds_directional_validation_claim",
            "NextAction": "do_not_compute_expanded_directional_readout_until_more_public_sparc_inputs_are_available",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "R20A02",
            "Decision": "raw_data_publication_status",
            "Status": "raw_sparc_rotmods_not_redistributed",
            "Rationale": "The public packet records derived availability, point counts, and checksums only.",
            "Blocks": "none",
            "NextAction": "keep_raw_sparc_data_out_of_public_repo",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "DecisionID": "R20A03",
            "Decision": "velocity_endpoint_status",
            "Status": "closed",
            "Rationale": "This audit does not calculate expanded scores or compare them to Reynolds asymmetry.",
            "Blocks": "S_tau_full_velocity_formula",
            "NextAction": "switch_to_larger_external_family_or_acquire_public_sparc_inputs",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(summary: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lookup = {row["Metric"]: row for row in summary}
    lines = [
        "# Reynolds 2020 SPARC Rotmod Availability Audit v0.1",
        "",
        "This audit checks whether the frozen Reynolds et al. (2020) seed-expansion queue has enough locally available SPARC rotmod inputs to support an expanded `W_tau_eff` validation. It records derived availability only and does not redistribute raw SPARC rotmod files.",
        "",
        "## Result",
        "",
        f"- Predeclared expansion candidates: {lookup['predeclared_expansion_candidates']['Value']}",
        f"- Rotmod available candidates: {lookup['rotmod_available_candidates']['Value']}",
        f"- Minimum radial-point gate passed: {lookup['minimum_radial_point_gate_passed']['Value']}",
        f"- High-priority Avel candidates passed: {lookup['high_priority_avel_passed']['Value']}",
        f"- Passed names: {lookup['minimum_radial_point_gate_passed']['SecondaryValue']}",
        f"- Expanded validation minimum-N gate: {lookup['expanded_validation_minimum_n_gate']['Value']}",
        "",
        "## Decision",
        "",
        f"`{decisions[0]['Status']}`",
        "",
        decisions[0]["Rationale"],
        "",
        "The seed-expansion idea remains methodologically clean, but the currently available local SPARC rotmod overlap is too small for a paper-grade Reynolds directional validation. The next scientific move should either acquire more public SPARC inputs for the predeclared queue or switch to a larger external source family with better overlap.",
        "",
        "## Generated Files",
        "",
        "- `reynolds2020_sparc_rotmod_availability_v01.csv`",
        "- `reynolds2020_sparc_rotmod_availability_summary_v01.csv`",
        "- `reynolds2020_sparc_rotmod_availability_decision_v01.csv`",
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
    for path in [AVAIL_OUT, SUMMARY_OUT, DECISION_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["reynolds2020_sparc_rotmod_availability_status"] = (
        "current_local_rotmod_overlap_below_minimum_n"
    )
    manifest["paper2_next_gate"] = (
        "acquire_more_public_sparc_inputs_or_switch_external_family"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = availability_rows()
    summary = summary_rows(rows)
    decisions = decision_rows(summary)
    write_csv(
        AVAIL_OUT,
        rows,
        [
            "Survey",
            "ExternalName",
            "CanonicalSPARCNameCandidate",
            "ExpansionStatus",
            "PreScorePriority",
            "RotmodAvailable",
            "LocalRotmodPath",
            "RotmodSHA256",
            "DistanceMpcFromRotmod",
            "NRotmodPoints",
            "MinRadiusKpc",
            "MaxRadiusKpc",
            "PassesMinimumRadialPointGate",
            "AllowedPublicUse",
            "InterpretationGuardrail",
        ],
    )
    write_csv(
        SUMMARY_OUT,
        summary,
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
    write_report(summary, decisions)
    update_manifest()


if __name__ == "__main__":
    main()
