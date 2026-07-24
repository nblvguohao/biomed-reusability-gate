# Getting the two Zenodo DOIs

## Status (2026-07-24, updated) — both DOIs done

- **Part 2 (data)**: `10.5281/zenodo.21510503`, verified resolving —
  "Squidiff CAR-NK reusability report — model checkpoints, splits, and
  figure source data" (v1, CC BY 4.0). Single author by deliberate choice.
  Filled into `reusability_report.md` (Data availability) and
  `REPORTING_SUMMARY.md` §3.
- **Part 1 (code)**: `10.5281/zenodo.21525939` (v1.0.1, published
  2026-07-24), verified resolving — supersedes the earlier `v1.0.0` /
  `10.5281/zenodo.21510468`, which predated the Phase 2 robustness work and
  VO structure-metric replication. `origin/feat/biomed-reusability-gate`
  was fully pushed and in sync before this release was cut. Filled into
  `reusability_report.md` (Code availability) and `REPORTING_SUMMARY.md`.

Both walkthroughs below are kept for reference (e.g. cutting a future
`v1.0.2` / new data version).

### What's staged, ready to upload (`zenodo_upload/`, 3.4 GB, 14 files + README)

| File | Size | Content |
|---|---|---|
| `01_source_data.zip` | 98 MB | combined AnnData |
| `02_positive_control.zip` | 1.0 MB | released-checkpoint verification |
| `03_simulated_benchmark.zip` | 162 MB | upstream Gaussian benchmark reproduction |
| `04_splits.zip` | 38 MB | CAR-NK temporal splits (raw + log-normalized) |
| `05_barrier1_probe.zip` | 1.1 GB | Barrier 1 class-conditional probe models |
| `06_barrier1_published_protocol.zip` | 599 MB | Barrier 1 confirmed under published protocol |
| `07_latent_extrapolation_budget_sweep.zip` | 598 MB | budget sweep feeding Barrier 3 |
| `08_barrier3_noise_scale.zip` | 1.5 KB | noise-scale sweep (Fig. 3b) |
| `09_seed_study.zip` | 1.0 GB | five-seed performance study (Fig. 3c) |
| `10_manuscript_figures.zip` | 1.1 MB | **refreshed today** — null-anchor band + structure panel |
| `11_vo_positive_control.zip` | 3.7 KB | **new** — VO baseline comparison + structure-metric replication (Supp. Notes 8, 11) |
| `12_baseline_provenance.zip` | 1.6 KB | **new** — baseline fit sets, energy-distance decomposition (Supp. Note 7) |
| `13_evaluation_robustness.zip` | 40 MB | **new** — null anchors, bootstrap CIs, LOSO, MMD grid, structure metrics (Supp. Notes 9-10) |
| `README.md` | 3.5 KB | folder-to-manuscript-section map (also fixed a real UTF-8 encoding bug that was corrupting every em dash) |


Two separate DOIs are needed, because code and data are different kinds of
record and the manuscript cites them separately (see Data availability / Code
availability in `reusability_report.md`):

1. **Code DOI** — an automatic snapshot of the GitHub repository, taken the
   moment you publish a GitHub Release. Zenodo does this for you; you never
   upload code files by hand.
2. **Data DOI** — a manual upload of the curated ~3.4 GB artefact package at
   `zenodo_upload/` (fourteen zip files + a README), since git-ignored
   training outputs cannot live in the GitHub repository itself.

Both use the same Zenodo account.

---

## Part 1 — Code DOI (GitHub → Zenodo integration) — DONE

**Published**: `10.5281/zenodo.21525939` (v1.0.1). Kept below for
reference (e.g. cutting a future `v1.0.2`).

1. ~~Go to https://zenodo.org and log in with GitHub.~~ Done.
2. ~~Go to https://zenodo.org/account/settings/github/.~~ Done.
3. ~~Flip the **biomed-reusability-gate** toggle ON.~~ Done — confirmed
   still on, since `v1.0.0` archived successfully.
4. Go to the GitHub repository →
   **https://github.com/nblvguohao/biomed-reusability-gate/releases** →
   **"Draft a new release"**.
   - **Tag**: `v1.0.1`. The branch (`feat/biomed-reusability-gate`) is
     pushed and up to date as of commit `e3b2c2e`. Either merge into `main`
     first (recommended, so the archived snapshot is the reviewable state
     of record), or pick `feat/biomed-reusability-gate` directly as the
     release target — GitHub lets you
     tag any branch.
   - **Title**: e.g. "v1.0.1 — Phase 2 statistical robustness + VO structure replication".
   - **Description**: one or two lines is enough; Zenodo will also read the
     repository's own README.
   - Click **Publish release**.
5. Wait 1-2 minutes, then check
   **https://zenodo.org/account/settings/github/** again — the repository
   entry now shows a DOI badge. Click through to the Zenodo record.
6. The record page shows two identifiers:
   - a **version DOI** (resolves to exactly this release — `10.5281/zenodo.21510468`
     was the `v1.0.0` version DOI, `10.5281/zenodo.21525939` is `v1.0.1`'s;
     each new release gets its own, different version DOI)
   - a **concept DOI** (always resolves to whatever the latest release is —
     use this one if you expect to cut further releases later and want a
     single stable citation)
   For a Reusability Report, cite the **version DOI** in the manuscript,
   since you want the reviewed record to point at an immutable snapshot —
   if you cut a further release, send the new version DOI and it'll be
   swapped in and re-verified the same way.
