#!/usr/bin/env python3
"""Freeze acquisition plan for expanded external validation sources."""

from __future__ import annotations

import json

from make_packet_v01_seed import PACKET, write_csv


SOURCE_OUT = PACKET / "external_source_acquisition_plan_v01.csv"
FIELD_OUT = PACKET / "external_source_required_fields_v01.csv"
REPORT = PACKET / "external_source_acquisition_plan_v01.md"

GUARDRAIL = "source_acquisition_plan_no_raw_data_redistribution_no_velocity_endpoint"


def source_rows() -> list[dict[str, str]]:
    return [
        {
            "SourceID": "SRC01",
            "TargetID": "EVT01",
            "SourceFamily": "THINGS harmonic velocity-field controls",
            "PrimaryReference": "Trachternach et al. 2008, AJ 136, 2720",
            "AccessURL": "https://arxiv.org/abs/0810.2116",
            "DataAccessMode": "published_tables_or_manually_curated_summary",
            "CandidateSPARCOverlap": "DDO154;NGC2366;NGC2403;NGC2976;NGC3198;NGC5055;NGC7331",
            "ExpansionGoal": "recover all usable THINGS harmonic galaxies with SPARC overlap",
            "RedistributionPolicy": "store derived summary columns only",
            "FirstAction": "audit paper tables and existing THINGS overlap against SPARC names",
            "Priority": "high",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "SourceID": "SRC02",
            "TargetID": "EVT02",
            "SourceFamily": "LITTLE THINGS pressure-support controls",
            "PrimaryReference": "Hunter et al. 2012 LITTLE THINGS survey; public NRAO data products",
            "AccessURL": "https://science.nrao.edu/science/surveys/littlethings/data",
            "DataAccessMode": "public_FITS_products_or_derived_summary_only",
            "CandidateSPARCOverlap": "DDO154;DDO168;NGC2366",
            "ExpansionGoal": "identify additional SPARC dwarf overlap or replacement pressure-support catalogue",
            "RedistributionPolicy": "do not commit FITS cubes; commit source URL and derived summary",
            "FirstAction": "inventory MOM2 velocity-dispersion products and SPARC dwarf aliases",
            "Priority": "medium",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "SourceID": "SRC03",
            "TargetID": "EVT03",
            "SourceFamily": "HALOGAS linewidth or cube-derived stress",
            "PrimaryReference": "Heald et al. HALOGAS DR1 public data release",
            "AccessURL": "https://zenodo.org/records/2552349",
            "DataAccessMode": "public_FITS_products_with_MD5_then_derived_summary",
            "CandidateSPARCOverlap": "NGC2403;NGC3198;NGC4559;NGC5055;NGC5585",
            "ExpansionGoal": "extend cube/linewidth stress to all HALOGAS-SPARC overlaps",
            "RedistributionPolicy": "do not commit raw cubes; commit checksums and derived small summary",
            "FirstAction": "download only needed cube/moment files locally with size and MD5 verification",
            "Priority": "medium",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "SourceID": "SRC04",
            "TargetID": "EVT04",
            "SourceFamily": "non-WHISP resolved HI asymmetry catalogues",
            "PrimaryReference": "LVHIS/VIVA/HALOGAS resolved HI asymmetry literature",
            "AccessURL": "https://doi.org/10.1093/mnras/staa597",
            "DataAccessMode": "published_summary_tables_or_literature_curated_flags",
            "CandidateSPARCOverlap": "to_be_crossmatched",
            "ExpansionGoal": "obtain at least 15 non-WHISP resolved-HI asymmetry overlaps",
            "RedistributionPolicy": "store bibliographic provenance and derived flags only",
            "FirstAction": "crossmatch catalogue names against SPARC and current Paper 1 A/C labels",
            "Priority": "high",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "SourceID": "SRC05",
            "TargetID": "EVT05",
            "SourceFamily": "observer-distance/resolution matched external sample",
            "PrimaryReference": "SPARC metadata plus external source-family controls",
            "AccessURL": "https://astroweb.cwru.edu/SPARC/",
            "DataAccessMode": "metadata_join_and_matched_summary_only",
            "CandidateSPARCOverlap": "all Paper 2 galaxies with external source-family rows",
            "ExpansionGoal": "build matched A/C or matched source-family split with N>=20",
            "RedistributionPolicy": "store derived matching table only",
            "FirstAction": "define matching variables before adding any new velocity endpoint",
            "Priority": "high",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def field_rows() -> list[dict[str, str]]:
    return [
        {
            "FieldID": "FLD01",
            "AppliesTo": "all_sources",
            "FieldName": "GalaxyName",
            "Required": "yes",
            "Purpose": "SPARC join key after alias normalization",
            "AllowedUse": "join_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "FieldID": "FLD02",
            "AppliesTo": "all_sources",
            "FieldName": "SourceFamily",
            "Required": "yes",
            "Purpose": "held-out family tracking",
            "AllowedUse": "stratification_and_reporting",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "FieldID": "FLD03",
            "AppliesTo": "THINGS",
            "FieldName": "NonCircularAmplitudeOrHarmonicResidual",
            "Required": "yes",
            "Purpose": "non-circular motion competitor",
            "AllowedUse": "external_proxy_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "FieldID": "FLD04",
            "AppliesTo": "LITTLE_THINGS",
            "FieldName": "VelocityDispersionOrSigmaOverVc",
            "Required": "yes",
            "Purpose": "dwarf pressure-support control",
            "AllowedUse": "external_proxy_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "FieldID": "FLD05",
            "AppliesTo": "HALOGAS",
            "FieldName": "LinewidthStressOrCubeDerivedProxy",
            "Required": "yes",
            "Purpose": "independent HI cube stress control",
            "AllowedUse": "external_proxy_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "FieldID": "FLD06",
            "AppliesTo": "resolved_HI_asymmetry",
            "FieldName": "AsymmetryOrDisturbanceFlag",
            "Required": "yes",
            "Purpose": "non-WHISP replication of WHISP asymmetry direction",
            "AllowedUse": "external_proxy_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "FieldID": "FLD07",
            "AppliesTo": "all_sources",
            "FieldName": "DistanceMpc;AngularSizeOrResolution;Inclination",
            "Required": "yes",
            "Purpose": "observability and matched-control stress",
            "AllowedUse": "controls_only",
            "InterpretationGuardrail": GUARDRAIL,
        },
        {
            "FieldID": "FLD08",
            "AppliesTo": "all_sources",
            "FieldName": "VobsResidualOrFormulaSelectedQuantity",
            "Required": "no",
            "Purpose": "explicitly forbidden in source acquisition phase",
            "AllowedUse": "forbidden",
            "InterpretationGuardrail": GUARDRAIL,
        },
    ]


def write_report(sources: list[dict[str, str]], fields: list[dict[str, str]]) -> None:
    lines = [
        "# External Source Acquisition Plan v0.1",
        "",
        "This packet freezes the first acquisition plan for expanding non-WHISP external validation. It records public source locations and required derived fields, but it does not redistribute raw survey products and does not open a velocity endpoint.",
        "",
        "## Priority Sources",
        "",
    ]
    for row in sources:
        lines.append(
            f"- {row['SourceID']} -> {row['TargetID']} ({row['SourceFamily']}): "
            f"{row['FirstAction']}; access={row['AccessURL']}."
        )
    lines.extend(
        [
            "",
            "## Required Fields",
            "",
        ]
    )
    for row in fields:
        lines.append(
            f"- {row['FieldID']} ({row['AppliesTo']}): {row['FieldName']} "
            f"[required={row['Required']}; use={row['AllowedUse']}]."
        )
    lines.extend(
        [
            "",
            "## Guardrail",
            "",
            "Raw FITS cubes or large survey products should remain outside the publication repository unless their licence explicitly permits redistribution and redistribution is necessary. The public packet should prefer source URLs, checksums, download instructions, and derived summary tables.",
            "",
            f"`{GUARDRAIL}`",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [SOURCE_OUT, FIELD_OUT, REPORT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["external_source_acquisition_plan_status"] = (
        "source_targets_and_required_fields_frozen"
    )
    manifest["paper2_next_gate"] = "source_alias_crossmatch_before_downloads"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    sources = source_rows()
    fields = field_rows()
    source_fields = [
        "SourceID",
        "TargetID",
        "SourceFamily",
        "PrimaryReference",
        "AccessURL",
        "DataAccessMode",
        "CandidateSPARCOverlap",
        "ExpansionGoal",
        "RedistributionPolicy",
        "FirstAction",
        "Priority",
        "InterpretationGuardrail",
    ]
    field_fields = [
        "FieldID",
        "AppliesTo",
        "FieldName",
        "Required",
        "Purpose",
        "AllowedUse",
        "InterpretationGuardrail",
    ]
    write_csv(SOURCE_OUT, sources, source_fields)
    write_csv(FIELD_OUT, fields, field_fields)
    write_report(sources, fields)
    update_manifest()


if __name__ == "__main__":
    main()
