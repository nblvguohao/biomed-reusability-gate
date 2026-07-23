# Supplementary Information

Supplementary material to *Reusability report: Squidiff reproduces as
released but is silently undermined by undocumented preprocessing and a
hardcoded sampling constant*. Every number below names the script and
artefact file that produced it, per the same convention as
`manuscript/RESULTS.md`.

---

## Supplementary Note 1 | Environment and software versions

| Component | Version |
|---|---|
| OS | Windows 11 Pro, build 10.0.26200 |
| Python | 3.10.11 (GPU/production environment, `--system-site-packages` venv), 3.11 (lint/type-check parity environment) |
| PyTorch | 2.11.0+cu128 |
| CUDA (via PyTorch) | 12.8 |
| GPU | NVIDIA GeForce RTX 5070 Ti, 17.1 GB VRAM |
| scanpy | 1.11.5 |
| anndata | 0.11.4 |
| numpy | 2.2.6 |
| scipy | 1.15.3 |
| scikit-learn | 1.7.2 |
| pandas | 2.3.3 |
| Squidiff (upstream) | commit `abdfc27d84947dcccd745d1067c0840a41d32eb8` (v1.0.8) |
| Container/environment strategy | Docker unavailable on the evaluation machine; a pinned venv was used instead (see Discussion, Boundaries) |

Full dependency lockfiles are in the code repository (`pyproject.toml`,
`uv.lock`) and archived at the code DOI.

---

## Supplementary Note 2 | The three conditional-branch defects (Barrier 2), in detail

Summarized in the main text; full technical detail, exact patch diffs, and
the regression-test strategy for each are in `vendor/patches/squidiff/README.md`
in the code repository, reproduced in structure here:

| Defect | File patched | Symptom | Root cause |
|---|---|---|---|
| i. Label dtype | `Squidiff/scrna_datasets.py` | `RuntimeError: mat1 and mat2 must have the same dtype, but got Long and Float` | `AnnDataDataset.__init__` assigns the raw `int64` NumPy array of group labels directly to the encoded-label tensor; the correct `dtype=torch.float32` cast is present in the upstream source but commented out on the line immediately above, in an unrelated conditional branch. |
| ii. Label device placement | `Squidiff/train_util.py` | `RuntimeError: Expected all tensors to be on the same device, but got mat1 is on cpu, different from other tensors on cuda:0` | `TrainLoop.forward_backward` moves every other batch tensor to the compute device except `batch['group']`. Invisible on a CPU-only run, because host and compute device then coincide — reachable only when training actually runs on a GPU. |
| iii. Label embedding rank | `Squidiff/MLPModel.py` | `RuntimeError: mat1 and mat2 shapes cannot be multiplied (1x64 and 1x2048)` | `label_embed` is `nn.Linear(1, hidden)`, requiring rank-2 input `(batch, 1)`; the DataLoader yields rank-1 labels `(batch,)`. |

All three are dtype/device/rank defects only; none touches the diffusion
process, the loss, the sampler, or any hyperparameter. They surface in the
fixed order i → ii → iii: correcting one exposes the next on the following
optimizer step, which is why they are recorded as three separate patches
rather than one. The released configuration sets `class_cond=False`,
consistent with this path never having been exercised end-to-end upstream.

Regression tests: `tests/regression/test_squidiff_patches.py`. The dtype and
rank patches are verified functionally on CPU; the device patch is guarded by
a source-level assertion plus a `@pytest.mark.gpu` end-to-end training step
that reproduces the original failure when the patch is reverted. All three
were confirmed to turn red on a throwaway tree copy with the corresponding
patch reverted.

---

## Supplementary Table 1 | Barrier 3 noise-scale sweep, full values

One trained model (published protocol, 50,000 steps, seed 13), latent
dimension 60, direction norm (D7→D14) 0.0808, within-D14 spread norm 0.808.
Source: `artifacts/squidiff_latent_extrap/latent_noise_scale_sweep.json`.

