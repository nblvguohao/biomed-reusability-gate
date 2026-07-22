"""Unit tests for distribution metrics — RED phase."""

import numpy as np
import pytest

from reuse_gate.metrics.distribution import energy_distance_multivariate


def test_identical_distributions_have_zero_energy_distance():
    """Identical samples must yield zero energy distance."""
    x = np.array([[0.0], [1.0], [2.0]])
    assert energy_distance_multivariate(x, x) == 0.0


def test_different_distributions_have_positive_energy_distance():
    """Different samples must yield positive energy distance."""
    x = np.array([[0.0], [1.0], [2.0]])
    y = np.array([[5.0], [6.0], [7.0]])
    assert energy_distance_multivariate(x, y) > 0.0


def test_energy_distance_symmetric():
    """Energy distance must be symmetric."""
    x = np.array([[0.0, 1.0], [1.0, 2.0]])
    y = np.array([[3.0, 4.0], [5.0, 6.0]])
    assert energy_distance_multivariate(x, y) == pytest.approx(
        energy_distance_multivariate(y, x)
    )
