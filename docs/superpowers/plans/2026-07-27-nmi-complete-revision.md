# NMI Complete Revision and Submission Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two leakage-safe temporal-cutoff retraining studies, fair temporal and structure-capable baselines, validated structure metrics, a fully synchronized NMI manuscript, and a visually verified submission ZIP.

**Architecture:** Training and evaluation logic remains in focused, testable modules under `src/reuse_gate`, while Squidiff-specific GPU orchestration remains under `external_runners/squidiff`. Every narrative and figure is generated from a consolidated result manifest. A dedicated submission builder creates DOCX/PDF deliverables from final Markdown and figures, then produces a checksum-verified ZIP.

**Tech Stack:** Python 3.10/3.11, NumPy, SciPy, scikit-learn, AnnData/Scanpy, PyTorch/CUDA, pytest, python-docx, LibreOffice/Poppler, Paramiko, Markdown.

## Global Constraints

- Use biological samples, not cells, as independent observational units.
- No held-out population may influence training, normalization, feature selection, noise-scale selection or baseline fitting.
- Use Squidiff with `class_cond=False`, `use_encoder=True`, `num_layers=3`, `diffusion_steps=1000`, 50,000 steps and batch size 64.
- Use seeds `13, 37, 73, 101, 137`.
- Preserve `manuscript/reusability_report_draft.md` as archival and exclude it from every package.
- Never commit or package credentials, passwords, private keys, host IPs, remote history or local absolute paths.
- Follow RED-GREEN-REFACTOR for production-code changes.
- Run the complete test suite before every commit; record the known NumPy/PyTorch GPU regression separately if it remains unchanged.
- Final abstract must be at most 150 words; final main text must target 3,300-3,400 words and remain below 3,500.

---

## File map

- `src/reuse_gate/splits/temporal_cutoffs.py`: build early/current/late cutoff datasets and leakage manifests.
- `src/reuse_gate/models/temporal_baselines.py`: retain existing baselines and add task-aligned temporal diagonal and factor Gaussians.
- `src/reuse_gate/metrics/structure.py`: normalized correlation distance, same-distribution references and cluster-mass metrics.
- `external_runners/squidiff/cutoff_study.py`: train/evaluate five seeds for one cutoff from a declarative config.
- `external_runners/squidiff/consolidate_revision_results.py`: merge existing and new artifacts into one manuscript result manifest.
- `scripts/remote/lab_a100_hop.py`: reusable two-hop transport copied without credentials from the reference project.
- `external_runners/squidiff/dispatch_cutoff_study.py`: package, upload, launch, monitor and retrieve remote cutoff runs.
- `external_runners/squidiff/make_manuscript_figures.py`: regenerate synchronized manuscript figures and source data.
- `manuscript/*.md`: final scientific and administrative source documents.
- `scripts/build_submission_package.py`: create DOCX/PDF deliverables, copy figures/source data, write manifest and ZIP.
- `tests/unit/` and `tests/integration/`: information-boundary, baseline, metric, figure, manuscript and package tests.

### Task 1: Leakage-safe temporal cutoff construction

**Files:**
- Create: `src/reuse_gate/splits/temporal_cutoffs.py`
- Create: `tests/unit/test_temporal_cutoffs.py`
- Modify: `src/reuse_gate/splits/__init__.py`

**Interfaces:**
- Produces: `CutoffSpec`, `CutoffManifest`, `build_temporal_cutoff(adata, spec)`.
- `CutoffSpec(name, train_times, test_times, direction_times, validation_triplet)`.
- `CutoffManifest` records sample IDs, cell counts, feature-fit set and SHA256-ready metadata.

- [ ] **Step 1: Write failing split and leakage tests**

```python
def test_late_cutoff_uses_d28_only_for_test(toy_adata):
    spec = CutoffSpec(
        name="late_d28",
        train_times=(0, 7, 14, 21),
        test_times=(28,),
        direction_times=(14, 21),
        validation_triplet=(7, 14, 21),
    )
    split = build_temporal_cutoff(toy_adata, spec)
    assert set(split.train.obs["timepoint_numeric"]) == {0, 7, 14, 21}
    assert set(split.test.obs["timepoint_numeric"]) == {28}
    assert set(split.train.obs["sample_id"]).isdisjoint(split.test.obs["sample_id"])


def test_early_cutoff_has_no_test_selected_noise_scale(toy_adata):
    spec = early_cutoff_spec()
    assert spec.validation_triplet is None
    assert spec.fixed_scale_sensitivity == (0.0, 0.03)
```

