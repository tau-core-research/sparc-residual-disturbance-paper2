# Reynolds 2020 SPARC Rotmod Availability Audit v0.1

This audit checks whether the frozen Reynolds et al. (2020) seed-expansion queue has enough locally available SPARC rotmod inputs to support an expanded `W_tau_eff` validation. It records derived availability only and does not redistribute raw SPARC rotmod files.

## Result

- Predeclared expansion candidates: 123
- Rotmod available candidates: 6
- Minimum radial-point gate passed: 5
- High-priority Avel candidates passed: 5
- Passed names: NGC0300;NGC0247;NGC2915;UGCA442;NGC7793
- Expanded validation minimum-N gate: not_met

## Decision

`current_local_sparc_rotmod_overlap_below_minimum_n`

Predeclared candidates=123; rotmod gate passed=5; frozen minimum N=15.

The seed-expansion idea remains methodologically clean, but the currently available local SPARC rotmod overlap is too small for a paper-grade Reynolds directional validation. The next scientific move should either acquire more public SPARC inputs for the predeclared queue or switch to a larger external source family with better overlap.

## Generated Files

- `reynolds2020_sparc_rotmod_availability_v01.csv`
- `reynolds2020_sparc_rotmod_availability_summary_v01.csv`
- `reynolds2020_sparc_rotmod_availability_decision_v01.csv`

## Guardrail

`reynolds2020_sparc_rotmod_availability_no_raw_redistribution`
