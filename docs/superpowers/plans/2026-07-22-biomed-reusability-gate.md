# Biomedical Reusability Candidate Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Every production change follows RED → GREEN → REFACTOR. Steps use checkbox syntax for tracking.

**Goal:** Build an auditable, test-driven feasibility gate that evaluates NicheTrans, Squidiff, and CMonge, deterministically selects exactly one candidate, and then executes only that candidate's Tier 0/Tier 1 Reusability Report workflow.

**Architecture:** A Python 3.11 orchestration package owns manifests, downloads, data contracts, leakage audits, metrics, immutable run records, candidate gates, and final selection. Each upstream model runs in its own pinned container and communicates through a JSON/file interface. The common feasibility stage is mandatory; branch-specific implementation is forbidden until `reports/selection_decision.json` selects one route.

**Tech Stack:** Python 3.11, `uv`, Pydantic v2, Typer, pytest, Ruff, mypy, pandas, NumPy, SciPy, scikit-learn, AnnData/Scanpy, PyTorch, Snakemake, Docker or Apptainer, Git, JSON/YAML/Parquet.

## Global Constraints

- Evaluation date is fixed as `2026-07-22`.
- Candidate priority is deterministic: NicheTrans if all NicheTrans hard gates pass; otherwise Squidiff if all Squidiff hard gates pass; otherwise CMonge if all CMonge hard gates pass; otherwise `NO_GO`.
- Do not execute full experiments for more than one candidate.
- No production code without a test that failed first for the expected reason.
- Unit tests must not access the network, GPU, or full public datasets.
- Integration tests must be marked `integration`; GPU tests must also be marked `gpu`; expensive tests must also be marked `slow`.
- Main scientific results must never use random cell/spot-level splitting when donor, patient, sample, slice, time point, drug, or perturbation identifiers are available.
- Test data must not be used for early stopping, hyperparameter selection, feature selection, normalization fitting, target transformation fitting, or probability calibration.
- Every downloaded or generated artifact must have SHA256, source URI, creation command, software commit, and environment/container identifier.
- Upstream scientific code must remain untouched. Compatibility patches must live under `vendor/patches/<candidate>/`, have regression tests, and be documented.
- All failures are retained. Never delete failed-run logs to make the pipeline look successful.
- Main conclusions must be supported by independent biological groups, not by treating individual cells/spots as biological replicates.
- Do not claim causal, therapeutic, or clinical validity from association, attention, feature importance, or in-silico masking alone.
- Stop after candidate selection if the selected branch does not meet its branch-specific Tier 0 gate.

---

# 1. Research decision encoded by this repository

This repository does not begin by assuming which paper should be pursued. It tests three routes:

1. **NicheTrans route:** spatial cross-omics translation in gastric cancer and immune niches.
2. **Squidiff route:** temporal and engineering-state prediction of CAR-NK cell distributions.
3. **CMonge route:** out-of-distribution single-cell perturbation prediction under independent-control evaluation.

The repository must produce:

```text
reports/
├── environment_inventory.md
├── literature_scope_2026-07-22.md
├── candidate_scorecard.md
├── selection_decision.json
├── selection_decision.md
├── nichetrans_feasibility.md
├── squidiff_feasibility.md
├── cmonge_feasibility.md
└── selected_candidate_feasibility.md
```

`selection_decision.json` is the machine-readable gate. Its schema is:

```json
{
  "evaluation_date": "2026-07-22",
  "selected_candidate": "nichetrans|squidiff|cmonge|NO_GO",
  "decision_rule": "string",
  "candidate_results": {
    "nichetrans": {
      "hard_gate_pass": false,
      "failed_gates": [],
      "evidence_paths": []
    },
    "squidiff": {
      "hard_gate_pass": false,
      "failed_gates": [],
      "evidence_paths": []
    },
    "cmonge": {
      "hard_gate_pass": false,
      "failed_gates": [],
      "evidence_paths": []
    }
  },
  "repository_commit": "string"
}
```

Once created, this file is immutable. A changed decision requires a new file named:

```text
reports/selection_decision_amendment_<N>.json
```

with a stated reason and evidence.

---

# 2. Candidate hard gates

## 2.1 NicheTrans hard gates

All must pass:

- `NT-G1`: Official repository and paper-associated archived version can be pinned and built.
- `NT-G2`: One official example completes end-to-end and emits predictions from source modality to target modality.
- `NT-G3`: At least two independent gastric biological units are available with paired or reliably registerable source and target spatial modalities.
- `NT-G4`: Each usable biological unit has at least 500 matched spatial locations after QC.
- `NT-G5`: At least 30 target features pass prevalence and variance filters in every evaluation unit.
- `NT-G6`: Registration/matching succeeds for at least 90% of retained source locations.
- `NT-G7`: A patient/slice-held-out split can be created with no biological-unit overlap.
- `NT-G8`: At least three simple baselines can run on the same split.
- `NT-G9`: A one-epoch or reduced-data NicheTrans smoke run completes within available GPU memory.
- `NT-G10`: Full data can be obtained without an unresolved manual-access dependency that blocks execution.

If all pass, select NicheTrans immediately.

## 2.2 Squidiff hard gates

Evaluated only if NicheTrans fails. All must pass:

- `SQ-G1`: Official repository and archived version can be pinned and built.
- `SQ-G2`: One official reproduction example completes and emits generated cell states.
- `SQ-G3`: CAR-NK longitudinal data contain at least three ordered time points.
- `SQ-G4`: The temporal holdout has at least two independent sample groups on the training side and two on the test side.
- `SQ-G5`: Every evaluated time/condition group has at least 100 cells after QC.
- `SQ-G6`: A time-extrapolation split can be created with no sample overlap.
- `SQ-G7`: At least three distributional baselines can run on the same split.
- `SQ-G8`: A reduced Squidiff smoke model can train and sample within available GPU memory.
- `SQ-G9`: At least one endpoint represents a scientifically meaningful CAR-NK transition rather than only a technical batch label.
- `SQ-G10`: Evaluation can use independent held-out groups and does not depend on reconstructing test cells one-to-one.

