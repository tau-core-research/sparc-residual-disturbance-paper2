# Source-Side History Proxy Inventory v0.1

This inventory starts the `source_side_history_proxy` gate. It lists residual-free proxy families that could predict `W_env_obs(R)` or compete with it as systematics controls. No velocity endpoint is evaluated here.

## Target

The next model target remains:

`S_tau_full(R)=1+g(W_env_obs(R))`

`W_env_obs(R)` must be predicted from predeclared source-side, geometry-side, environment-side, or observer-state proxies before endpoint readout.

## Inventory Summary

- Proxy families: 9
- Ready broad/holdout proxy IDs: P01, P07
- Mandatory controls include inclination/systematics and non-circular-motion proxies.

## Recommended Next Gate

Freeze one primary source-family holdout design. The safest first target is a two-track design: use Paper 1 external evidence as the broad galaxy-level prior, and WHISP/THINGS families as held-out or small-overlap stress tests. Do not tune a velocity formula from this inventory.

## Generated Files

- `source_side_history_proxy_inventory_v01.csv`
- `source_side_history_proxy_readiness_v01.csv`
