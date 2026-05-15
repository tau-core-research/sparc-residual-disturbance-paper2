# W_env_obs Proxy Design v0.1

This gate freezes the first source-side design for predicting the environment/observer weight candidate `W_env_obs`. It intentionally does not evaluate a velocity endpoint and does not select coefficients.

## Frozen Design

- Primary broad prior: `P01` Paper 1 external evidence type.
- Source-family holdout: `P07` WHISP lopsidedness/asymmetry.
- Small-overlap sanity checks: `P03/P04` THINGS stress and geometry proxies.
- Mandatory control: `P09` inclination/systematics.

## Frozen Direction

Regular or low-asymmetry external evidence is treated as lower `W_env_obs` burden. Disturbed HI, tidal, interaction, and warp evidence is treated as higher `W_env_obs` burden. This is directional only; no amplitude or velocity coefficient is fitted here.

## Blocked Actions

- No `S_tau_full` coefficient selection.
- No velocity endpoint readout.
- No use of current-point residuals, empirical `S_tau_eff`, or history-state targets as proxy inputs.

## Next Gate

The next allowed gate is `proxy_direction_vs_W_tau_eff_candidate_score`: test the frozen P01 direction against the already-defined `W_tau_eff` candidate score, then use P07 as a source-family holdout.

## Generated Files

- `w_env_obs_proxy_design_v01.csv`
- `w_env_obs_proxy_rule_freeze_v01.csv`
- `w_env_obs_proxy_endpoint_plan_v01.csv`
