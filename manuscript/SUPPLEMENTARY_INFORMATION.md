# Supplementary Information

## A leakage-safe reusability audit of Squidiff for single-cell temporal prediction

Guohao Lv, Yingchun Xia, Huichao Liu, Xiaolei Zhu, Shuai Yang, Ailian Zhou and Lichuan Gu

## Supplementary Note 1 | Audit scope and evidence levels

The audit distinguishes three evidence levels. Functional verification asks
whether released files load strictly, build the documented architecture and
produce finite samples. Interface verification exercises public execution
paths with minimal synthetic or released inputs. Predictive assessment requires
a target population that remains outside model fitting, feature selection,
validation and baseline fitting. Evidence at one level is not promoted to the
next without the corresponding information-boundary checks.

The upstream revision is commit
`abdfc27d84947dcccd745d1067c0840a41d32eb8` (v1.0.8). The released VO
checkpoint contains 62 tensors and 54,565,522 parameters. It loads with zero
missing and zero unexpected state-dictionary keys. Sampling 512 cells produces
finite values and energy distance 2.098 to the sampled released reference
population. The associated matrix contains 6,838 cells and 596 genes (mean
1.781, maximum 14.468), consistent with log-normalized expression.

## Supplementary Note 2 | Label-conditional interface corrections

The label-conditional interface was tested with both encoder and class
conditioning enabled. Three independent incompatibilities appear in a fixed
sequence on an accelerator:

1. labels arrive at the linear embedding as integer tensors;
2. labels remain on the host while model parameters are on the accelerator;
3. labels have shape `(batch,)` while `Linear(1, hidden)` expects
   `(batch, 1)`.

The corrections cast labels to floating point, move them to the model device
and reshape them to one column. Each change is covered by a regression test
that exercises the affected code path. The diffusion objective, schedule,
architecture width and sampling procedure are unchanged. The released
development configuration sets class conditioning to false; the finding
therefore applies to reuse of the public label-conditional interface and is not
attributed to the encoder-development workflow.

## Supplementary Note 3 | Expression scale is part of the model specification

Raw CAR-NK counts and the released training data occupy different numerical
ranges. In the controlled A/B comparison, the same split, seed, architecture,
training budgets and latent-noise scale were used, and only preprocessing
changed.

| Training steps | Raw-count energy distance | Normalized + log1p energy distance |
|---:|---:|---:|
| 5,000 | 376.755 | 312.449 |
| 20,000 | 514.824 | 69.632 |
| 50,000 | 561.719 | 27.679 |

The transformation was per-cell library-size normalization to 10,000 followed
by `log1p`. Loss decreased in both conditions. Thus an optimization trace alone
cannot identify an incompatible expression scale, and the transformation must
be recorded with the checkpoint or validated at the data boundary.

## Supplementary Note 4 | Accessible Gaussian simulation

The accessible upstream Gaussian simulation contains 3,000 cells, 100 genes
and three classes. Before normalization, class means are 5.001, 7.999 and
9.996, and the silhouette coefficient is 0.472. After library-size
normalization, every class has mean 50.0. After `log1p`, class means are 3.911,
3.924 and 3.927 and the silhouette coefficient is −0.064. The simulation
continues to execute but no longer provides a discriminative class target. The
separate Splatter input referenced through an institution-specific location
was unavailable and is outside the audit.

## Supplementary Note 5 | Temporal-cutoff manifests

| Cutoff | Training timepoints | Direction | Validation policy | Test timepoints | Biological test samples |
|---|---|---|---|---|---:|
| Early | D0, D7 | D0→D7 | Fixed scales 0 and 0.03 | D14 primary; D21/D28 exploratory | 4 at D14; 5 later |
| Primary | D0, D7, D14 | D7→D14 | D0→D7 scored at D14 | D21, D28 | 5 |
| Late | D0, D7, D14, D21 | D14→D21 | D7→D14 scored at D21 | D28 | 1 |

Train and test sample identifiers are disjoint in every manifest. Early
training contains 7,378 cells from 9 samples; primary training contains 11,588
cells from 13 samples; late training contains 15,746 cells from 17 samples.
Feature selection ranks genes by training-set variance and retains 500 genes.
Normalization is applied per cell and does not estimate a population parameter
from the test set. The late cutoff is descriptive because its test population
contains one biological sample.

## Supplementary Note 6 | Baseline definitions

All baselines are refitted for every cutoff and seed and receive only the
corresponding training population.

