# Reviewer-Revision TDD — Squidiff Reusability Report

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Every production change follows RED → GREEN → REFACTOR. Steps use checkbox syntax for tracking.
>
> This plan governs **revision of the manuscript** (`manuscript/reusability_report.md`) in response to the pre-submission mock review dated 2026-07-23. It does NOT introduce new candidate models, new datasets, or changes to `src/reuse_gate/` scoring logic unless a task explicitly says so.

**Goal:** Close the two blocking evidentiary gaps (baseline provenance + positive control), verify every load-bearing word in the title/abstract against primary sources, resolve the Fig. 3a self-contradiction, and re-center the narrative on the transferable contribution — without invalidating any number that survives.

**Verdict from review:** Salvageable. The three-barrier skeleton is publishable. Two blocking items require **no new dataset** (one is pure clarification; one reuses the released checkpoint already in hand). Do **not** scale the work down silently — complete every task or flag explicitly.

**Tech Stack:** Python 3.10 (GPU venv, `--system-site-packages`), PyTorch 2.11.0+cu128, scanpy/anndata, pytest, Ruff, mypy, JSON artifacts under `artifacts/` (gitignored → Zenodo before submission).

## Global Constraints (carried from CLAUDE.md + master TDD)

- TDD mandatory: failing test → confirm RED → minimal implementation → confirm GREEN → lint + typecheck → commit.
- No backfill tests: no production/analysis code without a test that failed first for the expected reason.
- Unit tests: no network, no GPU, no full public datasets. Integration/GPU/slow marked accordingly.
- Group-level (sample-level) splits only; never random cell-level splits.
- Test data never used for early stopping, HP tuning, feature selection, or normalization fitting.
- Every artifact carries SHA256, source URI, creation command, software commit, environment id.
- Upstream code untouched; patches only under `vendor/patches/squidiff/`.
- All failures retained; never delete failed-run logs.
- Any new claim in the manuscript must trace to a named script + artifact file (same convention as `manuscript/RESULTS.md`).

## Manuscript files this plan touches

- `manuscript/reusability_report.md` (title, abstract, Barrier 1/2/3, Performance, Discussion, Outlook, Fig. 3a/3c legends)
- `manuscript/RESULTS.md` (new measured rows)
- `manuscript/SUPPLEMENTARY_INFORMATION.md` (new notes/tables)
- `manuscript/FIGURE_LEGENDS.md`
- `external_runners/squidiff/*.py` (new analysis scripts)
- `tests/` (new unit/integration tests)

---

# Phase 0 — Ground-truth verification (BLOCKING, zero compute)

These tasks verify words that are already in the title/abstract but were never checked against primary sources. Each produces a written finding stored in the repo. **Do these first — their outcomes change the wording of everything downstream.**

### Task 0.1 — Verify whether the original paper's Methods describes log-normalization
- [ ] **Step 1 (RED):** Write `tests/unit/test_manuscript_claims.py::test_normalization_documented_status_resolved` asserting that a checked-in evidence file `reports/upstream_methods_preprocessing.md` exists and contains a non-empty verdict field. Confirm it fails (file absent).
- [ ] **Step 2 (GREEN):** Retrieve the linked article (He et al., Nat. Methods 2025) Methods + any upstream README/reproducibility notebooks. Record verbatim whether library-size normalization to 10,000 + log1p is described, and **where** (Methods / notebook only / README / nowhere). Write `reports/upstream_methods_preprocessing.md` with quotes + locations. Test passes.
- [ ] **Step 3:** Branch the manuscript wording on the verdict:
  - If Methods **does** describe it → replace "undocumented" everywhere with precise wording: "not applied by the released training script and not stated in the main repository (it appears only in the authors' separate reproducibility notebooks / Methods)". Title must drop "undocumented".
  - If Methods does **not** describe it → "undocumented in the code path" may stand, but state explicitly that Methods was checked and does not describe it.
- [ ] **Step 4 (commit):** `docs: resolve normalization documentation status against upstream Methods`

