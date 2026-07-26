# NMI Revision Figure Contract

## Figure 1

- **Core conclusion:** The reuse assessment separates released-artefact
  verification, executable interfaces and leakage-safe predictive utility.
- **Archetype:** schematic-led composite.
- **Target/output:** Nature Machine Intelligence; 180 mm; editable SVG and PDF,
  600 dpi PNG.
- **Panel map:** a, evidence ladder; b, three temporal information boundaries;
  c, training-only versus test-only operations.
- **Evidence hierarchy:** the information boundary is the hero evidence;
  released-artefact checks and interface tests are supporting evidence.
- **Statistics:** cell and biological-sample counts only.
- **Source data:** split manifests and the consolidated revision manifest.
- **Reviewer risk:** avoid implying that an interface defect invalidates results
  produced by an unexercised branch.

## Figure 2

- **Core conclusion:** Operability of the released artefacts does not guarantee
  that every reuse-critical choice is explicit or robust.
- **Archetype:** quantitative grid.
- **Target/output:** Nature Machine Intelligence; 180 mm; editable SVG and PDF,
  600 dpi PNG.
- **Panel map:** a, strict checkpoint load and released-data sampling; b,
  preprocessing scale comparison; c, training-budget sensitivity; d,
  predeclared versus released latent noise scales.
- **Evidence hierarchy:** the single-variable preprocessing A/B is hero
  evidence; checkpoint verification and scale sensitivity are controls.
- **Statistics:** individual budgets or scales; no inferential p-values.
- **Source data:** consolidated revision manifest only.
- **Reviewer risk:** avoid “not documented”, “hardcoded” and causal language
  stronger than the audited release supports.

## Figure 3

- **Core conclusion:** Predictive utility is evaluated across three temporal
  cutoffs against train-only baselines, with marginal and structure-aware
  metrics kept distinct.
- **Archetype:** asymmetric quantitative grid.
- **Target/output:** Nature Machine Intelligence; 180 mm; editable SVG and PDF,
  600 dpi PNG.
- **Panel map:** a, cutoff-specific energy distance across five seeds; b,
  per-gene mean correlation; c, normalized correlation-structure distance; d,
  cluster-mass error and rare-state sensitivity.
- **Evidence hierarchy:** the three-cutoff comparison is hero evidence;
  same-distribution references and sensitivity grids are supporting evidence.
- **Statistics:** individual training seeds with mean and standard deviation
  shown as computational variability; biological-sample counts stated per
  cutoff; no seed-based population inference.
- **Source data:** consolidated revision manifest only, plus a machine-readable
  figure Source Data JSON generated from it.
- **Reviewer risk:** late D28 has one biological sample and is descriptive;
  early D21/D28 are exploratory; mean-expression correlation is invariant only
  to a shared positive affine transformation, not arbitrary rescaling.

## Supplementary VO sanity check

- **Core conclusion:** The released VO artefact shows that the mechanism can
  recover target structure under target-informed conditions.
- **Archetype:** quantitative grid.
- **Interpretation boundary:** the checkpoint and direction use target-day
  information, so this is neither prediction nor generalization evidence.
- **Reviewer risk:** never call this a positive control for out-of-sample
  forecasting.

## Shared visual and integrity rules

- Backend: Python/matplotlib exclusively.
- Final width: 180 mm; minimum text 6.5 pt at final size.
- Palette: neutral greys for references, blue for Squidiff, ochre/purple/green
  for distinct baseline families, red only for warnings or failures.
- Every panel reports its direction of improvement.
- No bars on logarithmic axes.
- No row, seed, cutoff or sensitivity setting is removed for appearance.
- No micrographs, blots or gels are used; image-manipulation declarations do
  not apply.