If all pass, select Squidiff.

## 2.3 CMonge hard gates

Evaluated only if NicheTrans and Squidiff fail. All must pass:

- `CM-G1`: Official repository and archived version can be pinned and built.
- `CM-G2`: One official example completes and predicts a treated-cell distribution.
- `CM-G3`: At least one external perturbation dataset has controls, perturbation labels, and independent sample/batch identifiers.
- `CM-G4`: At least 20 perturbations remain after QC.
- `CM-G5`: At least five perturbations can be held out from training.
- `CM-G6`: At least three independent control pools or batches are available for control splitting.
- `CM-G7`: A cold-perturbation or cold-context split can be created without perturbation/context overlap.
- `CM-G8`: At least three simple perturbation baselines can run.
- `CM-G9`: Original/shared-control and independent-control metrics can both be calculated.
- `CM-G10`: A reduced CMonge smoke run completes within available resources.

If all pass, select CMonge. Otherwise select `NO_GO`.

---

# 3. Branch-specific scientific questions

## 3.1 NicheTrans branch

Working title:

> Reusability report: Evaluating spatial cross-omics translation under patient, tissue and cancer-domain shifts

Primary questions:

- Does performance survive leave-one-patient/section-out evaluation?
- Is spatial context useful beyond expression-only and coordinate-only baselines?
- Does coordinate shuffling eliminate the reported advantage?
- Are predictions spatially coherent and feature-specific rather than mean-profile reconstruction?
- Can the method generalize to gastric tumor, adjacent tissue, and immune-rich regions?
- Are the reported explanatory features stable across seeds and spatial units?

## 3.2 Squidiff branch

Working title:

> Reusability report: Evaluating diffusion-based prediction of CAR-NK state dynamics under temporal and engineering shifts

Primary questions:

- Can early CAR-NK states predict D21/D28 distributions?
- Does the method outperform last-observation, linear interpolation, scVI-regression, and optimal-transport baselines?
- Can it preserve rare cytotoxic, proliferative, dysfunctional, or exhausted states?
- Does it generalize between engineered constructs or stimulation contexts?
- Are generated differential-expression and pathway changes reproducible across sample-held-out splits?
- Does performance remain after independent-control and group-level evaluation?

## 3.3 CMonge branch

Working title:

> Reusability report: Stress-testing conditional optimal transport for unseen immune perturbations

Primary questions:

- Does generalization persist for unseen perturbations, doses, cell contexts, and biological batches?
- Does performance survive independent-control evaluation?
- Does the method predict full distributions rather than only conditional means?
- How often do simple nearest-neighbour, additive, or low-rank baselines match it?
- Are rare responder states preserved?
- Are inferred transport maps stable and biologically interpretable across seeds?

---

# 4. Repository layout

```text
biomed-reusability-gate/
├── CLAUDE.md
├── README.md
├── LICENSE
├── CITATION.cff
├── Makefile
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .pre-commit-config.yaml
├── configs/
│   ├── candidates.yaml
│   ├── datasets/
│   │   ├── nichetrans_official.yaml
│   │   ├── gastric_spatial.yaml
│   │   ├── squidiff_official.yaml
│   │   ├── gse190976.yaml
│   │   ├── gse221552.yaml
│   │   ├── cmonge_official.yaml
│   │   └── immune_perturbation.yaml
│   ├── gates/
│   │   ├── nichetrans.yaml
│   │   ├── squidiff.yaml
│   │   └── cmonge.yaml
│   ├── experiments/
│   │   ├── nichetrans_tier0.yaml
│   │   ├── nichetrans_tier1.yaml
│   │   ├── squidiff_tier0.yaml
│   │   ├── squidiff_tier1.yaml
│   │   ├── cmonge_tier0.yaml
│   │   └── cmonge_tier1.yaml
│   └── models/
│       ├── baselines.yaml
│       └── upstream.yaml
├── containers/
│   ├── nichetrans/
│   │   └── Dockerfile
│   ├── squidiff/
│   │   └── Dockerfile
│   └── cmonge/
│       └── Dockerfile
├── vendor/
│   ├── manifests/
│   └── patches/
│       ├── nichetrans/
│       ├── squidiff/
│       └── cmonge/
├── src/reuse_gate/
│   ├── __init__.py
│   ├── cli.py
│   ├── schemas.py
│   ├── hashing.py
│   ├── provenance.py
│   ├── candidates.py
│   ├── decision.py
│   ├── data/
│   │   ├── download.py
│   │   ├── contracts.py
│   │   ├── spatial.py
│   │   ├── singlecell.py
│   │   ├── perturbation.py
│   │   ├── gse190976.py
│   │   └── gse221552.py
│   ├── splits/
│   │   ├── spatial_group.py
│   │   ├── temporal.py
│   │   ├── perturbation.py
│   │   └── audit.py
│   ├── models/
│   │   ├── protocol.py
│   │   ├── external.py
│   │   ├── spatial_baselines.py
│   │   ├── temporal_baselines.py
│   │   └── perturbation_baselines.py
│   ├── metrics/
│   │   ├── regression.py
│   │   ├── distribution.py
│   │   ├── spatial.py
│   │   ├── perturbation.py
│   │   └── bootstrap.py
│   ├── gates/
│   │   ├── base.py
│   │   ├── nichetrans.py
│   │   ├── squidiff.py
│   │   └── cmonge.py
│   ├── orchestration/
│   │   ├── run_id.py
│   │   ├── state.py
│   │   ├── plan.py
│   │   └── aggregate.py
│   └── reporting/
│       ├── feasibility.py
│       ├── decision.py
│       ├── tables.py
│       └── figures.py
├── external_runners/
│   ├── nichetrans/
│   │   ├── smoke.py
│   │   ├── train.py
│   │   └── predict.py
│   ├── squidiff/
│   │   ├── smoke.py
│   │   ├── train.py
│   │   └── sample.py
│   └── cmonge/
│       ├── smoke.py
│       ├── train.py
│       └── predict.py
├── tests/
│   ├── conftest.py
│   ├── fixtures/
│   │   ├── tiny_spatial/
│   │   ├── tiny_longitudinal.h5ad
│   │   └── tiny_perturbation.h5ad
│   ├── unit/
│   │   ├── test_schemas.py
│   │   ├── test_hashing.py
│   │   ├── test_data_contracts.py
│   │   ├── test_spatial_matching.py
│   │   ├── test_temporal_split.py
│   │   ├── test_perturbation_split.py
│   │   ├── test_leakage_audit.py
│   │   ├── test_external_runner.py
│   │   ├── test_spatial_metrics.py
│   │   ├── test_distribution_metrics.py
│   │   ├── test_control_split.py
│   │   ├── test_gates.py
│   │   └── test_decision.py
│   ├── integration/
│   │   ├── test_nichetrans_smoke.py
│   │   ├── test_squidiff_smoke.py
│   │   └── test_cmonge_smoke.py
│   └── regression/
│       ├── test_nichetrans_reference.py
│       ├── test_squidiff_reference.py
│       └── test_cmonge_reference.py
├── workflows/
│   └── Snakefile
├── scripts/
│   ├── pin_upstreams.sh
│   ├── build_containers.sh
│   └── reproduce_selected.sh
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── manifests/
├── runs/
├── artifacts/
├── reports/
└── docs/
    ├── protocol.md
    ├── progress.md
    ├── leakage_policy.md
    ├── metric_policy.md
    └── statistical_analysis_plan.md
```

