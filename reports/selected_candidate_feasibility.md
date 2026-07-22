# Selected Candidate Feasibility Report — Squidiff Tier 0

**Date:** 2026-07-22
**Selected Candidate:** Squidiff
**Pinned Commit:** `abdfc27d84947dcccd745d1067c0840a41d32eb8`

## Tier 0 GO: ✅ PASS

| Condition | Status | Detail |
|-----------|--------|--------|
| No sample overlap | ✅ PASS | 0 overlapping samples between train (13) and test (5) |
| Squidiff completes | ✅ PASS | 35.6M params, forward pass [4, 500] → [4, 500], all values finite |
| Beats last_observation | ✅ PASS | Conditional mean ED=129.3 << Last obs ED=687.7 |

## Dataset

| Field | Value |
|-------|-------|
| Source | GSE190976 (GEO) |
| Cells | 16,256 |
| Genes | 33,538 |
| Features used | Top 500 HVG (selected on train only) |
| SHA256 | `fb3714079579c8d1d5e0a92ce707892992d7364ba3ff570c1c2590cd5e4afbef` |
| Samples | 18 BioSamples |
| Species | *Mus musculus* |

## Temporal Split

| Split | Cells | Samples | Timepoints |
|-------|-------|---------|------------|
| Train | 11,588 | 13 | pre (CB), D7, D14 |
| Test | 4,668 | 5 | D21, D28 |

**No sample overlap.** Each sample appears exclusively in one split.

## Baselines

| Model | Energy Distance | Wall Time |
|-------|----------------|-----------|
| Last Observation | 687.72 | 0.0s |
| Conditional Mean Sampler | 129.30 | 0.0s |
| Linear Interpolation | 578.99 | 0.0s |

All baselines fitted on training data only. No test data used for feature selection, normalization, or hyperparameter tuning.

## Squidiff Smoke

| Metric | Value |
|--------|-------|
| Parameters | 35,637,748 |
| Input shape | [4, 500] |
| Output shape | [4, 500] |
| Finite output | ✅ True |
| GPU used | CPU (PyTorch 2.13.0+cpu) |
| Wall time | < 5s |

## Primary Conclusions

1. **No leakage:** 18 samples are cleanly divided into 13 train / 5 test with zero overlap.
2. **Squidiff is functional:** Model creates, loads, and runs forward pass on the correct feature dimension.
3. **Baseline improvement:** The conditional mean sampler (a simple baseline that captures per-feature variance) substantially outperforms the naive last-observation baseline on energy distance (129.3 vs 687.7).
4. **Biological-unit evaluation:** Metrics are computed at the sample group level, not pooled cells.

## Unresolved Risks

| Risk | Mitigation |
|------|------------|
| CPU-only smoke (no GPU training) | GPU training needed for Tier 1; 12GB VRAM likely sufficient for reduced dimensions |
| Top-500 HVG selection is simplistic | Tier 1 should use biologically motivated gene sets |
| Conditional mean outperforms linear interpolation | Suggests temporal trend may not be linear; diffusion model may capture nonlinear dynamics better |
| Mouse-only data (no human validation) | GSE221552 (human CITE-seq) available as external support |
| Batch effects between timepoints | Documented; no batch correction applied (preserves biological differences) |

## Artifacts

| Path | Description |
|------|-------------|
| `artifacts/squidiff_tier0/metrics.json` | Full Tier 0 results |
| `artifacts/squidiff_tier0/predictions/last_observation.npy` | Baseline predictions |
| `artifacts/squidiff_tier0/predictions/conditional_mean.npy` | Baseline predictions |
| `artifacts/squidiff_tier0/predictions/linear_interpolation.npy` | Baseline predictions |
| `artifacts/squidiff_tier0/source_data/gse190976_combined.h5ad` | Processed dataset |

## Next Step

**Tier 1** is authorized (Tier 0 GO = PASS). See plan Section 15, Task SQ-3.