7. Optional: copy the Markdown DOI badge Zenodo offers and paste it into the
   GitHub README, so anyone landing on the repo sees the citable DOI.

If you make further commits after this release and want the archived record
updated, cut a new GitHub release (`v1.0.1`, etc.) — Zenodo creates a new
version under the same concept DOI automatically.

---

## Part 2 — Data DOI (direct upload) — DONE

**Published**: `10.5281/zenodo.21510503`, verified resolving. Kept below
for reference (e.g. if a future version needs the same steps).

The files were staged at `zenodo_upload/` in the repository working tree —
14 zip files + README.md, 3.4 GB total, listed in the table above (not
committed to git; this directory is binary artefacts and belongs in
Zenodo, not GitHub). Fourteen smaller archives upload far more reliably
over a browser than one big blob — if any single one fails partway
through, you only redo that one. Note: each zip's internal paths start
with `zenodo_package/` (e.g. unzipping `01_source_data.zip` yields
`zenodo_package/01_source_data/gse190976_combined.h5ad`) — harmless, just
expect that wrapper folder when you unzip locally to check a file.

1. Go to **https://zenodo.org/uploads/21510503** (you must be logged in
   from Part 1 — same account).
2. Under **Files**, drag all fourteen `.zip` files plus `README.md` into
   the upload box, or click **Choose files**. Let them all finish
   uploading before touching anything else — a progress bar shows
   per-file status.
3. Fill in the metadata form:
   - **Digital Object Identifier**: leave blank — Zenodo mints one when you
     publish.
   - **Upload type**: `Dataset`.
   - **Title**: `Squidiff CAR-NK reusability report — model checkpoints, splits, and figure source data`.
   - **Authors**: same list as the manuscript, in the same order —
     - Guohao Lv (School of Artificial Intelligence, Anhui Agricultural University)
     - Yingchun Xia (School of Artificial Intelligence, Anhui Agricultural University)
     - Huichao Liu (School of Artificial Intelligence, Anhui Agricultural University)
     - Xiaolei Zhu (School of Artificial Intelligence, Anhui Agricultural University)
     - Shuai Yang (School of Artificial Intelligence, Anhui Agricultural University)
     - Ailian Zhou (Agricultural Information Institute, Chinese Academy of Agricultural Sciences)
     - Lichuan Gu (School of Artificial Intelligence, Anhui Agricultural University)
   - **Description**: paste the contents of `zenodo_package/README.md` (the
     folder-to-manuscript-section table). This is the single most important
     field for a reviewer opening the record cold.
   - **License**: `Creative Commons Attribution 4.0 International (CC-BY-4.0)`
     — matches the license on the released Squidiff checkpoint this work
     builds on.
   - **Keywords**: `single-cell RNA-seq`, `diffusion model`, `reusability`,
     `Squidiff`, `CAR-NK`.
   - **Related/alternate identifiers**: add `10.5281/zenodo.21525939` (the
     code DOI) as "is supplement to" / "cites" — Zenodo cross-links the two
     records both directions. Add the manuscript's own DOI here too, once
     assigned (preprint or final). Note: the data record was published
     before the code DOI was updated to `v1.0.1` — worth checking whether
     this field references the old `10.5281/zenodo.21510468` and, if so,
     whether Zenodo lets you correct it in place or requires a new version
     (not verified either way here).
   - **Funding**: if the submission system asks, enter the three grants from
     the Acknowledgements section (NSFC 32472007 / 62301006 / 62301008;
     Anhui Province NSF 2308085MF217 / 2308085QF202).
4. Click **Preview** to sanity-check the rendered record, then **Publish**.
   Note: once published, the files and the DOI are permanent — you can add a
   new *version* later if the data changes, but you cannot delete or replace
   this version's files. Double-check the file list before publishing.
5. Copy the resulting DOI (format `10.5281/zenodo.XXXXXXX`).

---

## Data DOI: done

`10.5281/zenodo.21510503` is filled into the `reusability_report.md` Data
availability statement and `REPORTING_SUMMARY.md` §3, and verified
resolving. Not added as a formal numbered reference-list citation — the
code DOI got the same treatment (inline URL in Code availability, no
reference-list entry) for consistency; say the word if you'd rather it be
a citable numbered reference instead.

If a dataset-citation entry is wanted later, the convention is:
`[Creators] ([Year]) [Title]. Zenodo. [DOI]`.

## Resolved

- **Code snapshot currency**: `v1.0.1` (`10.5281/zenodo.21525939`)
  published 2026-07-24, after all 14 pending commits were pushed. Current.
- **Data deposit author list**: the single author on
  `10.5281/zenodo.21510503` is a deliberate choice, not an oversight — the
  full 7-author list is on the manuscript itself, which is what governs
  authorship credit; the Zenodo record's author field doesn't need to
  duplicate it.

Nothing outstanding on either DOI. Both are closed items — see `STATUS.md`
for what (non-Zenodo) work remains before submission.
