# Nature Portfolio Reporting Summary

Answers below are drafted to be transcribed into the official fillable
Reporting Summary PDF from the journal's submission system (the form itself
is a template Nature Portfolio provides; this file is not a substitute for
it, just pre-written answers). Section numbering follows the standard
template: Statistics, Software and code, Data, Field-specific reporting,
Life sciences study design, Reporting for specific materials/systems/methods.

This is a computational reanalysis of previously published, publicly
deposited data. No new wet-lab, animal, or human-subjects work was performed
by the authors of this report; the underlying biological experiment (mouse
CAR-NK infusion, GSE190976) was performed by Li et al. (ref. 5), and its own
ethical approvals apply there, not here. Several template sections are
therefore correctly answered "not applicable" — that is a true description
of a reusability report, not a gap.

---

## 1. Statistics

For every reported panel and table, confirm or mark n/a:

| Item | Status |
|---|---|
| The exact sample size (n) for each experimental group/condition, given as a discrete number and unit of measurement | **Confirmed.** n = 16,256 cells total (GSE190976); train split 11,588 cells / 13 samples, held-out split 4,668 cells / 5 samples; n = 5 independently trained models (seeds 13, 37, 73, 101, 137) for every reported mean ± s.d. |
| A statement on whether measurements were taken from distinct samples or whether the same sample was measured repeatedly | **Confirmed, distinct.** Each seed is an independently initialized and independently trained model; held-out cells are never reused across the metric computed for different seeds. |
| The statistical test(s) used AND whether they are one- or two-sided | **Not applicable — no hypothesis test is reported.** All five seeds fall on the same side of both baselines on the marginal metrics (energy distance, per-gene mean correlation) and on the structure metrics (gene–gene correlation distance, rare-cluster recall); this is reported descriptively (mean ± s.d. across seeds; percentile bootstrap intervals; leave-one-sample-out folds) rather than via a significance test, per the statistics block in `manuscript/FIGURE_LEGENDS.md` and Supplementary Note 9. |
| A description of all covariates tested | n/a — no covariate-adjusted model is used. |
| A description of any assumptions or corrections, such as tests of normality and adjustment for multiple comparisons | n/a — no test performed, so no correction applies. |
| A full description of the statistical parameters including central tendency and variation | **Confirmed.** Mean and standard deviation across 5 training seeds for every metric (Fig. 3c; full values in `artifacts/squidiff_seed_study/seed_study_metrics.json`), supplemented by: a same-distribution null band (metric between random halves of the held-out population, 50 splits); 200-resample percentile bootstrap 95% intervals at cell level and at held-out-sample level; leave-one-held-out-sample-out re-scoring (5 folds per seed); and 10-draw baseline-resampling dispersion at fixed data. Full values and methodology in Supplementary Note 9 and `artifacts/evaluation_robustness/robustness.json`. |
| For null hypothesis testing, the test statistic and P value noted | n/a — no null hypothesis test performed (see above); uncertainty is reported via bootstrap intervals and a same-distribution reference band instead. |

## 2. Software and code

**Data collection.** No new data were collected for this report. The
single-cell dataset (GSE190976) was generated and deposited by Li et al.
(ref. 5); we downloaded it from GEO as-is.

**Data analysis.**
- Python 3.10.11 (production/GPU analysis, `--system-site-packages` venv
  inheriting system CUDA PyTorch) and Python 3.11 (lint/type-check parity
  environment).
- PyTorch 2.11.0+cu128, CUDA 12.8, on an NVIDIA GeForce RTX 5070 Ti (17.1 GB
  VRAM).
- scanpy 1.11.5, anndata 0.11.4, numpy 2.2.6, scipy 1.15.3, scikit-learn
  1.7.2, pandas 2.3.3.
- Squidiff, pinned at upstream commit `abdfc27d84947dcccd745d1067c0840a41d32eb8`
  (v1.0.8), with three compatibility patches applied
  (`vendor/patches/squidiff/`, each with a regression test).
- All custom analysis code is available at
  https://github.com/nblvguohao/biomed-reusability-gate (archived via
  Zenodo, DOI: 10.5281/zenodo.21510468). **Before submission, confirm this
  archived snapshot is current** — it was published 2026-07-23 and several
  commits (the Phase 2 statistical-robustness work and the VO structure-
  metric replication) landed after that date; if the Zenodo deposit predates
  them, cut a new version/release so the archived code matches what the
  manuscript describes.

