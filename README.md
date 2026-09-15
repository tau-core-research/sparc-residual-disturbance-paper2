# SPARC Residual-Disturbance Paper 2

This is the slim public reproducibility package for:

**Residual-shape inference and external-proxy audit of structural disturbance in SPARC rotation curves**

Archived release DOI:

```text
10.5281/zenodo.20285862
```

The repository contains only the files needed to inspect and regenerate the current Paper 2 submission candidate: LaTeX source, bibliography, generated PDF, publication figures, final derived tables, the final regeneration script, and tests.

Raw survey products and raw SPARC rotmod files are not redistributed.

## Author And Research Workflow

I am an independent researcher using an AI-assisted workflow to develop reproducible diagnostic tests around projection-sensitive residual hypotheses. I am not claiming expert-level validation. I would value criticism on whether the proposed gate/falsification structure is scientifically meaningful.

AI systems are used for drafting, mathematical organization, code generation, literature triage, and internal consistency checks. Numerical and symbolic audits can support reproducibility and error-finding, but they do not replace independent expert review or physical validation.

## Theory Context

The broader Tau Core / projection-theory background is maintained separately at:

```text
https://github.com/tau-core-research/tau-core-theory
```

This Paper 2 repository is a standalone reproducibility package. It does not require accepting the Tau Core theory hub; the manuscript should be read as a residual-shape inference and external-proxy audit.

The later observer-specific full-4D Tau descent does not change any reported
AUC or null test. The residual classifier remains a terminal information
diagnostic, not a reconstruction of lapse, shift, spatial geometry, photon
transfer, or a physical Tau metric.

Negative downstream proxy tests constrain the frozen finite morphology maps,
not a source-complete parent body. They also cannot be repaired after endpoint
access: a richer morphology representation must be source-only, frozen before
scoring, and tested on a new untouched packet.

## Current Claim Status

The original LOOGO AUC `0.771008403`, shuffled-label `p=0.002000000`, and
bootstrap interval are preserved as marginal or unconditional within-SPARC
class separation. They do not show that the projection feature adds
conditional information beyond observability, baryonic structure, or
MOND/RAR-common residual structure.

A later Paper 3 repeated-cross-fitting audit found no stable projection-
contrast predictive increment. A separate source-frozen seven-galaxy
EDGE-CALIFA morphology-proxy stress test also failed its directional gate:
mean `D=-0.058679293503004035`, exact one-sided `p=0.6015625`, median
`D=+0.11020194395988532`, and `4/7` positive values. The latter is an external
morphology-proxy stress test, not an independent Tau-specific test or a direct
replication of Paper 2. Conditional projection specificity and independent
matched-tracer replication remain open.

Later Paper 8 public-data routes do not raise that claim. LITTLE THINGS gives
mixed one-family transfer in `N=14`; the PHANGS low-order routes either retain
the morphology-orthogonal null or fail wrong-family/source-label specificity;
and the higher-dimensional PHANGS confirmatory packet fails its frozen
spatial-support gate without releasing a score.

## Main Files

```text
LICENSE
CITATION.cff
DATA_NOTICE.md
requirements.txt
paper2_submission_source/main.tex
paper2_submission_source/references.bib
paper2_submission_source/main.pdf
paper2_submission_source/figures/
arxiv_submission_source.zip
figures/
tests/test_public_reproducibility_package.py
studies/sparc_residual_disturbance_inference_v01/make_paper2_submission_source_v01.py
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/
```

## Final Derived Tables

The core derived tables used by the Paper 2 source generator are kept under:

```text
studies/sparc_residual_disturbance_inference_v01/packet_v01_seed/
```

The retained packet contains:

```text
residual_feature_table.csv
residual_inference_loogo_predictions.csv
residual_inference_projection_rms_error_audit.csv
paper2_external_proxy_summary_v03.csv
paper2_b_class_policy.csv
paper2_calibration_uncertainty.csv
paper2_observability_stress.csv
distance_resolution_environment_join_v01.csv
p09_observability_decomposition_join_v01.csv
multivariable_no_velocity_stress_metrics_v01.csv
paper2_ac_sample_appendix_v01.csv
paper2_baseline_auc_ci_v01.csv
paper2_external_proxy_gate_table_v01.csv
paper2_b_class_sensitivity_v01.csv
paper2_observability_covariate_appendix_v01.csv
paper2_outlier_failure_case_appendix_v01.csv
paper2_stability_effect_size_v01.csv
paper2_submission_source_gate_v01.csv
paper2_submission_readiness_v02.csv
paper2_submission_readiness_v02.md
paper2_figure_typography_audit_v01.csv
paper2_figure_typography_audit_v01.md
```

## Included Paper 1 Inputs

The Paper 2 script uses a small set of derived Paper 1 inputs. They are retained at their original relative paths:

```text
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/taucore_specificity_point_map.csv
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/baseline_score_by_galaxy.csv
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/scale_matched_pairs.csv
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/scale_matched_stress.csv
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/external_evidence_table.csv
```

These are derived reproducibility artifacts, not raw SPARC rotmod files.

## Full-4D Score Boundary

The later compiler requires the source-frozen standard excess
`E_K = (K_HH - K_std) - C K_VV^-1 C^dagger`. Paper 2's residual-shape
classifier does not reconstruct this object, so its AUC and permutation
results remain unchanged diagnostic evidence.

## Reproduce

Install the minimal dependencies:

```bash
python -m pip install -r requirements.txt
```

Regenerate the Paper 2 submission source, figures, derived appendix tables, and PDF:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_paper2_submission_source_v01.py
python -m pytest -q
```

The script requires `tectonic` to regenerate `paper2_submission_source/main.pdf`. If `tectonic` is unavailable, the source files still regenerate, but the PDF gate will report a compile blocker.

## arXiv Source Package

The repository includes:

```text
arxiv_submission_source.zip
```

This ZIP contains only the TeX submission source:

```text
main.tex
references.bib
figures/*.pdf
```

It intentionally excludes build logs, preview files, raw data, and the generated manuscript PDF.

## Data Boundary

The slim repository intentionally excludes:

- raw SPARC rotmod files,
- raw FITS cubes or moment maps,
- downloaded survey webpages and catalogues,
- exploratory Tau Core / S_tau / W_tau branches,
- closed THINGS route2 reconstruction work products,
- local build previews and cache files.

Those materials were useful during development but are not required to reproduce the current paper. Local-only raw and exploratory data were moved to:

```text
/Users/jolcsak/Projects/sparc-residual-disturbance-paper2_local_archive
```

That local archive is not part of the public publication repository.

<!-- BEGIN OBSERVER UPDATE 20260914 -->
## Observer realization update (2026-09-14)

For galactic inference, these observer constructions do not derive a rotation-curve correction or identify a measured residual as a parent effect. Existing endpoint freezes and scores are unchanged.

The manuscript distinguishes inherited BRAC contact, conditional coherent-state
selection and interacting local covariance from physical observer identification,
preparation and stable resolution. Those physical claims remain open. No
empirical score was changed. The [dependency and source-result ledger](data/derived/observer_update_2026_09_14.json) records the assumptions and controls.
<!-- END OBSERVER UPDATE 20260914 -->
