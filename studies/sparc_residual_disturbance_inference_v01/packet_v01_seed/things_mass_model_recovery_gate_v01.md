# THINGS Mass-Model Recovery Gate v0.1

This gate implements the requested order: first attempt direct recovery of public, compatible mass-model columns; if that does not work, move to a frozen reconstruction protocol.

## Route 1 Result

Checked missing galaxies: NGC925, NGC3031, NGC3621, NGC3627, NGC4736.

Direct score-ready public tables were not recovered for the missing five. The public SPARC LTG rotmod archive and SPARC machine-readable mass-model table do not include these rows, while the de Blok et al. source package documents the mass-model analysis without exposing SPARC-style per-radius `Vobs`, `Vgas`, `Vdisk`, and `Vbul` columns for these objects.

This closes route 1 for immediate scoring. It does not mean the galaxies are unusable; it means the current public-table path is not enough.

## Route 2 Opened

Route 2 is allowed only as a pre-registered reconstruction protocol. The protocol must be committed before any new `W_tau_eff` score is computed, and it must not tune gas, stellar, or mass-to-light choices to improve the endpoint.

## Route 2 Minimum

To cross the THINGS N>=15 gate, at least two of the five missing galaxies must receive frozen, source-documented per-radius baryonic components.

## Generated Files

- `things_mass_model_recovery_gate_v01.csv`
- `things_mass_model_route2_reconstruction_plan_v01.csv`
- `things_mass_model_recovery_gate_decision_v01.csv`

## Guardrail

`route1_then_route2_no_score_from_plots_no_target_refit`
