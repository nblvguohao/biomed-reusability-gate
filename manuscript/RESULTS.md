# Measured results

Numbers the rewritten report can draw on. Every row names the script that
produces it. Raw outputs live under `artifacts/`, which is gitignored by design,
so they must go to Zenodo before submission.

Dataset throughout: GSE190976, mouse CAR-NK, 16,256 cells. Preprocessing is the
upstream `normalize_total(1e4)` + `log1p`, then top-500 HVG fitted on training
cells only. Split: train pre-infusion/D7/D14 (11,588 cells, 13 samples), held
out D21/D28 (4,668 cells, 5 samples), zero sample overlap.

## Positive control: the released artefact works

`load_released_checkpoint.py`, on figshare 10.6084/m9.figshare.27948633 (CC BY 4.0)

| check | result |
|---|---|
| weights | 62 tensors, 54,565,522 parameters |
| `load_state_dict` | 0 missing, 0 unexpected, `strict=True` would pass |
| sampling | 512 cells, all finite, energy distance 2.098 |
| null anchor for that ED | random halves of the same 512 reference cells: ED 0.566 mean, 0.697 q95 (50 splits) — 2.098 is close to, though above, the same-distribution floor |
| released training data scale | mean 1.78, max 14.47, i.e. log-normalized |
| released config | `class_cond=False`, `use_encoder=True`, `num_layers=3`, `gene_size=596`, 2,400 steps at batch 16 |

## Barrier 1: a preprocessing requirement the code path never applies

Barriers are numbered in the order a reuser meets them, which is the order of
the workflow in Fig. 1a, not the order in which we happened to find them.

`train_step_sweep.py --log_normalize`, `output_calibration.py`

| | raw counts | log-normalized |
|---|---|---|
| energy distance 5k / 20k / 50k | 321.6 / 412.2 / 432.5 | 409.4 / 95.4 / 6.85 |
| trend with training | degrades | improves 60-fold |
| generated moments at 50k | 8.62 / 24.17 | 1.89 / 1.56 |
| real moments | 25.92 / 73.07 | 1.24 / 1.42 |
| rare-state recall at 50k | 0.0 | 1.0 |

## Barrier 1, confirmed under the published protocol

`latent_extrapolation_preprocessing_ab.py`, seed 13, released config
(`class_cond=False`, `use_encoder=True`, `num_layers=3`, `diffusion_steps=1000`),
noise scale fixed at 0.03 for both conditions and all budgets (not re-tuned, to
keep this a single-variable A/B) — closes the gap left by the class-conditional
probe above, which was chosen specifically to avoid the Barrier 3 noise-scale
confound. This run repeats the same comparison under the actual
latent-extrapolation protocol used for the performance result below.

| | raw counts | log-normalized |
|---|---|---|
| pooled energy distance, 5k / 20k / 50k | 376.8 / 514.8 / 561.7 | 312.4 / 69.6 / 27.7 |
| trend with training | degrades | improves 11.3-fold |

Same direction as the class-conditional probe, now under the protocol that
matters. Source data: `artifacts/squidiff_latent_extrap_ab/preprocessing_ab_metrics.json`.

## Barrier 2: a conditional branch that cannot run

`vendor/patches/squidiff/`, `tests/regression/test_squidiff_patches.py`

Three defects on `use_encoder=True` + `class_cond=True`, each raising on the
first optimizer step, in a fixed cascade. The released config sets
`class_cond=False`, so the branch was never exercised upstream. Each patch has a
regression test confirmed to turn red when reverted.

## Barrier 3: a sampling constant the released path never exposes

`latent_noise_scale_sweep.py`, `seed_study.py`

`sample_around_point` uses an absolute std of 0.7. On this encoder the
per-dimension latent std is 0.105 and the D7→D14 direction has norm 0.081, so
0.7 injects noise 67x the direction and 6.7x the within-timepoint spread. No
error is raised.

Validation-selected scale, one value chosen per seed on a training-only task:
**0.03, 0.0, 0.03, 0.03, 0.0**. None near 0.7.

## Performance, five seeds, published protocol and configuration

`seed_study.py`

| | energy distance | MMD (RBF) | per-gene mean correlation |
|---|---|---|---|
| Squidiff, scale 0.7 | 1244.01 ± 48.57 | saturated, see below | 0.4423 ± 0.0300 |
| Squidiff, validation-selected | 27.15 ± 1.78 | 0.1579 ± 0.0081 | 0.8321 ± 0.0128 |
| conditional-mean baseline | 4.26 | 0.0577 | +0.9375 |
| last-observation baseline (D14 resample) | 0.72 | 0.0108 | +0.9760 |
| last-observation variant (pooled-mean point mass) | 19.10 | 0.1145 | +0.9378 |

