"""Security and provenance tests for A100 cutoff-study dispatch."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "external_runners" / "squidiff"))

from dispatch_cutoff_study import (  # noqa: E402
    REMOTE_ROOT,
    build_remote_manifest,
    launch_commands,
    validate_remote_root,
)


def test_manifest_contains_no_credentials():
    manifest = build_remote_manifest("abc123", "deadbeef", ["early_d14", "late_d28"])
    text = json.dumps(manifest).lower()

    assert "password" not in text
    assert "private_key" not in text
    assert "lab_host" not in text
    assert manifest["remote_root"] == REMOTE_ROOT


def test_remote_root_is_project_scoped():
    assert validate_remote_root("/data/lgh/reusability_report_nmi_20260727")
    with pytest.raises(ValueError):
        validate_remote_root("/data/lgh")
    with pytest.raises(ValueError):
        validate_remote_root("/")


def test_launch_commands_pin_one_cutoff_to_each_gpu():
    commands = launch_commands(("early_d14", "late_d28"))

    assert len(commands) == 2
    assert "CUDA_VISIBLE_DEVICES=0" in commands[0]
    assert "--name early_d14" in commands[0]
    assert "CUDA_VISIBLE_DEVICES=1" in commands[1]
    assert "--name late_d28" in commands[1]
    assert all("nohup" in command and "pid" in command for command in commands)
