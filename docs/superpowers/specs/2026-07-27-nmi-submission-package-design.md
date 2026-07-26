# NMI reusability report: complete revision and submission-package design

Date: 2026-07-27

## Objective

Revise the Squidiff reusability report so that every scientific claim is
supported by an evaluation with the same information boundary as the claimed
prediction task, every manuscript component reports the same result version,
and the final deliverables form a complete initial-submission package for
Nature Machine Intelligence (NMI).

The approved scope is the evidence-first complete revision ("方案 A"): add two
temporal-cutoff retraining studies, add fair temporal and structure-capable
baselines, strengthen the structure-metric audit, moderate claims that cannot
be closed experimentally, and rebuild all submission materials.

## Source-of-truth rules

1. `manuscript/reusability_report.md` is the live manuscript.
   `reusability_report_draft.md` remains archival and is never packaged.
2. Numerical statements must be generated from machine-readable artifacts;
   manually copied result text is treated as a derived view.
3. The held-out population for a split must not influence model training,
   feature selection, normalization fitting, noise-scale selection or baseline
   fitting.
4. Biological samples, not cells, are the independent observational units.
   Cell-level summaries may describe populations but must not be presented as
   independent biological replication.
5. The released VO experiment uses day-1 target information and is therefore a
   target-informed reconstruction sanity check, not an external prediction
   control.
6. Claims about the "published configuration" must distinguish the published
   mechanism from dataset-adapted training choices.

## Experimental design

### Existing primary split

- Train: pre-infusion, D7 and D14; 11,588 cells from 13 samples.
- Test: D21 and D28; 4,668 cells from 5 samples.
- Retain the existing five seeds: 13, 37, 73, 101 and 137.
- Retain training-only noise-scale selection: pre-infusion to D7 direction,
  scored against D14.
- Retain the existing result as the primary external-reuse analysis.

### New early-cutoff stress test

- Train the model on pre-infusion and D7 only.
- Fit normalization and the 500 highly variable genes on this training
  population only.
- Estimate the extrapolation direction from pre-infusion to D7.
- Test D14 as the one-step future target; report D21 and D28 only as
  increasingly distant exploratory horizons.
- Because no third training time point is available for nested noise-scale
  validation, pre-specify the two near-zero settings supported by the primary
  analysis (`0.0` and `0.03`) and report their sensitivity without selecting
  between them on test data.
- Train five independently initialized models using the existing seed set.

### New late-cutoff replication

- Train the model on pre-infusion, D7, D14 and D21.
- Fit normalization and feature selection on that training population only.
- Estimate the test direction from D14 to D21 and predict D28.
- Select the noise scale using only earlier training data: estimate D7 to D14
  and score the one-step prediction against D21.
- Test only the D28 sample; describe the single-sample boundary explicitly and
  avoid population-level generality claims.
- Train five independently initialized models using the existing seed set.

### Training configuration

- Use the released model mechanism (`class_cond=False`, `use_encoder=True`,
  `num_layers=3`, `diffusion_steps=1000`).
- Use the existing CAR-NK training budget of 50,000 steps and batch size 64 so
  the cutoff study isolates the temporal split rather than mixing split and
  optimization changes.
- Label this configuration "published latent-extrapolation mechanism with
  dataset-adapted training choices", not "published configuration".
- Record every model checkpoint, seed, input hash, feature list, split manifest,
  wall time and selected/fixed noise scale.

## Baseline design

All baselines use only the training data available at each temporal cutoff.

1. **Last observation**: resample cells from the latest observed time point.
2. **Pooled diagonal Gaussian**: retain as a deliberately static marginal
   baseline, but do not describe it as performing temporal extrapolation.
3. **Temporal diagonal Gaussian**: extrapolate per-gene means from the last two
   observed time points and estimate diagonal residual variance from training
   data. This is the task-aligned simple baseline.
4. **Temporal factor Gaussian**: fit a training-only PCA/factor covariance
   representation, extrapolate factor means over the last two observed time
   points and sample in factor space plus diagonal residual noise. This is the
   structure-capable baseline.

Hyperparameters for the factor baseline (component count and any shrinkage)
must be selected from training data only. A small pre-specified grid will be
used, with the smallest dimension explaining at least 90% of training
variance as the default when nested validation is unavailable.

## Metrics and uncertainty

### Primary metrics

- Multivariate energy distance.
- Per-gene mean correlation, described as invariant to a shared positive
  affine transformation rather than to arbitrary affine rescaling.
- Gene-gene correlation distance, reported both as the raw Frobenius norm and
  normalized by the number of retained non-constant genes.

### Structure and rare-state metrics

- Same-distribution reference distributions for correlation distance, computed
  between random halves of the held-out population.
- Correlation-distance uncertainty by sample-aware bootstrap where at least
  two held-out biological samples exist.
- Rare-cluster coverage retained only as a secondary diagnostic.
- Add cluster-mass absolute error, cluster-mass Jensen-Shannon divergence and
  cluster-assignment precision/recall.
- Sensitivity grid: k in {6, 8, 10, 12}; rare threshold in {0.05, 0.10, 0.15}.
- Do not interpret a single generated cell in a rare cluster as recovery of
  that cluster's mass.

### Reporting boundary

- Training seeds quantify optimization variability, not biological
  replication.
- Sample-level resampling uses biological sample identifiers.
- D28 in the late-cutoff study has one biological sample; no confidence
  interval or generalization claim will be inferred from that one sample.
