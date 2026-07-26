# A leakage-safe reusability audit of Squidiff for single-cell temporal prediction

Guohao Lv¹˒², Yingchun Xia¹˒², Huichao Liu¹˒², Xiaolei Zhu¹˒², Shuai Yang¹˒², Ailian Zhou³˒⁴†, Lichuan Gu¹˒²†

† Correspondence: zhouailian@caas.cn; glc@ahau.edu.cn

## Abstract

Generative models for single-cell dynamics are difficult to reuse because successful execution does not establish predictive validity. We audited the released Squidiff checkpoint, code and data, then retrained the model for temporal prediction in an independent CAR-NK dataset. The release was operable, but reuse exposed an implicit data-scale requirement, three faults in a label-conditional interface and an unpropagated sampling default that dominated the latent trajectory. We therefore evaluated five seeds at three leakage-safe temporal cutoffs against four training-only baselines, same-distribution references and complementary marginal, dependence and population-composition metrics. Results depended strongly on the cutoff and estimand: simple temporal baselines were competitive on marginal distances, whereas Squidiff retained dependence structure in settings where diagonal samplers could not. A released VO analysis confirmed mechanism operation but was target-informed and does not support out-of-sample generalization. The audit provides executable corrections, information-boundary tests and reporting guidance for reuse.

<!-- END ABSTRACT -->

Predicting the distribution of future cell states is a recurring objective in developmental biology, cell therapy and perturbation modelling. Diffusion models are appealing because they can generate populations rather than a single conditional mean and could therefore retain heterogeneous or rare states that are biologically important. Squidiff applies a denoising diffusion model to single-cell transcriptomes and reports predictions of cellular development and responses to perturbations.¹ Its public package, repository, checkpoint and associated data make it a suitable subject for a reusability assessment.

Reusability has at least three separable levels. A released object may load and execute; a published workflow may be reconstructable from its code, data and documentation; and the reconstructed procedure may support a new predictive claim under a defensible information boundary. Conflating these levels can turn a successful sampling command into evidence for generalization, or turn a mismatch on new data into a claim that the software is broken. This distinction is especially important for longitudinal single-cell studies, where cells are numerous but biological samples are few, feature selection can leak across time and target populations may enter latent directions or hyperparameter selection without an obvious error.

We assessed the pinned Squidiff release before introducing new data, then applied its development-prediction mechanism to GSE190976, a longitudinal mouse CAR-NK dataset containing 16,256 cells from 18 deposited samples.⁵ The main task trained through day 14 (D14) and predicted D21 and D28. To determine whether an apparent result depended on that single split, we added an early cutoff trained on D0 and D7 with D14 as the primary endpoint, and a late cutoff trained through D21 with D28 as the endpoint. Every cutoff used sample-disjoint train and test populations, training-only preprocessing and feature selection, five predeclared model seeds and baselines fitted to the same training window. This design turns a software audit into a test of which claims remain valid as the temporal information boundary moves.

## Results

### Released artefacts are operable but do not by themselves establish prediction

We first tested the released VO checkpoint and its associated AnnData object using the architecture recorded by the authors (Fig. 1a). The checkpoint contains 62 tensors and 54,565,522 parameters and loads with zero missing and zero unexpected keys. Sampling 512 cells produced finite values; the energy distance between the generated and reference populations was 2.10. The released training matrix contains 6,838 cells and 596 genes, has mean expression 1.78 and maximum 14.47, and is consistent with log-normalized expression. These checks establish functional compatibility of the released objects with the pinned code path. They do not establish that a future population can be predicted, because the released checkpoint was fitted using both VO days and the released latent direction uses target-day cells.

The accessible upstream Gaussian simulation also executed, but its construction limits what it can verify (Fig. 2). Its three cell types differ through global expression levels of approximately 5, 8 and 10. Library-size normalization makes the per-type mean 50 for all three; log transformation then leaves means of 3.91–3.93. The silhouette coefficient falls from 0.472 in the raw simulation to −0.064 after the prescribed transformation. Thus the executable simulation verifies code movement through a conditioning path after normalization, but it cannot test recovery of its intended classes because the transformation removes the feature that defines them. We did not assess the separate Splatter input referenced through an inaccessible institutional path.

