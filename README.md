# SPARC Residual-Disturbance Paper 2

This is the slim public reproducibility package for:

**Residual-shape inference and external-proxy audit of structural disturbance in SPARC rotation curves**

Archived release DOI:

```text
10.5281/zenodo.20210154
```

The repository contains only the files needed to inspect and regenerate the current Paper 2 submission candidate: LaTeX source, bibliography, generated PDF, publication figures, final derived tables, the final regeneration script, and tests.

Raw survey products and raw SPARC rotmod files are not redistributed.

## Theory Context

The broader Tau Core / projection-theory background is maintained separately at:

```text
https://github.com/tau-core-research/tau-core-theory
```

This Paper 2 repository is a standalone reproducibility package. It does not require accepting the Tau Core theory hub; the manuscript should be read as a residual-shape inference and external-proxy audit.

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
