# Nature Portfolio Reporting Summary — prepared answers

These answers are prepared for transfer to the current Nature Portfolio
Reporting Summary form. The study is a computational reanalysis of public data.
It introduces no new intervention involving people, animals or biological
materials.

## Statistics

### Sample sizes

The reused GSE190976 expression matrix contains 16,256 cells from 18 deposited
samples. Temporal cutoffs were predeclared:

| Analysis | Training population | Test population | Interpretation |
|---|---|---|---|
| Early | D0 and D7: 7,378 cells from 9 samples | Primary D14: 4 samples; exploratory D21 and D28: 5 samples | D14 is the primary endpoint; later endpoints are exploratory. |
| Primary | D0, D7 and D14: 11,588 cells from 13 samples | D21 and D28: 4,668 cells from 5 samples | Prespecified main analysis. |
| Late | D0, D7, D14 and D21: 15,746 cells from 17 samples | D28: 510 cells from 1 sample | Descriptive only because the test endpoint contains one biological sample. |

Five independently initialized training runs were completed for each cutoff
(seeds 13, 37, 73, 101 and 137). These runs quantify computational variability;
they are not treated as independent biological samples. The public dataset
fixed the available biological sample size, and no prospective power
calculation was performed.

### Data exclusions

No deposited sample was removed. The analysis began from the expression matrix
that passed the original study’s processing and quality-control workflow.
Within each cutoff, the 500 genes with the largest training-set variance were
retained. This is a train-fitted feature-selection rule, not a post hoc
cell-exclusion rule.

### Replication

All 15 planned model-training runs completed successfully; no run is omitted
on the basis of its metric value.
Repeated seeds are computational replicates. Biological replication is
represented by the deposited sample identifiers within each cutoff. The
D28-only analysis has one biological test sample and is therefore reported
descriptively, without population-level inference.

### Randomization

Biological samples were not randomly assigned because this is a retrospective
computational analysis. Temporal membership deterministically defines each
train and test split. Random-number seeds were fixed before model training,
baseline sampling and same-distribution reference sampling.

### Blinding

Blinding was not applicable. Timepoint labels are required to define the
prediction task, and all metrics are computed automatically from frozen arrays
after generation. No investigator-selected outcome measurement or manual image
assessment was performed.

### Statistical analysis

The study reports descriptive effect estimates rather than seed-based
null-hypothesis tests. For each cutoff, individual seed values and mean ±
standard deviation across five computational runs are shown. Biological sample
counts are stated separately. The primary analysis also includes a repeated
same-distribution reference and sample-level resampling checks. No P value or
multiple-testing correction is reported.

Metrics comprise multivariate energy distance; Pearson correlation between
per-gene population means; raw and gene-count-normalized Frobenius distance
between gene-correlation matrices; cluster-mass mean absolute error;
Jensen–Shannon divergence; rare-mass recall; and rare-mass precision. Cluster
sensitivity uses 6, 8, 10 and 12 clusters and rare-mass thresholds of 0.05,
0.10 and 0.15. Mean-expression correlation is invariant only to a shared
positive affine transformation, not to gene-specific transformations.

## Software and code

The audit code is archived at https://doi.org/10.5281/zenodo.21525939. The
upstream Squidiff code is pinned to commit
`abdfc27d84947dcccd745d1067c0840a41d32eb8` (release v1.0.8). Python, PyTorch,
CUDA and analysis-library versions, GPU identity, execution commands, source
hashes and wall times are recorded in the accompanying environment and cutoff
provenance manifests. Machine-readable metric and figure manifests are included
in the submission’s Source Data directory.

## Data availability

GSE190976 is available from the Gene Expression Omnibus. The released Squidiff
checkpoint and training data are available from Figshare at
https://doi.org/10.6084/m9.figshare.27948633. The existing derived-data archive
is available at https://doi.org/10.5281/zenodo.21510503. Source data supporting
the revised figures and the three-cutoff analysis are included with the
submission and will be deposited with a versioned public release.

## Life-sciences study design

This report reuses a deposited mouse CAR-NK single-cell transcriptomic dataset.
The authors performed no new animal procedure. Ethical approval and husbandry
information for the experiment that generated GSE190976 are reported in the
original publication and are not reassigned to this computational study.

| Reporting category | Applicability |
|---|---|
| Antibodies | Not involved in this computational reanalysis |
| Eukaryotic cell lines | Not newly used |
| Animals and other organisms | No new procedure; public data only |
| Human research participants | Not involved |
| Clinical data | Not involved |
| Dual-use research of concern | Not involved |
| Plants | Not involved |
| ChIP–seq | Not involved |
| Flow cytometry | Not performed in this report |
| MRI-based neuroimaging | Not involved |

## Artificial-intelligence assistance

Generative artificial intelligence assisted language editing, code support and
preparation of submission materials. The authors reviewed the generated text
and code, reran the analyses and remain responsible for the accuracy,
originality and integrity of the work.
