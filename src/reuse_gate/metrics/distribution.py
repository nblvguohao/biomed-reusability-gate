"""Distribution-level metrics for comparing generated and real sample populations."""

from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt
from scipy.spatial.distance import cdist


def energy_distance_multivariate(x: npt.NDArray[Any], y: npt.NDArray[Any]) -> float:
    """Compute the multivariate energy distance between two sample sets.

    E(x, y) = 2 * mean(||x_i - y_j||) - mean(||x_i - x_j||) - mean(||y_i - y_j||)

    Returns 0 when x and y are identically distributed (in expectation).
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)

    # Pairwise distances
    d_xy = cdist(x, y, metric="euclidean")
    d_xx = cdist(x, x, metric="euclidean")
    d_yy = cdist(y, y, metric="euclidean")

    a = np.mean(d_xy)  # cross-distance
    b = np.mean(d_xx)  # within-x
    c = np.mean(d_yy)  # within-y

    return float(max(0.0, 2.0 * a - b - c))