- [ ] **Step 2: Confirm RED**

Run: `.\.venv310\Scripts\python.exe -m pytest tests/unit/test_temporal_cutoffs.py -v`

Expected: collection fails because `temporal_cutoffs` does not exist.

- [ ] **Step 3: Implement cutoff models and builder**

```python
@dataclass(frozen=True)
class CutoffSpec:
    name: str
    train_times: tuple[int, ...]
    test_times: tuple[int, ...]
    direction_times: tuple[int, int]
    validation_triplet: tuple[int, int, int] | None
    fixed_scale_sensitivity: tuple[float, ...] = ()


def build_temporal_cutoff(adata: ad.AnnData, spec: CutoffSpec) -> TemporalCutoff:
    train = adata[adata.obs["timepoint_numeric"].isin(spec.train_times)].copy()
    test = adata[adata.obs["timepoint_numeric"].isin(spec.test_times)].copy()
    audit_group_disjoint(train.obs["sample_id"], test.obs["sample_id"])
    return TemporalCutoff(train=train, test=test, manifest=manifest_for(train, test, spec))
```

- [ ] **Step 4: Confirm GREEN and regression safety**

Run: `.\.venv310\Scripts\python.exe -m pytest tests/unit/test_temporal_cutoffs.py tests/unit/test_temporal_split.py tests/unit/test_leakage_audit.py -v`

Expected: all pass.

- [ ] **Step 5: Commit**

```powershell
git add src/reuse_gate/splits tests/unit/test_temporal_cutoffs.py
git commit -m "feat: add leakage-safe temporal cutoff specifications"
```

### Task 2: Task-aligned temporal and factor Gaussian baselines

**Files:**
- Modify: `src/reuse_gate/models/temporal_baselines.py`
- Create: `tests/unit/test_temporal_structured_baselines.py`

**Interfaces:**
- Produces:
  - `temporal_diagonal_gaussian(x_prev, x_last, steps, n_samples, rng)`.
  - `fit_temporal_factor_gaussian(x_prev, x_last, variance_grid, train_only)`.
  - `TemporalFactorGaussian.sample(steps, n_samples, rng)`.

- [ ] **Step 1: Write failing behavioral tests**

```python
def test_temporal_diagonal_extrapolates_feature_means():
    prev = np.array([[0., 2.], [0., 2.]])
    last = np.array([[1., 4.], [1., 4.]])
    got = temporal_diagonal_gaussian(prev, last, steps=1, n_samples=2000,
                                     rng=np.random.RandomState(1))
    np.testing.assert_allclose(got.mean(0), [2., 6.], atol=0.12)


def test_factor_gaussian_reproduces_training_correlation():
    rng = np.random.RandomState(2)
    z = rng.normal(size=(1000, 1))
    prev = np.c_[z[:, 0], z[:, 0] + rng.normal(0, .05, 1000)]
    last = prev + np.array([1., 1.])
    model = fit_temporal_factor_gaussian(prev, last, component_grid=(1,))
    gen = model.sample(steps=1, n_samples=1000, rng=np.random.RandomState(3))
    assert np.corrcoef(gen, rowvar=False)[0, 1] > 0.9
```

- [ ] **Step 2: Confirm RED**

Run: `.\.venv310\Scripts\python.exe -m pytest tests/unit/test_temporal_structured_baselines.py -v`

Expected: imports fail for the two new functions.

- [ ] **Step 3: Implement minimal baselines**

