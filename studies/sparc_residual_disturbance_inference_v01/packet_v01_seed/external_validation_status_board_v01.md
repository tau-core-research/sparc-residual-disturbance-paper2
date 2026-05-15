# External Validation Status Board v0.1

This board summarizes the current external source-family validation status after the WHISP observer-distance stress test. It is a status readout only: it does not fit coefficients, does not open a velocity endpoint, and does not claim a Tau Core field detection.

## Summary

- P07 (WHISP resolved HI asymmetry): positive_small_source_family_sanity_check; AUC=0.760000000;Pearson=0.441950994.
- ODW (WHISP observer-distance stress): direction_not_reproduced_in_small_whisp_overlap; rawPearson=0.167726020;partialPearson=-0.224079320;partialAUC=0.360000000.
- P05 (THINGS harmonic non-circular motions): does_not_absorb_direction_in_small_overlap; Pearson=0.217454567;AUC=0.333333333.
- P06 (LITTLE THINGS pressure support): too_small_for_directional_validation; N=2 usable overlap.
- P08 (HALOGAS linewidth stress): weak_small_overlap_control_only; N=5 usable overlap.
- R20 (Reynolds 2020 resolved HI asymmetry): catalog_ingested_exact_overlap_below_minimum_n; AmapPearson=0.514475616;AvelPearson=0.063521995.
- LVH (LVHIS alias-resolved Reynolds 2020 asymmetry): alias_resolution_improves_overlap_but_below_minimum_n; AmapPearson=-0.233039744;AvelPearson=0.375346400;AvelAUC=0.777777778.

## Decision

- EVS01: `mixed_external_validation_supporting_w_tau_direction_not_observer_distance`
- EVS02: `closed`

The broad `W_tau_eff` direction still has a positive WHISP source-family sanity check, but the observer-distance hypothesis is not externally validated by WHISP after controls. The Reynolds/LVHIS alias path improves non-WHISP resolved-HI overlap but remains below the frozen directional gate. The next productive step is therefore expanded non-WHISP validation with enough overlap for directional tests.

Current support is therefore for the broad residual-inferred weight direction, not for the observer-distance interpretation.

## Generated Files

- `external_validation_status_board_v01.csv`
- `external_validation_status_decision_v01.csv`

## Guardrail

`external_validation_status_no_velocity_endpoint_no_tau_core_claim`
