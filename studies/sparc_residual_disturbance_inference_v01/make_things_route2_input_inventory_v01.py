#!/usr/bin/env python3
"""Inventory route 2 source inputs for missing THINGS galaxies."""

from __future__ import annotations

import json
from pathlib import Path

from make_packet_v01_seed import PACKET, write_csv


INVENTORY = PACKET / "things_route2_input_inventory_v01.csv"
MANIFEST = PACKET / "things_route2_input_download_manifest_v01.csv"
GATE = PACKET / "things_route2_input_inventory_gate_v01.csv"
REPORT = PACKET / "things_route2_input_inventory_v01.md"

GUARDRAIL = "route2_input_inventory_no_new_scores_no_endpoint_tuning"


GALAXIES = [
    {
        "GalaxyName": "NGC925",
        "CandidatePriority": "primary_candidate",
        "THINGS_MOM0_URL": "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_925_NA_MOM0_THINGS.FITS",
        "THINGS_MOM0_SizeBytes": "4253760",
        "THINGS_RO_MOM0_URL": "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_925_RO_MOM0_THINGS.FITS",
        "THINGS_RO_MOM0_SizeBytes": "4253760",
        "SINGS_IRAC1_URL": "https://irsa.ipac.caltech.edu/data/SPITZER/SINGS/galaxies/ngc0925/IRAC/ngc0925_v7.phot.1.fits",
        "SINGS_IRAC1_SizeBytes": "13046400",
        "DeblokTextSupport": "constant_disk_ML_0p65_no_bright_central_component",
        "BulgePolicySeed": "zero_bulge_candidate_from_deBlok_text_before_scoring",
        "MLPolicySeed": "disk_ML_3p6_equals_0p65",
    },
    {
        "GalaxyName": "NGC3031",
        "CandidatePriority": "primary_candidate",
        "THINGS_MOM0_URL": "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_3031_NA_MOM0_THINGS.FITS",
        "THINGS_MOM0_SizeBytes": "19465920",
        "THINGS_RO_MOM0_URL": "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_3031_RO_MOM0_THINGS.FITS",
        "THINGS_RO_MOM0_SizeBytes": "not_head_verified_in_this_packet",
        "SINGS_IRAC1_URL": "https://irsa.ipac.caltech.edu/data/SPITZER/SINGS/galaxies/ngc3031/IRAC/ngc3031_v7.phot.1.fits",
        "SINGS_IRAC1_SizeBytes": "42042240",
        "DeblokTextSupport": "disk_ML_0p8_central_component_ML_1p0_exp_disk_mu0_12p2_h_0p25kpc",
        "BulgePolicySeed": "central_component_required_from_deBlok_text_before_scoring",
        "MLPolicySeed": "disk_ML_3p6_equals_0p8_central_component_ML_3p6_equals_1p0",
    },
    {
        "GalaxyName": "NGC3621",
        "CandidatePriority": "secondary_candidate",
        "THINGS_MOM0_URL": "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_3621_NA_MOM0_THINGS.FITS",
        "THINGS_MOM0_SizeBytes": "not_head_verified_in_this_packet",
        "THINGS_RO_MOM0_URL": "https://www2.mpia-hd.mpg.de/THINGS/Data_files/NGC_3621_RO_MOM0_THINGS.FITS",
        "THINGS_RO_MOM0_SizeBytes": "not_head_verified_in_this_packet",
        "SINGS_IRAC1_URL": "https://irsa.ipac.caltech.edu/data/SPITZER/SINGS/galaxies/ngc3621/IRAC/ngc3621_v7.phot.1.fits",
        "SINGS_IRAC1_SizeBytes": "directory_listing_confirms_file",
        "DeblokTextSupport": "surface_brightness_profiles_and_mass_models_discussed",
        "BulgePolicySeed": "needs_protocol_review_before_scoring",
        "MLPolicySeed": "needs_protocol_review_before_scoring",
    },
]


def inventory_rows() -> list[dict[str, str]]:
    rows = []
    for gal in GALAXIES:
        rows.append(
            {
                "GalaxyName": gal["GalaxyName"],
                "CandidatePriority": gal["CandidatePriority"],
                "ObservedRotationCandidate": "THINGS_velocity_field_or_published_deBlok_rotation_curve",
                "GasInputCandidate": "THINGS_MOM0_available_for_Vgas_derivation",
                "StellarInputCandidate": "SINGS_IRAC_3p6um_channel1_available_for_Vdisk_derivation",
                "BulgePolicySeed": gal["BulgePolicySeed"],
                "MLPolicySeed": gal["MLPolicySeed"],
                "DeblokTextSupport": gal["DeblokTextSupport"],
                "CurrentCompleteness": "source_inputs_identified_not_component_arrays",
                "CanScoreNow": "no",
                "NextRequiredStep": "download_manifest_then_component_extraction_protocol_run",
                "Guardrail": GUARDRAIL,
            }
        )
    return rows