| Scale | Injected noise norm | Pooled energy distance | Generated mean / s.d. |
|---|---|---|---|
| 0.7 (upstream default) | 5.422 | 1302.39 | 42.63 / 56.69 |
| 0.3 | 2.324 | 153.23 | 7.32 / 7.12 |
| 0.107 (= 1× latent s.d.) | 0.830 | 35.29 | 3.63 / 4.16 |
| 0.054 | 0.415 | 29.86 | 3.37 / 3.89 |
| 0.0 | 0.0 | 27.56 | 3.29 / 3.88 |

Baselines on this split: conditional-mean 4.26, last-observation (D14
resample) 0.72. A zero-variance point-mass variant of last-observation
(pooled training mean tiled to each cell) scores 19.10; see Supplementary
Note 7 for the decomposition that explains the difference.

---

## Supplementary Table 2 | Validation-based scale selection, all five seeds

Validation task: direction estimated pre-infusion→D7 (training data only),
extrapolated one step, scored against real D14 (also training data — D14
labels are never used to fit the direction). Selected scale = argmin energy
distance over candidates {0.7, 0.3, 0.1, 0.03, 0.0}. Source:
`artifacts/squidiff_seed_study/seed_study_metrics.json`.

| Seed | ED @ 0.7 | ED @ 0.3 | ED @ 0.1 | ED @ 0.03 | ED @ 0.0 | Selected |
|---|---|---|---|---|---|---|
| 13 | 1169.41 | 129.88 | 32.06 | **26.22** | 26.55 | 0.03 |
| 37 | 1202.80 | 141.27 | 33.60 | 28.94 | **27.29** | 0.0 |
| 73 | 1256.17 | 139.10 | 30.41 | **23.90** | 23.96 | 0.03 |
| 101 | 1216.08 | 130.15 | 33.32 | **27.30** | 28.37 | 0.03 |
| 137 | 1290.41 | 134.57 | 32.27 | 28.51 | **28.40** | 0.0 |

Selected scales: 0.03, 0.0, 0.03, 0.03, 0.0 — none near the upstream default
of 0.7, and the two candidates nearest zero are essentially tied for every
seed, meaning the noise term contributes negligibly once past the
order-of-magnitude correction.

---

## Supplementary Table 3 | Performance under the published protocol, per-timepoint breakdown

Test task: direction D7→D14 (training data), extrapolated to D21 (1 step)
and D28 (2 steps), scored against the corresponding held-out cells.
Validation-selected scale per seed as in Table 2. Source: same metrics file
as Table 2.

| Seed | Timepoint | n | Energy distance | MMD (RBF) | Mean expr. correlation |
|---|---|---|---|---|---|
| 13 | D21 | 4,158 | 28.04 | 0.1584 | 0.8025 |
| 13 | D28 | 510 | 26.41 | 0.1954 | 0.8374 |
| 37 | D21 | 4,158 | 29.48 | 0.1667 | 0.8123 |
| 37 | D28 | 510 | 27.66 | 0.1888 | 0.8325 |
| 73 | D21 | 4,158 | 24.75 | 0.1494 | 0.8388 |
| 73 | D28 | 510 | 24.26 | 0.1837 | 0.8412 |
| 101 | D21 | 4,158 | 28.57 | 0.1701 | 0.8087 |
| 101 | D28 | 510 | 30.21 | 0.2050 | 0.8336 |
| 137 | D21 | 4,158 | 27.99 | 0.1644 | 0.8130 |
| 137 | D28 | 510 | 25.54 | 0.1957 | 0.8345 |

Pooled (both timepoints combined) values per seed and the cross-seed
mean ± s.d. are reported in the main text (Fig. 3c) and
`manuscript/RESULTS.md`.

---

## Supplementary Note 3 | Barrier 1 confirmed under the published protocol, full values

