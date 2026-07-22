"""Diagnose why Squidiff's raw samples lose to a per-feature Gaussian baseline.

Energy distance is scale-sensitive, so a generator whose outputs drift in mean
and variance is penalised heavily regardless of how well it captures structure.
This script separates the two contributions:

  raw            Squidiff samples as generated
  rescaled       samples affinely mapped onto the TRAINING moments
  shuffled       rescaled samples with each feature independently permuted,
                 which preserves every marginal exactly and destroys only the
                 cross-feature structure

The rescaling uses training statistics only. The shuffle is a negative control:
if rescaled Squidiff beats the conditional-mean baseline purely because it now
carries the right marginals, shuffling must leave the score unchanged.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


def _dense(adata) -> np.ndarray:  # noqa: ANN001
    x = adata.X
    return np.asarray(x.toarray() if hasattr(x, "toarray") else x, dtype=np.float64)


def rescale_to_moments(
    samples: np.ndarray, mean: np.ndarray, std: np.ndarray
) -> np.ndarray:
    """Map `samples` onto the given per-feature moments.

    Standardises by the samples' own statistics, then applies the target
    moments. Only the target moments carry outside information, so passing
    training statistics keeps the transform free of test-set leakage.
    """
    own_std = samples.std(axis=0, ddof=1)
    own_std = np.maximum(own_std, 1e-8)
    return (samples - samples.mean(axis=0)) / own_std * std + mean


def shuffle_within_features(
    samples: np.ndarray, rng: np.random.RandomState
) -> np.ndarray:
    """Permute each feature independently: marginals survive, structure does not."""
    out = samples.copy()
    for j in range(out.shape[1]):
        out[:, j] = out[rng.permutation(out.shape[0]), j]
    return out


def run(sweep_dir: Path, step_counts: list[int], seed: int = 13) -> dict:
    import anndata as ad

    from reuse_gate.metrics.distribution import energy_distance_multivariate
    from reuse_gate.models.temporal_baselines import conditional_mean_sampler

    test = _dense(ad.read_h5ad(sweep_dir / "test.h5ad"))
    train = _dense(ad.read_h5ad(sweep_dir / "train.h5ad"))
    train_mean = train.mean(axis=0)
    train_std = train.std(axis=0, ddof=1)

    baseline = conditional_mean_sampler(
        train, n_samples=test.shape[0], rng=np.random.RandomState(seed)
    )
    baseline_ed = float(energy_distance_multivariate(test, baseline))

    results: dict = {
        "seed": seed,
        "test_moments": {"mean": float(test.mean()), "std": float(test.std())},
        "train_moments": {"mean": float(train.mean()), "std": float(train.std())},
        "conditional_mean_ed": baseline_ed,
        "steps": [],
    }

    print(f"{'steps':>7} | {'raw':>8} | {'rescaled':>9} | {'shuffled':>9} | {'gen mean':>9} | {'gen std':>8}")
    print("-" * 7 + "-+-" + "-" * 8 + "-+-" + "-" * 9 + "-+-" + "-" * 9 + "-+-" + "-" * 9 + "-+-" + "-" * 8)

    for steps in step_counts:
        path = sweep_dir / f"steps_{steps}" / "squidiff_generated.npy"
        if not path.exists():
            print(f"{steps:>7} | missing {path}")
            continue

        raw = np.load(path).astype(np.float64)
        rescaled = rescale_to_moments(raw, train_mean, train_std)
        shuffled = shuffle_within_features(rescaled, np.random.RandomState(seed))

        entry = {
            "steps": steps,
            "ed_raw": float(energy_distance_multivariate(test, raw)),
            "ed_rescaled": float(energy_distance_multivariate(test, rescaled)),
            "ed_shuffled": float(energy_distance_multivariate(test, shuffled)),
            "generated_mean": float(raw.mean()),
            "generated_std": float(raw.std()),
            "marginals_preserved_by_shuffle": bool(
                np.allclose(np.sort(rescaled, axis=0), np.sort(shuffled, axis=0))
            ),
        }
        results["steps"].append(entry)
        print(
            f"{steps:>7} | {entry['ed_raw']:>8.2f} | {entry['ed_rescaled']:>9.2f} | "
            f"{entry['ed_shuffled']:>9.2f} | {entry['generated_mean']:>9.3f} | {entry['generated_std']:>8.3f}"
        )

    print(f"\n  conditional-mean baseline: {baseline_ed:.2f}")
    print(f"  real test moments:         mean {test.mean():.3f}, std {test.std():.3f}")

    if results["steps"]:
        best = min(results["steps"], key=lambda e: e["ed_rescaled"])
        raw_eds = [e["ed_raw"] for e in results["steps"]]
        res_eds = [e["ed_rescaled"] for e in results["steps"]]
        results["verdict"] = {
            "raw_degrades_with_training": all(
                raw_eds[i] <= raw_eds[i + 1] for i in range(len(raw_eds) - 1)
            ),
            "rescaled_improves_with_training": all(
                res_eds[i] >= res_eds[i + 1] for i in range(len(res_eds) - 1)
            ),
            "best_rescaled_steps": best["steps"],
            "best_rescaled_ed": best["ed_rescaled"],
            "rescaled_beats_baseline": best["ed_rescaled"] < baseline_ed,
            "shuffled_matches_baseline": abs(best["ed_shuffled"] - baseline_ed)
            < 0.1 * baseline_ed,
        }
        v = results["verdict"]
        print()
        print(f"  raw ED degrades monotonically with training:      {v['raw_degrades_with_training']}")
        print(f"  rescaled ED improves monotonically with training: {v['rescaled_improves_with_training']}")
        print(f"  rescaled beats conditional-mean baseline:         {v['rescaled_beats_baseline']}")
        print(f"  shuffling returns it to the baseline floor:       {v['shuffled_matches_baseline']}")

    out_path = sweep_dir / "calibration_metrics.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nResults saved: {out_path}")
    return results


if __name__ == "__main__":
    sweep = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("artifacts/squidiff_step_sweep")
    steps_arg = (
        [int(s) for s in sys.argv[2].split(",")] if len(sys.argv) > 2 else [5000, 20000, 50000]
    )
    run(sweep, steps_arg)
