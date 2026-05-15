# External Source Acquisition Plan v0.1

This packet freezes the first acquisition plan for expanding non-WHISP external validation. It records public source locations and required derived fields, but it does not redistribute raw survey products and does not open a velocity endpoint.

## Priority Sources

- SRC01 -> EVT01 (THINGS harmonic velocity-field controls): audit paper tables and existing THINGS overlap against SPARC names; access=https://arxiv.org/abs/0810.2116.
- SRC02 -> EVT02 (LITTLE THINGS pressure-support controls): inventory MOM2 velocity-dispersion products and SPARC dwarf aliases; access=https://science.nrao.edu/science/surveys/littlethings/data.
- SRC03 -> EVT03 (HALOGAS linewidth or cube-derived stress): download only needed cube/moment files locally with size and MD5 verification; access=https://zenodo.org/records/2552349.
- SRC04 -> EVT04 (non-WHISP resolved HI asymmetry catalogues): crossmatch catalogue names against SPARC and current Paper 1 A/C labels; access=https://doi.org/10.1093/mnras/staa597.
- SRC05 -> EVT05 (observer-distance/resolution matched external sample): define matching variables before adding any new velocity endpoint; access=https://astroweb.cwru.edu/SPARC/.

## Required Fields

- FLD01 (all_sources): GalaxyName [required=yes; use=join_only].
- FLD02 (all_sources): SourceFamily [required=yes; use=stratification_and_reporting].
- FLD03 (THINGS): NonCircularAmplitudeOrHarmonicResidual [required=yes; use=external_proxy_only].
- FLD04 (LITTLE_THINGS): VelocityDispersionOrSigmaOverVc [required=yes; use=external_proxy_only].
- FLD05 (HALOGAS): LinewidthStressOrCubeDerivedProxy [required=yes; use=external_proxy_only].
- FLD06 (resolved_HI_asymmetry): AsymmetryOrDisturbanceFlag [required=yes; use=external_proxy_only].
- FLD07 (all_sources): DistanceMpc;AngularSizeOrResolution;Inclination [required=yes; use=controls_only].
- FLD08 (all_sources): VobsResidualOrFormulaSelectedQuantity [required=no; use=forbidden].

## Guardrail

Raw FITS cubes or large survey products should remain outside the publication repository unless their licence explicitly permits redistribution and redistribution is necessary. The public packet should prefer source URLs, checksums, download instructions, and derived summary tables.

`source_acquisition_plan_no_raw_data_redistribution_no_velocity_endpoint`