```python
def temporal_diagonal_gaussian(x_prev, x_last, *, steps, n_samples, rng):
    target_mean = x_last.mean(0) + steps * (x_last.mean(0) - x_prev.mean(0))
    residual_var = np.maximum(np.var(x_last - x_last.mean(0), axis=0), 1e-8)
    return rng.normal(target_mean, np.sqrt(residual_var), size=(n_samples, x_last.shape[1]))


@dataclass
class TemporalFactorGaussian:
    pca: PCA
    previous_factor_mean: np.ndarray
    last_factor_mean: np.ndarray
    residual_std: np.ndarray

    def sample(self, *, steps, n_samples, rng):
        mean = self.last_factor_mean + steps * (
            self.last_factor_mean - self.previous_factor_mean
        )
        factors = rng.normal(mean, np.sqrt(self.pca.explained_variance_),
                             size=(n_samples, self.pca.n_components_))
        return self.pca.inverse_transform(factors) + rng.normal(
            0, self.residual_std, size=(n_samples, self.pca.n_features_in_)
        )
```

- [ ] **Step 4: Confirm GREEN**

Run: `.\.venv310\Scripts\python.exe -m pytest tests/unit/test_temporal_structured_baselines.py tests/unit/test_temporal_baselines.py -v`

Expected: all pass.

- [ ] **Step 5: Commit**

```powershell
git add src/reuse_gate/models/temporal_baselines.py tests/unit/test_temporal_structured_baselines.py
git commit -m "feat: add task-aligned temporal Gaussian baselines"
```

### Task 3: Structure metrics, reference bands and sensitivity

**Files:**
- Create: `src/reuse_gate/metrics/structure.py`
- Create: `tests/unit/test_structure_metrics.py`
- Modify: `external_runners/squidiff/evaluation_robustness.py`

**Interfaces:**
- Produces:
  - `correlation_frobenius(real, generated, normalized=True)`.
  - `same_distribution_structure_reference(real, n_splits, rng)`.
  - `cluster_mass_metrics(real, generated, n_clusters, rare_below, random_state)`.
  - `structure_sensitivity_grid(real, generated, cluster_counts, rare_thresholds)`.

- [ ] **Step 1: Write failing metric tests**

```python
def test_normalized_frobenius_divides_by_retained_gene_count():
    raw = correlation_frobenius(REAL, GEN, normalized=False)
    norm = correlation_frobenius(REAL, GEN, normalized=True)
    assert norm == pytest.approx(raw / REAL.shape[1])


def test_cluster_mass_metrics_penalize_one_cell_coverage():
    result = cluster_mass_metrics(REAL_WITH_RARE_MASS, ONE_CELL_PER_CLUSTER,
                                  n_clusters=3, rare_below=.15, random_state=0)
    assert result["rare_coverage"] == 1.0
    assert result["cluster_mass_mae"] > 0.05
    assert result["cluster_mass_jsd"] > 0
```

- [ ] **Step 2: Confirm RED**

Run: `.\.venv310\Scripts\python.exe -m pytest tests/unit/test_structure_metrics.py -v`

Expected: import failure.

- [ ] **Step 3: Implement the metrics**

```python
def cluster_mass_metrics(real, generated, *, n_clusters, rare_below, random_state):
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10).fit(real)
    real_mass = np.bincount(km.labels_, minlength=n_clusters) / len(real)
    gen_labels = km.predict(generated)
    gen_mass = np.bincount(gen_labels, minlength=n_clusters) / len(generated)
    rare = real_mass < rare_below
    return {
        "rare_coverage": float(np.mean(gen_mass[rare] > 0)) if rare.any() else 1.0,
        "cluster_mass_mae": float(np.abs(real_mass - gen_mass).mean()),
        "cluster_mass_jsd": float(jensenshannon(real_mass, gen_mass) ** 2),
        "rare_mass_recall": float(np.minimum(real_mass[rare], gen_mass[rare]).sum()
                                  / real_mass[rare].sum()) if rare.any() else 1.0,
    }
```

- [ ] **Step 4: Confirm GREEN and integrate**

Run: `.\.venv310\Scripts\python.exe -m pytest tests/unit/test_structure_metrics.py tests/unit/test_robustness.py -v`

Expected: all pass.

- [ ] **Step 5: Commit**

```powershell
git add src/reuse_gate/metrics/structure.py tests/unit/test_structure_metrics.py external_runners/squidiff/evaluation_robustness.py
git commit -m "feat: validate structure and rare-state metrics"
```