### Task 0.2 — Confirm whether 0.7 is a literal in the function body or an overridable default
- [ ] **Step 1 (RED):** Add `tests/unit/test_manuscript_claims.py::test_noise_constant_is_source_literal` that greps the pinned vendored source for `sample_around_point` and asserts the recorded finding in `reports/noise_constant_provenance.md` matches the actual code form. Confirm RED.
- [ ] **Step 2 (GREEN):** Inspect `vendor/Squidiff/Squidiff/` for `sample_around_point`. Record whether `0.7` is a hardcoded literal in the body, or a default parameter that a caller can override. Write `reports/noise_constant_provenance.md` with the exact line + signature.
- [ ] **Step 3:** If it is an overridable default → soften "hardcoded" to "a default that accepts override" and adjust title/Barrier 3 wording accordingly. If it is a literal → "hardcoded" stands.
- [ ] **Step 4 (commit):** `docs: record noise-constant provenance and align wording`

### Task 0.3 — Map original-paper claims to code paths (recalibrates Barrier 2 impact)
- [ ] **Step 1 (RED):** Add `tests/unit/test_manuscript_claims.py::test_claim_to_codepath_map_complete` asserting `reports/claim_to_codepath_map.md` exists and covers, at minimum: development prediction, perturbation response, and the released config. Confirm RED.
- [ ] **Step 2 (GREEN):** Build the table: each original-paper claim → the code path that produces it (`class_cond=True/False`, encoder, latent extrapolation) → this report's verification status. Write `reports/claim_to_codepath_map.md`.
- [ ] **Step 3:** Decide Barrier 2 framing from the table:
  - If the original perturbation-response results also use `class_cond=False` → Barrier 2 blocks a path the original authors never used; downgrade "its headline perturbation-response use" to "an exposed but non-functional API option" and restate impact honestly.
  - If original results do depend on `class_cond=True` → strengthen Barrier 2 prominently.
- [ ] **Step 4 (commit):** `docs: add claim-to-codepath map and recalibrate Barrier 2`

---

# Phase 1 — Blocking evidence gaps (no new dataset required)

### Task 1.1 — Baseline fit provenance (BLOCKING, pure clarification)
- [ ] **Step 1 (RED):** Add `tests/unit/test_results_provenance.py::test_baselines_state_fit_set` asserting `manuscript/RESULTS.md` and the Methods/legend text each name, for **both** baselines, (a) the exact set of cells the per-gene mean/variance was fit on and (b) the timepoint. Confirm RED (currently absent).
- [ ] **Step 2 (GREEN):** Read the baseline construction in `external_runners/squidiff/seed_study.py` (and any baseline module under `src/reuse_gate/models/`). State verbatim the fit set for conditional-mean and last-observation. Insert into manuscript Methods + Fig. 3c legend + `RESULTS.md`.
- [ ] **Step 3 — Mechanism explanation:** Determine empirically why conditional-mean ED (4.26) < last-observation ED (19.10). Add a short analysis (see Task 1.4 null-anchor script can host this) comparing within-D14 joint structure vs held-out joint structure, and write a one-paragraph explanation. If the explanation cannot be established from evidence, state the claim more cautiously in text.
- [ ] **Step 4 (commit):** `docs: state baseline fit provenance and explain baseline ordering`

### Task 1.2 — Positive control: run the same baselines on the authors' successful setting (BLOCKING, uses released checkpoint in hand)
- [ ] **Step 1 (RED):** Add `tests/integration/test_positive_control.py` (marked `integration`, `gpu` if it samples) asserting `artifacts/positive_control/positive_control_metrics.json` exists with energy distance + MMD + per-gene mean correlation for both Squidiff and the conditional-mean baseline **on the released checkpoint's own data/task**. Confirm RED.
- [ ] **Step 2 (GREEN):** Write `external_runners/squidiff/positive_control.py`: load released checkpoint (figshare 10.6084/m9.figshare.27948633), reproduce its documented successful prediction setting, and score Squidiff vs the identical conditional-mean baseline fit **on training-window cells only**. Emit the metrics JSON with full provenance (SHA256, command, commit, env).
- [ ] **Step 3:** Interpret:
  - Baseline also wins there → the CAR-NK negative result is a property of the evaluation regime; rewrite the performance claim as "on this class of low-drift task, no generative model beats a moment-matched sampler" (still valuable, different claim).
  - Baseline loses there → "Squidiff fails to transfer" is established; foreground it.
