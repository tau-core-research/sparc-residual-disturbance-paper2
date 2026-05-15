#!/usr/bin/env python3
"""Freeze THINGS route 2 geometry, conversion, and solver policy."""

from __future__ import annotations

import json

from make_packet_v01_seed import PACKET, write_csv


GEOMETRY_OUT = PACKET / "things_route2_geometry_policy_v01.csv"
CONVERSION_OUT = PACKET / "things_route2_surface_density_conversion_policy_v01.csv"
SOLVER_OUT = PACKET / "things_route2_velocity_solver_policy_v01.csv"
GATE_OUT = PACKET / "things_route2_geometry_solver_gate_v01.csv"
REPORT_OUT = PACKET / "things_route2_geometry_solver_protocol_v01.md"

GUARDRAIL = "geometry_conversion_solver_policy_frozen_no_component_arrays_no_scores"


def geometry_rows() -> list[dict[str, str]]:
    return [
        {
            "GalaxyName": "NGC925",
            "AliasResolution": "NGC925",
            "GeometrySource": "deBlok_THINGS_adopted_parameters_table",
            "RAJ2000": "02 27 16.5",
            "DEJ2000": "+33 34 43.5",
            "DistanceMpc": "9.2",
            "ScaleArcsecPerKpc": "3.0",
            "VsysKms": "546.3",
            "InclinationDeg": "66.0",
            "PositionAngleDeg": "286.6",
            "RadiusGridPolicy": (
                "use_published_rotation_curve_grid_if_recovered_else_predeclare_annular_grid_before_velocity_extraction"
            ),
            "CanTuneAfterScore": "no",
            "ScoreUse": "frozen_geometry_seed_only_no_score_here",
            "Guardrail": GUARDRAIL,
        },
        {
            "GalaxyName": "NGC3031",
            "AliasResolution": "NGC3031_M81_header_alias_M81NORTH",
            "GeometrySource": "deBlok_THINGS_adopted_parameters_table",
            "RAJ2000": "09 55 33.1",
            "DEJ2000": "+69 03 54.7",
            "DistanceMpc": "3.6",
            "ScaleArcsecPerKpc": "6.0",
            "VsysKms": "-39.8",
            "InclinationDeg": "59.0",
            "PositionAngleDeg": "330.2",
            "RadiusGridPolicy": (
                "use_published_rotation_curve_grid_if_recovered_else_predeclare_annular_grid_before_velocity_extraction"
            ),
            "CanTuneAfterScore": "no",
            "ScoreUse": "frozen_geometry_seed_only_no_score_here",
            "Guardrail": GUARDRAIL,
        },
    ]


def conversion_rows() -> list[dict[str, str]]:
    return [
        {
            "Component": "HI_gas",
            "InputRole": "THINGS_HI_MOM0",
            "InputBUNIT": "JY/B*M/S",
            "FrozenConversionPolicy": (
                "convert_beam_flux_integrated_intensity_to_HI_surface_density_with_documented_beam_and_pixel_scale"
            ),
            "MassFactor": "1.4",
            "MLPolicy": "not_applicable",
            "AllowedInputs": "MOM0_header;beam;pixel_scale;distance;fixed_geometry",
            "ForbiddenInputs": "Vobs;residuals;W_tau_eff;score_direction",
            "CanTuneAfterScore": "no",
            "CanScoreNow": "no",
            "Guardrail": GUARDRAIL,
        },
        {
            "Component": "stellar_disk_NGC925",
            "InputRole": "SINGS_IRAC1_3P6UM",
            "InputBUNIT": "MJy/sr",
            "FrozenConversionPolicy": (
                "convert_IRAC1_surface_brightness_to_stellar_surface_density_using_fixed_deBlok_seed_ML"
            ),
            "MassFactor": "not_applicable",
            "MLPolicy": "disk_ML_3p6_equals_0p65_zero_bulge_candidate",
            "AllowedInputs": "IRAC1_header;pixel_scale;distance;fixed_geometry;frozen_ML_seed",
            "ForbiddenInputs": "Vobs;residuals;W_tau_eff;score_direction",
            "CanTuneAfterScore": "no",
            "CanScoreNow": "no",
            "Guardrail": GUARDRAIL,
        },
        {
            "Component": "stellar_disk_and_central_component_NGC3031",
            "InputRole": "SINGS_IRAC1_3P6UM",
            "InputBUNIT": "MJy/sr",
            "FrozenConversionPolicy": (
                "convert_IRAC1_surface_brightness_to_disk_plus_central_component_using_fixed_deBlok_seed_ML_and_central_exponential"
            ),
            "MassFactor": "not_applicable",
            "MLPolicy": (
                "disk_ML_3p6_equals_0p8_central_component_ML_3p6_equals_1p0_mu0_12p2_h_0p25kpc"
            ),
            "AllowedInputs": "IRAC1_header;pixel_scale;distance;fixed_geometry;frozen_ML_seed;central_component_seed",
            "ForbiddenInputs": "Vobs;residuals;W_tau_eff;score_direction",
            "CanTuneAfterScore": "no",
            "CanScoreNow": "no",
            "Guardrail": GUARDRAIL,
        },
    ]