These observations motivated a conservative vocabulary for the rest of the audit. We call a component operable when strict loading, finite sampling or an end-to-end training step succeeds. We reserve predictive language for analyses in which the evaluated timepoint is excluded from model fitting, feature selection, preprocessing-parameter estimation, scale selection and baseline fitting. This separation is carried through the result manifest and figure source data.

### Reuse exposes data-scale, interface and sampling boundaries

The first boundary concerns expression scale. The released training script accepts an expression matrix but does not apply or validate the library-size normalization and log transformation used by the released data. On CAR-NK cells, raw counts reached 12,167, whereas the released matrix had a maximum of 14.47. With code, split, seed, architecture and latent noise scale held fixed, training longer on raw counts increased pooled energy distance from 376.76 at 5,000 steps to 561.72 at 50,000 steps even as optimization loss decreased. Applying `normalize_total(target_sum=10,000)` followed by `log1p` reversed the trajectory: energy distance decreased from 312.45 to 27.68. The numerical scale is therefore part of the executable model specification. A falling training loss cannot diagnose its omission.

The second boundary is an advertised label-conditional interface (Fig. 1b). With the released encoder enabled and class conditioning enabled, the first optimization step encounters three faults in sequence: labels enter the linear embedding with an integer type, remain on the host when the model is on the accelerator and have rank one although the embedding expects a column. Correcting one exposes the next. The corrections affect input plumbing rather than the diffusion objective or sampler and are paired with regression tests. The released development configuration uses `class_cond=False`, so this finding concerns reuse of the label-conditional interface and is not evidence that the authors’ encoder-based development results used that branch.

The third boundary is latent sampling variance. Development prediction encodes two observed populations, forms a direction from their mean latent representations, extrapolates from the later anchor and samples around the extrapolated point before decoding. The sampling function defaults to a latent standard deviation of 0.7, while the released prediction wrapper does not pass a value. In the CAR-NK primary model, the D7→D14 direction norm was 0.081, compared with an expected injected-noise norm of 5.42 at scale 0.7. Energy distance was 1,302.39 at that default and 27.56 at scale 0 in the one-seed sensitivity run. We therefore treated scale as part of the prediction protocol: primary and late cutoffs selected it using only transitions contained in their training windows, while the early cutoff compared the two predeclared scales 0 and 0.03 without target-based selection.

### Three temporal cutoffs define distinct predictive questions

The early cutoff trained on D0 and D7 (7,378 cells from 9 samples), used the D0→D7 direction and tested D14 as the primary endpoint (4 biological samples). D21 and D28 were retained as exploratory extensions because their extrapolation horizon is longer than the primary question. Both scales were reported for every one of the five seeds. The primary cutoff trained on D0, D7 and D14 (11,588 cells from 13 samples), selected scale using the D0→D7 transition scored at D14, and tested the pooled D21/D28 population (4,668 cells from 5 samples). The late cutoff trained on D0 through D21 (15,746 cells from 17 samples), selected scale using the D7→D14 transition scored at D21, and tested 510 D28 cells from one sample. Its metrics are descriptive because one test sample cannot support population-level biological inference.

At each cutoff we compared Squidiff with four task-aligned, training-only alternatives. Last observation resamples cells from the latest observed time. The pooled diagonal Gaussian estimates per-gene moments from the complete training window. The temporal diagonal Gaussian extrapolates the change in per-gene means between the two direction times and samples using the latest residual variance. The temporal factor Gaussian performs the same temporal extrapolation in a training-fitted factor space and adds training-fitted residual noise, allowing a simple baseline to retain cross-gene dependence. These baselines distinguish the value of recency, marginal moments, temporal trend and low-rank covariance.