---

# 5. Common data contracts

## 5.1 Spatial pair contract

A spatial cross-omics pair is represented by:

```python
class SpatialPair:
    source: AnnData
    target: AnnData
    pair_id: str
    biological_unit_id: str
    patient_id: str
    tissue_state: str
    source_modality: str
    target_modality: str
    match_table: pandas.DataFrame
```

`match_table` must contain:

```text
source_location_id
target_location_id
distance_normalized
match_method
match_confidence
```

The source and target matrices must not be joined until matching has passed audit.

## 5.2 Longitudinal single-cell contract

`AnnData.obs` must contain:

```text
cell_id
dataset_id
sample_id
donor_id
species
timepoint_raw
timepoint_numeric
engineering_state
stimulation_state
tumor_context
split_group
endpoint_label
```

Unknown non-applicable metadata must be the string `"NA"`, not an empty value.

## 5.3 Perturbation contract

`AnnData.obs` must contain:

```text
cell_id
dataset_id
sample_id
batch_id
cell_context
perturbation_id
perturbation_type
dose
time
is_control
control_pool_id
split_group
```

The object must preserve raw counts where available and explicitly state how controls were matched.

## 5.4 Provenance contract

Every processed object must include:

```text
source_accession
source_files
source_sha256
parser_version
upstream_commit
created_at_utc
normalization_state
feature_mapping_version
```

---

# 6. Common model-run interface

```python
from pathlib import Path
from typing import Literal, Protocol
from pydantic import BaseModel

class RunRequest(BaseModel):
    run_id: str
    candidate: Literal["nichetrans", "squidiff", "cmonge"]
    model_id: str
    train_path: Path
    validation_path: Path
    test_path: Path
    config_path: Path
    output_dir: Path
    seed: int

class RunResult(BaseModel):
    run_id: str
    status: Literal["success", "failed"]
    predictions_path: Path | None
    metrics_path: Path | None
    checkpoint_path: Path | None
    stdout_path: Path
    stderr_path: Path
    error_type: str | None
    error_message: str | None
    git_commit: str
    container_digest: str
    peak_cuda_allocated_mb: float | None
    train_seconds: float | None

class ModelRunner(Protocol):
    model_id: str

    def run(self, request: RunRequest) -> RunResult:
        ...
```

No upstream runner may return metrics without also returning raw predictions or generated samples.

---

# 7. Common split and leakage policy

## 7.1 NicheTrans

Main split unit:

```text
patient_id or biological_unit_id
```

Forbidden overlap:

```text
patient_id
biological_unit_id
slice_id
```

Feature filtering, spatial scaling, dimensionality reduction, and target transformation must be fitted on training units only.

## 7.2 Squidiff

Main split unit:

```text
sample_id
```

Temporal extrapolation:

```text
train: pre-infusion, D7, D14
validation: held-out training-side samples
test: D21, D28
```

If actual labels differ, map them through an explicit YAML table. Never infer time ordering lexicographically.

## 7.3 CMonge

Main split unit depends on endpoint:

```text
cold perturbation -> perturbation_id
cold context -> cell_context
cold batch -> batch_id
```

Controls are divided into disjoint training, validation, and test control pools. A control profile/cell must never be reused across metric sides when calculating independent-control metrics.

---

# 8. Metrics

## 8.1 NicheTrans

Primary:

- feature-wise Pearson and Spearman across held-out locations;
- location-wise Pearson;
- MAE;
- R²;
- spatial Moran's I concordance;
- spatial structure recovery relative to shuffled-coordinate null;
- target-feature rank correlation.

Baselines:

- target train mean;
- source-to-target ridge regression;
- partial least squares;
- k-nearest spatial neighbour;
- expression-only neural baseline;
- coordinate-only baseline;
- coordinate-shuffled NicheTrans.

## 8.2 Squidiff

Primary:

- energy distance;
- Wasserstein distance in train-fitted PCA space;
- MMD with fixed kernel policy;
- mean-expression correlation;
- variance recovery;
- differential-expression rank agreement;
- cell-state proportion error;
- rare-state recall;
- train-on-generated/test-on-real classifier performance.

Baselines:

- last observed distribution;
- linear interpolation in train-fitted latent space;
- conditional mean sampler;
- scVI latent regression;
- regularized optimal transport;
- CMonge only if CMonge can be run without expanding the selected branch scope.