def solver_rows() -> list[dict[str, str]]:
    return [
        {
            "SolverID": "R2SOLVER01",
            "SolverRole": "preferred_external_equivalent",
            "FrozenPolicy": (
                "GIPSY_ROTMOD_equivalent_thin_HI_disk_and_sech2_stellar_disk_with_z0_equals_h_over_5"
            ),
            "ValidationRequirement": (
                "validate_against_existing_THINGS_SPARC_overlap_before_scoring_missing_galaxies"
            ),
            "AllowedInputs": "surface_density_profiles;fixed_geometry;fixed_vertical_scale_policy",
            "ForbiddenInputs": "Vobs_endpoint_fit;residuals;W_tau_eff;score_direction",
            "CanTuneAfterScore": "no",
            "CanScoreNow": "no",
            "Guardrail": GUARDRAIL,
        },
        {
            "SolverID": "R2SOLVER02",
            "SolverRole": "fallback_internal_solver",
            "FrozenPolicy": (
                "deterministic_ring_potential_solver_allowed_only_after_separate_overlap_validation"
            ),
            "ValidationRequirement": (
                "must_reproduce_existing_SPARC_component_curves_with_predeclared_tolerance_before_use"
            ),
            "AllowedInputs": "surface_density_profiles;fixed_geometry;fixed_numerical_grid",
            "ForbiddenInputs": "Vobs_endpoint_fit;residuals;W_tau_eff;score_direction",
            "CanTuneAfterScore": "no",
            "CanScoreNow": "no",
            "Guardrail": GUARDRAIL,
        },
    ]


