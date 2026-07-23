"""Unit tests for the evaluation-robustness helpers (TDD Phase 2).

Pure-function tests on synthetic data: null-distribution anchors, bootstrap
CIs (cell- and cluster-level), gene-correlation structure distance, and
rare-cluster mass recall. No network, GPU, or full datasets.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "external_runners" / "squidiff"))

from evaluation_robustness import (  # noqa: E402
    bootstrap_metric_ci,
    cluster_mass_recall,
    correlation_frobenius_distance,
    null_energy_distance,
)


def test_null_energy_distance_is_near_zero_for_identical_distribution():
    rng = np.random.RandomState(13)
    real = rng.randn(400, 20)
    null = null_energy_distance(real, n_splits=25, rng=np.random.RandomState(7))
    assert len(null) == 25
    assert abs(float(np.mean(null))) < 1.0
    # A genuinely different distribution must sit far above the null band.
    shifted = real + 3.0
    from reuse_gate.metrics.distribution import energy_distance_multivariate

    ed_shifted = energy_distance_multivariate(real, shifted)
    assert ed_shifted > float(np.quantile(null, 0.95))


def test_bootstrap_ci_contains_estimate_and_tracks_clusters():
    rng = np.random.RandomState(13)
    real = rng.randn(300, 10)
    gen = rng.randn(300, 10) * 1.1

    def metric(a, b):
        return float(np.mean(a) - np.mean(b))

    est, lo, hi = bootstrap_metric_ci(real, gen, metric, n_boot=100, rng=np.random.RandomState(3))
    assert lo <= est <= hi

    # Cluster-level bootstrap: with 5 clusters, resampling clusters must give
    # a CI at least as wide as cell-level (fewer effective units).
    clusters = np.repeat(np.arange(5), 60)
    est_c, lo_c, hi_c = bootstrap_metric_ci(
        real, gen, metric, n_boot=100, rng=np.random.RandomState(3), cluster=clusters
    )
    assert lo_c <= est_c <= hi_c
    assert (hi_c - lo_c) >= 0.0


def test_correlation_frobenius_distance_catches_structure():
    rng = np.random.RandomState(13)
    # Real data with genuine gene-gene correlation.
    base = rng.randn(500, 1)
    real = np.hstack([base + 0.1 * rng.randn(500, 1) for _ in range(5)])
    # Diagonal sampler: same marginals, zero covariance.
    gen = rng.randn(500, 5) * real.std(axis=0) + real.mean(axis=0)

    assert correlation_frobenius_distance(real, real) < 1e-9
    d = correlation_frobenius_distance(real, gen)
    assert d > 1.0, "diagonal sampler must be exposed on correlated data"


def test_cluster_mass_recall_perfect_for_identical_population():
    rng = np.random.RandomState(13)
    # Two clusters: one common (90%), one rare (10%).
    common = rng.randn(450, 8)
    rare = rng.randn(50, 8) + 6.0
    real = np.vstack([common, rare])

    recall = cluster_mass_recall(real, real.copy(), n_clusters=2, rare_below=0.2, rng=np.random.RandomState(1))
    assert recall == 1.0

    # A generator that drops the rare cluster entirely scores 0.
    gen_missing = common[rng.choice(450, 500, replace=True)]
    recall_missing = cluster_mass_recall(real, gen_missing, n_clusters=2, rare_below=0.2, rng=np.random.RandomState(1))
    assert recall_missing == 0.0
