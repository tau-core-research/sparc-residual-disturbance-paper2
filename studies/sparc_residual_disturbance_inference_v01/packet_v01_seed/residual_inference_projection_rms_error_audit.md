# Projection RMS Error Audit v0.1

This packet audits where the frozen `Projection_RMS` residual-disturbance baseline fails under leave-one-galaxy-out validation.

## Error Counts

- Correct: 34
- False positive A-as-C: 3
- False negative C-as-A: 8

## False Positives

CamB, NGC5585, UGC05764

These are externally regular/calmer galaxies whose residual burden is C-like. They are the most interesting candidates for hidden systematics or a physically hard regular disk.

## False Negatives

NGC5055, UGC04499, UGC05253, UGC05829, UGC05918, UGC06917, UGC07323, UGC12632

These are externally disturbed galaxies whose projection residual burden is low. They show that external disturbance is not guaranteed to appear as high residual RMS.

## Interpretation

The error pattern is scientifically useful: the baseline is fairly precise for C predictions, but misses several C-labeled systems. This supports using residuals as a diagnostic screen, not as a replacement for external evidence.

## Next Gate

Use this audit to define candidate follow-up categories: hidden-systematics A-as-C, quiet-disturbance C-as-A, and robust C-like residual cases. Do not relabel galaxies from residuals alone.

## Generated Files

- `residual_inference_projection_rms_error_audit.csv`
- `residual_inference_projection_rms_error_summary.csv`
