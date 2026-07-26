"""Re-score correction-safe baselines and same-distribution references.

This CPU-only pass exists so that baseline corrections do not require model
retraining. In particular, the pooled diagonal Gaussian is fit on the complete
configured training window, never only on the latest time point.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cutoff_study import (  # noqa: E402
    CutoffRunConfig,
    _baseline_populations,
    _dense,
    _score_generated,
    load_cutoff_config,
)

ALL_BASELINES = (
    "last_observation_resample",
    "pooled_diagonal_gaussian",
    "temporal_diagonal_gaussian",
    "temporal_factor_gaussian",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reference_summary(
    test: npt.NDArray[Any],
    *,
    repeats: int,
    seed: int = 13,
) -> dict[str, Any]:
    from reuse_gate.metrics.distribution import (
        energy_distance_multivariate,
        mean_expression_correlation,
    )
    from reuse_gate.metrics.structure import correlation_frobenius

    if repeats <= 0:
        raise ValueError("reference_splits must be positive")
    if test.shape[0] < 4:
        raise ValueError("at least four target cells are required")
    rng = np.random.RandomState(seed)
    half = test.shape[0] // 2
    rows = []
    for _ in range(repeats):
        order = rng.permutation(test.shape[0])
        left = test[order[:half]]
        right = test[order[half : 2 * half]]
        rows.append(
            {
                "energy_distance": energy_distance_multivariate(left, right),
                "mean_expression_correlation": mean_expression_correlation(left, right),
                "correlation_frobenius_raw": correlation_frobenius(
                    left, right, normalized=False
                ),
                "correlation_frobenius_normalized": correlation_frobenius(
                    left, right, normalized=True
                ),
            }
        )
    summary = {}
    for metric in rows[0]:
        values = np.asarray([row[metric] for row in rows], dtype=np.float64)
        summary[metric] = {
            "mean": float(values.mean()),
            "q05": float(np.quantile(values, 0.05)),
            "q95": float(np.quantile(values, 0.95)),
            "values": [float(value) for value in values],
        }
    return {"repeats": repeats, "random_seed": seed, "summary": summary}


def evaluate_cutoff(
    config: CutoffRunConfig,
    train_path: Path,
    test_path: Path,
    *,
    seeds: tuple[int, ...] | None = None,
    baseline_names: tuple[str, ...] = ALL_BASELINES,
    reference_splits: int = 50,
) -> dict[str, Any]:
    """Evaluate selected baselines with the immutable cutoff specification."""
    import anndata as ad

    unknown = set(baseline_names) - set(ALL_BASELINES)
    if unknown:
        raise ValueError(f"unknown baselines: {sorted(unknown)}")
    selected_seeds = config.seeds if seeds is None else seeds
    if not set(selected_seeds).issubset(config.seeds):
        raise ValueError("all seeds must be predeclared in the cutoff config")

    train_ad = ad.read_h5ad(train_path)
    test_ad = ad.read_h5ad(test_path)
    train, test = _dense(train_ad), _dense(test_ad)
    train_times = train_ad.obs["timepoint_numeric"].to_numpy()
    test_times = test_ad.obs["timepoint_numeric"].to_numpy()

    from reuse_gate.metrics.distribution import median_pairwise_distance

    bandwidth = median_pairwise_distance(train)
    per_seed = []
    for seed in selected_seeds:
        populations = _baseline_populations(
            train,
            train_times,
            test_times,
            config,
            seed,
        )
        baselines = {
            name: _score_generated(
                test,
                test_times,
                populations[name],
                bandwidth,
                config,
            )
            for name in baseline_names
        }
        generated_summary = {
            name: {
                str(timepoint): {
                    "n_cells": int(values.shape[0]),
                    "mean": float(values.mean()),
                    "std": float(values.std()),
                }
                for timepoint, values in populations[name].items()
            }
            for name in baseline_names
        }
        per_seed.append(
            {
                "seed": seed,
                "baselines": baselines,
                "generated_summary": generated_summary,
            }
        )

    primary_test = np.concatenate(
        [test[test_times == value] for value in config.primary_test_times],
        axis=0,
    )
    return {
        "schema_version": "1.0",
        "cutoff": config.name,
        "correction_reason": (
            "pooled_diagonal_gaussian is fit on the complete configured training "
            "window; post-hoc scoring avoids unnecessary model retraining"
        ),
        "baseline_names": list(baseline_names),
        "expected_seeds": list(selected_seeds),
        "completed_seeds": [entry["seed"] for entry in per_seed],
        "complete": len(per_seed) == len(selected_seeds),
        "input_sha256": {
            "train_h5ad": _sha256(train_path),
            "test_h5ad": _sha256(test_path),
        },
        "mmd_bandwidth_fitted_on_training": bandwidth,
        "same_distribution_reference": _reference_summary(
            primary_test,
            repeats=reference_splits,
        ),
        "per_seed": per_seed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=REPO / "configs/cutoff_studies.yaml")
    parser.add_argument("--name", required=True)
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, action="append")
    parser.add_argument(
        "--baseline",
        choices=ALL_BASELINES,
        action="append",
        dest="baselines",
    )
    parser.add_argument("--reference-splits", type=int, default=50)
    args = parser.parse_args()

    result = evaluate_cutoff(
        load_cutoff_config(args.config, args.name),
        args.train,
        args.test,
        seeds=tuple(args.seed) if args.seed else None,
        baseline_names=tuple(args.baselines) if args.baselines else ALL_BASELINES,
        reference_splits=args.reference_splits,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
