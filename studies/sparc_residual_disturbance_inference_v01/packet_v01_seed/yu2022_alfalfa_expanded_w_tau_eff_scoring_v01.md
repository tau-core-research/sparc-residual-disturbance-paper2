# Yu 2022 ALFALFA Expanded W_tau_eff Scoring v0.1

This packet computes frozen-calibration `W_tau_eff` scores for the predeclared Yu et al. (2022) ALFALFA expansion candidates. It does not compute the Af/Ac directional readout.

## Scoring Policy

Existing `W_tau_eff` seed overlaps are retained as anchors without refit. New candidates are scored from SPARC rotmod residual-shape diagnostics and calibrated against the frozen original `W_tau_eff` component distributions.

The first scoring pass requires at least 8 valid radial rotmod points.

## Counts

- Anchors retained without refit: 7
- Scored expansion candidates: 15
- Excluded expansion candidates: 4
- Directional-readout-ready rows: 22
- Expanded scoring gate: met
- Directional readout gate: ready_after_commit

## Exclusions

The following predeclared candidates remain documented but are not scored in this first pass because they have fewer than eight valid radial points:

UGC00634, UGC00891, UGC05999, UGC07261

## Endpoint Boundary

Af and Ac are not used in this script. A separate directional-readout script may join the committed score table to Af/Ac after this packet is committed.

## Generated Files

- `yu2022_alfalfa_expanded_w_tau_eff_point_trace_v01.csv`
- `yu2022_alfalfa_expanded_w_tau_eff_scores_v01.csv`
- `yu2022_alfalfa_expanded_w_tau_eff_summary_v01.csv`
- `yu2022_alfalfa_expanded_w_tau_eff_decision_v01.csv`

## Guardrail

`yu2022_alfalfa_expanded_scoring_no_af_ac_directional_readout`
