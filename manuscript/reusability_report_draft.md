# Reusability report: Output scale calibration limits a conditional diffusion model of single-cell dynamics

*Linked article: He et al., Squidiff: predicting cellular development and responses to perturbations using a diffusion model. Nature Methods (2025). https://doi.org/10.1038/s41592-025-02877-y*

---

## Abstract

Generative models are increasingly used to predict how cell populations change
over time, yet their behaviour outside the settings in which they were
developed is rarely examined. He et al. proposed Squidiff, a conditional
diffusion model that predicts cellular development and responses to
perturbations from single-cell transcriptomes. Here we reproduce Squidiff's
conditioned training path and apply it to temporal extrapolation in chimeric
antigen receptor natural killer (CAR-NK) cells, predicting late post-infusion
states from early ones. Three defects prevented the conditioned path from
running at all, each raising on the first optimizer step. After correcting
them, generated samples scored worse than a per-feature Gaussian baseline, and
worsened as training continued. We show that this is an output scale
calibration defect rather than a modelling failure: an affine map onto training
moments reverses the ordering and beats the baseline twofold, and a
marginal-preserving shuffle attributes the gain to learned cross-feature
structure. We provide the patches, the diagnostic and guidance for reuse.

---

## Main

Predicting how a cell population will look at a future time point is a
recurring problem in cell therapy, developmental biology and drug response
modelling. Diffusion models are attractive for this task because they generate
whole distributions rather than conditional means, and so can in principle
preserve the heterogeneity that makes a population biologically meaningful.
Squidiff, introduced by He et al., applies a conditional denoising diffusion
model to single-cell transcriptomes and reports prediction of cellular
development and of responses to perturbations. The accompanying code is
installable from PyPI and the repository is public, which makes it a natural
candidate for reuse.

We asked a narrow question: can Squidiff be trained on early post-infusion
CAR-NK cells and used to predict the population at later time points, when the
later time points are held out entirely? This is a demanding but realistic
setting. CAR-NK products are profiled longitudinally, samples are scarce, and
the states that matter clinically, such as exhausted or highly cytotoxic
subpopulations, are rare. Any method that could extrapolate a population
forward from early samples would be useful. We report what we found when we
tried, together with the corrections and diagnostics needed to reproduce it.

### The conditioned training path could not be run as published

We pinned the upstream repository at commit `abdfc27` (v1.0.8) and attempted a
training run with `use_encoder=True` and `class_cond=True`, the configuration
required for conditional generation. Training failed on the first optimizer
step. Three separate defects lie on this path, and they surface in a fixed
cascade: correcting one exposes the next (Fig. 1b).

First, conditioning labels leave the data loader as an `int64` array rather
than a float tensor, so the first linear layer raises `mat1 and mat2 must have
the same dtype, but got Long and Float`. The correct call is present in the
upstream source, commented out on the line directly above. Second, the
conditioning labels are not moved to the compute device although the model is,
which raises a CPU versus CUDA device mismatch. This defect is unreachable on a
CPU-only host, because host and compute device then coincide. Third, the label
embedding is an `nn.Linear(1, hidden)` layer and therefore requires rank-2
input, but receives the rank-1 labels the loader produces.

None of the three touches the diffusion process, the loss, the sampler or any
hyperparameter; each concerns dtype, device placement or tensor rank only. That
every one raises immediately, and that they cascade, indicates that this
configuration had not been executed end to end before release. We record the
corrections as three separate patches against the pinned commit, each with a
regression test that we confirmed turns red when its patch is reverted.

Everything else reproduced without intervention, and this is worth stating
plainly. Installation from PyPI succeeded at the pinned version, the model and
diffusion objects were constructed from the documented entry point, and the
scientific components ran unmodified. Once the three patches were applied,
training proceeded stably for 50,000 steps with a monotonically falling loss,
and DDIM sampling produced finite output of the expected dimension in under
three seconds for 4,668 cells. The defects we found are packaging faults on one
configuration branch, not evidence of a flawed model, and a reader should not
take them as a verdict on the method. They do, however, mean that anyone
reaching for conditional generation will be blocked at the first step, which is
the point at which most potential users would abandon the tool.

### Squidiff underperforms a trivial baseline on temporal extrapolation

