# THINGS Route 2 Input Inventory v0.1

This packet searches for source inputs that could complete at least two missing THINGS galaxies under the frozen route 2 protocol. It does not download raw products into the public repository and does not compute new `W_tau_eff` scores.

## Primary Candidates

- `NGC925`: THINGS HI moment products are available; SINGS IRAC 3.6 micron channel 1 is available; de Blok et al. text gives a constant disk `M/L_3.6 = 0.65` and no bright central component.
- `NGC3031`: THINGS HI moment products are available; SINGS IRAC 3.6 micron channel 1 is available; de Blok et al. text gives disk `M/L_3.6 = 0.8`, central component `M/L_3.6 = 1.0`, and an exponential central component seed.

## Status

The minimum two-galaxy source-input target is reachable at the source-product level, but not yet score-ready. The next step is to download or stage the referenced products outside the public repository and derive radius-matched component arrays under the frozen protocol.

## Guardrail

`route2_input_inventory_no_new_scores_no_endpoint_tuning`
