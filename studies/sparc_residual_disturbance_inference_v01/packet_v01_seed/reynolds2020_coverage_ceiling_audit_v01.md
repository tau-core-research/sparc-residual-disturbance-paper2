# Reynolds 2020 Coverage Ceiling Audit v0.1

This audit asks a narrow reproducibility question: after exact-name matching and LVHIS ID resolution, how much Reynolds et al. (2020) resolved H I asymmetry coverage can the current frozen `W_tau_eff` seed possibly support?

## Result

- Reynolds catalog rows: 142
- Current seed matches after alias resolution: 6
- Matched names: NGC0055;NGC1705;NGC3198;NGC4559;NGC5055;NGC5585
- Frozen minimum directional gate: 15
- Gate status: below_minimum_directional_gate

## Survey Breakdown

- LVHIS: 2/79 matched; names=NGC0055;NGC1705.
- VIVA: 0/45 matched; names=none.
- HALOGAS: 4/18 matched; names=NGC3198;NGC4559;NGC5055;NGC5585.

## Decision

`hard_ceiling_below_gate`

The current W_tau_eff seed can provide at most 6 Reynolds 2020 matches after LVHIS alias resolution; the frozen gate needs at least 15.

This closes the simple-alias route. Reynolds 2020 remains useful as a small external control, especially for checking whether velocity-field asymmetry behaves differently from map asymmetry, but it cannot become a paper-grade non-WHISP validation family without a predeclared seed expansion or a different source family.

## Generated Files

- `reynolds2020_coverage_ceiling_audit_v01.csv`
- `reynolds2020_coverage_ceiling_next_actions_v01.csv`

## Guardrail

`reynolds2020_coverage_ceiling_no_velocity_endpoint`