In the primary cutoff, the same-distribution reference placed the finite-sample
scale of the metrics at energy distance 0.031 (95th percentile 0.070),
mean-expression correlation 0.9995 and normalized correlation-matrix distance
0.0263. Squidiff remained far above that reference, with energy distance
27.83 ± 1.80 and mean-expression correlation 0.830 ± 0.013 across five seeds.
All four baselines had better marginal fit. Last observation was strongest
(0.768 ± 0.037 and 0.974 ± 0.001, respectively), followed in energy distance
by the temporal factor Gaussian (1.953 ± 0.024), temporal diagonal Gaussian
(3.482 ± 0.008) and pooled diagonal Gaussian (4.265 ± 0.010). The result is
not explained by one training initialization: the Squidiff energy-distance
range, 24.90–29.26, did not overlap any baseline range.

Dependence and population composition qualified that marginal ordering.
Squidiff normalized correlation-matrix distance was 0.276 ± 0.017, better than
the pooled and temporal diagonal Gaussians (both 0.532) but worse than the
temporal factor Gaussian (0.151 ± 0.002) and last observation
(0.159 ± 0.002). Thus correlation recovery was not unique to the diffusion
model once a structure-capable baseline was included. At the nominal
eight-cluster setting, Squidiff cluster-mass error was 0.097 ± 0.002: lower
than the factor Gaussian (0.123 ± 0.001) and both diagonal Gaussians
(0.230–0.238), but higher than last observation (0.058 ± 0.001). Squidiff had
the highest rare-mass precision, 0.490 ± 0.015, whereas its rare-mass recall
was 0.679 ± 0.013, below the factor Gaussian (0.939 ± 0.001) and last
observation (0.910 ± 0.022). The diffusion model therefore generated a more
selective rare-state allocation than the Gaussian alternatives, but recovered
less of the target’s rare mass.

The early cutoff gave an even sharper recency result. Squidiff energy distance
was 20.99 ± 6.40 at scale 0 and 22.01 ± 6.29 at scale 0.03, with broad but
non-overlapping ranges relative to the temporal baselines (11.88–29.27 and
12.81–30.06, respectively). Resampling the D7 population reached
0.089 ± 0.009; the pooled diagonal, temporal factor and temporal diagonal
Gaussians reached 2.736 ± 0.005, 4.696 ± 0.062 and 5.974 ± 0.009,
respectively. Mean-expression correlation was 0.831 ± 0.043 and
0.827 ± 0.042 for the two Squidiff scales, 0.9980 ± 0.0002 for last
observation, 0.969 ± 0.0002 for the pooled Gaussian and approximately 0.905
for both temporal Gaussians. The two predeclared Squidiff scales therefore led
to the same substantive result; scale 0.03 did not rescue marginal prediction
and was not selected after inspecting D14.

Dependence and population composition did not reverse the early-cutoff
conclusion. Squidiff normalized correlation-matrix distance was
0.296 ± 0.045 at scale 0 and 0.289 ± 0.043 at scale 0.03, compared with
0.0436 ± 0.0043 for last observation, 0.104 ± 0.003 for the temporal factor
Gaussian and approximately 0.445 for both diagonal Gaussians. Cluster-mass
error was approximately 0.094 for Squidiff, 0.013 for last observation, 0.092
for the factor Gaussian and 0.210–0.234 for the diagonal Gaussians. Squidiff
rare-mass recall
was 0.692 ± 0.104 and 0.700 ± 0.093 at the two scales, with precision
0.633 ± 0.052 and 0.647 ± 0.043. Last observation retained both higher recall
(0.937 ± 0.014) and higher precision (0.884 ± 0.010). The exploratory D21 and
D28 extensions are reported in Supplementary Information because their
forecast horizon differs from the prespecified D14 question.

