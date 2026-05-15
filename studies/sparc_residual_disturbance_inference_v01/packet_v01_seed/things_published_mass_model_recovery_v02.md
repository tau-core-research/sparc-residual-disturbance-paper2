# THINGS Published Mass-Model Recovery Audit v0.2

This audit rechecks whether published machine-readable mass-model columns can be recovered for the missing THINGS Table 3 galaxies. It explicitly separates official machine-readable tables from figures, paper text, and reconstruction inputs.

## Sources Checked

- `SPARC_ROTMOD_LTG`: exists=yes, size=110737, use=machine_per_radius_R_Vobs_eVobs_Vgas_Vdisk_Vbul_if_galaxy_present.
- `SPARC_TABLE2_MRT`: exists=yes, size=269518, use=machine_mass_model_summary_and_per_radius_status_check.
- `SPARC_MASS_MODEL_FIGURES`: exists=yes, size=5113182, use=figure_presence_only_not_machine_columns.
- `DEBLOK2008_ARXIV_SOURCE`: exists=yes, size=255982, use=method_global_fit_tables_geometry_ML_policy_but_not_machine_per_radius_columns.

## Recovery Results

- `NGC925`: SPARC rotmod=absent, SPARC Table2=absent, deBlok source mention=yes, recovered=no.
- `NGC3031`: SPARC rotmod=absent, SPARC Table2=absent, deBlok source mention=yes, recovered=no.
- `NGC3621`: SPARC rotmod=absent, SPARC Table2=absent, deBlok source mention=yes, recovered=no.
- `NGC3627`: SPARC rotmod=absent, SPARC Table2=absent, deBlok source mention=yes, recovered=no.
- `NGC4736`: SPARC rotmod=absent, SPARC Table2=absent, deBlok source mention=yes, recovered=no.

## Decision

- `TPMMR02D01`: insufficient_for_THINGS_N15 (score_ready_recovered=0).
- `TPMMR02D02`: keep_route2_blocked_no_synthetic_mass_models (official_SPARC_and_deBlok_sources_do_not_expose_missing_per_radius_columns).

Conclusion: the published machine-readable route still does not recover score-ready `R,Vobs,eVobs,Vgas,Vdisk,Vbul` rows for at least two of the missing galaxies. The route remains blocked unless original ROTMOD-style tables are obtained from an author/supplementary archive or another citable machine-readable source.

No synthetic mass-model columns are created here.
No `W_tau_eff` score is computed here.

Guardrail: `published_mass_model_recovery_no_synthetic_columns_no_scores`
