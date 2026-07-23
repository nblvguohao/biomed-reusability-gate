# Reusability report: Squidiff reproduces as released but is silently undermined by undocumented preprocessing and a hardcoded sampling constant

Guohao Lv<sup>1,2</sup>, Yingchun Xia<sup>1,2</sup>, Huichao Liu<sup>1,2</sup>, Xiaolei Zhu<sup>1,2</sup>, Shuai Yang<sup>1,2</sup>, Ailian Zhou<sup>3,4</sup>\*, Lichuan Gu<sup>1,2</sup>\*

<sup>1</sup>School of Artificial Intelligence, Anhui Agricultural University, Hefei 230036, China.
<sup>2</sup>Anhui Province Key Laboratory of Intelligent Agricultural Technology and Equipment, Anhui Agricultural University, Hefei 230036, China.
<sup>3</sup>Agricultural Information Institute, Chinese Academy of Agricultural Sciences, Beijing 100081, China.
<sup>4</sup>Key Laboratory of Agricultural Blockchain Application, Ministry of Agriculture and Rural Affairs, Beijing 100081, China.

\*Corresponding authors. Email: zhouailian@caas.cn (A.Z.); glc@ahau.edu.cn (L.G.)

*Linked article: He et al., Squidiff: predicting cellular development and responses to perturbations using a diffusion model. Nature Methods (2025). https://doi.org/10.1038/s41592-025-02877-y*

---

## Abstract

Generative models that forecast how cell populations change over time are increasingly influential, yet are rarely examined outside their development settings. He et al. proposed Squidiff, a conditional diffusion model that predicts cellular development and perturbation responses from single-cell transcriptomes. Here we verify Squidiff's released artefacts and apply the method to a new task: temporal extrapolation in chimeric antigen receptor natural killer (CAR-NK) cells, predicting late post-infusion states from early ones. The released checkpoint and data reproduce exactly; the method installs and trains unmodified. Reuse on new data, however, meets three barriers: a preprocessing requirement the released code path never applies nor checks, which silently inverts conclusions; a conditional-generation branch that cannot run as released; and a sampling constant the released prediction path never exposes, which swamps the predicted trajectory without raising an error. Under the published protocol, Squidiff underperforms a per-gene Gaussian baseline on all three metrics across five seeds — and the same ordering holds on the authors' own released data, pointing to the evaluation regime rather than to a transfer failure. We provide patches, regression tests and guidance for reuse.

---

Predicting how a cell population will look at a future time is a recurring need in cell therapy, developmental biology and drug-response modelling. Diffusion models are attractive for this task because they generate whole distributions rather than conditional means, and so can in principle preserve the heterogeneity that makes a population biologically meaningful. Squidiff, introduced by He et al., applies a conditional denoising diffusion model to single-cell transcriptomes and reports prediction both of cellular development and of responses to perturbation. The code installs from PyPI and the repository is public, which makes it a natural candidate for reuse.

We asked a narrow question: trained on early post-infusion CAR-NK cells, can Squidiff predict the population at later time points that are held out entirely? This is a demanding but realistic setting — CAR-NK products are profiled longitudinally, samples are scarce, and the clinically important states are rare. A reusability report is the right vehicle for the answer, because what we found is less a verdict on the method than a map of where reuse on new data actually fails. Two of the three failures are silent, and both produced wrong conclusions in our own hands before we caught them.

## The released artefacts reproduce

We began by verifying what the authors released, before introducing any new data (Fig. 1a). The published checkpoint loads into the documented architecture with 62 tensors and 54,565,522 parameters, zero missing and zero unexpected keys, so a strict load would pass. Sampling 512 cells from it yields finite output that matches the authors' reference population with a multivariate energy distance of 2.10 (Fig. 2a). Installation from PyPI succeeded at the pinned version (commit `abdfc27`, v1.0.8), the model and diffusion objects built from the documented entry point, and training and DDIM sampling ran unmodified. The released artefacts, in short, work as released, and this is worth stating plainly: nothing that follows is a claim that the method is broken.

One detail in the released data proved decisive later. The authors' own training matrix is log-normalized, with a mean of 1.78 and a maximum value of 14.5 (Fig. 2b). The released training script does not apply this transformation and the main repository does not state it. The published article's Methods describe it only as a one-line generic phrase — the count data were "normalized and log-transformed to correct for sequencing depth variability" — with no executable recipe, no library-size target and no log1p specification; the full transform appears only in the authors' separate reproducibility notebooks.

