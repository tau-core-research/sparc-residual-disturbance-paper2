# Yu 2022 ALFALFA Seed-Expansion Freeze v0.1

This packet freezes the Yu et al. (2022) ALFALFA profile-asymmetry seed-expansion queue. It does not calculate expanded residual scores and does not compare Af or Ac against `W_tau_eff`.

## Frozen Rule

All Yu2022 ALFALFA rows with AGC<100000 mapped to UGC, local SPARC rotmod availability, and not already in W_tau_eff enter the expansion queue.

The first scoring pass is restricted to primary-quality candidates: S/N>=20 and no catalogue confusion note `c`.

## Counts

- Existing anchors: 7
- Predeclared expansion candidates: 19
- Primary-quality scoring candidates: 19
- Anchors plus primary-quality candidates: 26
- Minimum N gate after expansion: met

## Endpoint Lock

`closed`

The next allowed step is the expanded scoring script. The Af/Ac directional readout remains forbidden until the script and expanded score table are committed.

## Generated Files

- `yu2022_alfalfa_seed_expansion_policy_v01.csv`
- `yu2022_alfalfa_seed_expansion_queue_v01.csv`
- `yu2022_alfalfa_seed_expansion_gate_v01.csv`

## Guardrail

`yu2022_alfalfa_seed_expansion_freeze_no_directional_readout`
