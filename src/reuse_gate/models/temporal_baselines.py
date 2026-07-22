"""Simple temporal baselines for CAR-NK state prediction.

All baselines must fit only on training data. No test data used for fitting,
early stopping, normalization, or feature selection.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt


def last_observation(
    train: npt.NDArray[Any], test: npt.NDArray[Any]
) -> npt.NDArray[np.float64]:
    """Predict the training mean for every test cell.

    This represents the simplest baseline: the most recent observed state
    is assumed to persist unchanged.
    """
    train = np.asarray(train, dtype=np.float64)
    test = np.asarray(test, dtype=np.float64)
    mean = train.mean(axis=0, keepdims=True)
    return np.tile(mean, (test.shape[0], 1))


def conditional_mean_sampler(
    train: npt.NDArray[Any],
    n_samples: int,
    rng: np.random.RandomState | None = None,
) -> npt.NDArray[np.float64]:
    """Sample from a Gaussian centered at the training mean with train variance.

    Adds diagonal Gaussian noise scaled by per-feature training variance.
    Fits only on train data.
    """
    train = np.asarray(train, dtype=np.float64)
    if rng is None:
        rng = np.random.RandomState(13)

    mean = train.mean(axis=0)
    std = train.std(axis=0, ddof=1)
    std = np.maximum(std, 1e-8)  # avoid zero std

    samples = np.asarray(rng.randn(n_samples, train.shape[1]) * std + mean, dtype=np.float64)
    return samples


def linear_interpolation(
    train_early: npt.NDArray[Any],
    train_late: npt.NDArray[Any],
    n_samples: int,
    alpha: float = 1.0,
    rng: np.random.RandomState | None = None,
) -> npt.NDArray[np.float64]:
    """Extrapolate via linear interpolation between early and late timepoints.

    direction = mean(late) - mean(early)
    prediction = mean(late) + alpha * direction + small noise

    alpha=0 → stay at late mean
    alpha=1 → extrapolate one step forward
    """
    train_early = np.asarray(train_early, dtype=np.float64)
    train_late = np.asarray(train_late, dtype=np.float64)
    if rng is None:
        rng = np.random.RandomState(13)

    early_mean = train_early.mean(axis=0)
    late_mean = train_late.mean(axis=0)
    direction = late_mean - early_mean
    base = late_mean + alpha * direction

    # Add small noise scaled by late std
    late_std = train_late.std(axis=0, ddof=1)
    late_std = np.maximum(late_std, 1e-8)
    noise = rng.randn(n_samples, train_late.shape[1]) * late_std * 0.1

    return np.asarray(base[np.newaxis, :] + noise, dtype=np.float64)