The main text (Barrier 1) reports this confirmation in one sentence; full
per-budget values follow. Protocol: latent extrapolation, released
architecture (`class_cond=False`, `use_encoder=True`, `num_layers=3`,
`diffusion_steps=1000`), noise scale fixed at 0.03 for both preprocessing
conditions and all three budgets (chosen from Table 2 rather than re-tuned,
to keep this a single-variable comparison), seed 13. Source:
`artifacts/squidiff_latent_extrap_ab/preprocessing_ab_metrics.json`.

| Training steps | Raw counts, pooled ED | Log-normalized, pooled ED |
|---|---|---|
| 5,000 | 376.76 | 312.45 |
| 20,000 | 514.82 | 69.63 |
| 50,000 | 561.72 | 27.68 |

Baselines on the raw-count split: conditional-mean 129.30, last-observation
(point-mass variant) 687.72. Baselines on the log-normalized split:
conditional-mean 4.26, last-observation (point-mass variant) 19.10; the
D14-resample last-observation scores 0.72 on the log-normalized split
(Supplementary Note 7). (Baselines differ between the two rows because
energy distance is scale-sensitive and the two splits are on different
scales by construction — this is the same reason the main comparison uses a
scale-invariant third metric.)

---

## Supplementary Note 4 | Upstream simulated benchmark, full degeneracy detail

Source: `artifacts/squidiff_reproduction/reproduction_metrics.json` and
`reproduce_upstream_simulated.py`, reproducing `prep_simu_data.ipynb`
(upstream reproducibility repository), 3,000 simulated cells, 1,000 per
type, `np.random.seed(42)`.

| Stage | Type A mean | Type B mean | Type C mean | Silhouette (3 types) |
|---|---|---|---|---|
| Before preprocessing | 5.001 | 7.999 | 9.996 | 0.4723 |
| After `normalize_total` (prescribed) | 50.000 | 50.000 | 50.000 | −0.0625 |

The three simulated types differ only by a global expression-level offset by
construction; library-size normalization is defined to remove exactly that
signal, so this is an internal inconsistency in the benchmark's own design
rather than an implementation bug. Scope: the Gaussian simulation only; the
splatter-simulated dataset in the same notebook sits behind an
institution-internal HPC path and was not accessible for reproduction.

No quantitative metric of any kind (accuracy, distance, correlation, or
otherwise) appears in the 83 code cells across the two upstream
reproducibility notebooks (`prep_simu_data.ipynb`,
`fig4_VO_reproducibility.ipynb`) — visual inspection of plots is the only
form of validation upstream provides.

---

## Supplementary Note 5 | Rare-state recall under the class-conditional probe

Reported for completeness alongside the Barrier 1 probe (main text Fig. 3a);
not a claim about the published latent-extrapolation protocol, which does
not target specific rare subpopulations by construction. Using k-means
clusters fitted on held-out cells and counting any cluster below 10%
prevalence as rare: raw counts recover 0.0 rare-cluster mass at every
training budget tested; log-normalized data recover 0.0 at 5,000 steps,
rising to 1.0 by 50,000 steps under the class-conditional probe used for
Barrier 1. This tracks the same preprocessing effect as the energy-distance
result above and should be read as a demonstration of the same barrier, not
as an independent performance claim about rare-state discovery under the
published protocol.

---

## Supplementary Note 6 | Positive-control checkpoint, full verification detail

Source: `artifacts/released_checkpoint/released_checkpoint_check.json`,
`load_released_checkpoint.py`, figshare 10.6084/m9.figshare.27948633
(CC BY 4.0).

| Check | Result |
|---|---|
| Tensors in state dict | 62 |
| Total parameters | 54,565,522 |
| `load_state_dict(strict=True)` | 0 missing keys, 0 unexpected keys |
| Sampled population | 512 cells, all finite |
| Energy distance to reference population | 2.098 |
| Released training data scale | mean 1.78, max 14.47 (confirms log-normalization independently of our own preprocessing sweep) |
| Released training configuration | `class_cond=False`, `use_encoder=True`, `num_layers=3`, `gene_size=596`, 2,400 steps, batch size 16 |

---

## Supplementary Note 7 | Baseline fit sets and the energy-distance decomposition

