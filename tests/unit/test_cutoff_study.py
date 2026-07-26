"""Tests for the declarative temporal-cutoff Squidiff runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "external_runners" / "squidiff"))

from cutoff_study import load_cutoff_config, prepare_cutoff_data  # noqa: E402

CONFIG = ROOT / "configs" / "cutoff_studies.yaml"


def test_early_config_predeclares_scales():
    config = load_cutoff_config(CONFIG, "early_d14")

    assert config.fixed_scales == (0.0, 0.03)
    assert config.validation_triplet is None
    assert config.seeds == (13, 37, 73, 101, 137)


def test_late_scale_selection_uses_training_times_only():
    config = load_cutoff_config(CONFIG, "late_d28")

    assert set(config.validation_triplet or ()).issubset(config.train_times)
    assert set(config.test_times).isdisjoint(config.validation_triplet or ())


def test_released_training_configuration_is_fixed():
    config = load_cutoff_config(CONFIG, "late_d28")

    assert config.steps == 50_000
    assert config.batch_size == 64
    assert config.class_cond is False
    assert config.use_encoder is True
    assert config.num_layers == 3
    assert config.diffusion_steps == 1_000


def test_prepare_cutoff_fits_features_on_training_cells_only(tmp_path):
    rows = []
    matrices = []
    for timepoint in (0, 7, 14, 21, 28):
        for cell in range(4):
            rows.append(
                {
                    "sample_id": f"sample_{timepoint}",
                    "timepoint_numeric": timepoint,
                }
            )
            matrices.append([cell, timepoint, 0.0, 1.0])
    # A held-out-only high-variance feature must not be selected.
    matrices[-4:] = [[0.0, 28.0, 1_000.0 * cell, 1.0] for cell in range(4)]
    adata = ad.AnnData(
        X=np.asarray(matrices, dtype=np.float32),
        obs=pd.DataFrame(rows, index=[f"cell_{i}" for i in range(len(rows))]),
        var=pd.DataFrame(index=["cell_axis", "time_axis", "test_only", "constant"]),
    )
    source = tmp_path / "full.h5ad"
    adata.write_h5ad(source)

    config = load_cutoff_config(CONFIG, "early_d14")
    prepared = prepare_cutoff_data(
        source,
        tmp_path / "run",
        config,
        n_genes=2,
        log_normalize=False,
    )
    manifest = json.loads(prepared.manifest_path.read_text(encoding="utf-8"))

    assert "test_only" not in manifest["selected_features"]
    assert set(manifest["train_sample_ids"]).isdisjoint(manifest["test_sample_ids"])
    assert Path(prepared.train_path).exists()
    assert Path(prepared.test_path).exists()
