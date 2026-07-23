# Figure legends

Written to the Nature-family convention: `Fig. N |` plus a nominal title, panels
in telegraphic present tense, statistics carried in the legend, source-data line
at the end. Each legend is meant to be readable away from the body text.

Barriers are numbered in the order a reuser meets them, matching Fig. 1a.

---

**Fig. 1 | Reusability assessment of Squidiff and the three points at which reuse fails**

**a** Assessment workflow. Upstream is pinned at commit `abdfc27` (v1.0.8); the
released checkpoint and its training data are verified before any new data is
introduced; the upstream simulated benchmark is reproduced; the method is then
applied to CAR-NK temporal extrapolation. Each barrier is drawn beside the step
at which it surfaces. Green outline, the step that succeeded without
intervention. Red, the three barriers.
**b** The conditioning data path under `use_encoder = True` and
`class_cond = True`, with the three defect sites marked i to iii. Each raises a
`RuntimeError` on the first optimizer step, in the order shown, so correcting
one exposes the next. The released configuration sets `class_cond = False`, so
this path was not exercised upstream. Schematic; no measured values are plotted.

---

**Fig. 2 | The released artefacts reproduce, but the upstream simulated benchmark cannot test them**

**a** Distribution of expression values for 512 reference cells from the released
training data (grey) and 512 cells generated from the released checkpoint
(green outline), plotted as densities over the same bins. The checkpoint loads
into the released architecture with 0 missing and 0 unexpected keys, so a strict
load would pass; multivariate energy distance between the two populations is
2.10.
**b** Value range of three datasets on a logarithmic axis. Dot, mean; tick,
maximum. The authors' released training data (green, max 14.5) and CAR-NK data
after `normalize_total` and `log1p` (blue, max 9.0) occupy the same scale; raw
CAR-NK counts (red, max 12,167) are three orders of magnitude away.
**c** Cell-type separability of the upstream Gaussian simulated benchmark through
its own prescribed preprocessing, quantified as the silhouette coefficient over
the three simulated types (n = 3,000 cells, 1,000 per type). Mean expression of
each type is given beneath the stage label. The three types differ only by a
global expression level, and library-size normalization removes exactly that, so
separability falls from 0.472 to −0.063 and the benchmark can no longer
distinguish them. Scope: the Gaussian simulation written by
`prep_simu_data.ipynb`; the splatter dataset in the same notebook was not
accessible and is not assessed. Source data are provided as a Source Data file.

---

**Fig. 3 | Two silent barriers to reuse, and CAR-NK performance once both are cleared**

**a** Energy distance to the held-out D21 and D28 cells against training budget,
for models trained on raw counts (red) and on `normalize_total` + `log1p` data
(blue). Code, data, split and seed are identical between the two series; only
preprocessing differs. The undocumented step decides whether additional training
improves the fit (409.4 to 6.85) or degrades it (321.6 to 432.5), while training
loss falls in both.
**b** Energy distance against the latent noise scale used by
`sample_around_point`, for one trained model with everything else fixed. Red
circle, the hardcoded upstream default of 0.7. Dotted lines, the values chosen
independently for each seed on a validation task built only from training data.
The constant spans a 47-fold range in score and raises no error at any setting.
**c** Squidiff under the published protocol and configuration against two
baselines, on three metrics. Filled circle, mean over five independently trained
seeds (13, 37, 73, 101, 137); error bar, standard deviation; open circles,
individual seeds. Solid line, conditional-mean sampler; dashed line,
last-observation. Squidiff is worse than the conditional-mean baseline on all
three metrics in all five seeds. Per-gene mean correlation is invariant to
affine rescaling of the generated values, so the gap is not an artefact of
output scale. MMD uses an RBF kernel whose bandwidth was fixed on training data
(35.39); at the upstream noise scale the kernel saturates and returns
mean(k_xx) for every seed, so that condition is deliberately not plotted.

Split: training pre-infusion, D7 and D14, 11,588 cells from 13 samples; held out
D21 and D28, 4,668 cells from 5 samples, with no sample on both sides. Feature
selection retained the top 500 highly variable genes and was fitted on training
cells only. Source data are provided as a Source Data file.

---

## Statistics reported

```
train/validation/test split : train pre/D7/D14 (11,588 cells, 13 samples);
                              held out D21/D28 (4,668 cells, 5 samples);
                              validation for scale selection is a training-only
                              task, direction pre -> D7, scored against real D14
number of seeds             : 5 (13, 37, 73, 101, 137)
center statistic            : mean across seeds
spread                      : standard deviation across seeds
metric definitions          : multivariate energy distance; MMD with an RBF
                              kernel, bandwidth fixed on training data by the
                              median pairwise distance; Pearson correlation of
                              per-gene means
baseline definitions        : last-observation, the training mean repeated;
                              conditional-mean sampler, per-gene Gaussian fitted
                              on training cells
test / correction           : none applied; all five seeds fall on the same side
                              of both baselines on all three metrics, reported
                              as such rather than as a p-value
source-data file            : artifacts/manuscript_figures/source_data.json
```

No micrographs, blots or gels appear in this figure set, so image-integrity
declarations do not apply.
