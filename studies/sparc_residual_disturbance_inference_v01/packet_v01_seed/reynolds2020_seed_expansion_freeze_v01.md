# Reynolds 2020 Seed-Expansion Freeze v0.1

This packet freezes the candidate universe for a possible Reynolds et al. (2020) `W_tau_eff` seed expansion. It intentionally does not calculate any new residual score and does not compare Reynolds asymmetry against an expanded score.

## Frozen Candidate Rule

All Reynolds2020 rows with a resolved canonical name, at least one published asymmetry proxy, and not already in W_tau_eff enter the expansion queue.

A queued galaxy still needs a separate public SPARC rotmod/mass-model availability audit before any expanded `W_tau_eff` score can be generated.

## Counts

- Reynolds rows: 142
- Already in frozen seed: 6
- Predeclared expansion candidates: 123
- High-priority candidates with Avel: 91
- Excluded before scoring: 13
- Candidate breakdown: LVHIS=64; VIVA=45; HALOGAS=14

## Endpoint Lock

`closed`

The next allowed step is an input-availability audit. A Reynolds Amap/Avel directional readout is still forbidden until the availability audit and expanded scoring table are generated and committed.

## Generated Files

- `reynolds2020_seed_expansion_policy_v01.csv`
- `reynolds2020_seed_expansion_candidate_queue_v01.csv`
- `reynolds2020_seed_expansion_gate_v01.csv`

## Guardrail

`reynolds2020_seed_expansion_freeze_no_directional_readout`
