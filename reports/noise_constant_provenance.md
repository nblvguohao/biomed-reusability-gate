# Noise-constant provenance: `sample_around_point` scale = 0.7

Date: 2026-07-24
Source of truth: pinned vendored upstream `vendor/Squidiff/sample_squidiff.py`
(commit `abdfc27d84947dcccd745d1067c0840a41d32eb8`, v1.0.8)

## Exact code form

Line 145–146:

```python
def sample_around_point(self, point, num_samples=None, scale=0.7):
    return point + scale * np.random.randn(num_samples, point.shape[0])
```

verdict: 0.7 is a **default parameter value** in the `sample_around_point`
signature — not a literal inside the function body — but it is **unreachable
from the released prediction path**: the only internal call site,
`interp_with_direction` (line 165), invokes
`self.sample_around_point(z_sem_interp_, num_samples=z_sem_origin.shape[0])`
without passing `scale`, and no configuration, CLI argument, or notebook
parameter forwards a value either.

## Supporting detail

1. `interp_with_direction(self, ..., scale=1, add_noise_term=True)` has its own
   `scale` parameter, but that parameter multiplies the **direction**
   (line 163: `direction.detach().cpu().numpy() * scale`) and is never
   forwarded to `sample_around_point`. The naming collision makes the trap
   worse: a reuser who sets `scale` on `interp_with_direction` changes the
   extrapolation step size, not the injected noise.
2. The `sampler` class exposes no argparse/CLI path for the noise scale;
   `parse_args` builds defaults in code only.
3. A reuser can only change the 0.7 by (a) editing library source, or
   (b) bypassing the published `interp_with_direction` entry point and calling
   `sample_around_point` directly with an explicit `scale=`.

## Consequence for manuscript wording

"Hardcoded" is accurate in effect for anyone using the released prediction
path, but the precise statement is:

> The noise scale defaults to 0.7 in the `sample_around_point` signature, and
> the released prediction path `interp_with_direction` never exposes or
> forwards it, so in practice it is fixed at 0.7 unless the reuser edits the
> library source or bypasses the published entry point.

Title wording should shift from "a hardcoded sampling constant" to wording
that survives author rebuttal, e.g. "an unexposed sampling default" or
"a sampling constant the released path never exposes". Body text may keep
"hardcoded" only if immediately qualified by the sentence above.