def gate_rows() -> list[dict[str, str]]:
    return [
        {
            "GateID": "R2SOLV01",
            "Status": "geometry_policy_frozen_for_NGC925_NGC3031",
            "CanDeriveComponentArraysNow": "partial_after_conversion_script",
            "CanScoreNow": "no",
            "NextAction": "derive_geometry_inventory_and_radius_grid_without_score_feedback",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2SOLV02",
            "Status": "conversion_policy_frozen_not_implemented",
            "CanDeriveComponentArraysNow": "no",
            "CanScoreNow": "no",
            "NextAction": "implement_MOM0_and_IRAC_surface_density_profiles_under_frozen_policy",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2SOLV03",
            "Status": "velocity_solver_policy_frozen_requires_validation",
            "CanDeriveComponentArraysNow": "no",
            "CanScoreNow": "no",
            "NextAction": "validate_solver_on_existing_THINGS_SPARC_overlap_before_missing_scores",
            "Guardrail": GUARDRAIL,
        },
        {
            "GateID": "R2SOLV04",
            "Status": "component_arrays_still_absent",
            "CanDeriveComponentArraysNow": "no",
            "CanScoreNow": "no",
            "NextAction": "do_not_compute_W_tau_eff_until_required_component_arrays_exist",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report() -> None:
    lines = [
        "# THINGS Route 2 Geometry and Solver Protocol v0.1",
        "",
        "This packet freezes the geometry, surface-density conversion, and velocity-solver policy for the route 2 reconstruction of NGC925 and NGC3031. It is a pre-scoring protocol gate, not a result.",
        "",
        "## Frozen Geometry Seeds",
        "",
        "- `NGC925`: distance 9.2 Mpc, inclination 66.0 deg, position angle 286.6 deg, systemic velocity 546.3 km/s.",
        "- `NGC3031`: distance 3.6 Mpc, inclination 59.0 deg, position angle 330.2 deg, systemic velocity -39.8 km/s. The staged THINGS header may identify the object as `M81NORTH`; the frozen alias resolution is `NGC3031/M81`.",
        "",
        "The geometry seed comes from the THINGS/de Blok adopted parameter table and must not be retuned after inspecting a `W_tau_eff` endpoint.",
        "",
        "## Conversion Policy",
        "",
        "- THINGS MOM0 images have `JY/B*M/S` units and require a documented beam/pixel conversion into HI surface density before `Vgas` can be derived.",
        "- The gas component uses the already frozen 1.4 helium/metals factor.",
        "- SINGS IRAC1 images have `MJy/sr` units and use fixed de Blok 3.6 micron mass-to-light seeds: 0.65 for NGC925; 0.8 disk plus 1.0 central component for NGC3031.",
        "",
        "## Solver Policy",
        "",
        "The preferred rule is a GIPSY ROTMOD-equivalent calculation: thin gas disk, stellar `sech^2` disk, and fixed vertical scale `z0 = h/5`. A deterministic internal ring-potential solver is allowed only after separate validation against existing THINGS/SPARC overlap galaxies with known component curves.",
        "",
        "No component arrays are derived here.",
        "No `W_tau_eff` score is computed here.",
        "",
        "## Next Gate",
        "",
        "Validate the component-derivation solver on existing THINGS/SPARC overlap galaxies before applying it to the missing NGC925 and NGC3031 scores.",
        "",
        f"Guardrail: `{GUARDRAIL}`",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [GEOMETRY_OUT, CONVERSION_OUT, SOLVER_OUT, GATE_OUT, REPORT_OUT]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["things_route2_geometry_solver_status"] = (
        "geometry_conversion_solver_policy_frozen_no_component_arrays_no_scores"
    )
    manifest["paper2_next_gate"] = (
        "route2_validate_solver_on_existing_sparc_overlap_before_missing_scores"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_csv(
        GEOMETRY_OUT,
        geometry_rows(),
        [
            "GalaxyName",
            "AliasResolution",
            "GeometrySource",
            "RAJ2000",
            "DEJ2000",
            "DistanceMpc",
            "ScaleArcsecPerKpc",
            "VsysKms",
            "InclinationDeg",
            "PositionAngleDeg",
            "RadiusGridPolicy",
            "CanTuneAfterScore",
            "ScoreUse",
            "Guardrail",
        ],
    )
    write_csv(
        CONVERSION_OUT,
        conversion_rows(),
        [
            "Component",
            "InputRole",
            "InputBUNIT",
            "FrozenConversionPolicy",
            "MassFactor",
            "MLPolicy",
            "AllowedInputs",
            "ForbiddenInputs",
            "CanTuneAfterScore",
            "CanScoreNow",
            "Guardrail",
        ],
    )
    write_csv(
        SOLVER_OUT,
        solver_rows(),
        [
            "SolverID",
            "SolverRole",
            "FrozenPolicy",
            "ValidationRequirement",
            "AllowedInputs",
            "ForbiddenInputs",
            "CanTuneAfterScore",
            "CanScoreNow",
            "Guardrail",
        ],
    )
    write_csv(
        GATE_OUT,
        gate_rows(),
        [
            "GateID",
            "Status",
            "CanDeriveComponentArraysNow",
            "CanScoreNow",
            "NextAction",
            "Guardrail",
        ],
    )
    write_report()
    update_manifest()
    print(REPORT_OUT)


if __name__ == "__main__":
    main()