### Task 4: Declarative five-seed cutoff GPU runner

**Files:**
- Create: `external_runners/squidiff/cutoff_study.py`
- Create: `tests/unit/test_cutoff_study.py`
- Create: `configs/cutoff_studies.yaml`

**Interfaces:**
- Consumes Tasks 1-3.
- Produces one directory per cutoff containing `split_manifest.json`,
  `seed_<seed>/model.pt`, `seed_<seed>/metrics.json` and
  `cutoff_summary.json`.

- [ ] **Step 1: Write failing config and information-boundary tests**

```python
def test_early_config_predeclares_scales():
    cfg = load_cutoff_config(CONFIG, "early_d14")
    assert cfg.fixed_scales == (0.0, 0.03)
    assert cfg.validation_triplet is None


def test_late_scale_selection_uses_training_times_only():
    cfg = load_cutoff_config(CONFIG, "late_d28")
    assert set(cfg.validation_triplet).issubset(set(cfg.train_times))
    assert set(cfg.test_times).isdisjoint(cfg.validation_triplet)
```

- [ ] **Step 2: Confirm RED**

Run: `.\.venv310\Scripts\python.exe -m pytest tests/unit/test_cutoff_study.py -v`

Expected: `cutoff_study` import fails.

- [ ] **Step 3: Implement runner configuration and dry-run**

```python
@dataclass(frozen=True)
class CutoffRunConfig:
    name: str
    train_times: tuple[int, ...]
    test_times: tuple[int, ...]
    direction_times: tuple[int, int]
    validation_triplet: tuple[int, int, int] | None
    fixed_scales: tuple[float, ...]
    seeds: tuple[int, ...]
    steps: int = 50_000
    batch_size: int = 64


def run_cutoff(config, full_adata_path, output_dir, *, dry_run=False):
    split = prepare_training_only_features(full_adata_path, config)
    write_manifest(split, config, output_dir)
    if dry_run:
        return output_dir / "split_manifest.json"
    for seed in config.seeds:
        train_one_seed(split, config, seed, output_dir / f"seed_{seed}")
    return consolidate_cutoff(output_dir)
```

- [ ] **Step 4: Confirm GREEN with synthetic dry-run**

Run: `.\.venv310\Scripts\python.exe -m pytest tests/unit/test_cutoff_study.py -v`

Expected: all pass without GPU.

- [ ] **Step 5: Commit**

```powershell
git add external_runners/squidiff/cutoff_study.py configs/cutoff_studies.yaml tests/unit/test_cutoff_study.py
git commit -m "feat: add declarative Squidiff cutoff study runner"
```

### Task 5: Remote A100 dispatch with provenance

**Files:**
- Create: `scripts/remote/lab_a100_hop.py`
- Create: `external_runners/squidiff/dispatch_cutoff_study.py`
- Create: `tests/unit/test_remote_dispatch.py`
- Modify: `.gitignore`

**Interfaces:**
- `build_remote_manifest(commit, archive_sha256, cutoffs)`.
- `dispatch(hop, manifest, remote_root, credential_paths)`.
- Remote root: `/data/lgh/reusability_report_nmi_20260727/`.

- [ ] **Step 1: Write failing security and manifest tests**

```python
def test_manifest_contains_no_credentials(tmp_path):
    manifest = build_remote_manifest("abc123", "deadbeef", ["early_d14", "late_d28"])
    text = json.dumps(manifest).lower()
    assert "password" not in text
    assert "private_key" not in text


def test_remote_root_is_project_scoped():
    assert validate_remote_root("/data/lgh/reusability_report_nmi_20260727")
    with pytest.raises(ValueError):
        validate_remote_root("/data/lgh")
```

- [ ] **Step 2: Confirm RED**

Run: `.\.venv310\Scripts\python.exe -m pytest tests/unit/test_remote_dispatch.py -v`

Expected: dispatch module missing.

- [ ] **Step 3: Copy the generic hop helper and implement dispatch**

