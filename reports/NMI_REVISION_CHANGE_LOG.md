# NMI revision change log

## Article format and claims

- Recast the manuscript as an Article-format Reusability Report under the
  current *Nature Machine Intelligence* content-type instructions.
- Reduced the abstract to the 150-word limit and reorganized the main text into
  an unheaded introduction, Results, Discussion and Methods.
- Replaced exact-reproduction language with separate claims for strict loading,
  finite sampling, executable interfaces and predictive assessment.
- Restricted the released VO analysis to a target-informed mechanism sanity
  check; it does not support out-of-sample generalization.

## Experimental design

- Retained the D0/D7/D14→D21/D28 analysis as the primary temporal cutoff.
- Added an early D0/D7→D14 cutoff with fixed scales 0 and 0.03 and exploratory
  D21/D28 extensions.
- Added a late D0/D7/D14/D21→D28 cutoff whose validation transition remains
  inside the training window.
- Completed five independently initialized 50,000-step training runs for each
  cutoff using seeds 13, 37, 73, 101 and 137.
- Added explicit tests for sample-disjoint splits, training-only feature
  selection and target-free scale selection.

## Baselines and metrics

- Refit four baselines at every cutoff: last-observation resampling, pooled
  diagonal Gaussian, temporal diagonal Gaussian and temporal factor Gaussian.
- Corrected the pooled diagonal Gaussian to use the complete training window.
- Added raw and gene-count-normalized correlation-matrix distance.
- Replaced binary rare-cluster occupancy as the primary composition summary
  with cluster-mass error, Jensen–Shannon divergence, rare-mass recall and
  rare-mass precision.
- Added sensitivity across cluster counts 6, 8, 10 and 12 and rare thresholds
  0.05, 0.10 and 0.15.
- Added same-distribution reference estimates for every cutoff.

## Presentation and submission materials

- Rebuilt the three main figures under a common figure contract with PDF, SVG,
  PNG and TIFF exports and machine-readable source data.
- Corrected reference metadata, including the Squidiff and GEARS volume years,
  and added missing volumes, pages and DOIs.
- Rewrote the Supplementary Information, figure legends and Reporting Summary
  answers to distinguish biological samples from cells and computational
  seeds.
- Added a title page, cover letter, software checklist, readiness checklist,
  checksum manifest and reproducible DOCX/PDF package builder.
- Added a Methods disclosure for generative-artificial-intelligence assistance.
