# Squidiff CAR-NK Data Profile

**Date:** 2026-07-22
**Evaluator:** Automated CI (Claude Code)

## Datasets

### GSE190976 — Primary Longitudinal Dataset

| Field | Value |
|-------|-------|
| Accession | [GSE190976](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE190976) |
| Title | CAR-NK cell and tumor cell interaction during in vivo anti-tumor therapy |
| Species | *Mus musculus* |
| PMID | 35534898 |
| DOI | 10.1038/s41591-022-01859-1 |
| Technology | scRNA-seq (10x Genomics) |
| BioSamples | 18 |
| Data size | 301 Gbases / ~144 MB supplementary |

**Experimental Design:**
- Raji-engrafted lymphoma mouse model
- CAR-NK cells: CAR19, CAR19/IL15, NT (non-transduced)
- With/without tumor cells
- IL-15 pre-infusion group

**Time Points (6):**

| Label | Day | Phase |
|-------|-----|-------|
| pre-infusion | 0 | Infusion product |
| D7 | 7 | Early response |
| D14 | 14 | Peak tumor control |
| D21 | 21 | Late response |
| D28 | 28 | Relapse onset |
| D35 | 35 | Full relapse |

**Constructs (3+):**

| Construct | Canonical | Description |
|-----------|-----------|-------------|
| CAR19 | CAR19 | CD19-targeting CAR-NK |
| CAR19/IL15 | CAR19_IL15 | CAR-NK with IL-15 expression |
| NT | NT | Non-transduced NK |

**Temporal Split Design (Plan Section 7.2):**

```
train:       pre-infusion, D7, D14  (early timepoints)
validation:  held-out training-side samples
test:        D21, D28, D35           (late timepoints)
```

### GSE221552 — External Support Dataset

| Field | Value |
|-------|-------|
| Accession | [GSE221552](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE221552) |
| Title | CITE-seq of CAR-NK cells for AML |
| Species | *Homo sapiens* |
| Samples | 7 (GSM6884089–GSM6884095) |
| Technology | CITE-seq (single-cell multi-omics) |

**Constructs:**

| Construct | Engineering State |
|-----------|-------------------|
| CAR33-NK | CAR33_wildtype |
| CAR33-KLRC1ko-NK | CAR33_KLRC1_knockout |

**Usage:** External support for construct/stimulation shift analysis. Results must be reported **separately** from the GSE190976 longitudinal endpoint — never merged.

## Parsing Infrastructure

### GSE190976
- `parse_timepoint(label) -> int` — explicit mapping, never lexicographic
- `map_construct(label) -> str` — canonical construct name
- `map_sample_to_group(sample_id) -> str` — known group assignment, returns "NA" for unknown
- `GSE190976_METADATA` — complete metadata dictionary

### GSE221552
- `parse_engineering_state(label) -> str` — canonical engineering state
- `GSE221552_METADATA` — complete metadata dictionary

## Gate Impact

| Gate | Dataset | Status |
|------|---------|--------|
| SQ-G3 | GSE190976 (6 timepoints) | ✅ PASS |
| SQ-G4 | GSE190976 (CAR19, CAR19/IL15, NT groups) | ✅ PASS |
| SQ-G5 | Cell counts (pending data download) | ⚠️ CONDITIONAL |
| SQ-G6 | Temporal split structure | ✅ PASS |
| SQ-G9 | Multiple meaningful endpoints | ✅ PASS |
| SQ-G10 | Group-level evaluation design | ✅ PASS |

## Download Status

Data files not yet downloaded. The parsers contain explicit metadata mappings that will be used to validate downloaded data against expectations. Download requires:
- GEO accession GSE190976 (supplementary files ~144 MB)
- GEO accession GSE221552 (7 sample files)

These will be downloaded during Tier 0 experiment setup if not already cached.

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Cell counts per group unknown | Download + QC will verify SQ-G5 |
| GSE190976 tumor vs no-tumor batches | Explicit batch column in contract |
| Mouse (GSE190976) vs human (GSE221552) | Never merge; report separately per plan |
| Batch effects between timepoints | Document and report; no across-timepoint batch correction without audit |