## Barrier 1: a preprocessing requirement the code path never applies

That gap between prose and code is the most dangerous barrier we met, because it is silent and it flips results. We first trained on raw counts, the natural default for a transcriptomics tool following the repository. We worked on GSE190976 (ref. 5; 16,256 mouse CAR-NK cells), training on pre-infusion, day 7 and day 14 (11,588 cells, 13 samples) and holding out day 21 and day 28 (4,668 cells, 5 samples), with no sample on both sides and the top 500 highly variable genes fitted on training cells only. Under the published latent-extrapolation protocol and architecture, at a single fixed noise scale (0.03, so Barrier 3 below cannot be responsible), energy distance to the held-out population rose with more raw-count training, from 376.8 at 5,000 steps to 514.8 at 20,000 and 561.7 at 50,000, while training loss fell throughout. Every conclusion we drew from such a run — that the model degrades with training, that it fails to recover rare states — was wrong.

Applying the upstream transformation, library-size normalization to 10,000 counts per cell followed by a log1p transform, reversed the picture (Fig. 3a). The same code, data, split, seed and protocol now improve with training, from 312.4 to 69.6 to 27.7 — an 11-fold gain — with preprocessing the only variable (source data in `artifacts/squidiff_latent_extrap_ab/`). The effect is therefore a property of the training data and the noise schedule, not of how the output is later conditioned or decoded; a class-conditional probe held fixed across the two conditions shows the same reversal, with rare-state recall rising from 0.0 to 1.0 (Supplementary Note 5). The generated output then sits on the same scale as the authors' released data (maximum 9.0 versus 14.5), where raw counts, with a maximum of 12,167, are three orders of magnitude away (Fig. 2b). The preprocessing step is therefore not optional, and because the released code path never applies it or checks for it, a reuser who follows the repository rather than the paper's prose has no signal that they have omitted it; they simply get a plausible-looking but inverted result.

## The provided benchmark cannot catch this

A reuser's natural check — validate the setup against the authors' own benchmark before trusting new data — is unavailable, because the provided benchmark cannot test the model. The upstream Gaussian simulation constructs three cell types that differ only by a global expression level, with mean expression 5.0, 8.0 and 10.0. The same library-size normalization the method requires removes exactly that signal, collapsing the three means to 50.0, 50.0 and 50.0 and dropping cell-type separability, measured by the silhouette coefficient, from 0.472 to −0.063 (Fig. 2c). After its own prescribed preprocessing the benchmark cannot distinguish its own classes (Supplementary Note 4). Compounding this, the reproducibility repository reports no quantitative metric anywhere in the 83 code cells of its two analysis notebooks, so there is no numeric target to reproduce against.

## Barrier 2: a conditional branch that cannot run

Squidiff is presented as a conditional model, but the conditional-generation path does not run as released. With `use_encoder=True` and `class_cond=True`, training fails on the first optimizer step, and three separate defects surface in a fixed cascade, each exposing the next (Fig. 1b). Conditioning labels leave the data loader as an int64 array, so the first linear layer raises a dtype error — the correct float call sits commented out on the line directly above. The labels are then not moved to the compute device although the model is, raising a CPU-versus-CUDA mismatch that is invisible on a CPU-only host. Finally, the label embedding is an `nn.Linear(1, hidden)` layer that expects rank-2 input but receives the rank-1 labels the loader produces. None of the three touches the diffusion process, the loss, the sampler or any hyperparameter. That all three raise immediately, and cascade, indicates the branch was never executed end to end, and the released configuration confirms this by setting `class_cond=False`. The development-prediction path we benchmark below uses the encoder with `class_cond=False`, so it avoids this branch; the barrier stands for anyone reusing Squidiff for conditional generation, its headline perturbation-response use. We record the corrections as three patches against the pinned commit, each with a regression test that turns red when its patch is reverted (Supplementary Note 2). This barrier is loud rather than silent: it blocks reuse at the first step, which is where most users would abandon the tool.

## Barrier 3: a sampling constant the released path never exposes