## 8.3 CMonge

Primary:

- independent-control differential-expression correlation;
- shared-control correlation, reported separately;
- energy distance;
- Wasserstein distance;
- MMD;
- mean/variance recovery;
- top-k DEG precision and recall;
- pathway activity correlation;
- rare-state recovery.

Baselines:

- conditional mean;
- nearest perturbation;
- nearest chemical/genetic neighbour where metadata permit;
- additive context + perturbation model;
- ridge regression;
- low-rank matrix factorization.

All confidence intervals use biological-group bootstrap rather than cell-level bootstrap.

---

# 9. TDD tasks: common feasibility stage

## Task 1: Scaffold the typed repository

**Files:**
- Create: `pyproject.toml`
- Create: `Makefile`
- Create: `src/reuse_gate/__init__.py`
- Create: `src/reuse_gate/cli.py`
- Create: `src/reuse_gate/schemas.py`
- Create: `tests/unit/test_schemas.py`
- Create: `CLAUDE.md`

**Interfaces:**
- Produces `CandidateName`, `RunRequest`, `RunResult`, `GateResult`, and `SelectionDecision`.

- [ ] **Step 1: Write the failing test**

```python
import pytest
from pydantic import ValidationError

from reuse_gate.schemas import RunRequest, SelectionDecision

def test_run_request_rejects_identical_train_and_test_paths(tmp_path):
    same = tmp_path / "same.h5ad"
    with pytest.raises(ValidationError, match="train_path and test_path"):
        RunRequest(
            run_id="r1",
            candidate="squidiff",
            model_id="squidiff",
            train_path=same,
            validation_path=tmp_path / "val.h5ad",
            test_path=same,
            config_path=tmp_path / "config.yaml",
            output_dir=tmp_path / "out",
            seed=13,
        )

def test_selection_decision_rejects_unknown_candidate():
    with pytest.raises(ValidationError):
        SelectionDecision(
            evaluation_date="2026-07-22",
            selected_candidate="unknown",
            decision_rule="invalid",
            candidate_results={},
            repository_commit="abc",
        )
```

- [ ] **Step 2: Verify RED**

```bash
uv run pytest tests/unit/test_schemas.py -v
```

Expected: failure because `reuse_gate.schemas` does not exist.

- [ ] **Step 3: Implement the minimal schemas and CLI**

The CLI must expose:

```text
reuse-gate inventory
reuse-gate data
reuse-gate gate
reuse-gate decide
reuse-gate report
reuse-gate run-selected
```

- [ ] **Step 4: Verify GREEN**

```bash
uv run pytest tests/unit/test_schemas.py -v
uv run ruff check .
uv run mypy src
```

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "chore: scaffold typed biomedical reuse gate"
```

---

## Task 2: Environment and hardware inventory

**Files:**
- Create: `src/reuse_gate/provenance.py`
- Create: `tests/unit/test_provenance.py`

**Interfaces:**
- Produces `collect_environment_inventory() -> EnvironmentInventory`.
- Writes `reports/environment_inventory.md` and `.json`.

- [ ] **Step 1: Write the failing test**

```python
from reuse_gate.provenance import collect_environment_inventory

def test_inventory_contains_required_fields():
    inventory = collect_environment_inventory()
    assert inventory.python_version
    assert inventory.platform
    assert inventory.git_version
    assert inventory.disk_free_bytes >= 0
    assert inventory.docker_available in {True, False}
    assert inventory.apptainer_available in {True, False}
```

- [ ] **Step 2: Verify RED**

```bash
uv run pytest tests/unit/test_provenance.py -v
```

- [ ] **Step 3: Implement without assuming GPU or Docker exist**

Inventory commands must time out after 10 seconds and preserve stderr.

- [ ] **Step 4: Verify**

```bash
uv run pytest tests/unit/test_provenance.py -v
uv run reuse-gate inventory
test -f reports/environment_inventory.md
```

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: record reproducibility environment inventory"
```

---

## Task 3: Checksum-verified data and upstream manifests

**Files:**
- Create: `src/reuse_gate/hashing.py`
- Create: `src/reuse_gate/data/download.py`
- Create: `tests/unit/test_hashing.py`
- Create: `tests/unit/test_download.py`
- Create: `configs/candidates.yaml`

**Interfaces:**
- `sha256_file(path: Path) -> str`
- `download_verified(url: str, destination: Path, expected_sha256: str) -> Path`
- `pin_git_repository(url: str, ref: str, destination: Path) -> PinnedRepository`

- [ ] **Step 1: Failing tests**

```python
import pytest
from reuse_gate.hashing import sha256_file
from reuse_gate.data.download import verify_existing_file

def test_sha256_known_value(tmp_path):
    path = tmp_path / "abc.txt"
    path.write_bytes(b"abc")
    assert sha256_file(path) == (
        "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad"
    )

def test_wrong_checksum_is_rejected(tmp_path):
    path = tmp_path / "x.bin"
    path.write_bytes(b"x")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        verify_existing_file(path, "0" * 64)
```

- [ ] **Step 2: Verify RED**
- [ ] **Step 3: Implement `.partial` downloads, atomic rename, corruption quarantine, and manifest writes**
- [ ] **Step 4: Run tests**
- [ ] **Step 5: Commit**

```bash
git commit -m "feat: add immutable upstream and data manifests"
```

The first successful upstream pin must record exact commit hashes in:

```text
vendor/manifests/nichetrans.json
vendor/manifests/squidiff.json
vendor/manifests/cmonge.json
```

Do not follow `main` after pinning.

---

## Task 4: Common AnnData and spatial-pair contracts

**Files:**
- Create: `src/reuse_gate/data/contracts.py`
- Create: `tests/unit/test_data_contracts.py`

- [ ] **Step 1: Failing test**

