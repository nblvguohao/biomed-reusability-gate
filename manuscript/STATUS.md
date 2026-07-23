# Draft status

`reusability_report_draft.md` is **superseded** and must not be submitted or
circulated. It is kept only as a record of what the evidence looked like before
two methodology errors were found.

`reusability_report.md` is the **current live manuscript**, rewritten on the
corrected evidence base. Submit that one.

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

## Reproducing the current evidence

```
external_runners/squidiff/reproduce_upstream_simulated.py    finding 3, 4
external_runners/squidiff/load_released_checkpoint.py        finding 2, and the scale check
external_runners/squidiff/train_step_sweep.py                budget sweep, log_normalize flag
external_runners/squidiff/output_calibration.py              rescaling and shuffle control
external_runners/squidiff/carnk_latent_extrapolation.py      published protocol
```