## 3. Data

Confirm the data availability policy has been followed: **Yes.** Reused
public data (GSE190976) is cited to its accession; newly generated derived
data (splits, model checkpoints, generated populations, metrics, figure
source data) are deposited via Zenodo, DOI: 10.5281/zenodo.21510503
(verified resolving — published record, CC BY 4.0), separate from the code
archive above, per the Data availability statement in
`reusability_report.md`.

## 4. Field-specific reporting

Select one: ☒ **Life sciences** ☐ Behavioural & social sciences
☐ Ecological, evolutionary & environmental sciences

## 5. Life sciences study design

All studies must disclose on these points even when the disclosure is
negative.

| Item | Answer |
|---|---|
| **Sample size** | The CAR-NK dataset size (16,256 cells, 18 samples) was fixed by the original depositors (ref. 5); this report performs no new sample collection and therefore no sample-size power calculation. The number of independently trained model seeds (5) was chosen as a practical minimum for reporting a mean and spread across training runs, following standard practice for reproducibility/variance reporting in generative-model studies; no formal power calculation determined this number. |
| **Data exclusions** | None. All cells passing the original depositors' quality control were used; no cells or samples were excluded by us. |
| **Replication** | The central replication claim of this report *is* the five-seed study: five independently initialized and trained models were evaluated under identical protocol, data, and split, and all five agreed in direction (worse than the conditional-mean baseline on all three metrics, in all five seeds). All five attempts succeeded; none were excluded. |
| **Randomization** | Not applicable in the sense of group allocation — there are no experimental groups to randomize. The train/held-out split is a **deliberately non-random**, sample-disjoint temporal split (train: pre-infusion/D7/D14; held out: D21/D28), chosen specifically to test extrapolation to unseen later timepoints rather than interpolation, and to guarantee zero sample overlap between train and test. |
| **Blinding** | Not applicable. This is a fully computational reanalysis; there is no investigator-facing measurement step where blinding to group identity could affect the result — the split itself is defined deterministically by timepoint metadata already present in the public data. |

## 6. Reporting for specific materials, systems and methods

Mark "Involved in the study" only where true for *this* report (the
computational reanalysis), not for the original biological experiment that
generated GSE190976.

| Materials & experimental systems | Involved? |
|---|---|
| Antibodies | Not involved |
| Eukaryotic cell lines | Not involved |
| Palaeontology and archaeology | Not involved |
| **Animals and other organisms** | **Not involved in this study.** GSE190976's underlying mouse experiments were performed by the original authors (ref. 5); this report reuses only the deposited, de-identified single-cell expression matrices and does not involve any new animal procedure. Refer to ref. 5 for that study's own ethical approval (IACUC or equivalent). |
| Clinical data | Not involved |
| Dual use research of concern | Not involved |
| Plants | Not involved |

| Methods | Involved? |
|---|---|
| ChIP-seq | Not involved |
| Flow cytometry | Not involved |
| MRI-based neuroimaging | Not involved |

---

## Notes for the author team

- Content is complete and internally consistent with `RESULTS.md` and
  `FIGURE_LEGENDS.md`. Author contributions (main text) are confirmed.
- Both DOIs are now minted, verified resolving: data (§3)
  10.5281/zenodo.21510503, code (§2) 10.5281/zenodo.21510468. One item
  remains before submission: the code deposit was published 2026-07-23 and
  analysis work continued after that — confirm a current snapshot has been
  archived (cut a `v1.0.1` GitHub release if not; see `ZENODO_HOWTO.md`)
  before treating this as final.
- Confirm the funding-grant numbers are transcribed correctly into the
  submission system's own funder-lookup field (some systems require
  choosing a matched funder name from a dropdown rather than free text).
- If NMI's specific Reporting Summary version differs in section wording
  from the general Nature Portfolio template used here, map the answers
  across by content, not by section number.
- The original authors (He et al.) have not been contacted about this
  reusability report. If NMI's editorial process expects notification or a
  right-of-reply window, address that in the cover letter, not in this
  form.