Source: `artifacts/baseline_provenance/baseline_provenance.json`,
`baseline_provenance.py`. Stated because the headline comparison depends on
it: **both baselines are fit only on the pooled training window**
(pre-infusion + D7 + D14, 11,588 cells); held-out cells are never touched.

| Baseline | Fit set | cross | within_real | within_generated | ED | MMD | mean corr |
|---|---|---|---|---|---|---|---|
| Conditional-mean sampler | per-gene mean/variance, pooled training window | 36.53 | 32.69 | 36.11 | 4.26 | 0.0577 | 0.9375 |
| Last-observation, as first implemented | pooled training mean tiled to every cell (constant, zero variance) | 25.90 | 32.69 | **0.0** | 19.10 | 0.1145 | 0.9378 |
| Last-observation, D14 resample (used in the main text) | real D14 training cells resampled with replacement | 33.85 | 32.69 | 34.29 | **0.72** | 0.0108 | 0.9760 |

Two points follow. First, the early "last-observation" implementation and
its name disagreed: it was a zero-variance point mass, and with
ED = 2·cross − within_real − within_generated it forfeited the entire
within-generated term (0.0 vs 32.69 for the real population). Its cross term
is actually the best of the three (25.90 — the pooled training mean sits
centrally), so the 4.26-vs-19.10 ordering reflects the metric's treatment of
a zero-variance prediction, not centering. Second, the D14-resample
last-observation is the strongest baseline of all (ED 0.72), consistent with
the low-drift task structure discussed in the main text — the CAR-NK
population moves little between the training and held-out windows, so a
method that simply replays the last observed population is hard to beat on
distributional metrics. Squidiff (validation-selected ED 27.15 ± 1.78)
trails both baselines on every metric.

---

## Supplementary Note 8 | Positive control on the authors' own released setting

Source: `artifacts/positive_control/positive_control_metrics.json`,
`positive_control.py`. Task: predict the day-1 VO population from the day-0
anchor through the published latent-extrapolation mechanism, using the
released VO checkpoint and its released training data (6,838 cells, 596
genes, days {0, 1}; figshare 10.6084/m9.figshare.27948633, CC BY 4.0).
Latent geometry on the released encoder: direction norm 0.84, within-day-1
spread 1.36, injected noise norm at the released default scale 0.7 is 5.42 —
6.5× the direction being extrapolated.

| Condition | Fit set | ED | MMD (RBF) | Mean corr |
|---|---|---|---|---|
| Squidiff, released default 0.7 | released checkpoint; direction E\[z_day1\]−E\[z_day0\] | 626.55 | saturated (0.638) | 0.451 |
| Squidiff, scale 0.03 | as above; 3 sampling seeds | 7.24 ± 0.07 | 0.031 | 0.975 |
| Conditional-mean, pooled | per-gene mean/variance on all 6,838 training cells (days 0+1) | **1.51** | 0.012 | 0.974 |
| Last-observation, day-0 resample | real day-0 cells resampled | 47.58 | 0.378 | 0.281 |
| Oracle Gaussian | per-gene mean/variance on day-1 cells (not usable for prediction) | 0.45 | 0.003 | 1.000 |

Three readings. (i) The released default scale destroys the prediction on
the authors' own data too — Barrier 3 is not specific to our CAR-NK encoder.
(ii) Even at a repaired scale, Squidiff trails a per-gene Gaussian fit on
the same pooled training data (7.24 vs 1.51) whose mean sits midway between
the two days; per-gene mean correlation is a dead heat (0.975 vs 0.974).
(iii) The VO task is not trivial — the day-0 resample scores 47.58, so the
population genuinely moves — yet the moment-matched baseline wins there as
well. The CAR-NK ordering therefore reflects what these distributional
metrics reward (marginal moments), not a CAR-NK-specific or low-drift
artefact; and because the upstream reproducibility material reports no
quantitative metric (Supplementary Note 4), nothing upstream could have
surfaced it.
