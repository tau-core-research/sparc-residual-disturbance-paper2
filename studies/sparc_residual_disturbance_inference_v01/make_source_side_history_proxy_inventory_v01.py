#!/usr/bin/env python3
"""Create a no-leakage inventory for source-side W_env_obs/history proxies."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from make_packet_v01_seed import PACKET


INVENTORY_OUT = PACKET / "source_side_history_proxy_inventory_v01.csv"
READINESS_OUT = PACKET / "source_side_history_proxy_readiness_v01.csv"
REPORT = PACKET / "source_side_history_proxy_inventory_v01.md"

GUARDRAIL = "proxy_inventory_only_no_velocity_endpoint_no_rule_selection"


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def inventory_rows() -> list[dict[str, str]]:
    return [
        {
            "ProxyID": "P01",
            "ProxyFamily": "paper1_external_evidence_type",
            "SourcePacket": "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/external_evidence_table.csv",
            "CoverageGalaxies": "73",
            "Resolution": "galaxy_level",
            "AllowedInputs": "EvidenceType;Confidence;ResidualBlind external evidence",
            "ForbiddenInputs": "Vobs;Vbar;TPG_residual;S_tau_eff;history_state;endpoint_velocity",
            "ResidualLeakageRisk": "low",
            "CandidateUse": "broad_source_side_prior_for_W_env_obs",
            "Limitation": "coarse classes; subjective literature synthesis; not radial",
            "ReadinessTier": "ready_as_broad_prior",
            "Guardrail": GUARDRAIL,
        },
        {
            "ProxyID": "P02",
            "ProxyFamily": "radial_source_inventory_soft_s_tau",
            "SourcePacket": "tau-core/studies/sparc_radial_s_tau_pilot_v01/packet_v01_seed/radial_source_inventory.csv",
            "CoverageGalaxies": "73",
            "Resolution": "galaxy_level",
            "AllowedInputs": "external source families; soft source-side S_tau calibration metadata",
            "ForbiddenInputs": "velocity residual endpoint;S_tau_eff endpoint",
            "ResidualLeakageRisk": "medium",
            "CandidateUse": "candidate broad source-side W_env_obs prior after audit",
            "Limitation": "contains previous soft calibration choices; must audit provenance before use",
            "ReadinessTier": "audit_before_freeze",
            "Guardrail": GUARDRAIL,
        },
        {
            "ProxyID": "P03",
            "ProxyFamily": "THINGS_moment_map_kinematic_stress",
            "SourcePacket": "tau-core/studies/sparc_radial_s_tau_pilot_v01/packet_v01_seed/things_kinematic_galaxy_summary.csv",
            "CoverageGalaxies": "8",
            "Resolution": "radial_ring_and_galaxy_summary",
            "AllowedInputs": "HI moment-map stress;dispersion/asymmetry proxy;ring profiles",
            "ForbiddenInputs": "TPG residual endpoint;current point residual",
            "ResidualLeakageRisk": "low",
            "CandidateUse": "radial W_env_obs proxy candidate",
            "Limitation": "small overlap; earlier direct stress-to-S_tau mapping was too crude",
            "ReadinessTier": "ready_for_small_heldout_sanity_check",
            "Guardrail": GUARDRAIL,
        },
        {
            "ProxyID": "P04",
            "ProxyFamily": "THINGS_global_geometry_stress",
            "SourcePacket": "tau-core/studies/sparc_radial_s_tau_pilot_v01/packet_v01_seed/things_global_geometry_galaxy_summary.csv",
            "CoverageGalaxies": "8",
            "Resolution": "radial_ring_and_galaxy_summary",
            "AllowedInputs": "global PA/inclination elliptical annuli stress",
            "ForbiddenInputs": "TPG residual endpoint;S_tau_eff endpoint",
            "ResidualLeakageRisk": "low",
            "CandidateUse": "geometry-aware W_env_obs proxy candidate",
            "Limitation": "small overlap; geometry assumptions may absorb inclination systematics",
            "ReadinessTier": "ready_for_small_heldout_sanity_check",
            "Guardrail": GUARDRAIL,
        },
        {
            "ProxyID": "P05",
            "ProxyFamily": "THINGS_published_harmonic_non_circular",
            "SourcePacket": "tau-core/studies/sparc_radial_s_tau_pilot_v01/packet_v01_seed/things_published_harmonic_residual_joined_galaxies.csv",
            "CoverageGalaxies": "7",
            "Resolution": "galaxy_level_with_inner_amplitude",
            "AllowedInputs": "published non-circular harmonic amplitudes",
            "ForbiddenInputs": "TPG residual endpoint as predictor",
            "ResidualLeakageRisk": "medium",
            "CandidateUse": "systematics_competition_control_and_possible_history_proxy",
            "Limitation": "joined table also contains residual readouts; only published harmonic columns are allowed",
            "ReadinessTier": "control_first_then_candidate",
            "Guardrail": GUARDRAIL,
        },
        {
            "ProxyID": "P06",
            "ProxyFamily": "LITTLE_THINGS_pressure_support",
            "SourcePacket": "tau-core/studies/sparc_radial_s_tau_pilot_v01/packet_v01_seed/littlethings_pressure_support_galaxy_summary.csv",
            "CoverageGalaxies": "3",
            "Resolution": "radial_profile_and_galaxy_summary",
            "AllowedInputs": "pressure support;dispersion over circular speed",
            "ForbiddenInputs": "TPG residual endpoint",
            "ResidualLeakageRisk": "low",
            "CandidateUse": "dwarf-specific systematics/control proxy",
            "Limitation": "very small overlap in current packet",
            "ReadinessTier": "control_only_until_more_overlap",
            "Guardrail": GUARDRAIL,
        },
        {
            "ProxyID": "P07",
            "ProxyFamily": "WHISP_lopsidedness_asymmetry",
            "SourcePacket": "tau-core/studies/sparc_radial_s_tau_pilot_v01/packet_v01_seed/whisp_vaneymeren2011_overlap.csv",
            "CoverageGalaxies": "14",
            "Resolution": "galaxy_level_with_radial_asymmetry_bins",
            "AllowedInputs": "published HI lopsidedness;tidal parameter;epsilon_kin",
            "ForbiddenInputs": "TPG residual endpoint",
            "ResidualLeakageRisk": "low",
            "CandidateUse": "source-side environment/disturbance proxy",
            "Limitation": "mostly B/C overlap; class balance limited",
            "ReadinessTier": "ready_for_source_family_holdout",
            "Guardrail": GUARDRAIL,
        },
        {
            "ProxyID": "P08",
            "ProxyFamily": "HALOGAS_LR_cube_linewidth_stress",
            "SourcePacket": "tau-core/studies/sparc_radial_s_tau_pilot_v01/packet_v01_seed/path_b_halogas_h07_lr_cube_galaxy_summary.csv",
            "CoverageGalaxies": "5",
            "Resolution": "galaxy_level_joined_radius_fraction",
            "AllowedInputs": "low-resolution cube linewidth stress proxy",
            "ForbiddenInputs": "TPG residual endpoint",
            "ResidualLeakageRisk": "low",
            "CandidateUse": "weak external-family control",
            "Limitation": "small overlap; previous readout did not produce strong Tau-specific signal",
            "ReadinessTier": "control_only",
            "Guardrail": GUARDRAIL,
        },
        {
            "ProxyID": "P09",
            "ProxyFamily": "inclination_systematics",
            "SourcePacket": "tau-core/studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/inclination_systematics_summary.csv",
            "CoverageGalaxies": "binned_summary",
            "Resolution": "control_summary",
            "AllowedInputs": "inclination bins;class counts;median residual stress",
            "ForbiddenInputs": "use_as_positive_tau_proxy",
            "ResidualLeakageRisk": "medium",
            "CandidateUse": "mandatory systematics competition control",
            "Limitation": "summary-level only in current public packet",
            "ReadinessTier": "control_required",
            "Guardrail": GUARDRAIL,
        },
    ]


def readiness_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    tiers = sorted({row["ReadinessTier"] for row in rows})
    output: list[dict[str, str]] = []
    for tier in tiers:
        subset = [row for row in rows if row["ReadinessTier"] == tier]
        output.append(
            {
                "ReadinessTier": tier,
                "NProxyFamilies": str(len(subset)),
                "ProxyIDs": ";".join(row["ProxyID"] for row in subset),
                "RecommendedUse": recommended_use(tier),
                "Guardrail": GUARDRAIL,
            }
        )
    return output


def recommended_use(tier: str) -> str:
    return {
        "audit_before_freeze": "audit provenance before using as W_env_obs predictor",
        "control_first_then_candidate": "use as systematics control before candidate predictor",
        "control_only": "use as negative or weak-control source family",
        "control_only_until_more_overlap": "do not use as primary predictor until coverage expands",
        "control_required": "include before interpretation of any W_env_obs signal",
        "ready_as_broad_prior": "eligible as coarse galaxy-level prior",
        "ready_for_small_heldout_sanity_check": "eligible for small overlap sanity check only",
        "ready_for_source_family_holdout": "eligible for source-family holdout design",
    }[tier]


def write_report(rows: list[dict[str, str]], readiness: list[dict[str, str]]) -> None:
    ready_ids = [
        row["ProxyID"]
        for row in rows
        if row["ReadinessTier"] in {"ready_as_broad_prior", "ready_for_source_family_holdout"}
    ]
    lines = [
        "# Source-Side History Proxy Inventory v0.1",
        "",
        "This inventory starts the `source_side_history_proxy` gate. It lists residual-free proxy families that could predict `W_env_obs(R)` or compete with it as systematics controls. No velocity endpoint is evaluated here.",
        "",
        "## Target",
        "",
        "The next model target remains:",
        "",
        "`S_tau_full(R)=1+g(W_env_obs(R))`",
        "",
        "`W_env_obs(R)` must be predicted from predeclared source-side, geometry-side, environment-side, or observer-state proxies before endpoint readout.",
        "",
        "## Inventory Summary",
        "",
        f"- Proxy families: {len(rows)}",
        f"- Ready broad/holdout proxy IDs: {', '.join(ready_ids)}",
        "- Mandatory controls include inclination/systematics and non-circular-motion proxies.",
        "",
        "## Recommended Next Gate",
        "",
        "Freeze one primary source-family holdout design. The safest first target is a two-track design: use Paper 1 external evidence as the broad galaxy-level prior, and WHISP/THINGS families as held-out or small-overlap stress tests. Do not tune a velocity formula from this inventory.",
        "",
        "## Generated Files",
        "",
        "- `source_side_history_proxy_inventory_v01.csv`",
        "- `source_side_history_proxy_readiness_v01.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    files.update(
        {
            "source_side_history_proxy_inventory_v01.md",
            "source_side_history_proxy_inventory_v01.csv",
            "source_side_history_proxy_readiness_v01.csv",
        }
    )
    manifest["files"] = sorted(files)
    manifest["source_side_history_proxy_inventory_status"] = "proxy_inventory_complete_no_endpoint_readout"
    manifest["paper2_next_gate"] = "freeze_primary_source_side_w_env_obs_proxy_design"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = inventory_rows()
    readiness = readiness_rows(rows)
    write_csv(
        INVENTORY_OUT,
        rows,
        [
            "ProxyID",
            "ProxyFamily",
            "SourcePacket",
            "CoverageGalaxies",
            "Resolution",
            "AllowedInputs",
            "ForbiddenInputs",
            "ResidualLeakageRisk",
            "CandidateUse",
            "Limitation",
            "ReadinessTier",
            "Guardrail",
        ],
    )
    write_csv(
        READINESS_OUT,
        readiness,
        ["ReadinessTier", "NProxyFamilies", "ProxyIDs", "RecommendedUse", "Guardrail"],
    )
    write_report(rows, readiness)
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
