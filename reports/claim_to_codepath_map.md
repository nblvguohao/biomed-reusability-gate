# Claim → code-path → verification map

Date: 2026-07-24
Purpose: recalibrate Barrier 2's impact statement. The manuscript currently
calls the broken `class_cond=True` branch "its headline perturbation-response
use". This map records, from local evidence only, which code path each
original-paper claim actually uses.

## Evidence inventory used

- `vendor/Squidiff/sample_squidiff.py` — the released prediction entry points.
- `vendor/Squidiff/Squidiff/script_util.py` — `NUM_CLASSES = 4`;
  `num_classes=(NUM_CLASSES if class_cond else None)`.
- `vendor/Squidiff/README.md` — upstream's own usage example (lines 30–42)
  samples via `sampler.pred(z_sem_scrna, ...)`, i.e. the **encoder** path with
  `model_kwargs={'z_mod': z_sem}`; no class labels involved.
- `manuscript/STATUS.md` — the args dict in the upstream
  `fig4_VO_reproducibility.ipynb` sets `class_cond=False` (direct evidence
  recorded earlier in this project).
- `manuscript/SUPPLEMENTARY_INFORMATION.md` Note 6 — released checkpoint
  config: `class_cond=False`, `use_encoder=True`, `num_layers=3`,
  `gene_size=596`, 2,400 steps, batch 16.
- `sample_squidiff.py::parse_args` — the released sampler defaults
  `class_cond=False`, `use_encoder=True`.

## The map

| Original-paper claim | Code path that produces it | Evidence for the mapping | Verification status in this report |
|---|---|---|---|
| Predicting cellular development (differentiation over time) | Encoder semantic latent space + **linear latent extrapolation**: `interp_with_direction` (encode two states → mean difference direction → step → sample around target → decode). `use_encoder=True`, `class_cond=False`. | `sample_squidiff.py:160-176`; manuscript Barrier 3; fig4 notebook args dict `class_cond=False` (STATUS.md) | Reproduced mechanically: checkpoint loads strict-clean (0 missing / 0 unexpected), sampling finite, energy distance 2.098 to reference (Supp. Note 6). Protocol re-implemented for CAR-NK task. |
| Predicting transcriptomic responses to **drug** perturbation (sci-Plex) | `use_drug_structure=True` branch with a control AnnData; sampling via encoder `z_mod` (`sampler.pred`). No `class_cond`. | README lines 24–28 (drug-structure training example) and 39–41 (encoder-path sampling example) | **Not tested** in this report (drug-structure branch untouched). |
| Predicting responses to **gene** perturbation | Listed as a feature (README line 19). The library's *only* label-conditional generation interface is `class_cond=True` (`Group` obs labels → `num_classes=4`). No released artifact, default, or documented workflow uses it. | `script_util.py:8,144`; all observed configs set `class_cond=False` | The branch **cannot run as released**: three dtype/device/rank defects, fixed cascade on the first optimizer step (Barrier 2); patches + regression tests in `vendor/patches/squidiff/`. |
| Released checkpoint & config | `class_cond=False`, `use_encoder=True` | Supp. Note 6 (`released_checkpoint_check.json`) | Verified directly. |

## Conclusion for Barrier 2 recalibration

No local evidence shows any published result produced with `class_cond=True`.
Every observed released configuration — sampler defaults, the fig4
reproducibility notebook args dict, and the released checkpoint config — sets
`class_cond=False`, and the README's own sampling example uses the encoder
path. The defensible claim is therefore:

> `class_cond=True` is the library's only label-conditional generation
> interface; it is exposed but non-functional as released, so the reuser's
> natural route to perturbation-conditional generation is blocked — while the
> original authors' own published results appear to use other branches
> (encoder latent extrapolation, drug-structure conditioning).

The current manuscript phrase "its headline perturbation-response use" is
**not supported** and must be replaced (planned edit in Phase 1/3).

Residual uncertainty (stated, not softened): this map rests on the pinned
vendored source, the README, and the earlier-recorded notebook args dict; if
the paper's perturbation figures were in fact generated with `class_cond=True`
in some unreleased configuration, Barrier 2's impact would upgrade. Nothing in
the local evidence supports that reading.
