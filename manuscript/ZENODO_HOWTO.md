# Getting the two Zenodo DOIs

Two separate DOIs are needed, because code and data are different kinds of
record and the manuscript cites them separately (see Data availability / Code
availability in `reusability_report.md`):

1. **Code DOI** — an automatic snapshot of the GitHub repository, taken the
   moment you publish a GitHub Release. Zenodo does this for you; you never
   upload code files by hand.
2. **Data DOI** — a manual upload of the curated ~4.3 GB artefact package at
   `zenodo_upload/` (ten zip files + a README), since git-ignored training
   outputs cannot live in the GitHub repository itself.

Both use the same Zenodo account. Do Part 1 first — it is faster and has no
file upload involved.

---

## Part 1 — Code DOI (GitHub → Zenodo integration)

1. Go to **https://zenodo.org** and click **Log in** → **Log in with GitHub**.
   Authorize Zenodo when GitHub asks. This creates a Zenodo account tied to
   your GitHub identity (`nblvguohao`) — no separate password to manage.
2. Go to **https://zenodo.org/account/settings/github/**. You will see a list
   of your GitHub repositories with toggle switches, all off by default.
3. Find **biomed-reusability-gate** in the list and **flip its toggle ON**.
   This step must happen *before* you publish the release below — Zenodo
   archives a release at the moment GitHub tells it one was published; it
   cannot retroactively archive a release made while the toggle was off.
4. Go to the GitHub repository →
   **https://github.com/nblvguohao/biomed-reusability-gate/releases** →
   **"Draft a new release"**.
   - **Tag**: something like `v1.0.0`. Since the work lives on
     `feat/biomed-reusability-gate` and has not been merged to a default
     branch, either merge that branch into `main` first (recommended, so the
     archived snapshot is the reviewable state of record), or explicitly pick
     `feat/biomed-reusability-gate` as the release target — GitHub lets you
     tag any branch.
   - **Title**: e.g. "v1.0.0 — Squidiff reusability report submission".
   - **Description**: one or two lines is enough; Zenodo will also read the
     repository's own README.
   - Click **Publish release**.
5. Wait 1-2 minutes, then check
   **https://zenodo.org/account/settings/github/** again — the repository
   entry now shows a DOI badge. Click through to the Zenodo record.
6. The record page shows two identifiers:
   - a **version DOI** (resolves to exactly this release, e.g. `v1.0.0`)
   - a **concept DOI** (always resolves to whatever the latest release is —
     use this one if you expect to cut further releases later and want a
     single stable citation)
   For a Reusability Report, cite the **version DOI** in the manuscript, since
   you want the reviewed record to point at an immutable snapshot.
7. Optional: copy the Markdown DOI badge Zenodo offers and paste it into the
   GitHub README, so anyone landing on the repo sees the citable DOI.

If you make further commits after this release and want the archived record
updated, cut a new GitHub release (`v1.0.1`, etc.) — Zenodo creates a new
version under the same concept DOI automatically.

---

## Part 2 — Data DOI (direct upload)

The files are staged at `zenodo_upload/` in the repository working tree (not
committed to git — this directory is 4.3 GB of binary artefacts and belongs
in Zenodo, not GitHub):

```
zenodo_upload/
  README.md
  01_source_data.zip                       (468 MB)
  02_positive_control.zip                  (1.2 MB)
  03_simulated_benchmark.zip               (176 MB)
  04_splits.zip                            (159 MB)
  05_barrier1_probe.zip                    (1.1 GB)
  06_barrier1_published_protocol.zip       (648 MB)
  07_latent_extrapolation_budget_sweep.zip (648 MB)
  08_barrier3_noise_scale.zip              (<1 MB)
  09_seed_study.zip                        (1.1 GB)
  10_manuscript_figures.zip                (1.5 MB)
```

Ten smaller archives upload far more reliably over a browser than one 4.3 GB
blob — if any single one fails partway through, you only redo that one. Note:
each zip's internal paths start with `zenodo_package/` (e.g. unzipping
`01_source_data.zip` yields `zenodo_package/01_source_data/gse190976_combined.h5ad`)
— harmless, just expect that wrapper folder when you unzip locally to check
a file.

1. Go to **https://zenodo.org/deposit/new** (you must be logged in from
   Part 1).
2. Under **Files**, drag all ten `.zip` files plus `README.md` into the
   upload box, or click **Choose files**. Let them all finish uploading
   before touching anything else — a progress bar shows per-file status.
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
   - **Related/alternate identifiers**: once you have the code DOI from
     Part 1, add it here as "is supplement to" / "cites" the code record —
     Zenodo cross-links the two records both directions. Add the manuscript's
     own DOI here too, once assigned (preprint or final).
   - **Funding**: if the submission system asks, enter the three grants from
     the Acknowledgements section (NSFC 32472007 / 62301006 / 62301008;
     Anhui Province NSF 2308085MF217 / 2308085QF202).
4. Click **Preview** to sanity-check the rendered record, then **Publish**.
   Note: once published, the files and the DOI are permanent — you can add a
   new *version* later if the data changes, but you cannot delete or replace
   this version's files. Double-check the file list before publishing.
5. Copy the resulting DOI (format `10.5281/zenodo.XXXXXXX`).

---

## After both DOIs exist

Send me both DOIs (code and data) and I will:
- replace the two `[DOI to be minted on acceptance]` placeholders in
  `reusability_report.md` (Data availability / Code availability) with the
  real, resolvable DOIs
- add the data DOI as a formal dataset citation in the reference list if you
  want it citable from the main text, per the dataset-citation convention
  (`[Creators] ([Year]) [Title]. Zenodo. [DOI]`)
- cross-check that both DOI pages actually resolve before we call the
  manuscript submission-ready

## Unresolved / to confirm

- Whether to merge `feat/biomed-reusability-gate` into `main` before tagging
  the release, or tag the feature branch directly. Either works technically;
  merging first is the more conventional signal that this is the reviewed
  state of the repository.
- Exact author order and affiliation indices in the Zenodo metadata should
  mirror whatever the manuscript ultimately uses — confirm before publishing,
  since author metadata cannot be silently corrected after a version is
  minted (a correction requires a new version).