The published mechanism for predicting development is not class-conditional sampling but linear extrapolation in the model's semantic latent space: encode two observed states, take their mean difference as a direction, step along it, and sample around the target point before decoding. That sampling step uses an absolute noise scale that defaults to 0.7 in the `sample_around_point` signature, and the released prediction path (`interp_with_direction`) never forwards a value, so in practice it is fixed at 0.7 unless the reuser edits the library source — and it fails silently. On the CAR-NK encoder the direction between day 7 and day 14 has norm 0.081, while a scale of 0.7 injects a latent perturbation of norm 5.4 — roughly 67 times the direction being extrapolated and 6.7 times the within-timepoint spread — without raising any error (Fig. 3b). Sweeping the constant spans a 47-fold range in energy distance. Selecting the scale on a validation task built only from training data (direction pre-infusion to day 7, scored against real day 14) chose 0.03, 0.0, 0.03, 0.03 and 0.0 across five seeds — none near the released default (Supplementary Tables 1-2). A reuser who accepts the default gets degraded output and no indication why. The default fails on the authors' own data as well: on the released VO checkpoint the same 0.7 default swamps a direction of norm 0.84 with noise of norm 5.4, and the released model scores an energy distance of 626.6 where the repaired scale reaches 7.24 (Supplementary Note 8).

## Performance under the published protocol

With both silent barriers cleared, we evaluated Squidiff under its own published configuration and protocol, across five independently trained seeds and three metrics (Fig. 3c; per-seed and per-timepoint values in Supplementary Table 3). Both baselines are fit only on the pooled training window (pre-infusion, day 7 and day 14); held-out cells are never used for fitting, tuning or feature selection (Methods). Squidiff is worse than a per-gene Gaussian baseline, which carries only per-gene means and variances fit on that window, on all three metrics in all five seeds. With the validation-selected noise scale, Squidiff reaches an energy distance of 27.15 ± 1.78 against the baseline's 4.26, a maximum mean discrepancy under an RBF-kernel two-sample test (ref. 6) of 0.158 ± 0.008 against 0.058, and a per-gene mean correlation of 0.832 ± 0.013 against 0.938. It trails a last-observation baseline — the real day-14 cells resampled — by a wider margin still (energy distance 0.72, maximum mean discrepancy 0.011, per-gene mean correlation 0.976). The third metric is invariant to affine rescaling of the output, so the gap is not an artefact of output scale; we note, however, that all three metrics are marginal or distance-based rather than structural, a point we return to in the Discussion. At the released noise scale of 0.7 the model is far worse still (energy distance 1,244 ± 49); the maximum mean discrepancy there saturates the kernel and returns the same value for every seed, so we do not report it as a number.

## The same ordering holds on the authors' own released setting

A CAR-NK-only result would admit two explanations: that Squidiff fails to transfer to new data, or that the evaluation regime — distributional metrics on a task of this kind — favours a moment-matched sampler regardless of the model. To separate them we replayed the comparison on the authors' own released artefacts, where the method is reported to work: the released VO checkpoint and its released training data (6,838 cells, two days), predicting the day-1 population from the day-0 anchor through the same published latent-extrapolation mechanism (Supplementary Note 8). At the released noise scale of 0.7 the released model fails on its own data too (energy distance 626.6, kernel saturated, correlation 0.451) — Barrier 3 is not specific to our encoder. At a repaired scale (0.03), Squidiff reaches an energy distance of 7.24, yet still trails a per-gene Gaussian fit on the same pooled training data (1.51), whose mean sits midway between the two days; correlation is a dead heat (0.975 versus 0.974). The VO task is not a trivial one — a day-0 resample scores 47.6, so the population genuinely moves — yet the moment-matched baseline wins there as well. We therefore read the CAR-NK comparison not as evidence that Squidiff fails to transfer, but as evidence that, on the distributional metrics the field would naturally apply, its predictions do not outperform per-gene moment matching — a gap the original work could never have surfaced, because its reproducibility material reports no quantitative metric at all.

## Discussion

The three barriers differ in kind, and the difference is the point. One is loud and blocking: the conditional branch simply does not run, so it can frustrate but not mislead. The other two are silent: a preprocessing requirement the code path never applies, and a sampling constant the released prediction path never exposes, each let a reuser proceed all the way to a plausible, wrong answer. Both did exactly that to us. The preprocessing gap had us report that the model degrades with training when, under the published protocol, it in fact improves 11-fold, and we initially selected the noise scale against the test set before catching that leak. A check that stops at "does it install and run" will never catch either, which is precisely the gap a reusability report exists to fill.

