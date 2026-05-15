# Residual-shape inference and external-proxy audit of structural disturbance in SPARC rotation curves

## Abstract

We test whether fixed rotation-curve residual-shape features can recover externally reviewed structural-disturbance labels in the SPARC sample and whether the resulting residual-inferred weight candidate is supported by independent disturbance proxies. The primary internal diagnostic is `Projection_RMS`, evaluated with leave-one-galaxy-out thresholding, shuffled-label null tests, bootstrap uncertainty, baseline-family comparisons, and observability stress checks. In the frozen A/C sample, `Projection_RMS` reaches LOOGO AUC=0.771008403 with empirical shuffled-label p=0.002000000; MOND-like and empirical RAR-like low-acceleration residual scores also separate A/C systems, while a Newtonian baryonic RMS control is near chance. External proxy readouts are mixed: WHISP resolved-HI asymmetry is directionally aligned in a small overlap, WHISP morphology is weaker, Reynolds/LVHIS velocity-field asymmetry is promising but below the frozen minimum sample size, and ALFALFA/HALOGAS readouts are weak or control-like. A THINGS missing-galaxy expansion route was explicitly audited and closed as not score-ready after published machine columns were not recovered and photometry/solver validation failed before scoring. The result is therefore a reproducible diagnostic and external-proxy audit, not a Tau Core validation claim, not a gravity-model selection result, and not independent paper-grade external validation.

## 1. Introduction

Rotation-curve residuals are often treated as model failures, but residual structure can also encode non-equilibrium dynamics, non-circular motions, observational resolution limits, pressure support, deprojection uncertainty, and morphology-dependent systematics. This paper asks a narrower diagnostic question: do fixed residual-shape features carry information about externally reviewed structural disturbance classes?

The answer is useful only if the claim is kept narrow. This paper does not validate Tau Core, does not select a unique gravity model, and does not replace external labels with residual-only labels. It audits whether residual-shape information and independent disturbance proxies point in a consistent direction, and where they fail.

## 2. Data and Frozen Inputs

The internal diagnostic uses the frozen SPARC A/C packet inherited from the residual-blind Paper 1 workflow. B-class systems remain excluded from primary truth labels because they are uncertain by construction. Residual features are derived from the fixed point map and are evaluated under predeclared rules.

The primary internal endpoint is `Projection_RMS`. External catalog readouts are treated as proxy checks, not as training data and not as endpoints for refitting.

## 3. Internal SPARC Residual Diagnostic

The primary classifier is intentionally simple: leave one galaxy out, recompute the A/C threshold from the remaining galaxies, and classify the held-out system by whether its residual score is above or below the frozen direction. `Projection_RMS` reaches LOOGO AUC=0.771008403 and accuracy=0.755555556. A shuffled-label null gives empirical p=0.002000000, and the bootstrap 95% AUC interval is [0.600802469, 0.909100262].

This is the strongest current Paper 2 result. It shows that residual-shape features recover external A/C information better than chance in the current SPARC packet. It does not show that the residual score is physically unique or that the underlying projection formula is validated.

## 4. Baseline-Family Comparison

The baseline-family comparison is important because it prevents over-branding the result. MOND-simple RMS reaches AUC=0.720588235, and empirical RAR-like RMS reaches AUC=0.731092437. The Newtonian baryonic RMS control is near chance at AUC=0.506302521.

The clean interpretation is that A/C separation appears mainly in low-acceleration residual-family scores. Projection-specific uniqueness is not established.

## 5. External Proxy Readouts

The external readouts are informative but not yet paper-grade validation. WHISP resolved-HI asymmetry is the strongest positive external context, with N=14, Pearson=0.391218683, and AUC=0.714285714. WHISP morphology is weaker and mixed: the Asymmetry A split is directionally suggestive, while the composite morphology burden is close to neutral.

Non-WHISP sources remain underpowered or mixed. Reynolds/LVHIS velocity-field asymmetry is promising after alias resolution, but N=6 is below the frozen N>=15 gate. ALFALFA profile asymmetry has larger overlap but weak directionality. HALOGAS is retained as a small-overlap control, not as positive validation.

## 6. Negative Audit: THINGS Route2 Closure

The THINGS route2 expansion was tested because adding missing THINGS galaxies could have strengthened the external validation story. That path is now closed as not score-ready. Official machine-readable SPARC and de Blok sources did not expose per-radius `R,Vobs,eVobs,Vgas,Vdisk,Vbul` columns for the missing galaxies. A reconstruction route was explored, but photometry and solver validation failed before missing-galaxy scoring.

This closure is a strength of the audit. It prevents synthetic mass models, plot digitization, or endpoint-driven reconstruction from entering the evidence chain. THINGS route2 is therefore a negative audit appendix, not positive evidence.

## 7. Limitations and Phase II

The current result is meaningful but bounded. The internal SPARC diagnostic is positive; external proxy support is mixed; observability and source-family selection remain important limitations. The work should be presented as a residual-inference audit with cautious external-proxy context.

The next paper-grade validation step is not more opportunistic data chasing. It is a frozen external source-family test with enough overlap, a predeclared evidence rule, no velocity endpoint refit, and explicit failure conditions.