At the late cutoff, four seeds selected scale 0 and one selected 0.03 using the
training-window validation transition. Squidiff energy distance was
29.97 ± 2.30, compared with 5.119 ± 0.319 for last observation,
6.049 ± 0.036 for the pooled diagonal Gaussian, 7.293 ± 0.045 for the temporal
diagonal Gaussian and 6.194 ± 0.253 for the temporal factor Gaussian. Squidiff
mean-expression correlation (0.814 ± 0.007) was marginally higher than last
observation (0.811 ± 0.013), but both were far from the same-distribution mean
of 0.995. The corresponding normalized correlation-matrix distance was
0.470 ± 0.018 for Squidiff, versus 0.236 ± 0.016 for last observation and
0.213 ± 0.011 for the factor Gaussian. Squidiff cluster-mass error
(0.126 ± 0.003) also exceeded last observation (0.105 ± 0.004) and the factor
Gaussian (0.111 ± 0.003). Because D28 contains 510 cells from one sample, these
comparisons describe that sample and are not population-level estimates.

Moving the information boundary changed the difficulty of the task and the
strength of the baselines. Last-observation energy distance increased from
0.089 at D14 to 0.768 at the pooled D21/D28 endpoint and 5.119 at D28, while
Squidiff remained between 20.99 and 29.97 across the corresponding primary
summaries. The same-distribution energy-distance mean also rose from 0.031 in
the pooled primary endpoint to 0.280 in the smaller D28 population, showing why
raw values should not be compared without a cutoff-specific reference.
Nevertheless, at each cutoff every Squidiff seed remained separated from the
best simple baseline on energy distance. Structure-aware baselines further
showed that retaining cross-gene dependence did not require a diffusion model.
The robust conclusion is therefore conditional rather than binary: the
software and latent mechanism operate, but these leakage-safe CAR-NK tasks do
not establish a predictive advantage over training-only alternatives.

### Complementary metrics change what counts as successful reuse

Energy distance assesses the multivariate population but can be dominated by marginal location and scale. Correlation between per-gene population means summarizes direction of the average expression profile; it is invariant to a shared positive affine transformation and is not invariant to gene-specific rescaling. Neither statistic isolates whether generated cells reproduce gene–gene dependence. We therefore reported the raw and gene-count-normalized Frobenius distance between real and generated correlation matrices. Normalization by the retained gene count makes comparisons across feature sets interpretable while retaining the raw value for auditability.

We also replaced binary rare-cluster occupancy with mass-sensitive quantities. K-means centroids are fitted to the real test population, generated cells are assigned to their nearest centroids, and the two mass vectors are compared by mean absolute error and Jensen–Shannon divergence. Rare-mass recall measures how much real rare-cluster mass is recovered, while rare-mass precision measures how much generated rare mass is assigned to clusters that are rare in the target. Results are evaluated across 6, 8, 10 and 12 clusters and rare thresholds 0.05, 0.10 and 0.15. A method can therefore receive no credit merely for placing one cell in every rare cluster.

Same-distribution references split each real test population repeatedly and score one part against the other. They are not a zero-valued theoretical optimum; they show the finite-sample variation that remains when both populations come from the same empirical distribution. Across model and baseline comparisons, individual seed values are displayed and mean ± s.d. summarizes computational variability. Seeds are never used as substitutes for biological replicates, and no P value is calculated across seeds.

### The released VO setting is a target-informed mechanism check

We retained the released VO setting to ask whether the latent extrapolation mechanism can generate a structured population when supplied with the released checkpoint and its own data. At scale 0.03, Squidiff reached energy distance 7.24 and mean-expression correlation 0.975. A pooled diagonal Gaussian reached energy distance 1.51, whereas resampling D0 cells reached 47.58, confirming that the target population differs from the anchor. Squidiff nevertheless preserved dependence that diagonal sampling omitted: its correlation-matrix Frobenius distance was 52.36, compared with 95.01 for the pooled Gaussian and 98.68 for D0 resampling.

This analysis is target-informed. The checkpoint was trained on all 6,838 VO cells from D0 and D1, and the latent direction is computed using D1 cells. It is therefore a mechanism sanity check, not a prediction experiment, and does not support out-of-sample generalization. Its role is narrower but still useful: it shows that marginal fit and dependence recovery can order methods differently, and that the sampling-scale boundary also appears with the released checkpoint rather than only after transfer to CAR-NK.