```python
import anndata as ad
import numpy as np
import pandas as pd
import pytest

from reuse_gate.data.contracts import validate_longitudinal_adata

def test_longitudinal_contract_requires_sample_id():
    adata = ad.AnnData(
        X=np.ones((2, 2)),
        obs=pd.DataFrame(
            {"cell_id": ["c1", "c2"]},
            index=["c1", "c2"],
        ),
        var=pd.DataFrame(index=["GZMB", "PRF1"]),
    )
    with pytest.raises(ValueError, match="sample_id"):
        validate_longitudinal_adata(adata)
```

- [ ] **Step 2: Verify RED**
- [ ] **Step 3: Implement validators for spatial, longitudinal, and perturbation objects**
- [ ] **Step 4: Verify GREEN**
- [ ] **Step 5: Commit**

```bash
git commit -m "feat: enforce common biomedical data contracts"
```

---

## Task 5: Group split and leakage audit

**Files:**
- Create: `src/reuse_gate/splits/audit.py`
- Create: `src/reuse_gate/splits/spatial_group.py`
- Create: `src/reuse_gate/splits/temporal.py`
- Create: `src/reuse_gate/splits/perturbation.py`
- Create: `tests/unit/test_leakage_audit.py`
- Create: `tests/unit/test_temporal_split.py`
- Create: `tests/unit/test_perturbation_split.py`

- [ ] **Step 1: Failing tests**

```python
import pytest
from reuse_gate.splits.audit import assert_no_overlap

def test_overlap_is_rejected():
    with pytest.raises(ValueError, match="overlap"):
        assert_no_overlap(
            train_values={"S1", "S2"},
            test_values={"S2", "S3"},
            field_name="sample_id",
        )
```

```python
from reuse_gate.splits.temporal import build_temporal_holdout

def test_temporal_holdout_places_late_samples_only_in_test(longitudinal_obs):
    split = build_temporal_holdout(
        longitudinal_obs,
        train_max_time=14,
        test_min_time=21,
        group_col="sample_id",
    )
    assert split.train_max_time == 14
    assert split.test_min_time == 21
    assert set(split.train_groups).isdisjoint(split.test_groups)
```

- [ ] **Step 2: Verify RED**
- [ ] **Step 3: Implement split artifacts with dataset checksum and exact IDs**
- [ ] **Step 4: Verify**
- [ ] **Step 5: Commit**

```bash
git commit -m "feat: add mandatory group-held-out split audits"
```

---

## Task 6: External container runner

**Files:**
- Create: `src/reuse_gate/models/protocol.py`
- Create: `src/reuse_gate/models/external.py`
- Create: `tests/unit/test_external_runner.py`

- [ ] **Step 1: Failing tests**

```python
from reuse_gate.models.external import ExternalProcessRunner

def test_external_runner_captures_failure(fake_failing_command, run_request):
    result = ExternalProcessRunner(fake_failing_command).run(run_request)
    assert result.status == "failed"
    assert result.stderr_path.exists()
    assert result.error_type
```

- [ ] **Step 2: Verify RED**
- [ ] **Step 3: Implement subprocess-array execution, timeout, stdout/stderr preservation, and result validation**
- [ ] **Step 4: Verify**
- [ ] **Step 5: Commit**

```bash
git commit -m "feat: isolate upstream models behind file protocol"
```

---

## Task 7: Common metrics and biological-group bootstrap

**Files:**
- Create: `src/reuse_gate/metrics/regression.py`
- Create: `src/reuse_gate/metrics/distribution.py`
- Create: `src/reuse_gate/metrics/spatial.py`
- Create: `src/reuse_gate/metrics/bootstrap.py`
- Create: `tests/unit/test_spatial_metrics.py`
- Create: `tests/unit/test_distribution_metrics.py`

- [ ] **Step 1: Failing tests**

```python
import numpy as np
from reuse_gate.metrics.regression import regression_metrics

def test_perfect_prediction_has_zero_mae_and_unit_r2():
    y = np.array([[1.0, 2.0], [2.0, 3.0]])
    result = regression_metrics(y, y)
    assert result["mae"] == 0.0
    assert result["r2"] == 1.0
```

```python
import numpy as np
from reuse_gate.metrics.distribution import energy_distance_multivariate

def test_identical_distributions_have_zero_energy_distance():
    x = np.array([[0.0], [1.0], [2.0]])
    assert energy_distance_multivariate(x, x) == 0.0
```

- [ ] **Step 2: Verify RED**
- [ ] **Step 3: Implement numerically stable metrics and group bootstrap**
- [ ] **Step 4: Verify**
- [ ] **Step 5: Commit**

```bash
git commit -m "feat: add group-aware spatial and distribution metrics"
```

---

## Task 8: Candidate gate engine

**Files:**
- Create: `src/reuse_gate/gates/base.py`
- Create: `src/reuse_gate/gates/nichetrans.py`
- Create: `src/reuse_gate/gates/squidiff.py`
- Create: `src/reuse_gate/gates/cmonge.py`
- Create: `tests/unit/test_gates.py`

- [ ] **Step 1: Failing test**

```python
from reuse_gate.gates.nichetrans import evaluate_nichetrans_gate

def test_nichetrans_gate_fails_when_only_one_biological_unit():
    evidence = {
        "official_smoke_pass": True,
        "biological_units": 1,
        "min_locations_per_unit": 1000,
        "target_features": 100,
        "match_rate": 0.95,
        "group_split_pass": True,
        "baseline_count": 3,
        "gpu_smoke_pass": True,
        "manual_access_blocked": False,
    }
    result = evaluate_nichetrans_gate(evidence)
    assert result.hard_gate_pass is False
    assert "NT-G3" in result.failed_gates
```

- [ ] **Step 2: Verify RED**
- [ ] **Step 3: Implement all exact gates from Section 2**
- [ ] **Step 4: Verify**
- [ ] **Step 5: Commit**

```bash
git commit -m "feat: encode deterministic candidate hard gates"
```

---

# 10. NicheTrans feasibility tasks

These tasks are mandatory in the common stage because NicheTrans has first priority. They do not authorize Tier 1.

