"""Guard tests for load-bearing manuscript claims (TDD Phase 0).

Each test asserts that a checked-in evidence report exists and contains the
verdict the manuscript wording depends on. The reports are produced by
Phase 0 of `docs/superpowers/plans/2026-07-23-reviewer-revision-tdd.md`:

- ``reports/upstream_methods_preprocessing.md`` — whether the linked article's
  Methods describes the library-size normalization + log1p step.
- ``reports/noise_constant_provenance.md`` — whether the 0.7 sampling scale is
  a function-body literal or a default the released prediction path exposes.
- ``reports/claim_to_codepath_map.md`` — original-paper claim -> code path ->
  verification-status mapping.

A missing or unresolved report must fail loudly here, because the manuscript
title/abstract wording is only valid while the underlying verdict is known.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS = REPO_ROOT / "reports"

_UNRESOLVED_MARKERS = ("TODO", "TBD", "AUTHOR_INPUT_NEEDED", "UNKNOWN", "FIXME")


def _read_report(name: str) -> str:
    path = REPORTS / name
    assert path.exists(), (
        f"{name} is missing: Phase 0 of the reviewer-revision TDD must produce "
        f"it before the manuscript wording that depends on it is valid."
    )
    text = path.read_text(encoding="utf-8")
    for marker in _UNRESOLVED_MARKERS:
        assert marker not in text, f"{name} still contains unresolved marker {marker!r}"
    return text


def test_normalization_documented_status_resolved():
    """The verdict on where upstream documents the log-normalization step.

    The report must state, for each candidate location (linked-article Methods,
    main repository, reproducibility notebooks), whether the library-size
    normalization to 10,000 + log1p transform is described there.
    """
    text = _read_report("upstream_methods_preprocessing.md")

    verdict = re.search(r"^verdict\s*:\s*(.+)$", text, flags=re.MULTILINE)
    assert verdict, "report must contain a `verdict:` line"
    assert verdict.group(1).strip(), "verdict must be non-empty"

    for location in ("Methods", "notebook", "repository"):
        assert location.lower() in text.lower(), (
            f"report must address the {location} location explicitly"
        )


def test_noise_constant_is_source_literal():
    """The recorded provenance of the 0.7 noise scale must match the code.

    The pinned vendored source defines
    ``def sample_around_point(self, point, num_samples=None, scale=0.7)`` and
    the released prediction entry point ``interp_with_direction`` never
    forwards a ``scale`` value to it. The report must record this exact form
    so the manuscript can justify calling the constant unreachable in
    practice.
    """
    text = _read_report("noise_constant_provenance.md")

    verdict = re.search(r"^verdict\s*:\s*(.+)$", text, flags=re.MULTILINE)
    assert verdict, "report must contain a `verdict:` line"

    # Cross-check the report against the pinned vendored source of truth.
    source_path = REPO_ROOT / "vendor" / "Squidiff" / "sample_squidiff.py"
    source = source_path.read_text(encoding="utf-8")

    signature = re.search(
        r"def\s+sample_around_point\s*\(self,\s*point,\s*num_samples=None,\s*scale=([0-9.]+)\)",
        source,
    )
    assert signature, "sample_around_point signature not found in vendored source"
    recorded_scale = signature.group(1)
    assert recorded_scale in text, (
        f"report must record the vendored default scale ({recorded_scale}) verbatim"
    )

    # The released prediction path must not forward a noise scale. Match call
    # sites only (a leading ``.`` or whitespace before the name); the ``def``
    # line is a definition, not a call.
    call_sites = re.findall(r"(?<!def )sample_around_point\(([^)]*)\)", source)
    forwarding = [c for c in call_sites if "scale" in c]
    assert not forwarding, (
        "vendored source now forwards a scale at a call site; re-audit the claim"
    )
    assert "interp_with_direction" in text, (
        "report must name interp_with_direction as the released prediction path"
    )


def test_claim_to_codepath_map_complete():
    """The claim -> code-path -> verification map must cover the key claims."""
    text = _read_report("claim_to_codepath_map.md")

    for claim in ("development", "perturbation"):
        assert claim in text.lower(), f"map must cover the {claim} claim"
    for codepath in ("class_cond", "latent"):
        assert codepath in text.lower(), f"map must reference the {codepath} code path"
    assert "verification" in text.lower(), "map must record a verification status column"