It would be a mistake to read this as a failed-method story. The released checkpoint and data reproduce exactly, the method installs and trains cleanly, and the defects we found are packaging and documentation faults, not evidence that the diffusion model is unsound. Our performance results also do not license the claim that Squidiff fails to transfer to new data: the same baseline ordering appears on the authors' own released setting, so what we document is a property of the evaluation regime — distributional metrics reward marginal moments, and no quantitative check existed upstream to reveal it — rather than a defect specific to new data. What our results do not support is the specific use we tested: under the published protocol, extrapolating a CAR-NK population forward does not beat a per-gene Gaussian baseline on any metric in any seed.

Several boundaries apply. Our CAR-NK evidence rests on one dataset and one task, now complemented by a single positive-control task on the authors' own data. We test temporal extrapolation, not the perturbation-response setting that is the other half of the original work, and nothing here speaks to it. The extrapolation direction is estimated from only two timepoints, so the linear assumption may not fit a non-linear exhaustion trajectory. The baselines are strong on CAR-NK for a structural reason — the population mean drifts little between the training and held-out windows — but the VO control, where the population genuinely moves, shows the same ordering, so low drift alone does not explain the deficit. Relatedly, our three metrics are marginal or distance-based: none measures gene–gene correlation structure, which is the one quantity a diagonal-Gaussian baseline cannot capture by construction, so the performance result should be read as a statement about moments and distances rather than about every aspect of population structure. A human CAR-NK dataset that would have provided a species check could not be obtained, and Docker was unavailable on the evaluation machine, so we pinned a virtual environment rather than a container image.

## Outlook

For anyone reusing Squidiff, four things follow. Log-normalize before training — library-size normalization to 10,000 counts per cell, then log1p — and treat the released data matrix, not the training script, as the statement of the required input. Apply the three patches before attempting conditional generation, since that branch does not run as released. Never accept the hardcoded latent noise scale; select it on a validation task built only from training data, as we do here, because the released default swamps the trajectory being predicted. And report a scale-invariant metric alongside any scale-sensitive one, since a single Euclidean metric alone cannot separate a scale artefact from a structural shortfall.

More broadly, the most expensive failures we met were the cheapest to prevent. Each silent barrier was a one-line omission — a transform not applied, a constant left at its default — and each was found not by running the code harder but by checking a released artefact against an independent reference: the authors' own data scale, and a validation task held out from training. We would encourage both checks as routine when reusing a generative model, and would encourage authors to ship the preprocessing in the code path rather than in a notebook, and to treat a hardcoded constant as a liability to be documented, not a default to be inherited.

---

## Figure legends

**Fig. 1 | Reusability assessment of Squidiff and the three points at which reuse fails**
**a** Assessment workflow. Upstream is pinned at commit `abdfc27` (v1.0.8); the released checkpoint and its training data are verified before any new data is introduced; the upstream simulated benchmark is reproduced; the method is then applied to CAR-NK temporal extrapolation. Each barrier is drawn beside the step at which it surfaces. Green outline, the step that succeeded without intervention. Red, the three barriers.
**b** The conditioning data path under `use_encoder = True` and `class_cond = True`, with the three defect sites marked i to iii. Each raises a `RuntimeError` on the first optimizer step, in the order shown, so correcting one exposes the next. The released configuration sets `class_cond = False`, so this path was not exercised upstream. Schematic; no measured values are plotted.

**Fig. 2 | The released artefacts reproduce, but the upstream simulated benchmark cannot test them**
**a** Distribution of expression values for 512 reference cells from the released training data (grey) and 512 cells generated from the released checkpoint (green outline), plotted as densities over the same bins. The checkpoint loads into the released architecture with 0 missing and 0 unexpected keys, so a strict load would pass; multivariate energy distance between the two populations is 2.10.
**b** Value range of three datasets on a logarithmic axis. Dot, mean; tick, maximum. The authors' released training data (green, max 14.5) and CAR-NK data after `normalize_total` and `log1p` (blue, max 9.0) occupy the same scale; raw CAR-NK counts (red, max 12,167) are three orders of magnitude away.
**c** Cell-type separability of the upstream Gaussian simulated benchmark through its own prescribed preprocessing, quantified as the silhouette coefficient over the three simulated types (n = 3,000 cells, 1,000 per type). Mean expression of each type is given beneath the stage label. The three types differ only by a global expression level, and library-size normalization removes exactly that, so separability falls from 0.472 to −0.063 and the benchmark can no longer distinguish them. Scope: the Gaussian simulation written by `prep_simu_data.ipynb`; the splatter dataset in the same notebook was not accessible and is not assessed. Source data are provided as a Source Data file.

