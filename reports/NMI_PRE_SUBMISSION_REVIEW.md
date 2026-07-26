# Nature Machine Intelligence pre-submission review

Manuscript: *A leakage-safe reusability audit of Squidiff for single-cell
temporal prediction*

Article type assessed: Article — Reusability Report

## Reviewer 1 — methods and statistics

### Overall assessment

The revised report asks a well-defined reusability question and separates
functional execution, workflow reconstruction and predictive assessment. Its
strongest methodological feature is the explicit temporal information
boundary: feature selection, model fitting, scale selection and baseline
fitting remain within each training window. Three cutoffs, five predeclared
model seeds, four task-aligned baselines and same-distribution references make
the conclusions substantially more robust than a one-split software
demonstration.

The statistical language is appropriate. Seeds are treated as computational
repeats rather than biological replicates; individual values and mean ± s.d.
are shown; no cell-level or seed-level hypothesis test is used. Biological
sample counts are stated separately, and the D28 result is explicitly
descriptive because it contains one test sample. The metric panel usefully
separates marginal fit, gene–gene dependence and population composition.

### Major comments

1. No unresolved methodological defect was identified in the revised
   analysis. The pooled diagonal Gaussian has been recomputed from the complete
   training window, and consolidation replaces the earlier affected values
   without changing cached model populations.
2. The early D21/D28 extensions must remain labelled exploratory. The
   manuscript and Supplementary Information do so consistently.
3. The manuscript should not imply biological inference from the late cutoff.
   It currently limits the result to the single deposited D28 sample.

### Minor comments

1. The public versioned archive should contain the consolidated JSON, figure
   source data, scalar CSV files, split manifests and the exact code revision
   used for the final figures.
2. The Reporting Summary should be transferred to the journal’s current form
   at submission rather than submitted only as free-text prepared answers.

### Recommendation

Minor revision, conditional only on archival and form-completion items.

## Reviewer 2 — biological interpretation and scope

### Overall assessment

The report makes a useful biological-methodological distinction: a generator
can preserve some dependence structure while still missing the future
population in marginal and compositional terms. The CAR-NK application is
therefore presented as a test bed for reuse rather than as a mechanistic study
of CAR-NK biology. This is the correct scope for the available deposited data.

The strongest result is not a universal ranking but the cutoff-dependent
comparison with recency and structure-capable baselines. Last-observation
resampling is especially strong at D14, weakens at later endpoints and still
outperforms Squidiff on energy distance. The factor Gaussian shows that
preserving covariance does not uniquely require a diffusion model. The
released VO analysis is correctly retained as a target-informed mechanism
check and is not used to support out-of-sample generalization.

### Major comments

1. Broader biological claims would require independent studies, laboratories
   or interventions. The revised Discussion clearly restricts inference to one
   dataset, one model family and training-selected 500-gene representations.
2. The D28 population contains many cells but only one biological sample. The
   revised wording correctly avoids treating cells as independent biological
   replication.

### Minor comments

1. Authors should verify that the supplied author-contribution statement
   accurately reflects responsibility for biological interpretation as well as
   software work.
2. The final public archive should preserve sample identifiers and cutoff
   manifests so readers can reconstruct the biological units behind every
   reported `n`.

### Recommendation

Minor revision. The scientific limitations are material but transparently
reported and compatible with a Reusability Report.

## Reviewer 3 — software reuse and reproducibility

### Overall assessment

The report provides unusually clear evidence separation for a software reuse
study. The released checkpoint is tested by strict state-dictionary loading
and finite sampling. Interface failures are localized to dtype, device and
rank handling in the label-conditional path, and the manuscript does not
misattribute them to the released encoder-development configuration, which
disabled class conditioning. The expression-scale and latent-noise checks
identify executable assumptions that are easy for downstream users to miss.

Reproducibility metadata are strong: the upstream commit is pinned; training
seeds and hyperparameters are fixed; Python, CUDA and package versions are
recorded; remote source and result archives are hash checked; and a
machine-readable single source of truth drives the final figures. The software
checklist and regression tests connect prose claims to executable artefacts.

### Major comments

1. The separate Splatter input behind an institution-specific path was not
   available. The report appropriately limits its simulation claim to the
   accessible Gaussian notebook rather than speculating about the missing
   input.
2. The existing code and data DOIs predate the final three-cutoff artefacts.
   A new versioned public release is needed before publication, and the
   manuscript must not imply that the older records already contain the final
   files.

### Minor comments

1. Confirm repository access from a clean environment and ensure that no
   credentials, local paths or large private checkpoints enter the submission
   archive.
2. Preserve the generative-AI disclosure in Methods and retain human
   responsibility for text, code and analysis.

### Recommendation

Minor revision, focused on public release and clean-environment verification.

## Cross-review synthesis

All three reviewers agree that the report now fits the Reusability Report
concept: it evaluates what can be run, what must be reconstructed and what can
support a predictive claim. They also agree that the strongest evidence is the
leakage-safe three-cutoff comparison against recency, marginal, temporal and
structure-capable baselines. No reviewer supports a claim of general
predictive superiority for Squidiff, and the manuscript no longer makes one.

The shared limitations are one independent biological dataset, only five test
samples in the primary cutoff, one sample at D28 and the absence of the
institution-specific Splatter input. These are stated as scope limits rather
than hidden exclusions. The remaining actions are administrative or archival:
author confirmation, transfer of prepared Reporting Summary answers, and a
versioned public deposit of the final code and source-data artefacts.

Consensus recommendation: scientifically ready for editorial assessment after
minor administrative and archival completion. Editorial fit remains a
judgement call because the paper reports a predominantly negative predictive
result, but the result is methodologically informative and directly aligned
with the journal’s reusability remit.
