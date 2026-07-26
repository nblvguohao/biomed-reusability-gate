# Software and computational reusability checklist

## Scope and identity

| Item | Submission record |
|---|---|
| Audited software | Squidiff |
| Pinned upstream revision | Commit `abdfc27d84947dcccd745d1067c0840a41d32eb8` |
| Linked release | v1.0.8 |
| Linked article | He et al., *Nature Methods* 23, 65–77 (2026) |
| Audit code archive | https://doi.org/10.5281/zenodo.21525939 |
| Derived-data archive | https://doi.org/10.5281/zenodo.21510503 |
| Upstream data archive | https://doi.org/10.6084/m9.figshare.27948633 |
| Reused biological dataset | GEO GSE190976 |

## Environment and execution

| Requirement | Status |
|---|---|
| Exact Python and package environment recorded | Yes; environment manifests and execution logs accompany the code archive. |
| GPU and CUDA environment recorded | Yes; the final cutoff provenance report records the A100 execution environment. |
| Random seeds predeclared | Yes; 13, 37, 73, 101 and 137. |
| Model configuration fixed across seeds | Yes; encoder enabled, class conditioning disabled, three model layers, 1,000 diffusion steps, 50,000 training steps and batch size 64. |
| Strict checkpoint-loading audit | Yes; key and tensor compatibility are checked before sampling. |
| Regression tests for compatibility corrections | Yes; each correction is paired with a test that exercises the affected interface. |
| Machine-readable result manifest | Yes; `Source_Data/Revision_Result_Manifest.json`. |
| Figure source data | Yes; `Source_Data/Figure_Source_Data.json`. |

## Information-boundary controls

| Control | Implementation |
|---|---|
| Biological sample separation | Train and test sample identifiers are disjoint at every temporal cutoff. |
| Feature selection | Highly variable genes are fitted using training cells only. |
| Normalization | The transformation is specified explicitly and applied without test-population fitting. |
| Noise-scale selection | Primary and late analyses use training-window validation; the early analysis uses predeclared fixed scales 0 and 0.03. |
| Baseline fitting | All baseline parameters are estimated from the corresponding training window. |
| Target use | The VO analysis is labelled target-informed and is not interpreted as predictive generalization. |

## Evaluation and reporting

| Item | Status |
|---|---|
| Marginal distribution metric | Multivariate energy distance. |
| Mean-expression metric | Per-gene mean Pearson correlation; invariant only to a shared positive affine transformation. |
| Dependence metric | Raw and gene-count-normalized correlation-matrix Frobenius distance. |
| Population-composition metrics | Cluster-mass mean absolute error, Jensen–Shannon divergence, rare-mass recall and rare-mass precision. |
| Metric sensitivity | Cluster counts 6, 8, 10 and 12; rare thresholds 0.05, 0.10 and 0.15. |
| Same-distribution reference | Repeated disjoint subsamples from each real test population. |
| Uncertainty unit | Training seeds are computational replicates; biological samples remain the independent observational units. |
| Inferential boundary | No seed-based P value is reported; the D28-only cutoff has one biological sample and is interpreted descriptively. |

## Archive hygiene

| Check | Status |
|---|---|
| Credentials or private host details excluded | Yes. |
| Local absolute paths excluded | Yes. |
| Archival draft excluded | Yes. |
| Editable figures included | Yes; SVG and PDF exports accompany PNG and TIFF renderings. |
| Checksums included | Yes; SHA-256 values are recorded for every deliverable. |

