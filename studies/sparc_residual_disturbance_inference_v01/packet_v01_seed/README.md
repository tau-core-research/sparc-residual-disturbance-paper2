# Paper 2 Slim Packet

This packet contains the final derived inputs and outputs needed by the Paper 2 submission-source generator.

It is not a full development archive. Earlier exploratory branches, raw-source manifests, Tau Core/S_tau probes, and closed external-validation work products were removed from the public slim repository.

The retained files support:

- primary residual-shape endpoint regeneration,
- baseline-family comparison,
- B-class sensitivity,
- observability/nuisance stress summaries,
- named outlier appendix,
- stability and effect-size appendix,
- source-gate and figure-audit records.

Regenerate the derived appendix tables and submission source with:

```bash
python studies/sparc_residual_disturbance_inference_v01/make_paper2_submission_source_v01.py
```
