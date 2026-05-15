# THINGS Route 2 Geometry and Solver Protocol v0.1

This packet freezes the geometry, surface-density conversion, and velocity-solver policy for the route 2 reconstruction of NGC925 and NGC3031. It is a pre-scoring protocol gate, not a result.

## Frozen Geometry Seeds

- `NGC925`: distance 9.2 Mpc, inclination 66.0 deg, position angle 286.6 deg, systemic velocity 546.3 km/s.
- `NGC3031`: distance 3.6 Mpc, inclination 59.0 deg, position angle 330.2 deg, systemic velocity -39.8 km/s. The staged THINGS header may identify the object as `M81NORTH`; the frozen alias resolution is `NGC3031/M81`.

The geometry seed comes from the THINGS/de Blok adopted parameter table and must not be retuned after inspecting a `W_tau_eff` endpoint.

## Conversion Policy

- THINGS MOM0 images have `JY/B*M/S` units and require a documented beam/pixel conversion into HI surface density before `Vgas` can be derived.
- The gas component uses the already frozen 1.4 helium/metals factor.
- SINGS IRAC1 images have `MJy/sr` units and use fixed de Blok 3.6 micron mass-to-light seeds: 0.65 for NGC925; 0.8 disk plus 1.0 central component for NGC3031.

## Solver Policy

The preferred rule is a GIPSY ROTMOD-equivalent calculation: thin gas disk, stellar `sech^2` disk, and fixed vertical scale `z0 = h/5`. A deterministic internal ring-potential solver is allowed only after separate validation against existing THINGS/SPARC overlap galaxies with known component curves.

No component arrays are derived here.
No `W_tau_eff` score is computed here.

## Next Gate

Validate the component-derivation solver on existing THINGS/SPARC overlap galaxies before applying it to the missing NGC925 and NGC3031 scores.

Guardrail: `geometry_conversion_solver_policy_frozen_no_component_arrays_no_scores`