## Task 9: Pin and reproduce NicheTrans official smoke example

**Files:**
- Create: `containers/nichetrans/Dockerfile`
- Create: `external_runners/nichetrans/smoke.py`
- Create: `tests/integration/test_nichetrans_smoke.py`
- Create: `vendor/manifests/nichetrans.json`

- [ ] Write a failing integration test that expects a `predictions.npz` and `run_result.json`.
- [ ] Confirm failure before the container and runner exist.
- [ ] Pin the paper-associated archived version; record exact commit and archive DOI in the manifest.
- [ ] Build the container.
- [ ] Execute the smallest official example or a documented subset.
- [ ] Assert output shapes, finite predictions, and no test-data tuning.
- [ ] Save official reference metrics and tolerance.
- [ ] Commit:

```bash
git commit -m "build: pin and smoke-test NicheTrans"
```

If the official example cannot run, preserve the failure and mark `NT-G1` or `NT-G2` failed. Do not rewrite the model.

---

## Task 10: Gastric spatial data profiler and registration audit

**Files:**
- Create: `src/reuse_gate/data/spatial.py`
- Create: `tests/unit/test_spatial_matching.py`
- Create: `configs/datasets/gastric_spatial.yaml`
- Create: `reports/nichetrans_data_profile.md`

- [ ] **Failing test**

```python
import pandas as pd
from reuse_gate.data.spatial import match_spatial_locations

def test_exact_ids_are_preferred_over_coordinate_matching():
    source = pd.DataFrame(
        {"location_id": ["A", "B"], "x": [0.0, 1.0], "y": [0.0, 1.0]}
    )
    target = pd.DataFrame(
        {"location_id": ["B", "A"], "x": [1.0, 0.0], "y": [1.0, 0.0]}
    )
    matches = match_spatial_locations(source, target)
    assert list(matches["source_location_id"]) == ["A", "B"]
    assert list(matches["target_location_id"]) == ["A", "B"]
```

- [ ] Implement exact-ID matching first and normalized nearest-neighbour matching second.
- [ ] Report match rate, normalized distance distribution, duplicate matches, and unmatched locations.
- [ ] Profile biological units, modalities, target-feature prevalence, and spatial location counts.
- [ ] Generate `reports/nichetrans_feasibility.md`.
- [ ] Commit:

```bash
git commit -m "feat: profile and audit gastric spatial modality alignment"
```

No image interpolation is allowed before registration audit passes.

---

## Task 11: NicheTrans simple baselines and reduced-data GPU smoke

**Files:**
- Create: `src/reuse_gate/models/spatial_baselines.py`
- Create: `external_runners/nichetrans/train.py`
- Create: `external_runners/nichetrans/predict.py`
- Create: `tests/unit/test_spatial_baselines.py`

Required baselines:

```text
target_train_mean
ridge
partial_least_squares
spatial_knn
```

- [ ] Write tests proving each baseline fits only training units.
- [ ] Train baselines on a patient/section-held-out synthetic split.
- [ ] Run NicheTrans for one epoch or a reduced subset.
- [ ] Capture peak GPU memory and runtime.
- [ ] Populate all NT-G1 through NT-G10 evidence.
- [ ] Commit:

```bash
git commit -m "feat: complete NicheTrans feasibility gate"
```

---

# 11. Squidiff feasibility tasks

Run only if NicheTrans hard gate fails.

## Task 12: Pin and reproduce Squidiff official smoke example

**Files:**
- Create: `containers/squidiff/Dockerfile`
- Create: `external_runners/squidiff/smoke.py`
- Create: `tests/integration/test_squidiff_smoke.py`
- Create: `vendor/manifests/squidiff.json`

The test must require:

```text
generated_cells.npy or generated_cells.h5ad
run_result.json
finite generated values
expected feature dimension
```

Pin the archived version, run the smallest official generation example, and register tolerance for one reported metric.

Commit:

```bash
git commit -m "build: pin and smoke-test Squidiff"
```

---

## Task 13: Parse and audit CAR-NK longitudinal data

**Files:**
- Create: `src/reuse_gate/data/gse190976.py`
- Create: `src/reuse_gate/data/gse221552.py`
- Create: `tests/unit/test_gse190976.py`
- Create: `tests/unit/test_gse221552.py`
- Create: `reports/squidiff_data_profile.md`

- [ ] **Failing test**

```python
from reuse_gate.data.gse190976 import parse_timepoint

def test_parse_timepoint_orders_pre_and_days():
    assert parse_timepoint("pre-infusion") == 0
    assert parse_timepoint("D7") == 7
    assert parse_timepoint("D28") == 28
```

- [ ] Implement explicit YAML mappings for sample names, constructs, and time points.
- [ ] Build train/validation/test sample-held-out temporal splits.
- [ ] Report cells per sample, time, engineering state, and tumor context.
- [ ] Fail the gate if the independent-group threshold is not met.
- [ ] Commit:

```bash
git commit -m "feat: profile CAR-NK longitudinal feasibility"
```

---

## Task 14: Temporal baselines and reduced Squidiff run

**Files:**
- Create: `src/reuse_gate/models/temporal_baselines.py`
- Create: `external_runners/squidiff/train.py`
- Create: `external_runners/squidiff/sample.py`
- Create: `tests/unit/test_temporal_baselines.py`

Required baselines:

```text
last_observation
latent_linear_interpolation
conditional_mean_sampler
scvi_latent_regression
regularized_optimal_transport
```

- [ ] Write tests for generated cell count, feature dimensions, and train-only fitting.
- [ ] Run one reduced temporal extrapolation experiment.
- [ ] Calculate distribution metrics and cell-state proportion error.
- [ ] Populate SQ-G1 through SQ-G10 evidence.
- [ ] Generate `reports/squidiff_feasibility.md`.
- [ ] Commit:

```bash
git commit -m "feat: complete Squidiff CAR-NK feasibility gate"
```

---