**Fig. 3 | Two silent barriers to reuse, and CAR-NK performance once both are cleared**
**a** Energy distance to the held-out D21 and D28 cells against training budget under the published latent-extrapolation protocol (released architecture, noise scale fixed at 0.03, seed 13), for models trained on raw counts (red) and on `normalize_total` + `log1p` data (blue). Code, data, split, seed and protocol are identical between the two series; only preprocessing differs. The preprocessing gap decides whether additional training improves the fit (312.4 to 27.7) or degrades it (376.8 to 561.7), while training loss falls in both. A class-conditional probe held fixed across the two conditions shows the same reversal (Supplementary Note 5).
**b** Energy distance against the latent noise scale used by `sample_around_point`, for one trained model with everything else fixed. Red circle, the hardcoded upstream default of 0.7. Dotted lines, the values chosen independently for each seed on a validation task built only from training data. The constant spans a 47-fold range in score and raises no error at any setting.
**c** Squidiff under the published protocol and configuration against two baselines, on three metrics. Filled circle, mean over five independently trained seeds (13, 37, 73, 101, 137); error bar, standard deviation; open circles, individual seeds. Solid line, conditional-mean sampler (per-gene mean and variance fit on the pooled training window only); dashed line, last-observation (real day-14 training cells resampled to held-out size). Both baselines are fit without touching held-out cells. Squidiff is worse than the conditional-mean baseline on all three metrics in all five seeds. Per-gene mean correlation is invariant to affine rescaling of the generated values, so the gap is not an artefact of output scale. MMD uses an RBF kernel whose bandwidth was fixed on training data (35.39; median pairwise distance heuristic, Methods); at the upstream noise scale the kernel saturates and returns mean(k_xx) for every seed, so that condition is deliberately not plotted.

Split: training pre-infusion, D7 and D14, 11,588 cells from 13 samples; held out D21 and D28, 4,668 cells from 5 samples, with no sample on both sides. Feature selection retained the top 500 highly variable genes and was fitted on training cells only. Source data are provided as a Source Data file.

---

## Acknowledgements

This work was supported by grants from the National Natural Science Foundation of China (32472007, 62301006, 62301008), the Natural Science Foundation of Anhui Province (2308085MF217, 2308085QF202), and the Anhui Province Key Laboratory of Intelligent Agricultural Technology and Equipment.

## Author contributions

[To be finalized with the author team — suggested split below, based on the work performed]
G.L. performed the reproduction, patching, training, evaluation and figure preparation, and wrote the manuscript. Y.X., H.L., X.Z. and S.Y. contributed to [data curation / analysis / manuscript review — confirm with each author]. A.Z. and L.G. supervised the study, acquired funding and revised the manuscript. All authors read and approved the final manuscript.

## Competing interests

The authors declare no competing interests.

---

## Data availability

The single-cell data analysed in this study are publicly available from the Gene Expression Omnibus under accession GSE190976, originally reported in ref. 5. The released Squidiff checkpoint and training data verified here are available via figshare at https://doi.org/10.6084/m9.figshare.27948633 (CC BY 4.0). The processed AnnData object, the temporal split, the generated populations for every condition and seed, and the source data for every figure are available via Zenodo at [DOI to be minted on acceptance].

## Code availability

All scripts for data preparation, training, sampling, evaluation and figure generation are available via GitHub at https://github.com/nblvguohao/biomed-reusability-gate and archived via Zenodo at [DOI to be minted on acceptance]. The three compatibility patches against the pinned upstream commit are provided under `vendor/patches/squidiff/`, each with a regression test under `tests/regression/`. The original Squidiff source is available via GitHub at https://github.com/siyuh/Squidiff, pinned here at commit `abdfc27d84947dcccd745d1067c0840a41d32eb8` (v1.0.8).

---

## References