Copy only `C:\CC\PlantPersulf-Code\scripts\remote\lab_a100_hop.py`; use
`C:\CC\PlantPersulf-Code\LAB_HOST` and `C:\CC\PlantPersulf-Code\A100` by
explicit runtime path. Do not copy credential files.

```python
def build_remote_manifest(commit, archive_sha256, cutoffs):
    return {
        "git_commit": commit,
        "source_archive_sha256": archive_sha256,
        "cutoffs": list(cutoffs),
        "remote_root": REMOTE_ROOT,
    }
```

- [ ] **Step 4: Confirm GREEN and run read-only preflight**

Run tests, then:

```powershell
.\.venv310\Scripts\python.exe external_runners\squidiff\dispatch_cutoff_study.py check --lab-host "C:\CC\PlantPersulf-Code\LAB_HOST" --target "C:\CC\PlantPersulf-Code\A100"
```

Expected: jump host reachable, A100 visible, free disk and Python/CUDA inventory printed.

- [ ] **Step 5: Commit**

```powershell
git add scripts/remote/lab_a100_hop.py external_runners/squidiff/dispatch_cutoff_study.py tests/unit/test_remote_dispatch.py .gitignore
git commit -m "feat: add provenance-safe A100 cutoff dispatch"
```

### Task 6: Execute and retrieve ten new model trainings

**Files:**
- Generate: `artifacts/cutoff_studies/early_d14/**`
- Generate: `artifacts/cutoff_studies/late_d28/**`
- Create: `reports/cutoff_study_provenance.md`

**Interfaces:**
- Consumes Task 5 remote launcher.
- Produces SHA256-verified checkpoints, logs and summary JSON used by Task 7.

- [ ] **Step 1: Create source archive and verify local dry-run**

Run:

```powershell
.\.venv310\Scripts\python.exe external_runners\squidiff\cutoff_study.py --config configs\cutoff_studies.yaml --name early_d14 --dry-run
.\.venv310\Scripts\python.exe external_runners\squidiff\cutoff_study.py --config configs\cutoff_studies.yaml --name late_d28 --dry-run
```

Expected: disjoint split manifests, no model files.

- [ ] **Step 2: Dispatch early and late studies**

```powershell
.\.venv310\Scripts\python.exe external_runners\squidiff\dispatch_cutoff_study.py launch --cutoffs early_d14 late_d28
```

Expected: ten seed jobs launched with separate logs and no overwrite.

- [ ] **Step 3: Monitor without blocking the conversation**

Run bounded status checks through the dispatcher. Validate that each completed
seed has `model.pt`, `metrics.json`, non-empty log and matching input hashes.

- [ ] **Step 4: Download and verify**

```powershell
.\.venv310\Scripts\python.exe external_runners\squidiff\dispatch_cutoff_study.py retrieve --cutoffs early_d14 late_d28
```

Expected: local SHA256 equals remote SHA256 for every result archive.

- [ ] **Step 5: Write provenance report and commit code-visible report only**

Do not commit large artifacts. Record commands, commits, hashes, environment,
wall times, successes and failures in `reports/cutoff_study_provenance.md`.

```powershell
git add reports/cutoff_study_provenance.md
git commit -m "docs: record temporal cutoff retraining provenance"
```

### Task 7: Consolidated result manifest and synchronized figures

**Files:**
- Create: `external_runners/squidiff/consolidate_revision_results.py`
- Modify: `external_runners/squidiff/make_manuscript_figures.py`
- Modify: `tests/unit/test_figure_source.py`
- Create: `tests/unit/test_revision_results.py`

**Interfaces:**
- Produces: `artifacts/revision_results/revision_results.json`.
- Figures consume only that manifest and write `source_data.json`.

- [ ] **Step 1: Write failing consolidation and stale-label tests**

```python
def test_revision_manifest_contains_all_cutoffs(result):
    assert set(result["cutoffs"]) == {"primary_d21_d28", "early_d14", "late_d28"}


def test_final_figure_source_has_no_stale_terms(tmp_path):
    source = make_all_figures(ROOT, tmp_path)
    text = json.dumps(source).lower()
    for banned in ("not documented", "hardcoded", "reproduce exactly"):
        assert banned not in text
```

