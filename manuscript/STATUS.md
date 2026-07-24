# Draft status

`reusability_report_draft.md` is **superseded** and must not be submitted or
circulated. It is kept only as a record of what the evidence looked like before
two methodology errors were found.

`reusability_report.md` is the **current live manuscript**, rewritten on the
corrected evidence base. Submit that one.

## 2026-07-24 reviewer-revision state (TDD: docs/superpowers/plans/2026-07-23-reviewer-revision-tdd.md)

Done and committed:

- **Phase 0 ground truths** (`reports/`): the log-normalization IS described
  in the published Methods as a one-line generic phrase ("normalized and
  log-transformed…") with no executable recipe — title/abstract/Barrier 1
  reworded from "undocumented" to the code–documentation gap. The 0.7 noise
  scale is a signature default the released prediction path never forwards —
  "hardcoded" reworded accordingly. Claim→code-path map built; Barrier 2
  recalibrated from "headline perturbation-response use" to "the library's
  only label-conditional interface, unused by any released configuration".
- **Phase 1.1 baseline provenance**: both baselines fit only on the pooled
  training window; the as-implemented last_observation is a zero-variance
  point mass (explains 4.26 vs 19.10 via the ED within-sample term); true
  D14-resample baseline added (ED 0.72). Methods section added to the
  manuscript; Supp. Note 7.
- **Phase 1.2 positive control**: on the authors' own VO checkpoint/data,
  the released default 0.7 fails there too (ED 626.6), and at scale 0.03
  Squidiff (7.24) still trails the pooled conditional-mean Gaussian (1.51);
  VO has genuine drift (day-0 resample 47.6), so the ordering is a property
  of the evaluation regime, not a CAR-NK/low-drift artefact. Performance
  claim reframed; Supp. Note 8. Ahlmann-Eltze et al. 2025 (Nat Methods)
  cited as precedent.
- **Phase 1.3 Fig 3a**: main panel now uses the published-protocol A/B
  (376.8→561.7 vs 312.4→27.7, 11-fold); class-conditional probe demoted to
  labelled corroboration. Title/abstract re-centred; references completed
  (11 refs, Crossref-verified); author contributions finalized and
  **confirmed by all authors (2026-07-24)**.

- **Phase 2 robustness** (`evaluation_robustness.py`, results in
  `artifacts/evaluation_robustness/robustness.json`): a deterministic
  parallel bootstrap driver (each (population × mode) task re-seeds its own
  `RandomState`, so distributing across an 8-core spawn Pool changes only
  wall-clock, ~4.8h → ~40min, never the numbers; unit-tested for bit-identity
  against the sequential loop) computed:
  - **Null anchors**: same-distribution reference band (random halves of
    held-out population) — ED 0.027 (q95 0.051), far below every reported
    gap. Drawn as a shaded band on Fig. 3c; RESULTS.md, Supp. Note 9.
  - **Uncertainty beyond training seed**: sample-level bootstrap CIs (no
    overlap between any Squidiff seed and either baseline), leave-one-
    sample-out (ordering holds in all 25 folds), baseline resampling
    dispersion (an order of magnitude below the seed-to-seed spread).
    Supp. Note 9. **Scoping note**: the TDD's Task 2.2 also asked for
    "≥2 alternative group-held-out splits" — read literally, that means
    retraining under different train/test partitions, which would mean
    5 more Squidiff models per alternative split (GPU-hours). We
    substituted leave-one-held-out-sample-out re-scoring, which tests the
    same concern (is the ordering driven by one atypical held-out sample)
    without retraining, at effectively zero extra cost given the cached
    populations. If reviewers want a literal alternative-split retrain,
    that is still open.
  - **MMD bandwidth sensitivity**: ordering flips at 0.25×/0.5× bandwidth
    (Squidiff wins) versus 1×/2×/4× (baseline wins) — MMD demoted from
    headline metric to Supp. Table 4 sensitivity check; Fig. 3c middle panel
    swapped from MMD to the structure metric below.
  - **Structure metrics** (gene–gene correlation Frobenius distance,
    rare-cluster mass recall — the properties a diagonal-covariance sampler
    cannot win by construction): Squidiff beats conditional-mean on both, in
    every seed, but trails last-observation (which trivially inherits real
    correlation structure). **This is the real headline nuance the TDD
    flagged as possible**: Squidiff loses the marginal/distance metrics the
    field would naturally report and wins the one property those metrics
    cannot see. Performance section, Discussion, Outlook, abstract, and Fig.
    3 legend all rewritten to carry this two-sided result; Supp. Note 10.
- **Structure metrics replicated on VO** (`positive_control_structure.py`,
  `artifacts/positive_control/structure_metrics.json`): repeats the
  structure-metric check on the authors' own released setting. Sharper than
  CAR-NK — Squidiff beats *every* baseline there, including last-observation
  and an oracle Gaussian fit on the target population, on both structure
  metrics. Surfaced and fixed a real bug along the way:
  `correlation_frobenius_distance` returned NaN when a gene is exactly
  constant in the real population (2 of 596 released VO genes are; CAR-NK's
  HVG-selected genes have none, so the already-published CAR-NK numbers are
  unaffected — checked directly, not assumed). Supp. Note 8 extended to four
  readings, new Supp. Note 11; Performance section, "same ordering" section,
  and Discussion boundaries updated.

## 2026-07-24 submission-status update

- **Code Zenodo DOI**: minted and verified resolving —
  `10.5281/zenodo.21510468` (published record, "v1.0.0 — Squidiff
  reusability report submission", 2026-07-23). Filled into
  `reusability_report.md` and `REPORTING_SUMMARY.md`. Confirmed the
  `v1.0.0` archive predated the Phase 2 robustness work and VO
  structure-metric replication (14 commits, `b685d67`..`e3b2c2e`) — **all
  now pushed to `origin/feat/biomed-reusability-gate`**, branch fully in
  sync. Cutting a `v1.0.1` GitHub release is the only step left to refresh
  the archive; that release itself must be done on GitHub's web UI
  (walkthrough in `ZENODO_HOWTO.md` Part 1).
- **Data Zenodo DOI**: minted and verified resolving —
  `10.5281/zenodo.21510503` (published record, "Squidiff CAR-NK
  reusability report — model checkpoints, splits, and figure source data",
  v1, 2026-07-23, CC BY 4.0). Filled into `reusability_report.md` and
  `REPORTING_SUMMARY.md` §3. Package: 13 zips + README (~3.5 GB) — the
  original 10, `10_manuscript_figures.zip` refreshed to the current
  figures, and three new ones (`11_vo_positive_control`,
  `12_baseline_provenance`, `13_evaluation_robustness`) covering everything
  from the Phase 2 session. **Worth a self-check**: the fetch used to
  verify this record showed only one author name — confirm the full
  7-author list made it into the Zenodo metadata (the record can't be
  silently corrected after publication; a mismatch needs a new version).
- **Author contributions**: confirmed by all authors.
- **Original-author contact**: decided — **not contacted**. If NMI's
  editorial process expects notification of He et al., that should be
  handled in the cover letter at submission, not in the manuscript body.
- **Reporting Summary**: content complete (`REPORTING_SUMMARY.md`);
  transcription into NMI's actual fillable PDF form is still a mechanical
  step for whoever submits.

Remaining before submission: (1) cut GitHub release `v1.0.1` so Zenodo
archives a current code snapshot (the only outstanding DOI item — data DOI
is done), then send the new version DOI for it to be swapped into the
manuscript; (2) double-check the Zenodo data record's author list is
complete (see note above); (3) transcribe REPORTING_SUMMARY.md into the
journal's actual form. Pre-existing failure retained: tests/regression GPU
step (test_training_step_runs_on_gpu) fails identically on clean HEAD
(numpy/torch drift in .venv310; out of revision scope).

## Retracted from the draft

| Claim in the draft | Why it is wrong |
|---|---|
| "Raw energy distance degrades monotonically with training" | Artefact of feeding raw counts to a linear noise schedule. With the upstream log-normalization it improves: 409.4 -> 95.4 -> 6.85 |
| "Rare states are not recovered" | Same artefact. Recall reaches 1.0 by 50k steps once preprocessing is correct |
| "A correctable calibration defect masks learned structure" | The whole framing rested on the two rows above |
| Every CAR-NK number | Generated with class-conditional sampling. The published mechanism for predicting development is latent-space extrapolation, so the protocol was wrong |

## What survives

- Three defects block `use_encoder=True` + `class_cond=True`, each raising on the
  first optimizer step. Patches and regression tests in `vendor/patches/squidiff/`
  and `tests/regression/`.
- The released configuration sets `class_cond=False`, so the authors never
  exercised that branch. Direct evidence, from the args dict in
  `fig4_VO_reproducibility.ipynb`.
- The released checkpoint loads and samples correctly: 0 missing, 0 unexpected
  keys, `strict=True` would pass, energy distance 2.098 from its reference.
- The authors' released training data is log-normalized (mean 1.78, max 14.47),
  independently confirming the preprocessing requirement.
- The upstream Gaussian simulated benchmark is degenerate under its own
  preprocessing: per-type means 5.001/7.999/9.996 collapse to 50.000/50.000/50.000
  after `normalize_total`, silhouette 0.4723 -> -0.0625.
- No quantitative metric appears anywhere in the reproducibility repository, in
  83 code cells across the two analysis notebooks.

## Rewriting checklist (all done)

1. CAR-NK re-run under the published latent-extrapolation protocol — done
   (`carnk_latent_extrapolation.py`, released config `class_cond=False`).
2. Multiple seeds — done, five seeds (`seed_study.py`).
3. A second and third metric — done: MMD (RBF, bandwidth fixed on training
   data) and a scale-invariant per-gene mean correlation.

The rewritten manuscript is `reusability_report.md`. Note on protocol: the
Barrier 1 preprocessing comparison (Fig. 3a) intentionally uses the
class-conditional probe from `train_step_sweep.py`, held fixed across the two
preprocessing conditions, because it isolates the training-data/noise-schedule
effect without the 0.7 latent-noise confound that dominates Barrier 3. It is a
training-pipeline A/B, not a prediction-performance claim; the published
protocol is used for the performance result (Fig. 3c).

That gap is now also closed directly: `latent_extrapolation_preprocessing_ab.py`
repeats the raw-vs-log-normalized comparison under the exact published
latent-extrapolation protocol, at a single fixed noise scale (0.03, chosen to
avoid re-tuning) rather than 0.7. Same reversal: raw 376.8 -> 514.8 -> 561.7
(degrades), log-normalized 312.4 -> 69.6 -> 27.7 (11.3-fold improvement). Cited
in the main text as corroboration; source data at
`artifacts/squidiff_latent_extrap_ab/preprocessing_ab_metrics.json`.

## Reproducing the current evidence

```
external_runners/squidiff/reproduce_upstream_simulated.py    finding 3, 4
external_runners/squidiff/load_released_checkpoint.py        finding 2, and the scale check
external_runners/squidiff/train_step_sweep.py                budget sweep, log_normalize flag
external_runners/squidiff/output_calibration.py              rescaling and shuffle control
external_runners/squidiff/carnk_latent_extrapolation.py      published protocol
```
