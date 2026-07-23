# Upstream documentation status of the log-normalization step

Date: 2026-07-24
Question: is the library-size normalization + log transform required by
Squidiff documented in the linked article's Methods, the main repository, or
only in the reproducibility notebooks?

## Sources checked

1. **Published article (author manuscript, PMC12872408)** — main text;
   Methods are in a supplementary .docx that is gated behind a JavaScript
   proof-of-work and could not be bulk-downloaded.
2. **bioRxiv v2, 10.1101/2024.11.16.623974v2 (posted 2025-08-26)** — the
   version the PMC record identifies as the basis of the published article
   (Nat Methods 2025;23(1):65–77). Full text retrieved and searched.
3. **bioRxiv v1 (posted 2024-11-16)** — full text retrieved and searched.
4. **Vendored main repository** (`vendor/Squidiff/`, pinned commit `abdfc27`,
   v1.0.8) — README + `train_squidiff.py` + `sample_squidiff.py`.

## Verbatim evidence

### Published-version Methods (bioRxiv v2 == published basis), section "Data preprocessing and quality control"

> "Following quality control, the gene count data were **normalized and
> log-transformed to correct for sequencing depth variability**. Analyses then
> focused on highly variable genes and specific genes of interest, using
> Scanpy V1.10.1 for processing."

This paragraph is general (it precedes the per-task "Squidiff training
tasks" subsections), so it applies to every task in the paper. **No
executable recipe is given**: no library-size target (10,000), no statement
of `log1p`, no order of operations beyond the words "normalized and
log-transformed".

### v1 preprint Methods, section "Processing of single-cell RNA sequencing data for model training"

> "In the section on the prediction of iPSC differentiation, we first
> **log normalized the gene counts** and selected the top 500 variable genes
> for the task considering the computing capabilities."

Task-specific (iPSC only); the published version broadened this to the
generic QC sentence above. (Side note: v2 changed the iPSC task to "top 203
most variable genes", days 0/3 train vs days 1/2 test — a v1↔v2 discrepancy
worth a footnote in the supplement, not a manuscript claim.)

### Main repository (vendored, pinned)

- `README.md`: no mention of normalization, log transform, or required input
  scaling. Model input is described only as "h5ad file with … single-cell
  count matrix".
- `train_squidiff.py` / `Squidiff/scrna_datasets.py`: the training data path
  applies **no** library-size normalization or log transform (verified in
  this project's Barrier 1 experiments).
- The released training data matrix is log-normalized (mean 1.78, max 14.47),
  independently confirming the transform is required (Supp. Note 6).

verdict: The transform IS documented in the published article's Methods —
but only as a one-line generic phrase ("normalized and log-transformed to
correct for sequencing depth variability", Scanpy) with no executable
recipe, no library-size target, and no log1p specification. It is NOT
applied by the released training script and NOT stated anywhere in the main
repository (README/code). The reuser who follows the **code** (install from
PyPI, run `train_squidiff.py` on an h5ad of raw counts, as the README
instructs) receives no signal that the transform is required and obtains a
silently inverted result.

## Consequence for manuscript wording (binding for Phase 1/3 edits)

- "**undocumented**" (title, abstract, Barrier 1 heading) is **not
  defensible** and must be replaced. Accurate framing: *a preprocessing
  requirement stated only as a one-line generic phrase in the article
  Methods, absent from the released code path and repository, with no
  executable recipe.*
- "it appears only in the authors' separate reproducibility notebooks"
  (main text, "The released artefacts reproduce") is **wrong** and must be
  corrected: it also appears, at a generic level, in the article Methods.
- The reusability finding survives and is arguably sharper: documentation
  and code **disagree**, and the code fails silently. The barrier is the
  code–documentation gap plus silent failure, not total absence of
  documentation.
- The abstract sentence "an undocumented preprocessing step that silently
  inverts conclusions" must be rewritten accordingly.
