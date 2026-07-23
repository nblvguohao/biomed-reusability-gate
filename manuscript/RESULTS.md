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
| released training data scale | mean 1.78, max 14.47, i.e. log-normalized |
| released config | `class_cond=False`, `use_encoder=True`, `num_layers=3`, `gene_size=596`, 2,400 steps at batch 16 |

## Barrier 1: a conditional branch that cannot run

`vendor/patches/squidiff/`, `tests/regression/test_squidiff_patches.py`

Three defects on `use_encoder=True` + `class_cond=True`, each raising on the
first optimizer step, in a fixed cascade. The released config sets
`class_cond=False`, so the branch was never exercised upstream. Each patch has a
regression test confirmed to turn red when reverted.

## Barrier 2: undocumented preprocessing

`train_step_sweep.py --log_normalize`, `output_calibration.py`

| | raw counts | log-normalized |
|---|---|---|
| energy distance 5k / 20k / 50k | 321.6 / 412.2 / 432.5 | 409.4 / 95.4 / 6.85 |
| trend with training | degrades | improves 60-fold |
| generated moments at 50k | 8.62 / 24.17 | 1.89 / 1.56 |
| real moments | 25.92 / 73.07 | 1.24 / 1.42 |
| rare-state recall at 50k | 0.0 | 1.0 |

## Barrier 3: a hardcoded sampling constant

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
| last-observation baseline | 19.10 | 0.1145 | +0.9378 |

Worse than the conditional-mean baseline on all three metrics in all five seeds.
The third metric is invariant to affine rescaling, so this is not an output-scale
artefact.

**MMD at scale 0.7 must not be quoted as a number.** All five independently
trained models return 0.638179 to six decimals, which is `mean(k_xx)` alone: the
generated samples share no support with the real data and are mutually
dispersed, so `k_xy` and `k_yy` both vanish. A synthetic shift check saturates
the kernel at 1.335 for any offset above 20.

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

Figures do not exist, only captions in the superseded draft. No Zenodo DOI. No
reference list, Supplementary Information or Reporting Summary. Author list and
affiliations. The perturbation-response half of the original work is untested.
