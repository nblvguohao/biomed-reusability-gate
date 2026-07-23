"""Guard test for the Fig. 3a evidence path (TDD Phase 1.3).

Barrier 2 argues the class-conditional branch cannot run as released, so the
main-text demonstration of Barrier 1 must not rest on the class-conditional
probe: Fig. 3a's main panel must use the published-protocol latent-
extrapolation A/B (`artifacts/squidiff_latent_extrap_ab/`), with the probe
demoted to corroboration.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "external_runners" / "squidiff"))

AB_ARTIFACT = REPO_ROOT / "artifacts" / "squidiff_latent_extrap_ab" / "preprocessing_ab_metrics.json"


def test_fig3a_uses_published_protocol(tmp_path):
    """Fig. 3a's returned source values must equal the published-protocol A/B."""
    import matplotlib

    matplotlib.use("Agg")
    from make_manuscript_figures import figure3

    result = figure3(REPO_ROOT, tmp_path)

    ab = json.loads(AB_ARTIFACT.read_text())
    expected_raw = [e["pooled_energy_distance"] for e in ab["conditions"]["raw"]["per_budget"]]
    expected_log = [e["pooled_energy_distance"] for e in ab["conditions"]["lognorm"]["per_budget"]]
    expected_steps = [e["steps"] for e in ab["conditions"]["raw"]["per_budget"]]

    panel = result["a_preprocessing_ab"]
    assert panel["steps"] == expected_steps, "Fig. 3a x-axis is not the published-protocol budget sweep"
    assert panel["raw_counts"] == expected_raw, (
        "Fig. 3a raw series is not the published-protocol latent-extrapolation A/B"
    )
    assert panel["log_normalized"] == expected_log
    assert result.get("a_protocol", "").startswith("latent extrapolation"), (
        "Fig. 3a must declare the published protocol as its evidence path"
    )
    # The class-conditional probe may remain only as a clearly-labelled
    # supplementary corroboration, not as the main panel.
    assert "a_class_conditional_probe" in result, (
        "the class-conditional probe values must be retained as labelled corroboration"
    )