| Baseline | Training information used | Generated target |
|---|---|---|
| Last observation | Cells at the latest observed time | Resampling with replacement |
| Pooled diagonal Gaussian | Per-gene mean and variance from the full training window | Independent per-gene Gaussian samples |
| Temporal diagonal Gaussian | Mean change between direction times and latest residual variance | Extrapolated per-gene mean with diagonal noise |
| Temporal factor Gaussian | Training-fitted factor space, factor-mean change and residual variance | Extrapolated low-rank factors plus residual noise |

The factor component count is selected from 5, 10, 20 and 50 using
training-window reconstruction criteria. Output population size is set to the
number of real target cells only after fitting. Random resampling is repeated
with the same seed schedule used for the model comparison.

## Supplementary Note 7 | Metric definitions

Energy distance compares multivariate populations using Euclidean distances.
Mean-expression correlation is Pearson correlation between vectors of
per-gene population means. It is invariant to a shared positive affine
transformation but not to gene-specific affine transformations.

For dependence, genes with zero variance in the real population are removed
because their Pearson correlations are undefined. The Frobenius norm between
real and generated gene-correlation matrices is reported both raw and divided
by the retained gene count.

For population composition, k-means is fitted to the real target population
and generated cells are assigned to their nearest target centroids. Let `p`
and `q` be the real and generated cluster-mass vectors. Cluster-mass error is
the mean of `|p − q|`; Jensen–Shannon divergence is calculated with natural
logarithms. Clusters with real mass below the specified threshold are rare.
Rare-mass recall is the recovered fraction of real rare mass. Rare-mass
precision is the fraction of generated mass assigned to real rare clusters
that corresponds to recovered real rare mass. Sensitivity crosses 6, 8, 10 and
12 clusters with thresholds 0.05, 0.10 and 0.15.

Repeated same-distribution references use disjoint random subsets of the real
target population. They quantify finite-sample metric variation and do not
enter model or hyperparameter selection.

## Supplementary Note 8 | Three-cutoff results

Values below are arithmetic mean ± sample standard deviation across the five
predeclared computational seeds. For the early cutoff, the two fixed Squidiff
scales are separate estimands. Primary and late Squidiff rows combine the
per-seed scales selected using only their training-window validation
transitions. Population-composition values use the nominal setting of eight
target-fitted clusters and a rare-mass threshold of 0.10.

### Supplementary Table 1 | Marginal and dependence metrics at the primary endpoints

| Cutoff | Method | Energy distance | Mean-expression r | Normalized correlation distance |
|---|---|---:|---:|---:|
| Early D14 | Squidiff, scale 0 | 20.995 ± 6.403 | 0.831 ± 0.043 | 0.296 ± 0.045 |
| Early D14 | Squidiff, scale 0.03 | 22.014 ± 6.291 | 0.827 ± 0.042 | 0.289 ± 0.043 |
| Early D14 | Last observation | 0.089 ± 0.009 | 0.998 ± 0.000 | 0.044 ± 0.004 |
| Early D14 | Pooled diagonal Gaussian | 2.736 ± 0.005 | 0.969 ± 0.000 | 0.445 ± 0.000 |
| Early D14 | Temporal diagonal Gaussian | 5.974 ± 0.009 | 0.904 ± 0.000 | 0.445 ± 0.000 |
| Early D14 | Temporal factor Gaussian | 4.696 ± 0.062 | 0.906 ± 0.001 | 0.104 ± 0.003 |
| Primary D21/D28 | Squidiff, training-selected scale | 27.830 ± 1.805 | 0.830 ± 0.013 | 0.276 ± 0.017 |
| Primary D21/D28 | Last observation | 0.768 ± 0.037 | 0.974 ± 0.001 | 0.159 ± 0.002 |
| Primary D21/D28 | Pooled diagonal Gaussian | 4.265 ± 0.010 | 0.938 ± 0.001 | 0.532 ± 0.000 |
| Primary D21/D28 | Temporal diagonal Gaussian | 3.482 ± 0.008 | 0.970 ± 0.000 | 0.532 ± 0.000 |
| Primary D21/D28 | Temporal factor Gaussian | 1.953 ± 0.024 | 0.970 ± 0.001 | 0.151 ± 0.002 |
| Late D28 | Squidiff, training-selected scale | 29.967 ± 2.301 | 0.814 ± 0.007 | 0.470 ± 0.018 |
| Late D28 | Last observation | 5.119 ± 0.319 | 0.811 ± 0.013 | 0.236 ± 0.016 |
| Late D28 | Pooled diagonal Gaussian | 6.049 ± 0.036 | 0.800 ± 0.002 | 0.427 ± 0.000 |
| Late D28 | Temporal diagonal Gaussian | 7.293 ± 0.045 | 0.783 ± 0.001 | 0.427 ± 0.000 |
| Late D28 | Temporal factor Gaussian | 6.194 ± 0.253 | 0.786 ± 0.007 | 0.213 ± 0.011 |