# 12. CMonge feasibility tasks

Run only if both prior candidates fail.

## Task 15: Pin and reproduce CMonge official smoke example

**Files:**
- Create: `containers/cmonge/Dockerfile`
- Create: `external_runners/cmonge/smoke.py`
- Create: `tests/integration/test_cmonge_smoke.py`
- Create: `vendor/manifests/cmonge.json`

The integration test must verify a treated distribution is produced and is not identical to the control input.

Commit:

```bash
git commit -m "build: pin and smoke-test CMonge"
```

---

## Task 16: Perturbation data contract and independent-control split

**Files:**
- Create: `src/reuse_gate/data/perturbation.py`
- Create: `src/reuse_gate/metrics/perturbation.py`
- Create: `tests/unit/test_control_split.py`
- Create: `reports/cmonge_data_profile.md`

- [ ] **Failing test**

```python
from reuse_gate.data.perturbation import split_control_pools

def test_control_pools_are_disjoint(perturbation_obs):
    pools = split_control_pools(
        perturbation_obs,
        pool_col="control_pool_id",
        seed=13,
    )
    assert set(pools.train).isdisjoint(pools.validation)
    assert set(pools.train).isdisjoint(pools.test)
    assert set(pools.validation).isdisjoint(pools.test)
```

- [ ] Implement control-pool splitting.
- [ ] Implement shared-control and independent-control metrics as separate outputs.
- [ ] Audit perturbation, context, batch, and control overlap.
- [ ] Commit:

```bash
git commit -m "feat: add independent-control perturbation evaluation"
```

---

## Task 17: Perturbation baselines and reduced CMonge run

**Files:**
- Create: `src/reuse_gate/models/perturbation_baselines.py`
- Create: `external_runners/cmonge/train.py`
- Create: `external_runners/cmonge/predict.py`
- Create: `tests/unit/test_perturbation_baselines.py`

Required baselines:

```text
conditional_mean
nearest_perturbation
additive_context_perturbation
ridge
low_rank_factorization
```

- [ ] Test cold-perturbation isolation.
- [ ] Run one reduced held-out-perturbation experiment.
- [ ] Compare shared-control and independent-control metrics.
- [ ] Populate CM-G1 through CM-G10.
- [ ] Generate `reports/cmonge_feasibility.md`.
- [ ] Commit:

```bash
git commit -m "feat: complete CMonge feasibility gate"
```

---

# 13. Candidate selection

## Task 18: Deterministic decision engine

**Files:**
- Create: `src/reuse_gate/decision.py`
- Create: `src/reuse_gate/reporting/decision.py`
- Create: `tests/unit/test_decision.py`

- [ ] **Step 1: Failing tests**

```python
from reuse_gate.decision import choose_candidate

def test_nichetrans_wins_when_all_candidates_pass(pass_gate):
    decision = choose_candidate(
        nichetrans=pass_gate("nichetrans"),
        squidiff=pass_gate("squidiff"),
        cmonge=pass_gate("cmonge"),
        evaluation_date="2026-07-22",
        repository_commit="abc",
    )
    assert decision.selected_candidate == "nichetrans"

def test_squidiff_is_selected_when_nichetrans_fails(pass_gate, fail_gate):
    decision = choose_candidate(
        nichetrans=fail_gate("nichetrans", "NT-G3"),
        squidiff=pass_gate("squidiff"),
        cmonge=pass_gate("cmonge"),
        evaluation_date="2026-07-22",
        repository_commit="abc",
    )
    assert decision.selected_candidate == "squidiff"

def test_no_go_when_all_fail(fail_gate):
    decision = choose_candidate(
        nichetrans=fail_gate("nichetrans", "NT-G3"),
        squidiff=fail_gate("squidiff", "SQ-G4"),
        cmonge=fail_gate("cmonge", "CM-G6"),
        evaluation_date="2026-07-22",
        repository_commit="abc",
    )
    assert decision.selected_candidate == "NO_GO"
```

- [ ] **Step 2: Verify RED**
- [ ] **Step 3: Implement exact priority rules**
- [ ] **Step 4: Verify GREEN**
- [ ] **Step 5: Write reports and commit**

```bash
uv run reuse-gate decide
git add reports/selection_decision.json reports/selection_decision.md
git commit -m "feat: select one reusable biomedical model route"
```

After this commit, Claude Code must read `selected_candidate`.

- If `NO_GO`, stop model work and finish the failure report.
- If `nichetrans`, execute only Section 14.
- If `squidiff`, execute only Section 15.
- If `cmonge`, execute only Section 16.

---

# 14. Selected branch: NicheTrans Tier 0 and Tier 1

Execute only when selected.

## Task NT-1: Immutable spatial experiment planner

Create deterministic run IDs from:

```text
dataset checksums
biological-unit split
model config
seed
code commit
container digest
```

Tests must prove run IDs change when any input changes and successful runs cannot be overwritten.

## Task NT-2: Tier 0 experiment

Run:

```text
one patient/section-held-out split
seed 13
ridge
partial least squares
spatial kNN
NicheTrans
coordinate-shuffled NicheTrans
```

Generate:

```text
reports/selected_candidate_feasibility.md
artifacts/nichetrans_tier0/metrics.parquet
artifacts/nichetrans_tier0/predictions.parquet
artifacts/nichetrans_tier0/source_data/
```

Tier 0 GO condition:

- NicheTrans completes without leakage;
- predictions beat target-train-mean on at least two primary metrics;
- coordinate-shuffled performance is not better than true-coordinate performance;
- at least one independent held-out biological unit is evaluated;
- raw predictions and source data are reproducible.

## Task NT-3: Tier 1

Only after Tier 0 GO:

- all available patient/section-held-out splits;
- seeds `13, 37, 73, 101, 137`;
- spatial and non-spatial baselines;
- tumor vs adjacent-tissue shift;
- target-feature prevalence strata;
- immune-rich vs immune-poor regions;
- coordinate shuffle and neighbourhood ablation;
- biological-unit bootstrap;
- feature explanation stability.