1. He, Y. et al. Squidiff: predicting cellular development and responses to perturbations using a diffusion model. *Nat. Methods* (2025). https://doi.org/10.1038/s41592-025-02877-y
2. Ho, J., Jain, A. & Abbeel, P. Denoising diffusion probabilistic models. *Adv. Neural Inf. Process. Syst.* (2020).
3. Song, J., Meng, C. & Ermon, S. Denoising diffusion implicit models. *Int. Conf. Learn. Represent.* (2021).
4. Székely, G. J. & Rizzo, M. L. Energy statistics: a class of statistics based on distances. *J. Stat. Plan. Inference* (2013).
5. Li, L. et al. Loss of metabolic fitness drives tumor resistance after CAR-NK cell therapy and can be overcome by cytokine engineering. *Sci. Adv.* 9, eadd6997 (2023). https://doi.org/10.1126/sciadv.add6997
6. Gretton, A., Borgwardt, K. M., Rasch, M. J., Schölkopf, B. & Smola, A. A kernel two-sample test. *J. Mach. Learn. Res.* 13, 723–773 (2012).

---

## Methods

### Data and split

We use mouse CAR-NK single-cell RNA-seq data from GSE190976 (ref. 5; 16,256 cells). Cells are split by sample, not by cell: training comprises pre-infusion, day-7 and day-14 cells (11,588 cells from 13 samples) and the held-out set comprises day-21 and day-28 cells (4,668 cells from 5 samples), with no sample present on both sides. Feature selection retains the top 500 highly variable genes, fitted on training cells only. Held-out cells are never used for fitting, early stopping, hyperparameter selection, feature selection or normalization fitting.

### Preprocessing

Where stated, log-normalization means library-size normalization to 10,000 counts per cell followed by a log1p transform (scanpy `normalize_total` + `log1p`), matching the scale of the authors' released training matrix (mean 1.78, maximum 14.47). The upstream training script applies no such transform; the published article's Methods describe the requirement only as a one-line generic phrase ("normalized and log-transformed to correct for sequencing depth variability") without an executable recipe.

### Model, released configuration, and deviations

Upstream Squidiff is pinned at commit `abdfc27d84947dcccd745d1067c0840a41d32eb8` (v1.0.8). Unless stated, we use the released configuration: `class_cond=False`, `use_encoder=True`, `num_layers=3`, `diffusion_steps=1000`. We deviate from the released training run in three respects, each deliberate: we train for 50,000 steps rather than the released 2,400 (to probe behaviour across training budget, Fig. 3a; the 50,000-step budget is used for the seed study for consistency), we use 500 highly variable genes rather than the released 596 (feature selection fitted on training cells only, to avoid leakage), and we use batch size 64 rather than 16 (throughput; no qualitative difference was observed across budgets). The released checkpoint itself is used unmodified for verification.

### Latent-extrapolation protocol and noise-scale selection

Prediction follows the published mechanism: encode two observed states, take their mean difference as a direction in the semantic latent space, step along it, sample around the target point with `sample_around_point`, and decode with DDIM. The noise scale is selected per seed on a validation task built only from training data (direction pre-infusion→D7, scored against real D14 cells) over the candidate set {0.7, 0.3, 0.1, 0.03, 0.0}; the held-out timepoints never influence the selection. The test task uses direction D7→D14 and extrapolates one step (D21) and two steps (D28).

### Baselines

Both baselines are fit only on the pooled training window. The conditional-mean sampler draws i.i.d. diagonal Gaussians with per-gene means and variances fit on that window. The last-observation baseline resamples the real day-14 training cells with replacement to held-out size. A third variant — the pooled training mean tiled to every held-out cell, a zero-variance point mass — is reported in Supplementary Note 7 for the energy-distance decomposition and is not used as a comparator in the main text.

### Metrics

Energy distance (ref. 4) between two populations is `2·E‖x−y‖ − E‖x−x'‖ − E‖y−y'‖`; we report the decomposition into cross, within-real and within-generated terms in Supplementary Note 7, since a zero-variance prediction forfeits the final term. Maximum mean discrepancy uses an RBF kernel whose bandwidth (35.39) is fixed once as the median pairwise distance on training data (median heuristic) and never adapted to the samples being scored; at the released noise scale of 0.7 the kernel saturates (all pairwise cross-terms vanish) and we do not report a number there. Per-gene mean correlation is the Pearson correlation between per-gene population means and is invariant to affine rescaling of the generated values.

### Checkpoint verification, patches and regression tests

The released checkpoint (figshare, CC BY 4.0) is verified by strict state-dict loading (0 missing, 0 unexpected keys), finite sampling, and energy distance against the released reference population (Supplementary Note 6). The three compatibility patches live under `vendor/patches/squidiff/` in the code repository, each with a regression test that fails when the patch is reverted (Supplementary Note 2).