- [ ] **Step 4:** Update abstract + Performance + Discussion to whichever branch the evidence supports. Record the numbers in `RESULTS.md`.
- [ ] **Step 5 (commit):** `feat: add positive-control baseline comparison on released setting`

### Task 1.3 — Resolve the Fig. 3a self-contradiction (swap main panel to the published-protocol A/B)
- [ ] **Step 1 (RED):** Add `tests/unit/test_figure_source.py::test_fig3a_uses_published_protocol` asserting Fig. 3a's source data is `artifacts/squidiff_latent_extrap_ab/preprocessing_ab_metrics.json` (the published-protocol A/B), not the class-conditional probe. Confirm RED.
- [ ] **Step 2 (GREEN):** Update `make_manuscript_figures.py` so Fig. 3a main panel plots the published-protocol A/B (raw 376.8→561.7 vs log-normalized 312.4→27.7). Move the class-conditional probe (60-fold) to a supplementary panel.
- [ ] **Step 3:** Change abstract + Barrier 1 text: "60-fold" → "11.3-fold" (and any other figure quoting the probe as the headline). Keep the probe as corroboration in SI.
- [ ] **Step 4 (commit):** `fix: use published-protocol A/B for Fig. 3a main panel`

---

# Phase 2 — Statistical robustness (medium cost)

### Task 2.1 — Null-distribution anchor for all distance metrics
- [ ] **Step 1 (RED):** Add `tests/unit/test_metrics_anchor.py::test_energy_distance_null_anchor` asserting the metrics module can produce a same-distribution reference ED by splitting the reference population in half. Confirm RED.
- [ ] **Step 2 (GREEN):** Implement a null-anchor helper (split reference population, compute within-distribution ED/MMD) and record the null scale in `RESULTS.md` + a reference line on Fig. 3c (and Fig. 2a). This resolves both the technical anchor and the readability anchor ("how big is 27 vs 4?").
- [ ] **Step 3 (commit):** `feat: add same-distribution null anchor for distance metrics`

### Task 2.2 — Uncertainty beyond training seed
- [ ] **Step 1 (RED):** Add `tests/integration/test_uncertainty.py` asserting the metrics JSON includes (a) baseline dispersion across resamples, (b) bootstrap CIs over both cells and **samples**, (c) at least 2 alternative group-held-out splits. Confirm RED.
- [ ] **Step 2 (GREEN):** Extend `seed_study.py` (or a new `uncertainty_study.py`) to: give conditional-mean / last-observation baselines sampling dispersion; add cell-level and sample-level bootstrap CIs for ED/MMD/correlation; add ≥2 leave-one-sample-out or alternative splits. Emit full JSON.
- [ ] **Step 3:** Update "worse on all three metrics in all five seeds" to reflect the broader uncertainty sources; if the conclusion only holds across training noise, restate it precisely.
- [ ] **Step 4 (commit):** `feat: add sample-level bootstrap and alternative splits`

### Task 2.3 — MMD bandwidth sensitivity
- [ ] **Step 1 (RED):** Add `tests/unit/test_mmd_bandwidth.py::test_mmd_stable_across_bandwidths` asserting MMD ranking is reported across median-heuristic and several fixed bandwidths. Confirm RED.
- [ ] **Step 2 (GREEN):** Run MMD across a bandwidth grid; report whether the Squidiff-vs-baseline ordering is stable. If it flips, do not count MMD as an independent metric in "all three metrics".
- [ ] **Step 3 (commit):** `test: add MMD bandwidth sensitivity analysis`

### Task 2.4 — Add at least one structure metric the baseline cannot win
- [ ] **Step 1 (RED):** Add `tests/unit/test_structure_metrics.py::test_gene_gene_correlation_metric` asserting a gene–gene correlation-structure metric (e.g., Frobenius distance between correlation matrices) and/or kNN local-density agreement is computed per condition. Confirm RED.
- [ ] **Step 2 (GREEN):** Implement the structure metric(s) + a rare-state/cluster-recall under the **published** latent-extrapolation protocol (currently SI Note 5 recall exists only for the class-conditional probe). Add to `seed_study.py` output and Fig. 3c / SI.
- [ ] **Step 3:** If Squidiff wins on structure while losing on marginal moments → that is the real headline; rewrite Performance accordingly.
- [ ] **Step 4 (commit):** `feat: add gene-correlation and cluster-recall structure metrics`

