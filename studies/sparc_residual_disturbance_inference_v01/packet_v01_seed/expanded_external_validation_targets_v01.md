# Expanded External Validation Targets v0.1

This packet freezes the next non-WHISP external validation targets after the WHISP observer-distance stress test. It is a target plan only: it does not add a velocity endpoint, does not fit a formula, and does not promote the observer-distance interpretation.

## Target Order

- EVT01 (THINGS harmonic velocity-field controls): priority=high; minimum N=12; endpoint=W_tau_eff_direction_only.
- EVT02 (LITTLE THINGS dwarf pressure-support controls): priority=medium; minimum N=10; endpoint=dwarf_pressure_systematics_only.
- EVT03 (HALOGAS linewidth or cube-derived stress): priority=medium; minimum N=10; endpoint=linewidth_stress_control_only.
- EVT04 (Non-WHISP resolved HI asymmetry catalogues): priority=high; minimum N=15; endpoint=external_asymmetry_direction_replication.
- EVT05 (Observer-distance and resolution matched external sample): priority=high; minimum N=20; endpoint=observer_distance_hypothesis_stress_only.

## Pass/Fail Gates

- EVG01 (minimum_coverage): not_yet_met.
- EVG02 (class_or_source_balance): not_yet_met.
- EVG03 (direction_replication): open.
- EVG04 (velocity_endpoint): closed.

## Current Decision

The next useful work is not another in-sample Tau Core interpretation. It is targeted external-data expansion. The highest-value path is either a larger non-WHISP resolved-HI asymmetry family or an expanded THINGS-like kinematic-control family with enough overlap for a predeclared directional readout.

## Generated Files

- `expanded_external_validation_targets_v01.csv`
- `expanded_external_validation_pass_fail_v01.csv`

## Guardrail

`expanded_external_validation_targets_no_velocity_endpoint_no_formula_fit`
