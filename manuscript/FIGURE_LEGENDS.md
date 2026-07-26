## Figure legends

**Fig. 1 | Evidence levels and information boundaries for the reusability
audit.** **a,** Evidence ladder separating functional checks of released
artefacts, executable tests of public interfaces and sample-disjoint temporal
prediction. **b,** Three CAR-NK cutoffs. Blue circles denote timepoints
available for training; ochre circles denote scored targets. The early cutoff
trains on D0/D7 and uses D14 as its primary endpoint, with D21/D28 exploratory.
The primary cutoff trains through D14 and evaluates D21/D28. The late cutoff
trains through D21 and evaluates D28. **c,** Operations separated by
information set. Normalization, feature selection, direction or validation
construction and baseline fitting use training information. Target populations
determine output count, metric scoring and same-distribution references only.
The D28-only cutoff contains one biological test sample and is interpreted
descriptively.

**Fig. 2 | Released artefacts are operable, whereas reuse depends on
preprocessing and latent sampling.** **a,** Audit of the released VO
checkpoint. The state dictionary contains 62 tensors and 54.6 million
parameters; strict loading yields zero missing and zero unexpected keys, and
512 generated cells contain finite values. The reported energy distance (2.10)
compares this generated population with a released reference sample and is a
functional check, not an out-of-sample prediction estimate. **b,** Pooled
energy distance to CAR-NK D21/D28 after training the same architecture, split
and seed for 5,000, 20,000 and 50,000 steps on either raw counts or
`normalize_total(target_sum=10,000)` followed by `log1p`. Latent-noise scale is
fixed at 0.03. **c,** Silhouette coefficient of the accessible upstream
Gaussian simulation before and after its prescribed normalization and log
transformation. The transformation removes the global expression level that
defines the simulated classes. **d,** Energy distance across latent-noise
scales for a 50,000-step primary model. The open orange marker denotes the
sampling-function default of 0.7. The y axis is logarithmic. Panels b–d show
single controlled or sensitivity runs and do not use seed error bars.

**Fig. 3 | Predictive performance across three leakage-safe temporal
cutoffs.** **a,** Multivariate energy distance; lower is better. **b,**
Pearson correlation between real and generated per-gene population means;
higher is better. This statistic is invariant only to a shared positive affine
transformation. **c,** Gene-count-normalized Frobenius distance between real
and generated gene-correlation matrices; lower is better. **d,** Mean absolute
error between real and generated cluster-mass vectors at the nominal setting
of eight target-fitted clusters and a rare threshold of 0.10; lower is better.
**e,** Rare-mass recall sensitivity for Squidiff and the temporal factor
Gaussian in the primary cutoff, averaged across cluster counts 6, 8, 10 and 12
at each displayed rare threshold. Points show individual computational seeds;
larger points and error bars show arithmetic mean ± s.d. across five
independently trained seeds (13, 37, 73, 101 and 137). Baselines are refitted
within each seed using only that cutoff’s training population. Early Squidiff
results are shown separately for the two predeclared scales 0 and 0.03;
primary and late results use scales selected exclusively within their training
windows. Seeds quantify computational variability and are not biological
replicates. No hypothesis test across seeds is reported. Machine-readable
values and all cluster-sensitivity settings are provided as Source Data.