- No raw value comparison will be made between unrelated metrics.

## Claim revisions

1. Replace "reproduce exactly" with functional verification: strict checkpoint
   loading, finite generation and quantitative distance to the released
   reference population.
2. Replace "published configuration" with the precise mechanism/training
   distinction defined above.
3. Reframe the VO result as a target-informed reconstruction sanity check.
4. Replace "the baseline cannot win by construction" with "the diagonal
   baseline cannot represent non-zero population covariance".
5. Attribute the marginal-versus-structure ordering to the tested data,
   metrics and comparators; do not claim that the evaluation regime has been
   established as the exclusive cause.
6. Present Barrier 2 as a documented, exposed interface defect that blocks a
   natural reuse path, while stating that no observed released result used that
   branch.
7. Describe preprocessing as a code-documentation gap: generically stated in
   the paper, absent from the released training path and repository recipe.

## Manuscript architecture

- Title: shorter, descriptive and non-accusatory.
- Abstract: no more than 150 words and unreferenced.
- Main text: target 3,300-3,400 words, excluding abstract, Methods, references
  and legends.
- Introduction: no heading.
- Results: explicit `Results` heading with topical subheadings.
- Discussion: no subheadings; the current Outlook paragraphs are merged into
  Discussion.
- Methods: topical subheadings including split construction, baselines,
  metrics, uncertainty and software provenance.
- References: include formal dataset and software/archive citations.

## Figure redesign

- Regenerate every figure from the final artifact set.
- Remove stale terms: "not documented", "hardcoded" and unqualified
  "reproduces".
- Revise Fig. 3 to distinguish marginal and structure metrics and to display
  same-distribution references only where they were actually computed.
- Add one main or Extended Data figure summarizing cutoff robustness and
  task-aligned baselines, subject to the six-display-item limit.
- Put metric sensitivity grids and detailed per-cutoff results in
  Supplementary Information.
- Generate PDF, SVG and 300-dpi PNG versions plus machine-readable source data.

## Submission deliverables

The final package directory will contain:

1. `01_Manuscript_clean.docx`
2. `01_Manuscript_clean.pdf`
3. `02_Supplementary_Information.docx`
4. `02_Supplementary_Information.pdf`
5. `03_Cover_Letter.docx`
6. `03_Cover_Letter.pdf`
7. `04_Reporting_Summary_answers.docx`
8. `05_Software_Submission_Checklist.docx`
9. `06_Title_Page.docx`
10. `Figures/` with final PDF/SVG/PNG figure files
11. `Source_Data/` with figure-source tables and a manifest
12. `Submission_Readiness_Checklist.md`
13. `Change_Log_from_PreSubmission_Review.md`
14. `README_SUBMISSION_PACKAGE.md`
15. a ZIP archive containing the clean submission set.

The official Nature Portfolio fillable Reporting Summary PDF will be used if
it can be retrieved and programmatically completed without corrupting its form
fields. Otherwise the package will include verified transcription-ready
answers and explicitly flag the remaining mechanical form-entry step.

## Implementation and test strategy

The repository's TDD rule applies:

1. Add failing tests for new split construction, information-boundary checks,
   temporal baselines, factor baseline, structure metrics and manuscript
   consistency.
2. Confirm each test fails for the intended reason.
3. Implement the minimum production code.
4. Run unit tests, then integration/GPU tests with the appropriate markers.
5. Record provenance and regenerate derived artifacts.
6. Add manuscript consistency tests for word limits, banned stale claims,
   matching figure legends and Reporting Summary statements.
7. Render every DOCX and PDF to page images and inspect every page.

## Remote GPU execution

The two five-seed cutoff studies may run on the laboratory A100 server through
the two-hop workflow documented in `ops/remote_a100_via_lab_jump_host.md`.

- Reuse the documented Paramiko-based hop tool and its SHA256-verified
  upload/download protocol when the helper script and local credential files
  are available.
- Run a read-only connectivity, GPU, disk and environment check before any
  upload.
- Create a dedicated remote directory under
  `/data/lgh/reusability_report_nmi_20260727/`; never write files directly into
  the shared `/data/lgh` root.
- Upload a source archive tied to a local git commit plus only the required
  split inputs. Record local and remote SHA256 values.
- Use a user-space virtual environment; do not assume sudo or conda.
- Launch each seed as an independently logged job with a manifest containing
  the split, seed, command, git commit, input hashes, CUDA/PyTorch versions and
  output path.
- Download checkpoints, JSON metrics and logs with SHA256 verification before
  incorporating any result into the manuscript.
- Treat the Windows jump host as a transport layer only. Remove interrupted
  transfer remnants from its `_hop_transfer` directory when required by the
  documented workflow.
- Credential files, host passwords, private keys, IP addresses and remote
  shell history must never be committed, copied into Zenodo, or included in the
  submission package.
- If the remote route is unavailable, fall back to the local CUDA environment
  without changing the scientific protocol.

## Completion criteria

The task is complete only when:

- all ten new model trainings finish or any irrecoverable failure is recorded
  with a scientifically conservative fallback;
- all final claims map to a checked artifact;
- no test data are used for fitting or model/metric hyperparameter selection;
- abstract and main-text limits pass automated checks;
- manuscript, figures, supplement and reporting documents agree numerically;
- the clean DOCX and PDFs render without clipping, overlap or missing glyphs;
- the package contains no archival draft, temporary file, credentials or local
  absolute path;
- the final ZIP can be unpacked and its manifest checksums verify.
