# Biomed Reusability Gate — CLAUDE.md

## Project summary

Auditable, test-driven feasibility gate that evaluates NicheTrans, Squidiff, and CMonge for biomedical reusability, deterministically selects one candidate, and executes Tier 0/Tier 1 workflows.

## Architecture

```
src/reuse_gate/          # Python 3.11 orchestration package
  schemas.py             # Pydantic v2 models
  cli.py                 # Typer CLI
  hashing.py             # SHA256 file hashing
  provenance.py          # Environment inventory
  candidates.py          # Candidate registry
  decision.py            # Deterministic selection engine
  data/                  # Data contracts, download, parsing
  splits/                # Group-held-out split logic
  models/                # Model runner protocol, baselines
  metrics/               # Regression, distribution, spatial metrics
  gates/                 # Candidate hard gate evaluation
  orchestration/         # Run IDs, state, planning
  reporting/             # Feasibility reports, tables, figures
external_runners/        # Per-candidate container/subprocess runners
containers/              # Dockerfiles per candidate
vendor/                  # Pinned upstream manifests and patches
tests/                   # unit / integration / regression
configs/                 # YAML configs for candidates, datasets, gates
workflows/               # Snakemake workflow
```

## Strict rules

1. **TDD mandatory**: Write failing test → confirm RED → minimal implementation → confirm GREEN → all tests + ruff + mypy → commit.
2. **No backfill tests**: No production code without a test that failed first.
3. **Unit test constraints**: No network, no GPU, no full public datasets.
4. **Integration tests**: Marked `@pytest.mark.integration`.
5. **GPU tests**: Marked `@pytest.mark.gpu`.
6. **Slow tests**: Marked `@pytest.mark.slow`.
7. **Group-level splits**: Never use cell/spot-level random splits when group identifiers exist.
8. **Test data isolation**: Test data must not be used for early stopping, HP tuning, feature selection, or normalization fitting.
9. **Candidate priority is fixed**: NicheTrans → Squidiff → CMonge → NO_GO.
10. **selection_decision.json is immutable once written**.
11. **Upstream code untouched**: Patches only in `vendor/patches/<candidate>/`.
12. **Run all tests before every commit**.

## Common commands

```bash
# Option A: Python 3.10 venv with CUDA torch (recommended for GPU)
python -m venv --system-site-packages .venv310
.venv310\Scripts\activate
pip install -e ".[metrics,dev]"

# Option B: Python 3.11 with uv (CPU-only by default)
uv venv --python 3.11
uv sync --extra torch --extra metrics --extra dev

make setup             # Create venv and install
make lint              # Ruff check
make typecheck         # Mypy
make test              # Unit tests
make smoke             # Fast tests only (no integration/gpu/slow)
make inventory         # Record environment
make decide            # Candidate selection
```

## Setup for CUDA GPU

Use Python 3.10 with `--system-site-packages` to inherit system CUDA torch:
```bash
python -m venv --system-site-packages .venv310
.venv310\Scripts\activate
pip install -e ".[metrics,dev]"
```

## Commit style

- `chore:` — scaffolding, config, non-functional changes
- `feat:` — new production capability
- `fix:` — bug fixes
- `test:` — test additions/changes
- `build:` — containers, upstream pins
- `docs:` — documentation only