We evaluated on GSE190976, a longitudinal mouse CAR-NK dataset of 16,256 cells
profiled from pre-infusion through day 28. We trained on pre-infusion, day 7
and day 14 (11,588 cells, 13 samples) and held out day 21 and day 28 (4,668
cells, 5 samples), with no sample appearing on both sides. Feature selection
retained the top 500 highly variable genes and was fitted on training cells
only. We scored agreement between generated and held-out populations with the
multivariate energy distance, and compared against three baselines fitted the
same way (Fig. 2).

After 5,000 training steps, Squidiff reached an energy distance of 321.6. This
beat a last-observation baseline (687.7) and linear interpolation (571.5). It
was, however, more than twice as far from the held-out population as a
conditional-mean sampler (129.3), which draws each gene independently from a
Gaussian fitted on the training cells. A 45.4M-parameter diffusion model was
therefore losing to a baseline carrying only per-gene means and variances.

### More training makes the raw output worse

The obvious explanation is an insufficient training budget. We tested it
directly by training independent models at 5,000, 20,000 and 50,000 steps, with
the split, seed, architecture and sampler held fixed (Fig. 3a).

Energy distance degraded monotonically, from 321.6 to 412.2 to 432.5, while the
training loss fell over the same range, from roughly 0.46 to 0.400 to 0.342.
The model was fitting its objective better and matching the held-out population
worse. Undertraining does not account for the gap.

The generated populations offered the explanation. Real day 21 and day 28 cells
had mean 25.9 and standard deviation 73.1 across the retained genes. Generated
cells drifted away from both as training continued, from mean 22.7 and standard
deviation 39.1 at 5,000 steps to mean 8.6 and standard deviation 24.2 at 50,000
steps (Fig. 3b). Energy distance is computed from Euclidean distances and is
therefore sensitive to scale. A generator whose output collapses toward low
magnitude and low variance is penalised heavily, however well it captures the
shape of the distribution.

### Rescaling separates scale from structure

To separate the two contributions we mapped generated samples onto the training
moments with a per-gene affine transform. The transform standardises samples by
their own statistics and then applies the training mean and standard deviation,
so only training data informs it and the held-out cells remain untouched.

Rescaling reversed the ordering entirely. Energy distance fell to 113.4, 74.1
and 62.8 at 5,000, 20,000 and 50,000 steps, improving monotonically with
training budget and beating the conditional-mean baseline by roughly twofold at
the largest budget (Fig. 3a). The learned representation was improving with
training throughout; only the output scale was degrading.

A rescaling that simply supplied the right marginals would be an uninteresting
result, since that is precisely what the conditional-mean baseline already
carries. We tested this with a negative control that permutes each gene
independently across cells. The permutation preserves every marginal exactly
and destroys only cross-gene structure. It returned energy distance to 127.0,
126.6 and 125.9 at the three budgets, stable across budgets and close to the
129.3 of the conditional-mean baseline (Fig. 3a). The advantage of rescaled
Squidiff over the baseline therefore comes from learned cross-gene structure,
not from the rescaling.

### Rare states are not recovered

The subpopulations that matter clinically remained out of reach. Using
clusters fitted on the held-out cells and counting any cluster below 10%
prevalence as rare, the conditional-mean baseline recovered none of the rare
cluster mass, and neither did raw Squidiff at any budget. Rescaled Squidiff
recovered a small and increasing fraction, 0.0 at 5,000 steps, 0.025 at 20,000
and 0.072 at 50,000. The trend matches the energy-distance result, but the
absolute level is low enough that we would not recommend this configuration
where rare-state recovery is the objective.

## Discussion

Squidiff learns genuine cross-gene structure from these data, and learns more
of it with more training, but its raw output is miscalibrated in scale and
becomes more so as training proceeds. Reported without correction, the model
appears to lose to a baseline that carries no structure at all. The distinction
matters for anyone deciding whether to reuse the method, and it is invisible to
any evaluation that reports a single scale-sensitive number.

We cannot localise the cause within the architecture from these experiments.
Drift in the noise schedule, the sampler and the encoder conditioning are all
consistent with what we observed, and separating them would require ablations
we did not run. What the rescaling and shuffle experiments do establish is
where the defect is not: it is not a failure to learn population structure.

