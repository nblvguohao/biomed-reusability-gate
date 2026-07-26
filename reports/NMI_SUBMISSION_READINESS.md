# Nature Machine Intelligence submission readiness

Assessment date: 27 July 2026

Target: *Nature Machine Intelligence*

Article type: Article — Reusability Report

## Outcome

The scientific and technical revision is ready for submission packaging. The
manuscript now addresses the principal review risks: target leakage, reliance
on one temporal split, weak baselines, incomplete dependence metrics,
cell-versus-sample ambiguity, overinterpretation of the released VO setting and
missing disclosure of generative-AI assistance.

Submission should proceed only after the corresponding authors complete the
administrative confirmations listed below and create a versioned public release
for the final source-data and code artefacts.

## Article-format audit

| Requirement | Current state | Result |
|---|---|---|
| Reusability Report format | Submitted as an Article linked to the Squidiff paper | Ready |
| Abstract | 144 words; no citations | Within the 150-word limit |
| Main text | 3,259 words from introduction through Discussion | Within the 3,500-word limit |
| Display items | 3 main figures | Within the limit of 6 |
| References | 11 | Within the approximate 50-reference guidance |
| Introduction | Begins without an “Introduction” heading | Ready |
| Required structure | Results, Discussion and Methods present | Ready |
| Results/Methods subheadings | Topical and descriptive | Ready |
| Discussion subheadings | None | Ready |
| Data and code availability | Separate statements with persistent identifiers and a future-version statement | Ready after new release |
| AI disclosure | Included in Methods and Reporting Summary answers | Ready |

The audit follows the journal’s current
[content-type description](https://www.nature.com/natmachintell/content),
[initial-formatting guidance](https://www.nature.com/natmachintell/submission-guidelines/initial-formatting),
[submission-preparation guidance](https://www.nature.com/natmachintell/submission-guidelines/preparing-your-submission)
and [reporting standards](https://www.nature.com/natmachintell/editorial-policies/reporting-standards).

## Evidence and statistics audit

- Early, primary and late cutoffs have 5/5 completed model seeds.
- Sample identifiers are disjoint across every train–test boundary.
- Preprocessing, feature ranking, scale selection and baseline fitting remain
  inside the corresponding training window.
- The early cutoff reports both predeclared scales without target-based
  selection.
- Four baselines separately test recency, pooled marginal moments, temporal
  marginal trend and training-fitted low-rank dependence.
- Individual computational seeds and mean ± s.d. are reported; seeds and cells
  are not treated as biological replicates.
- Same-distribution references use 50 random disjoint target splits.
- The late D28 analysis is explicitly descriptive because it has one
  biological test sample.
- No seed-based or cell-based null-hypothesis test is reported.

## Figure and source-data audit

Figures 1–3 are exported as editable PDF and SVG plus 600-dpi PNG and TIFF.
The source uses publication-safe sans-serif fonts, 8-point bold lowercase panel
labels, a colour-vision-accessible palette and no decorative grid. Strict
machine validation reports 14 passes, 0 warnings and 0 failures. Visual review
was also performed at final export size, and label collisions identified in
the first pass were corrected.

Machine-readable source data include every cutoff, seed, Squidiff scale,
baseline and cluster-sensitivity setting. Scalar CSV files accompany the full
JSON manifest.

## Author confirmations required before upload

1. Confirm author spelling, order, affiliations, email addresses and the two
   corresponding authors.
2. Confirm that all authors approve the final files, that the work is original
   and that it is not under consideration elsewhere.
3. Add ORCID identifiers in the submission system where available.
4. Confirm the Author contributions, funding numbers and competing-interests
   declaration.
5. Disclose any related manuscript, prior editorial discussion or preprint
   status in the cover letter and submission system.
6. Create a new versioned public release containing the final consolidated
   manifest, source-data tables, split manifests, figures and exact code
   revision; then replace the future-release wording with the public DOI or
   version before publication.
7. Transfer `04_Reporting_Summary_answers.docx` into the journal’s current
   Reporting Summary form if the submission portal requests it.

## Editorial risk

The principal editorial risk is breadth: predictive evaluation uses one
independent CAR-NK dataset, and the result is predominantly negative. The
manuscript addresses this by avoiding a universal performance claim and by
framing the contribution as an executable, leakage-safe reusability audit.
This framing is directly relevant to the journal’s Reusability Report remit,
but final editorial fit cannot be guaranteed.