## Discussion

This audit separates three questions that are often collapsed in computational reuse. The released Squidiff checkpoint and data are functionally compatible with the pinned code and generate finite output. Reconstructing a new workflow requires additional executable knowledge about data scale, input plumbing and latent sampling variance. Assessing prediction then requires a temporal boundary that excludes the target from every fitting and selection step. A report that states only whether software “runs” would miss the latter two questions; a benchmark that reports only a single held-out split would not reveal how the answer changes with temporal position.

The data-scale result illustrates why preprocessing should be treated as a model parameter. Raw counts and log-normalized values can both be stored in AnnData and can both produce a decreasing diffusion loss, but they lead to opposite relationships between training budget and held-out distance. Reusable releases should therefore validate expected range or distribution at entry, specify an executable transformation and record it with the checkpoint. Similarly, a sampling constant that is small relative to one latent direction may dominate another. Passing it explicitly through the public prediction function would make the assumption inspectable and allow a validation policy to be stated without editing library code.

The conditional-interface faults have a different interpretation. They are immediate and local, and their corrections are straightforward. Because the released development path disables class conditioning, they should not be used to discount results obtained through encoder extrapolation or drug-structure conditioning. They do show that an advertised interface can remain untested even when a package installs and another workflow succeeds. Minimal accelerator tests covering every public conditioning mode would have exposed type, device and rank errors before release.

The three cutoffs address a more substantive limitation. A future-state generator should be compared not only with a pooled moment sampler but also with the latest observed population and a temporal extrapolator that receives the same direction times. A structured factor Gaussian further tests whether any advantage reflects nonlinear generative modelling or simply preservation of covariance. These alternatives are intentionally simple: they establish the performance attainable from recency, marginal trends and low-rank dependence before credit is assigned to a diffusion model. The same-distribution reference then distinguishes a model–data gap from the finite-sample floor of the metric.

No single metric captures reusability for a generated cell population. Marginal distances reward location and dispersion; correlation-matrix distance rewards dependence; cluster-mass metrics reward population composition. Their disagreements are scientifically informative rather than an inconvenience to be removed. A diagonal Gaussian may match per-gene moments while omitting gene modules, whereas a model with less accurate marginals may retain cross-gene structure. The appropriate conclusion depends on whether the downstream use concerns average expression, joint programmes or rare-state abundance. Reporting both families prevents a method from being declared reusable on a property it was not shown to preserve.

The biological evidence remains limited. GSE190976 provides five test samples in the primary cutoff, four at the early D14 endpoint and only one at D28. Cells increase metric precision within a sample but do not create new biological replication. The late result is accordingly descriptive, and the cutoff comparison should not be interpreted as a general law of CAR-NK dynamics. The analysis also uses one dataset, one upstream model family and 500 training-selected genes. Broader conclusions require prospectively specified reuse across laboratories, species, interventions and preprocessing pipelines.

The practical output is therefore not a binary verdict on Squidiff. It is a set of conditions under which claims can be evaluated: verify released objects separately from generalization; make expression scale and sampling variance explicit; exercise every public interface; keep feature selection, scale selection and baseline fitting inside the training window; compare against temporal and structure-capable alternatives; and identify the biological unit behind every `n`. With these controls, reuse becomes an auditable scientific question rather than a successful command.

## Methods

### Upstream release and scope

