# Observer-Distance WHISP External Validation v0.1

This readout tests the observer-distance hypothesis inside the WHISP source-family overlap. It does not open a velocity endpoint and it is not class-balanced; the current overlap contains only C-class galaxies.

## Readout

- Joined WHISP galaxies: 10
- Class coverage: C
- Raw tau-distance Pearson: 0.167726020
- Raw tau-distance AUC: 0.560000000
- Partial Pearson after WHISP controls: -0.224079320
- Partial AUC after WHISP controls: 0.360000000

## Decision

`direction_not_reproduced_in_small_whisp_overlap`

raw Pearson=0.167726020; partial Pearson=-0.224079320; partial AUC=0.360000000.

This is a small source-family sanity check. It can support or weaken the hypothesis direction, but it cannot validate a Tau Core field or velocity formula.

## Generated Files

- `observer_distance_whisp_external_validation_join_v01.csv`
- `observer_distance_whisp_external_validation_metrics_v01.csv`
- `observer_distance_whisp_external_validation_decision_v01.csv`

## Guardrail

`whisp_external_validation_no_velocity_endpoint_no_formula_selection`