### Supplementary Table 2 | Population-composition metrics at the primary endpoints

| Cutoff | Method | Cluster-mass MAE | Rare-mass recall | Rare-mass precision |
|---|---|---:|---:|---:|
| Early D14 | Squidiff, scale 0 | 0.094 ± 0.003 | 0.692 ± 0.104 | 0.633 ± 0.052 |
| Early D14 | Squidiff, scale 0.03 | 0.095 ± 0.002 | 0.700 ± 0.093 | 0.647 ± 0.043 |
| Early D14 | Last observation | 0.013 ± 0.002 | 0.937 ± 0.014 | 0.884 ± 0.010 |
| Early D14 | Pooled diagonal Gaussian | 0.210 ± 0.001 | 0.409 ± 0.003 | 0.124 ± 0.001 |
| Early D14 | Temporal diagonal Gaussian | 0.234 ± 0.000 | 0.219 ± 0.000 | 0.063 ± 0.000 |
| Early D14 | Temporal factor Gaussian | 0.092 ± 0.001 | 0.760 ± 0.012 | 0.391 ± 0.008 |
| Primary D21/D28 | Squidiff, training-selected scale | 0.097 ± 0.002 | 0.679 ± 0.013 | 0.490 ± 0.015 |
| Primary D21/D28 | Last observation | 0.058 ± 0.001 | 0.910 ± 0.022 | 0.474 ± 0.003 |
| Primary D21/D28 | Pooled diagonal Gaussian | 0.230 ± 0.000 | 0.342 ± 0.000 | 0.079 ± 0.000 |
| Primary D21/D28 | Temporal diagonal Gaussian | 0.238 ± 0.000 | 0.215 ± 0.002 | 0.050 ± 0.000 |
| Primary D21/D28 | Temporal factor Gaussian | 0.123 ± 0.001 | 0.939 ± 0.001 | 0.305 ± 0.002 |
| Late D28 | Squidiff, training-selected scale | 0.126 ± 0.003 | 0.433 ± 0.078 | 0.564 ± 0.099 |
| Late D28 | Last observation | 0.105 ± 0.004 | 0.557 ± 0.076 | 0.938 ± 0.029 |
| Late D28 | Pooled diagonal Gaussian | 0.220 ± 0.000 | 0.738 ± 0.000 | 0.122 ± 0.000 |
| Late D28 | Temporal diagonal Gaussian | 0.237 ± 0.000 | 0.321 ± 0.000 | 0.053 ± 0.000 |
| Late D28 | Temporal factor Gaussian | 0.111 ± 0.003 | 0.729 ± 0.062 | 0.312 ± 0.011 |

### Supplementary Table 3 | Same-distribution references

Each reference reports the mean and the 5th–95th percentile interval from 50
random disjoint splits of the real primary target population.

| Cutoff | Energy distance | Mean-expression r | Normalized correlation distance |
|---|---:|---:|---:|
| Early D14 | 0.0311 (0.0200–0.0635) | 0.9995 (0.9989–0.9997) | 0.0278 (0.0254–0.0308) |
| Primary D21/D28 | 0.0314 (0.0150–0.0701) | 0.9995 (0.9989–0.9998) | 0.0263 (0.0234–0.0298) |
| Late D28 | 0.2795 (0.1621–0.4720) | 0.9951 (0.9895–0.9976) | 0.0846 (0.0749–0.1022) |

### Supplementary Table 4 | Exploratory extensions of the early model

These rows extend models trained only on D0 and D7 beyond the primary D14
endpoint. They are exploratory and do not enter scale selection.