def manifest_rows() -> list[dict[str, str]]:
    rows = []
    for gal in GALAXIES:
        rows.extend(
            [
                {
                    "GalaxyName": gal["GalaxyName"],
                    "SourceRole": "THINGS_HI_MOM0_NA",
                    "URL": gal["THINGS_MOM0_URL"],
                    "SizeBytes": gal["THINGS_MOM0_SizeBytes"],
                    "Use": "gas_component_candidate",
                    "RedistributionPolicy": "source_url_only_no_raw_redistribution",
                },
                {
                    "GalaxyName": gal["GalaxyName"],
                    "SourceRole": "THINGS_HI_MOM0_RO",
                    "URL": gal["THINGS_RO_MOM0_URL"],
                    "SizeBytes": gal["THINGS_RO_MOM0_SizeBytes"],
                    "Use": "gas_component_crosscheck_candidate",
                    "RedistributionPolicy": "source_url_only_no_raw_redistribution",
                },
                {
                    "GalaxyName": gal["GalaxyName"],
                    "SourceRole": "SINGS_IRAC1_3p6um",
                    "URL": gal["SINGS_IRAC1_URL"],
                    "SizeBytes": gal["SINGS_IRAC1_SizeBytes"],
                    "Use": "stellar_component_candidate",
                    "RedistributionPolicy": "source_url_only_no_raw_redistribution",
                },
            ]
        )
    return rows


def gate_rows() -> list[dict[str, str]]:
    return [
        {
            "GateID": "R2INV01",
            "Status": "at_least_two_primary_candidates_identified",
            "Galaxies": "NGC925;NGC3031",
            "Meaning": "both have THINGS HI source products, SINGS 3p6um source products, and deBlok text seeds for M/L and bulge policy",
            "CanScoreNow": "no",
        },
        {
            "GateID": "R2INV02",
            "Status": "component_arrays_not_yet_derived",
            "Galaxies": "NGC925;NGC3031",
            "Meaning": "source products are available, but radius-matched Vobs,Vgas,Vdisk,Vbul arrays still need extraction",
            "CanScoreNow": "no",
        },
        {
            "GateID": "R2INV03",
            "Status": "N15_gate_still_blocked",
            "Galaxies": "THINGS",
            "Meaning": "two candidates are promising but not score-ready",
            "CanScoreNow": "no",
        },
    ]


def write_report() -> None:
    lines = [
        "# THINGS Route 2 Input Inventory v0.1",
        "",
        "This packet searches for source inputs that could complete at least two missing THINGS galaxies under the frozen route 2 protocol. It does not download raw products into the public repository and does not compute new `W_tau_eff` scores.",
        "",
        "## Primary Candidates",
        "",
        "- `NGC925`: THINGS HI moment products are available; SINGS IRAC 3.6 micron channel 1 is available; de Blok et al. text gives a constant disk `M/L_3.6 = 0.65` and no bright central component.",
        "- `NGC3031`: THINGS HI moment products are available; SINGS IRAC 3.6 micron channel 1 is available; de Blok et al. text gives disk `M/L_3.6 = 0.8`, central component `M/L_3.6 = 1.0`, and an exponential central component seed.",
        "",
        "## Status",
        "",
        "The minimum two-galaxy source-input target is reachable at the source-product level, but not yet score-ready. The next step is to download or stage the referenced products outside the public repository and derive radius-matched component arrays under the frozen protocol.",
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
    for path in [INVENTORY, MANIFEST, GATE, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_route2_input_inventory_status"] = (
        "two_primary_source_input_candidates_identified_not_score_ready"
    )
    manifest["paper2_next_gate"] = "route2_stage_NGC925_NGC3031_inputs_outside_public_repo"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_csv(
        INVENTORY,
        inventory_rows(),
        [
            "GalaxyName",
            "CandidatePriority",
            "ObservedRotationCandidate",
            "GasInputCandidate",
            "StellarInputCandidate",
            "BulgePolicySeed",
            "MLPolicySeed",
            "DeblokTextSupport",
            "CurrentCompleteness",
            "CanScoreNow",
            "NextRequiredStep",
            "Guardrail",
        ],
    )
    write_csv(
        MANIFEST,
        manifest_rows(),
        ["GalaxyName", "SourceRole", "URL", "SizeBytes", "Use", "RedistributionPolicy"],
    )
    write_csv(
        GATE,
        gate_rows(),
        ["GateID", "Status", "Galaxies", "Meaning", "CanScoreNow"],
    )
    write_report()
    update_manifest()
    print(REPORT)


if __name__ == "__main__":
    main()
