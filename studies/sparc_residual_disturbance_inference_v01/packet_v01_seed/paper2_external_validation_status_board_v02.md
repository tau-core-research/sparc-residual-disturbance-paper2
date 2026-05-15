# Paper 2 External Validation Status Board v0.2

This board supersedes the route2-era working status. Route2 is closed as not score-ready; the paper-facing identity is now a cautious diagnostic and external-proxy audit, not a Tau Core validation claim.

## Family Status

- `CORE`: paper_candidate_with_caveats (primary_internal_diagnostic); metric=Projection_RMS_LOOGO_AUC=0.771008403;shuffle_null_p=0.002000000.
- `WHISP_RESOLVED`: directional_support_but_small_overlap (supporting_external_readout); metric=Pearson=0.391218683;AUC=0.714285714.
- `WHISP_MORPH`: mixed_directional_support (supporting_morphology_readout); metric=AsymmetryA_AUC=0.644230769;MorphologyBurden_AUC=0.506410256.
- `REYNOLDS_LVH`: promising_below_minimum_n (non_WHISP_candidate_support); metric=AvelPearson=0.375346400;AvelAUC=0.777777778.
- `ALFALFA`: weak_or_non_directional (broad_profile_asymmetry_control); metric=Pearson_Af=0.145935541;AUC_high_low=0.472222222.
- `HALOGAS`: weak_control_only (small_overlap_control); metric=Pearson=0.216413317;AUC=0.500000000.
- `THINGS_ROUTE2`: closed_not_score_ready (negative_audit_appendix); metric=closed_not_score_ready;THINGS_N15_not_reached.

## Claim Boundary

- `P2V02_C01`: required - Paper 2 is a diagnostic residual-inference and external-proxy audit, not a Tau Core validation paper.
- `P2V02_C02`: allowed_with_caveat - The strongest positive external context is WHISP resolved-HI, with small-overlap caveats.
- `P2V02_C03`: required - Non-WHISP sources are mixed or underpowered and motivate future validation.
- `P2V02_C04`: required - THINGS route2 is closed as a negative audit, not used as positive evidence.

## Decisions

- `P2V02D01`: diagnostic_external_proxy_audit -> rewrite_paper2_as_cautious_audit_short_paper.
- `P2V02D02`: manuscript_rewrite_before_more_data_chasing -> generate_paper2_v02_manuscript_skeleton_and_update_abstract.

## Bottom Line

Paper 2 remains meaningful as a reproducible residual-inference audit with cautious external-proxy readouts. It is not yet an independent external-validation paper and must not claim Tau Core validation.

Guardrail: `paper2_v02_route2_closed_no_tau_validation_no_velocity_endpoint`