Primary manuscript figures:

1. data and split design;
2. official reproduction;
3. held-out spatial cross-omics performance;
4. spatial-context ablation;
5. tissue/domain shift;
6. explanation stability.

---

# 15. Selected branch: Squidiff Tier 0 and Tier 1

Execute only when selected.

## Task SQ-1: Immutable temporal experiment planner

Run IDs include exact sample IDs and time mapping.

## Task SQ-2: Tier 0

Run:

```text
train: pre/D7/D14
validation: held-out training-side samples
test: D21/D28
seed 13
last observation
latent interpolation
scVI regression
regularized OT
Squidiff
```

Tier 0 GO condition:

- no sample overlap;
- Squidiff generates finite cells of the correct dimension;
- at least one distribution metric improves over last observation;
- rare-state proportions are not catastrophically lost;
- conclusions are consistent at biological-sample level, not only pooled-cell level.

## Task SQ-3: Tier 1

- five seeds;
- leave-one-sample-group-out;
- engineering-state holdout where supported;
- human/mouse results reported separately;
- GSE221552 stimulation/engineering analysis as external support, not merged with longitudinal endpoint;
- differential-expression/pathway agreement;
- rare-state retention;
- generated-vs-real classifier evaluation;
- compute and sampling-cost analysis;
- diffusion-step sensitivity.

Primary figures:

1. temporal design;
2. official reproduction;
3. early-to-late CAR-NK prediction;
4. state-proportion recovery;
5. construct/stimulation shift;
6. resource and sensitivity analysis.

---

# 16. Selected branch: CMonge Tier 0 and Tier 1

Execute only when selected.

## Task CM-1: Immutable perturbation experiment planner

Run IDs include control-pool split and perturbation holdout.

## Task CM-2: Tier 0

Run:

```text
one cold-perturbation split
seed 13
conditional mean
additive baseline
ridge
low-rank baseline
CMonge
shared-control metrics
independent-control metrics
```

Tier 0 GO condition:

- test perturbations are unseen;
- test control pool is disjoint;
- CMonge completes;
- at least one distribution metric improves over conditional mean;
- shared-control and independent-control conclusions are explicitly compared;
- raw generated distributions are retained.

## Task CM-3: Tier 1

- cold perturbation;
- cold cell context;
- cold batch;
- dose extrapolation if available;
- five seeds;
- rare-state recovery;
- control-split sensitivity;
- transport-map stability;
- pathway-level agreement;
- compute scaling.

Primary figures:

1. split and control policy;
2. official reproduction;
3. cold-perturbation results;
4. independent-control re-evaluation;
5. rare-state and distribution recovery;
6. transport stability.

---

# 17. Workflow commands

The final repository must support:

```bash
make setup
make lint
make typecheck
make test
make smoke
make inventory
make pin-upstreams
make profile-nichetrans
make gate-nichetrans
make profile-squidiff
make gate-squidiff
make profile-cmonge
make gate-cmonge
make decide
make selected-tier0
make selected-report
make selected-tier1
make selected-figures
```

`make decide` must short-circuit candidate work according to priority:

```text
NicheTrans pass -> do not run Squidiff/CMonge feasibility unless explicitly requested for audit
NicheTrans fail -> run Squidiff
Squidiff fail -> run CMonge
CMonge fail -> NO_GO
```

For strict comparison evidence, an optional command may run all three gates:

```bash
make audit-all-candidates
```

It must never automatically trigger all three Tier 1 branches.

---

# 18. CI

CPU CI:

```text
ruff
mypy
unit tests
synthetic smoke workflow
decision-engine tests
package build
```

GPU integration is manual or self-hosted:

```text
nichetrans smoke
squidiff smoke
cmonge smoke
selected Tier 0
```

CI must not download complete public datasets or large checkpoints on every push.

---

# 19. Claude Code execution rules

For every task:

1. Write one minimal failing test.
2. Run it and record the expected failure in `docs/progress.md`.
3. Write the minimum implementation.
4. Run the target test.
5. Run all unit tests.
6. Run Ruff and mypy.
7. Refactor only while tests remain green.
8. Commit with one focused message.
9. Update `docs/progress.md` with commands, outputs, artifacts, and commit SHA.

Do not ask for confirmation between tasks. Stop only when:

- a scientific hard gate fails and the decision policy requires moving to the next candidate;
- a missing permission or inaccessible dataset cannot be replaced without changing the research question;
- the repository contains uncommitted user work that would be overwritten;
- all candidates fail and `NO_GO` is selected.

When a candidate fails, generate a complete failure report before moving on.

---

# 20. First execution sequence

```bash
git init
git checkout -b feat/biomed-reusability-gate
mkdir -p docs/superpowers/plans
cp BIOMED_REUSABILITY_MASTER_TDD_2026-07-22.md \
  docs/superpowers/plans/2026-07-22-biomed-reusability-gate.md
claude
```

Claude Code then executes:

```text
Task 1–8
Task 9–11
evaluate NicheTrans
if failed: Task 12–14
evaluate Squidiff
if failed: Task 15–17
evaluate CMonge
Task 18
selected branch Tier 0
selected branch report
selected branch Tier 1 only if Tier 0 GO
```

---

# 21. Final deliverables

The selected project is complete only when it has:

- exact upstream commit and archive;
- container and lock files;
- checksum-verified public-data manifests;
- data contract and QC report;
- group-held-out splits;
- leakage audit;
- official reproduction report;
- at least three strong simple baselines;
- raw predictions/generated samples;
- primary metrics and biological-group confidence intervals;
- compute-resource report;
- negative controls and ablations;
- source-data files for every figure;
- deterministic one-command figure generation;
- Zenodo-ready release bundle;
- explicit limitations;
- no claims exceeding the data.

A successful software pipeline with no scientifically meaningful signal must be reported as a `NO_GO` or high-value negative result, not converted into an overstated application paper.