- [ ] **Step 2: Confirm RED**

Run: `.\.venv310\Scripts\python.exe -m pytest tests/unit/test_revision_results.py tests/unit/test_figure_source.py -v`

Expected: missing revision manifest interface or stale text failure.

- [ ] **Step 3: Implement consolidation and revised figures**

```python
def consolidate(root: Path) -> dict:
    return {
        "primary": read_primary(root),
        "cutoffs": {
            "early_d14": read_cutoff(root, "early_d14"),
            "late_d28": read_cutoff(root, "late_d28"),
        },
        "vo_sanity_check": {**read_vo(root), "interpretation": "target-informed"},
        "provenance": collect_hashes(root),
    }
```

- [ ] **Step 4: Confirm GREEN and render figures**

Run tests, then regenerate PDF/SVG/PNG and inspect all figures at full size.

- [ ] **Step 5: Commit**

```powershell
git add external_runners/squidiff/consolidate_revision_results.py external_runners/squidiff/make_manuscript_figures.py tests/unit/test_revision_results.py tests/unit/test_figure_source.py
git commit -m "feat: synchronize revision results and figures"
```

### Task 8: Rewrite manuscript and initial-submission materials

**Files:**
- Modify: `manuscript/reusability_report.md`
- Modify: `manuscript/SUPPLEMENTARY_INFORMATION.md`
- Modify: `manuscript/FIGURE_LEGENDS.md`
- Modify: `manuscript/REPORTING_SUMMARY.md`
- Modify: `manuscript/RESULTS.md`
- Create: `manuscript/COVER_LETTER.md`
- Create: `manuscript/SOFTWARE_SUBMISSION_CHECKLIST.md`
- Create: `manuscript/TITLE_PAGE.md`
- Create: `tests/unit/test_submission_text.py`

**Interfaces:**
- Consumes `revision_results.json` and final figure source data.
- Produces clean Markdown sources with no unresolved placeholders.

- [ ] **Step 1: Write failing text-consistency tests**

```python
def test_abstract_and_main_text_limits():
    parts = parse_manuscript(MANUSCRIPT)
    assert word_count(parts.abstract) <= 150
    assert word_count(parts.main_text) <= 3500


def test_no_unsupported_or_stale_claims():
    package_text = read_all_submission_markdown().lower()
    for banned in (
        "reproduce exactly",
        "preprocessing not documented",
        "hardcoded upstream",
        "cannot win by construction",
        "held-out cells are never reused",
    ):
        assert banned not in package_text


def test_required_article_sections():
    headings = manuscript_headings(MANUSCRIPT)
    assert "Results" in headings
    assert headings.count("Discussion") == 1
    assert "Outlook" not in headings
```

- [ ] **Step 2: Confirm RED**

Run: `.\.venv310\Scripts\python.exe -m pytest tests/unit/test_submission_text.py -v`

Expected: word-limit, headings and stale-claim failures.

- [ ] **Step 3: Load and apply the writing/statistics/figure skill fragments**

Use `nature-writing` with axes:
`task=manuscript+submission-package`, `paper_type=research`,
`sections=title,abstract,intro,experiments,discussion,method`,
`language=en`, `journal=nature`.

Use `nature-statistics` to align biological sample units, seed interpretation,
uncertainty and legends. Use `nature-figure` for final figure text and source
data.

- [ ] **Step 4: Rewrite every source document**

Use functional-verification language, target-informed VO wording,
task-aligned baseline definitions, cutoff-study boundaries and formal archive
citations. Cover letter must explain why the work is a Reusability Report
rather than a Matters Arising submission and disclose that the linked paper
appeared in Nature Methods.

- [ ] **Step 5: Confirm GREEN**

Run:

```powershell
.\.venv310\Scripts\python.exe -m pytest tests/unit/test_submission_text.py tests/unit/test_manuscript_claims.py tests/unit/test_results_provenance.py -v
```

Expected: all pass.

- [ ] **Step 6: Commit**

```powershell
git add manuscript tests/unit/test_submission_text.py
git commit -m "docs: revise NMI manuscript and submission materials"
```

### Task 9: Build DOCX/PDF deliverables

