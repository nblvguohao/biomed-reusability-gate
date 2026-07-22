# NicheTrans Feasibility Report

**Date:** 2026-07-22
**Evaluator:** Automated CI (Claude Code)

## Gate Results

| Gate | Description | Status |
|------|-------------|--------|
| NT-G1 | Official repo and archived version can be pinned and built | ❌ FAILED |
| NT-G2 | One official example completes end-to-end | ❌ FAILED |
| NT-G3 | >= 2 independent gastric biological units | ⚠️ NOT EVALUATED |
| NT-G4 | Each unit >= 500 matched locations after QC | ⚠️ NOT EVALUATED |
| NT-G5 | >= 30 target features pass filters in every unit | ⚠️ NOT EVALUATED |
| NT-G6 | Registration/matching >= 90% of source locations | ⚠️ NOT EVALUATED |
| NT-G7 | Patient/slice-held-out split without overlap | ⚠️ NOT EVALUATED |
| NT-G8 | >= 3 simple baselines on same split | ⚠️ NOT EVALUATED |
| NT-G9 | One-epoch/reduced NicheTrans smoke in GPU memory | ⚠️ NOT EVALUATED |
| NT-G10 | Full data accessible without manual dependency | ⚠️ NOT EVALUATED |

**Overall:** NicheTrans hard gate FAILED. Candidate cannot proceed.

## NT-G1 / NT-G2 Failure Detail

### NT-G1: Repository not found

NicheTrans (paper: "NicheTrans: Spatial-aware Cross-omics Translation", bioRxiv 2024.12.05.626986, authors Zhikang Wang, Senlin Lin, Qi Zou, Yan Cui, Zhiyuan Yuan, Jiangning Song) does not have a publicly accessible source code repository.

Search conducted across:
- GitHub.com (multiple search queries)
- bioRxiv (DOI: 10.1101/2024.12.05.626986)
- Zenodo (DOI: 10.5281/zenodo.15706278 — data only, no code)
- Google Scholar, Semantic Scholar
- Author profiles and institutional pages

The Zenodo record confirms: "This repository is for the under review paper." No GitHub link, no code availability statement found.

### NT-G2: No example to run

Without the repository, no official example can be executed.

### Blocking Status

This is a **hard blocking failure**. The plan states: "If the official example cannot run, preserve the failure and mark NT-G1 or NT-G2 failed. Do not rewrite the model."

The next candidate in priority order (Squidiff) will be evaluated.

## Environment Context

- No Docker or Apptainer available (container would require alternative approach)
- GPU available: NVIDIA RTX 3060 12GB
- Python 3.11 available via uv

## Recommendation

Move to Squidiff evaluation (Task 12).
