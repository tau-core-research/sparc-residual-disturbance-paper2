# SPARC Residual-Disturbance Inference v0.1

This study explores the reverse diagnostic question:

```text
residual pattern -> disturbance/coherence class
```

It is intentionally separate from Paper 1. Paper 1 tests whether external,
residual-blind labels predict residual scatter. This packet asks whether
residual structure itself can be used as a diagnostic fingerprint for
disturbance or non-equilibrium candidates.

## Guardrail

This is a prediction/diagnostic pilot, not a Tau Core proof and not an
external-label validation replacement. Any classifier trained on the Paper 1
labels must be treated as exploratory unless it is tested on held-out galaxies
or an independent source family.