| Method | Endpoint | Energy distance | Mean-expression r | Normalized correlation distance |
|---|---|---:|---:|---:|
| Squidiff, scale 0 | D21 | 27.907 ± 9.398 | 0.826 ± 0.047 | 0.172 ± 0.030 |
| Squidiff, scale 0 | D28 | 35.448 ± 14.665 | 0.806 ± 0.013 | 0.313 ± 0.045 |
| Squidiff, scale 0.03 | D21 | 28.101 ± 9.307 | 0.825 ± 0.047 | 0.169 ± 0.027 |
| Squidiff, scale 0.03 | D28 | 38.658 ± 16.936 | 0.804 ± 0.016 | 0.304 ± 0.042 |
| Last observation | D21 | 0.737 ± 0.035 | 0.976 ± 0.002 | 0.149 ± 0.002 |
| Last observation | D28 | 5.222 ± 0.146 | 0.805 ± 0.009 | 0.224 ± 0.005 |
| Pooled diagonal Gaussian | D21 | 5.374 ± 0.019 | 0.908 ± 0.001 | 0.541 ± 0.000 |
| Pooled diagonal Gaussian | D28 | 6.641 ± 0.030 | 0.781 ± 0.002 | 0.409 ± 0.000 |
| Temporal diagonal Gaussian | D21 | 14.590 ± 0.038 | 0.857 ± 0.001 | 0.541 ± 0.000 |
| Temporal diagonal Gaussian | D28 | 37.079 ± 0.101 | 0.534 ± 0.002 | 0.409 ± 0.000 |
| Temporal factor Gaussian | D21 | 13.392 ± 0.090 | 0.857 ± 0.001 | 0.178 ± 0.003 |
| Temporal factor Gaussian | D28 | 37.525 ± 0.572 | 0.532 ± 0.007 | 0.229 ± 0.003 |

## Supplementary Note 9 | Primary-cutoff robustness checks

The earlier primary analysis included sample-level uncertainty checks in
addition to the unified metric pass. A same-distribution energy-distance
reference over 50 splits had mean 0.0266 and 95th percentile 0.0509. The
conditional Gaussian estimate was 4.262 with a sample-level percentile
bootstrap interval 3.932–5.722. Individual Squidiff estimates ranged from
24.903 to 29.259, with the narrowest sample-level interval 22.441–28.297.
Leaving out each of the five test samples preserved the ordering between these
conditions. These intervals describe the finite set of deposited samples; they
do not turn model seeds or cells into biological replicates.

Kernel maximum mean discrepancy was retained only as a sensitivity analysis
because its ordering changed with the bandwidth. At the training-fitted
bandwidth 35.394, Squidiff values were higher than the pooled diagonal
Gaussian, but at smaller bandwidths the ordering changed for some seeds. It is
therefore not used for a headline conclusion.

## Supplementary Note 10 | Released VO mechanism check

The released VO checkpoint was trained on all 6,838 cells from D0 and D1, and
the latent direction uses both days. At latent scale 0.03, mean energy distance
across three sampling seeds was 7.241 and mean-expression correlation was
0.975. The pooled diagonal Gaussian had energy distance 1.505 and correlation
0.974; resampling D0 had energy distance 47.579 and correlation 0.281. At scale
0.7, Squidiff energy distance was 626.551 and correlation 0.451.

Dependence gave a different ordering. Squidiff correlation-matrix Frobenius
distance was 52.360, compared with 95.013 for the pooled diagonal Gaussian and
98.681 for D0 resampling. This result supports operation of the released
latent mechanism and illustrates the distinction between marginal and
dependence metrics. It is target-informed and does not support out-of-sample
generalization.

## Supplementary Note 11 | Statistical and computational interpretation

Each displayed model mean and standard deviation uses five independently
initialized computational runs. These seeds quantify training and sampling
variability. Biological sample identifiers are the observational units for
statements about the dataset. No null-hypothesis test is performed across
seeds, and no cell-level P value is reported.

Cutoff training used Python 3.10.20, PyTorch 2.4.1.post300 with CUDA 12.0 and
two NVIDIA A100-SXM4-80GB GPUs. NumPy 1.26.4, SciPy 1.15.3, scikit-learn 1.7.2,
pandas 2.3.3, anndata 0.11.4 and scanpy 1.11.5 were recorded. Source archives,
input matrices and retrieved archives are SHA-256 checked. Consolidation
requires every expected seed and overlays correction-safe post-hoc baseline
metrics without altering cached model populations.

## Supplementary Table 5 | Fixed training configuration

| Parameter | Value |
|---|---|
| Seeds | 13, 37, 73, 101, 137 |
| Training steps | 50,000 |
| Batch size | 64 |
| Encoder | Enabled |
| Class conditioning | Disabled |
| Model layers | 3 |
| Diffusion steps | 1,000 |
| Retained genes | 500, selected on training cells |
| Early latent scales | 0 and 0.03 |
| Primary/late candidate scales | 0, 0.03, 0.1, 0.3 and 0.7 |

## Supplementary Table 6 | Data and code records

| Resource | Persistent identifier |
|---|---|
| GSE190976 | Gene Expression Omnibus accession GSE190976 |
| Released Squidiff artefacts | https://doi.org/10.6084/m9.figshare.27948633 |
| Existing derived-data record | https://doi.org/10.5281/zenodo.21510503 |
| Audit code record | https://doi.org/10.5281/zenodo.21525939 |