Several boundaries apply. The generation step conditions on the latest observed
class, day 14, because day 21 and day 28 labels are unseen by construction.
This tests temporal extrapolation rather than in-distribution generation. The
original work claims prediction of cellular development, so extrapolation falls
within the claimed scope, but the two settings should not be conflated. Our
evidence also rests on one mouse dataset with five held-out samples; a human
CAR-NK CITE-seq set that would have provided a species check could not be
obtained through GEO download. Docker was unavailable on the evaluation
machine, so we pinned a virtual environment instead of a container image, which
weakens the environment guarantee. Finally, we did not evaluate the
perturbation-response setting that forms the other half of the original work,
and nothing here speaks to it.

## Outlook

For anyone reusing Squidiff, three things follow. Apply the three patches
before attempting conditional generation, since the path does not run without
them. Rescale generated samples onto training moments before computing any
scale-sensitive metric, and report both the raw and rescaled numbers so the
calibration behaviour stays visible. Include a marginal-preserving shuffle
control, which costs one permutation and separates learned structure from
correctly reproduced marginals.

More broadly, the sharpest test we ran was also the cheapest. Sweeping the
training budget and watching a held-out metric move against the training loss
took under twenty minutes on a single consumer GPU, and it converted an
apparent failure into a diagnosable and correctable defect. We would encourage
that check as routine practice when reusing a generative model, particularly
where the evaluation metric is sensitive to scale.

---

## Figure captions

**Fig. 1 | Reusability assessment workflow and the defects on the conditioned
training path.**
**a**, Assessment pipeline. The upstream repository is pinned at commit
`abdfc27` (v1.0.8), three blocking defects are corrected as separate patches,
and the patched model is evaluated on CAR-NK temporal extrapolation under a
training-budget sweep and a calibration diagnostic.
**b**, The conditioning path from AnnData to the label embedding, annotated
with the three defect sites: label dtype at the data loader, device placement
at the microbatch transfer, and tensor rank at the label embedding. Each raises
on the first optimizer step, and correcting one exposes the next.

**Fig. 2 | Temporal split and baseline comparison.**
**a**, Split design for GSE190976. Training uses pre-infusion, day 7 and day 14
(11,588 cells, 13 samples); day 21 and day 28 are held out (4,668 cells, 5
samples). No sample appears on both sides.
**b**, Multivariate energy distance to the held-out population for the three
baselines and for Squidiff after 5,000 training steps. Lower is better. The
conditional-mean sampler, which carries only per-gene means and variances,
outperforms the diffusion model.

**Fig. 3 | Scale collapse, not structural failure.**
**a**, Energy distance against training budget for raw samples, samples
rescaled onto training moments, and rescaled samples with each gene permuted
independently. Horizontal lines mark the conditional-mean and last-observation
baselines. Raw scores degrade with training while rescaled scores improve; the
permutation control returns to the baseline floor at every budget.
**b**, Mean and standard deviation of generated populations against training
budget, with the held-out population shown for reference. Both moments drift
away from the real values as training proceeds.
**c**, Training loss and raw energy distance against training budget, plotted
on twin axes. The two move in opposite directions, which rules out
undertraining.
**d**, Rare-state recall for the conditional-mean baseline and for raw and
rescaled Squidiff at each budget. Clusters are fitted on held-out cells; any
cluster below 10% prevalence counts as rare.

---

## Data availability

The single-cell data analysed in this study are publicly available from the
Gene Expression Omnibus under accession GSE190976. The processed AnnData
object, the temporal split, the generated populations at each training budget
and the source data for every figure are available via Zenodo at
[DOI to be minted on acceptance].

## Code availability

All scripts for data preparation, training, sampling, evaluation and figure
generation are available via GitHub at
https://github.com/nblvguohao/biomed-reusability-gate and archived via Zenodo
at [DOI to be minted on acceptance]. The three compatibility patches against
the pinned upstream commit are provided under `vendor/patches/squidiff/`, each
with a regression test under `tests/regression/`. The original Squidiff source
is available via GitHub at https://github.com/siyuh/Squidiff, pinned here at
commit `abdfc27d84947dcccd745d1067c0840a41d32eb8` (v1.0.8).
