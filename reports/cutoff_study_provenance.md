# Temporal-cutoff retraining provenance

Run date: 27 July 2026

## Source and inputs

| Field | Recorded value |
|---|---|
| Training source commit | `b9dc8874a2552f264380e6f8cf699cac0faeb0fa` |
| Source archive SHA-256 | `e08245be98036c933fcd8339d41cad34808b2216b13cbae1b2fa477c6c3e223c` |
| GSE190976 input SHA-256 | `7d1cd99b8f0c587b63a8ab139734c09976875a1e21a4090a5780fce8012518c7` |
| Model seeds | 13, 37, 73, 101 and 137 |
| Training steps | 50,000 per seed |
| Batch size | 64 |
| Model switches | `class_cond=False`, `use_encoder=True`, `num_layers=3`, `diffusion_steps=1000` |

The remotely executed source predates the correction-safe post-hoc evaluator.
Consequently, the pooled diagonal baseline emitted by that training archive is
not used in the manuscript. Baselines and same-distribution references are
recomputed from the cached train and test populations by the later evaluator,
and the corrected JSON replaces only the affected fields during consolidation.

## Hardware and software

| Component | Version |
|---|---|
| GPU | 2 × NVIDIA A100-SXM4-80GB |
| NVIDIA driver | 580.82.07 |
| Python | 3.10.20 |
| PyTorch | 2.4.1.post300 |
| PyTorch CUDA build | 12.0 |
| NumPy | 1.26.4 |
| SciPy | 1.15.3 |
| scikit-learn | 1.7.2 |
| pandas | 2.3.3 |
| anndata | 0.11.4 |
| scanpy | 1.11.5 |

## Information boundaries

The early cutoff trains on D0 and D7, evaluates D14 as its primary test and
reports D21 and D28 only as exploratory extensions. No target-informed
hyperparameter selection is performed; scales 0 and 0.03 were fixed before
training. The late cutoff trains through D21, validates its scale on the
training-window transition D7→D14 scored at D21, and evaluates D28. Train and
test sample identifiers are disjoint. Normalization and the selection of 500
highly variable genes are fitted without using test populations.

## Execution record

| Cutoff | GPU | Seeds expected | Completion | Interpretation |
|---|---:|---:|---|---|
| early D14 | 0 | 5 | 5/5 complete; 1,544.1–1,587.7 s per seed | D14 primary; D21/D28 exploratory |
| late D28 | 1 | 5 | 5/5 complete; 1,132.0–1,283.2 s per seed | Descriptive because D28 has one biological sample |

Remote outputs are retrieved as cutoff-scoped archives. The dispatcher checks
the remote archive SHA-256 before download and the local SHA-256 after download.
Per-seed model checkpoints, logs, generated populations and metric JSON files
remain in the audit artifacts; the submission package contains consolidated
metrics and source data rather than the large checkpoints.

## Correction-safe post-hoc evaluation

The post-hoc correction refits the affected pooled diagonal Gaussian on the
complete training window for each cutoff and computes repeated
same-distribution references. The other early and late baselines already use
the correction-safe training implementation. A separate primary-cutoff pass
applies the common metric schema to cached Squidiff populations with seed–scale
pairs 13–0.03, 37–0, 73–0.03, 101–0.03 and 137–0. The consolidation step
rejects any cutoff for which the expected and completed seed lists differ.

| Artefact | SHA-256 |
|---|---|
| Early D14 cutoff archive | `8fe82536c9b1c99b20842a074d092afaf765d66ca1043b5dcef9d2abf4307ff2` |
| Late D28 cutoff archive | `619f5fa699eb035dca768c52c14151f3fd7294a6158ba4e5519c7d7c1e43756d` |
| Early D14 post-hoc evaluation | `dead36212d9ffc450cc3093b1ae32f4ef10fe870374428c7921a4e88dbac2d5d` |
| Late D28 post-hoc evaluation | `d56ea9a760d14ce7eba53a84c578a62b83fc37d87bb60cc4fb0f50f7067439d3` |
| Consolidated three-cutoff manifest | `44f4304ea973740b5e23028dd88d22c38e710ac5eac47b723ee20d6dbda60c26` |
