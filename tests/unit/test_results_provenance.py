"""Guard tests for baseline provenance statements (TDD Phase 1.1).

The manuscript's headline comparison ("Squidiff is worse than a per-gene
Gaussian baseline on all three metrics in all five seeds") is only valid if
the baselines' fitting data is stated exactly. These tests fail until
`manuscript/RESULTS.md` records, for each baseline, the cell set its
quantities are fit on, and until the empirical mechanism behind the
conditional-mean vs last-observation ordering is documented.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_MD = REPO_ROOT / "manuscript" / "RESULTS.md"


def test_baselines_state_fit_set():
    """RESULTS.md must name, per baseline, the exact cell set fitted on."""
    text = RESULTS_MD.read_text(encoding="utf-8").lower()

    assert "conditional" in text and "mean" in text, "conditional-mean baseline missing"
    # The fit set must be identified as the pooled training window.
    assert "pooled training" in text, (
        "RESULTS.md must state that conditional_mean fits per-gene mean/variance "
        "on the pooled training window (pre-infusion + D7 + D14), not on held-out cells"
    )
    # The point-mass nature of the last-observation baseline must be explicit.
    assert "point" in text and ("zero variance" in text or "zero-variance" in text), (
        "RESULTS.md must state that last_observation is a constant point-mass "
        "prediction (zero variance) at the pooled training mean"
    )


def test_results_explain_baseline_ordering():
    """RESULTS.md must explain why conditional-mean ED < last-observation ED."""
    text = RESULTS_MD.read_text(encoding="utf-8").lower()

    assert "within" in text, (
        "RESULTS.md must reference the energy distance within-sample term that "
        "penalizes a zero-variance prediction"
    )
