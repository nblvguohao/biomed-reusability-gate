# Progress Log — Biomedical Reusability Candidate Gate

**Start:** 2026-07-22
**Branch:** `feat/biomed-reusability-gate`

---

## Common Feasibility Stage

### Common Tasks

- [x] **Task 1:** Scaffold the typed repository
- [x] **Task 2:** Environment and hardware inventory
- [ ] **Task 3:** Checksum-verified data and upstream manifests
- [ ] **Task 4:** Common AnnData and spatial-pair contracts
- [ ] **Task 5:** Group split and leakage audit
- [ ] **Task 6:** External container runner
- [ ] **Task 7:** Common metrics and biological-group bootstrap
- [ ] **Task 8:** Candidate gate engine

### NicheTrans Feasibility (always evaluated first)

- [ ] **Task 9:** Pin and reproduce NicheTrans official smoke example
- [ ] **Task 10:** Gastric spatial data profiler and registration audit
- [ ] **Task 11:** NicheTrans simple baselines and reduced-data GPU smoke

### Squidiff Feasibility (only if NicheTrans fails)

- [ ] **Task 12:** Pin and reproduce Squidiff official smoke example
- [ ] **Task 13:** Parse and audit CAR-NK longitudinal data
- [ ] **Task 14:** Temporal baselines and reduced Squidiff run

### CMonge Feasibility (only if both NicheTrans and Squidiff fail)

- [ ] **Task 15:** Pin and reproduce CMonge official smoke example
- [ ] **Task 16:** Perturbation data contract and independent-control split
- [ ] **Task 17:** Perturbation baselines and reduced CMonge run

### Candidate Selection

- [ ] **Task 18:** Deterministic decision engine — write `reports/selection_decision.json`

---

## Branch-Specific Tasks (only selected candidate)

### If NicheTrans selected

- [ ] **NT-1:** Immutable spatial experiment planner
- [ ] **NT-2:** Tier 0 experiment
- [ ] **NT-3:** Tier 1 (only if Tier 0 GO)

### If Squidiff selected

- [ ] **SQ-1:** Immutable temporal experiment planner
- [ ] **SQ-2:** Tier 0 experiment
- [ ] **SQ-3:** Tier 1 (only if Tier 0 GO)

### If CMonge selected

- [ ] **CM-1:** Immutable perturbation experiment planner
- [ ] **CM-2:** Tier 0 experiment
- [ ] **CM-3:** Tier 1 (only if Tier 0 GO)

---

## Per-Task Records

### Task 1: Scaffold the typed repository

| Field | Value |
|-------|-------|
| **Status** | ✅ COMPLETED |
| **Started** | 2026-07-22 17:14 |
| **RED test command** | `.venv\Scripts\python.exe -m pytest tests/unit/test_schemas.py -v` |
| **RED failure reason** | `ModuleNotFoundError: No module named 'reuse_gate.schemas'` |
| **GREEN test command** | `.venv\Scripts\python.exe -m pytest tests/unit/test_schemas.py -v` |
| **GREEN result** | 4 passed in 0.24s |
| **Generated files** | `pyproject.toml`, `Makefile`, `.gitignore`, `CLAUDE.md`, `src/reuse_gate/__init__.py`, `src/reuse_gate/cli.py`, `src/reuse_gate/schemas.py`, `tests/conftest.py`, `tests/unit/test_schemas.py`, `uv.lock` |
| **Data/upstream checksum** | N/A |
| **Git commit SHA** | `b1fd81b` |
| **Unresolved risks** | Windows LF→CRLF warnings; uv run spawns different resolver than uv pip install |

### Task 2: Environment and hardware inventory

| Field | Value |
|-------|-------|
| **Status** | ✅ COMPLETED |
| **Started** | 2026-07-22 17:13 |
| **RED test command** | `.venv\Scripts\python.exe -m pytest tests/unit/test_provenance.py -v` |
| **RED failure reason** | `ModuleNotFoundError: No module named 'reuse_gate.provenance'` |
| **GREEN test command** | `.venv\Scripts\python.exe -m pytest tests/unit/test_provenance.py -v` |
| **GREEN result** | 3 passed in 0.45s |
| **Generated files** | `src/reuse_gate/provenance.py`, `tests/unit/test_provenance.py`, `reports/environment_inventory.md` |
| **Data/upstream checksum** | N/A |
| **Git commit SHA** | `905f69d` |
| **Unresolved risks** | No Docker/Apptainer (container gate flags set to False); Windows ctypes RAM detection may fail on non-Windows |

---
