"""Guard test for the Fig. 3a evidence path (TDD Phase 1.3).

Barrier 2 argues the class-conditional branch cannot run as released, so the
main-text demonstration of Barrier 1 must not rest on the class-conditional
probe: Fig. 3a's main panel must use the published-protocol latent-
extrapolation A/B (`artifacts/squidiff_latent_extrap_ab/`), with the probe
demoted to corroboration.

Phase 1.1/2.1 additions: Fig. 3c's last-observation baseline must be the
true D14 resample from the provenance audit (the manuscript text cites those
values), and panel c must carry the same-distribution null anchor from the
robustness pass.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "external_runners" / "squidiff"))

AB_ARTIFACT = REPO_ROOT / "artifacts" / "squidiff_latent_extrap_ab" / "preprocessing_ab_metrics.json"
PROVENANCE = REPO_ROOT / "artifacts" / "baseline_provenance" / "baseline_provenance.json"

FIG3_INPUTS = [
    "squidiff_latent_extrap_ab/preprocessing_ab_metrics.json",
    "squidiff_step_sweep/sweep_metrics.json",
    "squidiff_sweep_lognorm/sweep_metrics.json",
    "squidiff_latent_extrap/latent_noise_scale_sweep.json",
    "squidiff_seed_study/seed_study_metrics.json",
    "baseline_provenance/baseline_provenance.json",
]


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


def test_fig3c_baselines_come_from_provenance_audit(tmp_path):
    """The dashed last-observation line must be the true D14 resample.

    The manuscript text cites 0.72 / 0.0108 / 0.9760 (Supplementary Note 7);
    the figure must not silently keep the stale point-mass variant (19.10)
    from the seed-study metrics file.
    """
    import matplotlib

    matplotlib.use("Agg")
    from make_manuscript_figures import figure3

    result = figure3(REPO_ROOT, tmp_path)

    prov = json.loads(PROVENANCE.read_text())["baselines"]
    expected = prov["last_observation_true_d14_resample"]["scores"]
    got = result["c_baselines"]["last_observation"]
    assert got["energy_distance"] == expected["energy_distance"], (
        "Fig. 3c last-observation is not the true D14 resample from the provenance audit"
    )
    assert got["mmd_rbf"] == expected["mmd_rbf"]
    assert got["mean_expression_correlation"] == expected["mean_expression_correlation"]
    assert result["c_baselines"]["conditional_mean"]["energy_distance"] == (
        prov["conditional_mean"]["scores"]["energy_distance"]
    )


def _synthetic_root(tmp_path: Path) -> Path:
    """A root with the real Fig. 3 inputs plus a synthetic robustness.json."""
    root = tmp_path / "root"
    for rel in FIG3_INPUTS:
        dst = root / "artifacts" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO_ROOT / "artifacts" / rel, dst)
    robustness = {
        "null_anchor": {
            "energy_distance": {"mean": 0.11, "q95": 0.22},
            "mmd_rbf": {"mean": 0.004, "q95": 0.009},
            "mean_expression_correlation": {"mean": 0.998, "q05": 0.995},
            "note": "synthetic test values",
        },
        "structure": {
            "conditional_mean": {"correlation_frobenius": 266.0, "rare_cluster_recall": 0.34},
            "last_observation_d14": {"correlation_frobenius": 79.0, "rare_cluster_recall": 1.0},
            "squidiff_seed_13": {"correlation_frobenius": 145.0, "rare_cluster_recall": 1.0},
            "squidiff_seed_37": {"correlation_frobenius": 141.0, "rare_cluster_recall": 1.0},
            "squidiff_seed_73": {"correlation_frobenius": 131.0, "rare_cluster_recall": 0.93},
            "squidiff_seed_101": {"correlation_frobenius": 127.0, "rare_cluster_recall": 1.0},
            "squidiff_seed_137": {"correlation_frobenius": 144.0, "rare_cluster_recall": 0.93},
        },
    }
    rob_dir = root / "artifacts" / "evaluation_robustness"
    rob_dir.mkdir(parents=True, exist_ok=True)
    (rob_dir / "robustness.json").write_text(json.dumps(robustness))
    return root


def test_fig3c_carries_null_anchor_when_robustness_exists(tmp_path):
    """Panel c must draw (and report) the same-distribution reference band."""
    import matplotlib

    matplotlib.use("Agg")
    from make_manuscript_figures import figure3

    root = _synthetic_root(tmp_path)
    result = figure3(root, tmp_path / "out")

    got = result.get("c_null_anchor")
    assert got is not None, "Fig. 3c must carry the null anchor from robustness.json"
    assert got["energy_distance"] == {"mean": 0.11, "q95": 0.22}
    assert got["mmd_rbf"] == {"mean": 0.004, "q95": 0.009}
    assert got["mean_expression_correlation"] == {"mean": 0.998, "q05": 0.995}


def test_fig3c_middle_panel_is_structure_not_mmd(tmp_path):
    """MMD is demoted (its Squidiff-baseline ordering flips with bandwidth);
    the middle panel must be the gene-gene correlation structure distance."""
    import matplotlib

    matplotlib.use("Agg")
    from make_manuscript_figures import figure3

    root = _synthetic_root(tmp_path)
    result = figure3(root, tmp_path / "out")

    assert result["c_metrics"][1] == "correlation_frobenius", (
        "the middle panel of Fig. 3c must be the structure metric, not MMD"
    )
    structure = result["c_structure"]
    assert structure["squidiff_values"] == [145.0, 141.0, 131.0, 127.0, 144.0]
    assert structure["conditional_mean"] == 266.0
    assert structure["last_observation_d14"] == 79.0


def test_fig3c_requires_robustness(tmp_path):
    """The final panel c (null band + structure metric) needs robustness.json."""
    import matplotlib

    matplotlib.use("Agg")
    from make_manuscript_figures import figure3

    root = _synthetic_root(tmp_path)
    (root / "artifacts" / "evaluation_robustness" / "robustness.json").unlink()
    import pytest

    with pytest.raises(FileNotFoundError):
        figure3(root, tmp_path / "out")