Worse than the conditional-mean baseline on these two marginal/distance metrics
in all five seeds. MMD's ordering is not stable across bandwidth (see below) and
is not used as a headline metric; on the structure metrics added later
(correlation Frobenius distance, rare-cluster recall — see "Uncertainty beyond
training seed" section below), Squidiff *beats* conditional_mean in all five
seeds. Per-gene mean correlation is invariant to affine rescaling, so that gap is not an output-scale
artefact.

## Baseline provenance and the energy-distance decomposition

`baseline_provenance.py`, on `artifacts/squidiff_sweep_lognorm` — states exactly
what each baseline is fit on, and decomposes energy distance (ED) into its three
terms to explain the baseline ordering. Source:
`artifacts/baseline_provenance/baseline_provenance.json`.

Fit sets (both baselines fit **only** on the pooled training window —
pre-infusion + D7 + D14, 11,588 cells; held-out D21/D28 cells are never touched):

- **conditional_mean**: per-gene mean and variance fit on the pooled training
  window; samples are i.i.d. diagonal Gaussian draws. No gene–gene covariance.
- **last_observation (as implemented in `temporal_baselines.last_observation`)**:
  the pooled training mean tiled to every held-out cell — a constant
  **point-mass** prediction with **zero variance**. Despite the name, it is not
  restricted to the last timepoint; the name and the implementation disagree.
- **last_observation (true D14 resample, added in this audit)**: real D14 cells
  from the training window, resampled with replacement to held-out size.

| baseline | cross | within_real | within_generated | ED | MMD | mean corr |
|---|---|---|---|---|---|---|
| conditional_mean | 36.53 | 32.69 | 36.11 | 4.26 | 0.0577 | 0.9375 |
| last_observation (point mass, as implemented) | 25.90 | 32.69 | **0.0** | 19.10 | 0.1145 | 0.9378 |
| last_observation (true D14 resample) | 33.85 | 32.69 | 34.29 | **0.72** | 0.0108 | 0.9760 |

Why conditional-mean (4.26) beats the point-mass last-observation (19.10): with
ED = 2·cross − within_real − within_generated, a zero-variance prediction
forfeits the entire within-generated term (0.0 vs 32.69 for the real
population). The point mass actually has the *best* cross term of the three
(25.90 — the pooled training mean sits centrally); it loses purely because the
metric credits matched variance. The ordering is therefore a property of the
metric acting on a zero-variance prediction, not evidence about centering.

The true D14 resample reaches ED 0.72 — the strongest baseline of all, and far
ahead of Squidiff's validation-selected 27.15 ± 1.78. This is consistent with
the low-drift task structure stated in the manuscript (the CAR-NK population
mean moves little between training and held-out windows), and it sharpens the
performance claim: Squidiff trails *both* a per-gene Gaussian and a resampled
last-observed population on every metric.

Consequence for the manuscript: the point-mass variant must be named as such
("pooled training-mean point prediction") wherever it appears, and the true
D14-resample baseline must be reported alongside it.

**MMD at scale 0.7 must not be quoted as a number.** All five independently
trained models return 0.638179 to six decimals, which is `mean(k_xx)` alone: the
generated samples share no support with the real data and are mutually
dispersed, so `k_xy` and `k_yy` both vanish. A synthetic shift check saturates
the kernel at 1.335 for any offset above 20.

## Positive control: the same baselines on the authors' own released setting

`positive_control.py`, on the released VO checkpoint + VO_trained_adata.h5ad
(figshare 10.6084/m9.figshare.27948633). Task: predict the day-1 VO population
from the day-0 anchor via the published latent-extrapolation mechanism.
Source: `artifacts/positive_control/positive_control_metrics.json`.
Latent geometry: direction norm 0.84, within-day-1 spread 1.36, noise injected
at the released default scale 0.7 has norm 5.42 (6.5x the direction).

| condition | ED | MMD (RBF) | mean corr |
|---|---|---|---|
| Squidiff, released default scale 0.7 | 626.55 | saturated (0.638) | 0.451 |
| Squidiff, scale 0.03 (3 sampling seeds) | 7.24 ± 0.07 | 0.031 | 0.975 |
| conditional-mean, fit on pooled days 0+1 | **1.51** | 0.012 | 0.974 |
| last-observation, day-0 resample | 47.58 | 0.378 | 0.281 |
| oracle Gaussian, fit on day-1 marginals | 0.45 | 0.003 | 1.000 |

Read-out:

- The released default 0.7 destroys the prediction on the authors' own data
  too — Barrier 3 is not CAR-NK-specific.
- Even at a repaired scale, Squidiff (7.24) trails a per-gene Gaussian fit on
  the *same pooled training data* (1.51) — a baseline whose mean sits midway
  between the two days. The CAR-NK ordering is therefore not specific to our
  low-drift task: it holds on the authors' own released setting.
- The day-0 resample loses badly (47.58), so the VO task has genuine drift —
  the "the task was just too easy" explanation does not cover this control.
- The oracle Gaussian (0.45) marks the marginal moment-matching ceiling.
- Consequence: the performance result must be framed as a property of the
  evaluation regime — distributional metrics reward marginal moments, and the
  upstream repository reports no quantitative metric that would have surfaced
  this — not as "Squidiff fails to transfer to new data".

## Uncertainty beyond training seed, MMD sensitivity, structure metrics

`evaluation_robustness.py`, on the same split as the performance table above.
Source: `artifacts/evaluation_robustness/robustness.json`.

**Null anchor** (metric between random halves of the held-out population, 50
splits): energy distance 0.0266 mean / 0.0509 q95; MMD (RBF, training
bandwidth) 0.00035 mean / 0.00090 q95; per-gene mean correlation 0.9995 mean /
0.9989 q05. Every reported energy distance below (0.72–1244) is far above this
floor.

**Bootstrap 95% CIs for energy distance** (200 resamples; cell-level and
sample-level, the latter resampling whole held-out biological samples):

| | estimate | cell-level CI | sample-level CI |
|---|---|---|---|
| conditional_mean | 4.26 | [4.18, 4.38] | [3.93, 5.72] |
| last_observation (D14 resample) | 0.72 | [0.67, 0.80] | [0.71, 3.65] |
| Squidiff seed 13 | 28.72 | [26.78, 30.85] | [25.90, 32.32] |
| Squidiff seed 37 | 29.26 | [27.19, 31.37] | [26.30, 33.34] |
| Squidiff seed 73 | 24.90 | [23.04, 26.93] | [22.44, 28.30] |
| Squidiff seed 101 | 28.99 | [27.04, 30.94] | [25.88, 32.80] |
| Squidiff seed 137 | 27.28 | [25.47, 29.34] | [24.65, 31.52] |

No Squidiff seed's sample-level CI overlaps either baseline's.
Leave-one-sample-out preserves the ordering in all 25 folds. Baseline
dispersion across 10 resampling draws: conditional_mean 4.263 ± 0.009,
last_observation 0.776 ± 0.042 — an order of magnitude below Squidiff's
24.9–29.3 training-seed spread.

**MMD bandwidth grid** (bandwidth × {0.25, 0.5, 1, 2, 4}): Squidiff beats
conditional_mean at 0.25× (0.082–0.087 vs 0.1103) and 0.5× (0.127–0.141 vs
0.1712); conditional_mean wins at 1×, 2×, 4×. Ordering flips across the grid
→ MMD demoted to a supplementary sensitivity table, not a headline metric.

**Structure metrics** (gene–gene correlation Frobenius distance, lower
better; rare-cluster mass recall, higher better):

| | correlation Frobenius | rare-cluster recall |
|---|---|---|
| conditional_mean | 266.17 | 0.34 |
| last_observation (D14 resample) | 79.09 | 1.00 |
| Squidiff (5 seeds) | 126.8–145.4 (mean 137.9 ± 8.4) | 0.93–1.00 (mean 0.97) |

Squidiff beats conditional_mean on both structure metrics in all 5 seeds
(wins the metric a diagonal-covariance sampler cannot capture by
construction) but trails last_observation, which trivially carries real
correlation structure. **This is the headline nuance**: Squidiff loses the
marginal/distance metrics the field typically reports and wins the one
metric a moment-matched Gaussian baseline cannot win — against the baseline
that shares its generative task. Performance section and Discussion rewritten
accordingly.

## Also found

- The upstream Gaussian simulated benchmark is degenerate under its own
  preprocessing: per-type means 5.001 / 7.999 / 9.996 collapse to
  50.000 / 50.000 / 50.000 after `normalize_total`, silhouette 0.4723 → −0.0625.
  Scoped to `prep_simu_data.ipynb` cells 6 and 14; the splatter dataset in the
  same notebook is behind an HPC path and is not assessed.
  (`reproduce_upstream_simulated.py`)
- No quantitative metric appears anywhere in the reproducibility repository, in
  83 code cells across the two analysis notebooks.

## Boundaries to state, not soften

One dataset, one task. Temporal extrapolation, not the perturbation-response
setting the original work also claims. Direction estimated from two timepoints
only, so the linear-extrapolation assumption may not suit a non-linear
exhaustion trajectory. The baseline is strong here because the CAR-NK population
mean drifts little between the training and held-out windows, which makes the
task unfavourable to a generative model rather than the model unfit.

## Still missing before submission

Figures now exist (`artifacts/manuscript_figures/`, built by
`make_manuscript_figures.py`), and the main text is rewritten
(`reusability_report.md`). Remaining: Zenodo DOI for code + artifacts;
completed reference list (currently provisional); Supplementary Information and
Nature Reporting Summary; author list and affiliations. The
perturbation-response half of the original work is untested.
