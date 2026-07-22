# Environment Inventory

**Generated:** 2026-07-22 17:13 UTC+8
**Repository:** `feat/biomed-reusability-gate` (no commits yet)

## Hardware

| Component | Detail |
|-----------|--------|
| CPU | AMD64 (x86_64) |
| RAM | ~32 GB |
| GPU | NVIDIA GeForce RTX 3060, 12 GB VRAM |
| CUDA | 12.9 |
| GPU Driver | 576.88 |
| Disk (G:) | 777 GB free / ~930 GB total (83% free) |

## Operating System

| Field | Value |
|-------|-------|
| OS | Windows 11 Pro (Windows NT 10.0.22000) |
| Architecture | AMD64 |

## Software

| Tool | Version | Path |
|------|---------|------|
| Git | 2.51.0.windows.1 | — |
| Python (current) | 3.8.20 | `C:\Users\Administrator\miniconda3\envs\TREE\python.exe` |
| Python 3.11 (uv) | 3.11.15 | `<download available>` |
| uv | 0.11.8 | — |
| Docker | **NOT AVAILABLE** | — |
| Apptainer | **NOT AVAILABLE** | — |

## Python 3.11 Availability

Python 3.11.15 is available for download via `uv`. The plan requires Python 3.11.
Python 3.13.13 is already cached at `C:\Users\Administrator\AppData\Roaming\uv\python\cpython-3.13-windows-x86_64-none\python.exe`.

The project will use `uv python install 3.11` to provision Python 3.11.

## Repository State

| Field | Value |
|-------|-------|
| Branch | `feat/biomed-reusability-gate` |
| Commits | 0 (newly initialized) |
| Untracked files | 3 |
| .gitignore | Not yet created |

## Container Strategy

Neither Docker nor Apptainer is available on this machine. The plan requires containers for upstream model isolation. Fallback options:

1. **uv + pip** virtual environment with pinned dependencies per candidate (no isolation guarantee but reproducible)
2. **Podman** if installable (not checked)
3. **Manual** reproduction with exact commit pinning and environment recording

For the feasibility gate, if a container cannot be built for smoke testing, the external runner will use a subprocess call into a uv-managed venv with the upstream commit checked out. Container digest fields will record `"containerless:uv-venv:<sha256-of-lockfile>"` instead.

## GPU Strategy

RTX 3060 with 12 GB VRAM is available. This is sufficient for reduced-data smoke runs for all three candidates. Full-scale training may require memory optimization.

- NicheTrans: spatial omics with GNN components — smoke run with subset of spatial locations expected to fit.
- Squidiff: diffusion model — smoke run with reduced cells/dimensions expected to fit.
- CMonge: optimal transport — smoke run with reduced features expected to fit.

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| No Docker/Apptainer | Medium | Use uv venv + exact commit pinning; record environment hash |
| Python 3.8 default | Low | uv will provision 3.11 on demand |
| Windows (no bash) | Low | Use uv/pyproject.toml scripts; Makefile may need PowerShell alternatives |
| 12 GB VRAM | Low-Medium | Smoke tests with reduced data; full runs may need gradient checkpointing |
| No pre-commits | Low | Will add after Task 1 scaffold |