---

# Phase 3 — Narrative re-centering + submission completeness

### Task 3.1 — Re-center abstract/title on the transferable contribution
- [ ] **Step 1:** Rewrite title + abstract so the lead is the silent-vs-loud failure taxonomy and the two cheap checks (compare against released-artifact scale; build a training-only validation task). Demote CAR-NK performance to a supporting case.
- [ ] **Step 2:** Ensure the abstract states the boundary ("the CAR-NK population drifts little, which makes the task unfavourable to any generative model") alongside the performance result — no selective presentation.
- [ ] **Step 3:** Add a plain-language definition at first use of energy distance / MMD / silhouette ("0 means identical distributions") and the latent-extrapolation mechanism (encode → difference direction → step → sample → decode), with a schematic panel if space allows.
- [ ] **Step 4 (commit):** `docs: re-center narrative on transferable contribution`

### Task 3.2 — Move methodological decisions out of figure legends
- [ ] **Step 1:** Move MMD bandwidth source (35.39), kernel-saturation "deliberately not plotted", and silhouette scope limitations from Fig. 2c/3c legends into Methods/Results prose. Legends keep only what is needed to read the figure.

### Task 3.3 — Scope-limited wording pass
- [ ] **Step 1:** Change "The provided benchmark cannot catch this" → accessible-half-scoped wording; note the splatter dataset was not accessible and what was tried (contacted authors?).
- [ ] **Step 2:** Change "the branch was never executed end to end" → "consistent with the branch never having been executed end to end" (keep SI direct evidence).
- [ ] **Step 3:** Surface the single-dataset / single-task / single-species limit in title-adjacent framing, not only in Discussion.
- [ ] **Step 4:** Discuss the "optimal noise scale ≈ 0" implication in main text (the published randomization step contributes ~nothing on this data), and state that validation-based selection is in practice near-equivalent to setting 0.

### Task 3.4 — Submission completeness (blocking for sending, not for science)
- [ ] **Step 1:** Finalize Author contributions (replace bracketed placeholders, confirm with each author).
- [ ] **Step 2:** Complete the reference list; add the three positioning literatures — prior reusability/reproducibility audits, competing single-cell perturbation/development generative models, and prior reports of simple/linear baselines matching deep perturbation models. Cite refs 2–4 in text by number.
- [ ] **Step 3:** Mint Zenodo DOI for code + artifacts; ensure Source Data files exist for every figure matching the "Source data are provided" promise; complete the Nature Reporting Summary.
- [ ] **Step 4:** Confirm communication status with the original authors per NMI policy for Reusability Reports (verify the policy; do not assume).
- [ ] **Step 5 (commit):** `docs: complete submission materials`

---

# Acceptance criteria (definition of done)

1. Both baselines' fit set + timepoint are stated verbatim in Methods, Fig. 3c legend, and `RESULTS.md`; the 4.26-vs-19.10 ordering has an evidence-backed explanation or the claim is appropriately hedged.
2. `artifacts/positive_control/` metrics exist; the performance claim is either established (baseline loses on released setting) or correctly reframed (evaluation-regime property), and abstract/Performance/Discussion match the evidence.
3. Fig. 3a main panel uses the published-protocol A/B; abstract/Barrier 1 quote "11.3-fold" as the headline (60-fold demoted to SI corroboration).
4. "Undocumented" and "hardcoded" wording matches the verified primary-source findings (Tasks 0.1, 0.2).
5. Barrier 2 impact matches the claim-to-codepath map (Task 0.3).
6. All distance metrics carry a same-distribution null anchor; sample-level bootstrap + ≥2 alternative splits reported; MMD bandwidth sensitivity reported; ≥1 structure metric the baseline cannot win is included.
7. Abstract presents the task-unfavourable boundary alongside the performance result.
8. No bracketed placeholders remain; references complete; Zenodo DOI minted; Source Data + Reporting Summary present.
9. `make lint`, `make typecheck`, `make test` all green; every new analysis script has a failing-first test.

# Out of scope

- New datasets, new species, the perturbation-response half of the original work (explicitly untested — keep the boundary statement).
- Any change to the candidate-selection gate (`reports/selection_decision.json` remains immutable).
- Editorial-fit judgment for NMI (out of this plan's authority).