Squidiff was pinned to commit `abdfc27d84947dcccd745d1067c0840a41d32eb8` (v1.0.8). The released VO checkpoint and AnnData object were obtained from Figshare (https://doi.org/10.6084/m9.figshare.27948633). Checkpoint tensors, architecture compatibility and strict state-dictionary loading were inspected before sampling. Functional verification used the recorded architecture (`use_encoder=True`, `class_cond=False`, three model layers and 1,000 diffusion steps) and a fixed random seed. The accessible Gaussian simulation from `prep_simu_data.ipynb` was reconstructed; the separate Splatter input behind an institution-specific path was outside scope.

### CAR-NK data and temporal splits

The public GSE190976 expression matrix contains 16,256 cells from 18 samples. Timepoints were mapped to D0, D7, D14, D21 and D28. Sample identifiers, not cells, defined train–test separation. Early, primary and late cutoffs were declared as described in Results. For each cutoff, train and test sample sets were checked for an empty intersection. Feature ranking used variance on training cells only, and the top 500 genes were applied to both partitions.

### Preprocessing

Each cutoff applied per-cell library-size normalization to a target sum of 10,000 followed by `log1p`. The raw-count versus log-normalized comparison held the data split, seed, architecture, training budgets and latent scale fixed. Values at 5,000, 20,000 and 50,000 optimization steps were generated from the corresponding saved checkpoints.

### Squidiff training and prediction

Every cutoff used five seeds (13, 37, 73, 101 and 137), 50,000 optimization steps, batch size 64, `use_encoder=True`, `class_cond=False`, three model layers and 1,000 diffusion steps. Development prediction encoded cells at two observed direction times, subtracted their mean latent representations, added that direction to the later latent anchor, sampled around the extrapolated point and decoded the result. Primary models selected among scales 0, 0.03, 0.1, 0.3 and 0.7 using the D0→D7 direction scored at D14. Late models used the D7→D14 direction scored at D21. Early models used fixed scales 0 and 0.03; neither D14 nor the exploratory later populations selected between them.

### Conditional-interface tests

The label-conditional path was exercised with both encoder and class conditioning enabled. Regression tests separately cover conversion of labels to floating point, transfer to the model device and reshaping to a single-column tensor before the linear label embedding. These patches do not alter the diffusion loss, noise schedule or sampling algorithm.

### Baselines

Baselines were fitted separately at each cutoff and seed using training cells only. Last observation resampled, with replacement, the latest observed population. The pooled diagonal Gaussian estimated a mean and variance for each gene from all cells in the cutoff’s training window. The temporal diagonal Gaussian extrapolated the per-gene mean change between the two direction times and used the latest-time residual variance. The temporal factor Gaussian fitted principal components and residual variance using training data, selected its component count from 5, 10, 20 and 50 using training-window reconstruction criteria, extrapolated the factor mean and sampled factor plus residual noise. Baseline output size matched the real population being scored.

### Metrics and sensitivity analyses

Multivariate energy distance was calculated from Euclidean pairwise distances. Mean-expression correlation was Pearson correlation between the real and generated vectors of per-gene population means. Correlation structure was compared after removing genes with zero variance in the real population; the Frobenius norm between gene-correlation matrices was reported raw and divided by the retained gene count.

For population composition, k-means was fitted to the real test population and generated cells were assigned to the nearest real centroid. Cluster-mass mean absolute error and Jensen–Shannon divergence compared the resulting mass vectors. Clusters below a real-mass threshold were labelled rare. Rare-mass recall was the recovered fraction of real rare mass, and rare-mass precision was the fraction of generated rare-assigned mass that corresponded to real rare clusters. Sensitivity combined cluster counts 6, 8, 10 and 12 with thresholds 0.05, 0.10 and 0.15. The nominal display uses 8 clusters and threshold 0.10.

Same-distribution references used repeated random disjoint subsamples of the real test population. Individual model seeds and arithmetic mean ± sample standard deviation across seeds summarize computational variability. Biological sample counts are reported for each cutoff. No hypothesis test treats seeds or cells as independent biological observations. The D28-only analysis is descriptive.

### Computational environment and reproducibility

Cutoff training used Python 3.10.20, PyTorch 2.4.1.post300 with CUDA 12.0, NumPy 1.26.4, SciPy 1.15.3, scikit-learn 1.7.2, pandas 2.3.3, anndata 0.11.4 and scanpy 1.11.5 on two NVIDIA A100-SXM4-80GB GPUs. Source archives, inputs, split manifests, model logs and returned result archives were SHA-256 checked. A correction-safe CPU pass recalculated all four baselines and the current metric schema from cached populations. Consolidation rejects a cutoff unless its expected and completed seed lists match.

Generative artificial intelligence assisted language editing, code support and preparation of submission materials. The authors inspected the generated text and code, reran the analyses and accept responsibility for the accuracy, originality and integrity of the work.

## Data availability

GSE190976 is available from the Gene Expression Omnibus. The released Squidiff checkpoint and training data are available from Figshare at https://doi.org/10.6084/m9.figshare.27948633. The existing derived-data record is available at https://doi.org/10.5281/zenodo.21510503. Figure source data and the consolidated three-cutoff result manifest accompany this submission and will be deposited as a versioned public release.

## Code availability

Audit code, regression tests and environment specifications are available at https://doi.org/10.5281/zenodo.21525939. The upstream Squidiff revision is identified above. The submission package includes a software checklist that maps claims to executable artefacts.

## Acknowledgements

This work was supported by the National Natural Science Foundation of China (32472007, 62301006 and 62301008), the Natural Science Foundation of Anhui Province (2308085MF217 and 2308085QF202), and the Anhui Province Key Laboratory of Intelligent Agricultural Technology and Equipment.

## Author contributions

G.L. conceived the audit, implemented compatibility corrections, conducted training and evaluation, prepared figures and drafted the manuscript. Y.X., H.L., X.Z. and S.Y. contributed data curation, analysis and manuscript review. A.Z. and L.G. supervised the work, acquired funding and revised the manuscript. All authors reviewed and approved the manuscript.

## Competing interests

The authors declare no competing interests.

## References

1. He, S. et al. Squidiff: predicting cellular development and responses to perturbations using a diffusion model. *Nat. Methods* **23**, 65–77 (2026). https://doi.org/10.1038/s41592-025-02877-y
2. Ho, J., Jain, A. & Abbeel, P. Denoising diffusion probabilistic models. *Adv. Neural Inf. Process. Syst.* **33**, 6840–6851 (2020).
3. Song, J., Meng, C. & Ermon, S. Denoising diffusion implicit models. *International Conference on Learning Representations* (2021).
4. Székely, G. J. & Rizzo, M. L. Energy statistics: a class of statistics based on distances. *J. Stat. Plan. Inference* **143**, 1249–1272 (2013). https://doi.org/10.1016/j.jspi.2013.03.018
5. Li, L. et al. Loss of metabolic fitness drives tumor resistance after CAR-NK cell therapy and can be overcome by cytokine engineering. *Sci. Adv.* **9**, eadd6997 (2023). https://doi.org/10.1126/sciadv.add6997
6. Gretton, A., Borgwardt, K. M., Rasch, M. J., Schölkopf, B. & Smola, A. A kernel two-sample test. *J. Mach. Learn. Res.* **13**, 723–773 (2012).
7. Lotfollahi, M., Wolf, F. A. & Theis, F. J. scGen predicts single-cell perturbation responses. *Nat. Methods* **16**, 715–721 (2019). https://doi.org/10.1038/s41592-019-0494-8
8. Roohani, Y., Huang, K. & Leskovec, J. Predicting transcriptional outcomes of novel multigene perturbations with GEARS. *Nat. Biotechnol.* **42**, 927–935 (2024). https://doi.org/10.1038/s41587-023-01905-6
9. Bunne, C. et al. Learning single-cell perturbation responses using neural optimal transport. *Nat. Methods* **20**, 1759–1768 (2023). https://doi.org/10.1038/s41592-023-01969-x
10. Revisiting code reusability. *Nat. Mach. Intell.* **4**, 801 (2022). https://doi.org/10.1038/s42256-022-00554-9
11. Ahlmann-Eltze, C., Huber, W. & Anders, S. Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines. *Nat. Methods* **22**, 1657–1661 (2025). https://doi.org/10.1038/s41592-025-02772-6