**Files:**
- Create: `scripts/build_submission_package.py`
- Create: `tests/integration/test_submission_package.py`
- Generate: `submission_package_nmi/`

**Interfaces:**
- `build_package(repo_root, output_dir) -> PackageManifest`.
- Produces the filenames listed in the design specification.

- [ ] **Step 1: Write failing package tests**

```python
def test_package_contains_required_files(tmp_path):
    manifest = build_package(ROOT, tmp_path)
    required = {
        "01_Manuscript_clean.docx", "01_Manuscript_clean.pdf",
        "02_Supplementary_Information.docx", "02_Supplementary_Information.pdf",
        "03_Cover_Letter.docx", "03_Cover_Letter.pdf",
        "04_Reporting_Summary_answers.docx",
        "05_Software_Submission_Checklist.docx", "06_Title_Page.docx",
    }
    assert required.issubset({p.name for p in manifest.files})


def test_package_excludes_archival_and_secrets(tmp_path):
    manifest = build_package(ROOT, tmp_path)
    names = "\n".join(str(p) for p in manifest.files).lower()
    assert "reusability_report_draft" not in names
    assert "lab_host" not in names
    assert "a100" not in names
```

- [ ] **Step 2: Confirm RED**

Run: `.\.venv310\Scripts\python.exe -m pytest tests/integration/test_submission_package.py -v`

Expected: builder import failure.

- [ ] **Step 3: Implement document and package builder**

Use `python-docx` with consistent Nature-style typography, embedded figures,
caption placement, page breaks and availability statements. Convert DOCX to
PDF using the bundled document renderer/LibreOffice. Write SHA256 for every
deliverable.

```python
def build_package(repo_root: Path, output_dir: Path) -> PackageManifest:
    clean_output(output_dir)
    build_manuscript_docx(repo_root, output_dir / "01_Manuscript_clean.docx")
    build_supplement_docx(repo_root, output_dir / "02_Supplementary_Information.docx")
    build_admin_documents(repo_root, output_dir)
    convert_required_pdfs(output_dir)
    copy_figures_and_source_data(repo_root, output_dir)
    return write_manifest_and_zip(output_dir)
```

- [ ] **Step 4: Confirm GREEN**

Run the package test and validate that all PDFs are non-empty and all checksums
match.

- [ ] **Step 5: Commit builder and tests**

```powershell
git add scripts/build_submission_package.py tests/integration/test_submission_package.py
git commit -m "feat: build NMI submission documents and archive"
```

### Task 10: Visual QA, privacy audit and final archive

**Files:**
- Generate: `submission_package_nmi/qa/`
- Modify: `submission_package_nmi/Submission_Readiness_Checklist.md`
- Generate: `submission_package_nmi.zip`

**Interfaces:**
- Consumes Task 9 package.
- Produces the final user-deliverable ZIP and clean individual files.

- [ ] **Step 1: Render every DOCX and PDF**

Use the document renderer for DOCX and Poppler for PDF. Render all pages, not
samples.

- [ ] **Step 2: Inspect every rendered page**

Check figure resolution, clipping, overlap, tables, headings, captions,
references, page numbers, Unicode glyphs and section transitions. Fix the
source or builder and repeat rendering after every layout change.

- [ ] **Step 3: Run content, privacy and checksum audits**

```powershell
rg -n -i "TODO|TBD|AUTHOR_INPUT_NEEDED|C:\\\\|password|private key|100\\.112|100\\.66" submission_package_nmi
.\.venv310\Scripts\python.exe -m pytest
git diff --check
```

Expected: no package matches; tests pass except a separately documented,
unchanged upstream GPU-environment regression if still present.

- [ ] **Step 4: Verify archive round-trip**

Extract the ZIP to a new temporary directory, verify its manifest checksums,
open every DOCX/PDF and confirm the archival draft and credentials are absent.

- [ ] **Step 5: Final commit**

Commit only source documents, builders, tests and small manifests. Keep large
generated artifacts and the submission ZIP outside git when required by
`.gitignore`.

```powershell
git add manuscript scripts tests reports docs
git commit -m "docs: finalize NMI submission package"
```
