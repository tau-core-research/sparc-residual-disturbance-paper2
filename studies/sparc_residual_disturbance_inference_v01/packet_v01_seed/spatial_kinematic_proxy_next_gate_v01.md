# Spatial/Kinematic Proxy Next Gate v0.1

This packet ranks the next validation direction after the Yu et al. (2022) global `Af/Ac` readout. It does not fit a new endpoint, does not change `W_tau_eff`, and does not define a velocity formula.

## Decision

- Primary next gate: select_WHISP_radial_lopsidedness_extension
- Mandatory control: retain_THINGS_non_circular_competition_control
- Negative proxy boundary: do_not_promote_Yu_global_Af_Ac

## Rationale

The global ALFALFA profile-asymmetry readout has useful coverage but does not point in the expected direction. The next useful proxy must therefore be more spatially resolved, more radial, or more kinematically targeted.

WHISP is prioritized because it already gives the strongest external source-family readout in this packet and includes HI lopsidedness/asymmetry quantities with radial structure. THINGS remains mandatory as a non-circular-motion competition control, because a positive disturbance/residual relation could still be ordinary kinematic disequilibrium rather than a Tau Core environment/observer field.

## Generated Files

- `spatial_kinematic_proxy_next_gate_matrix_v01.csv`
- `spatial_kinematic_proxy_next_gate_decision_v01.csv`

## Guardrail

`spatial_kinematic_proxy_gate_no_new_endpoint_fit`
