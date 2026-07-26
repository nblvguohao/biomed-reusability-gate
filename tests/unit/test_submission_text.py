"""Cross-file content guards for the NMI initial-submission sources."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "manuscript/reusability_report.md"
SUBMISSION_SOURCES = (
    MANUSCRIPT,
    ROOT / "manuscript/SUPPLEMENTARY_INFORMATION.md",
    ROOT / "manuscript/FIGURE_LEGENDS.md",
    ROOT / "manuscript/REPORTING_SUMMARY.md",
    ROOT / "manuscript/COVER_LETTER.md",
    ROOT / "manuscript/SOFTWARE_SUBMISSION_CHECKLIST.md",
    ROOT / "manuscript/TITLE_PAGE.md",
)


def _section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"missing section: {heading}"
    return match.group(1).strip()


def _words(text: str) -> list[str]:
    return re.findall(r"\b[\w'-]+\b", re.sub(r"<[^>]+>", " ", text))


def _package_text() -> str:
    missing = [path.name for path in SUBMISSION_SOURCES if not path.exists()]
    assert not missing, f"missing submission sources: {missing}"
    return "\n".join(path.read_text(encoding="utf-8") for path in SUBMISSION_SOURCES)


def test_abstract_and_main_text_limits():
    text = MANUSCRIPT.read_text(encoding="utf-8")
    abstract_match = re.search(
        r"^## Abstract\s*$\n(.*?)<!-- END ABSTRACT -->",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    main_match = re.search(
        r"<!-- END ABSTRACT -->(.*?)(?=^## Methods\s*$)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )

    assert abstract_match is not None, "abstract must have an explicit source boundary"
    assert main_match is not None, "main text must include Introduction, Results and Discussion"
    assert len(_words(abstract_match.group(1))) <= 150
    assert 3_000 <= len(_words(main_match.group(1))) <= 3_500


def test_required_article_sections_and_discussion_format():
    text = MANUSCRIPT.read_text(encoding="utf-8")
    headings = re.findall(r"^## (.+)$", text, flags=re.MULTILINE)

    assert headings.count("Results") == 1
    assert headings.count("Discussion") == 1
    assert headings.count("Methods") == 1
    assert "Outlook" not in headings
    discussion = _section(text, "Discussion")
    assert not re.search(r"^### ", discussion, flags=re.MULTILINE)


def test_no_unsupported_stale_or_placeholder_claims():
    text = _package_text().lower()
    banned = (
        "reproduce exactly",
        "preprocessing not documented",
        "hardcoded upstream",
        "cannot win by construction",
        "held-out cells are never reused",
        "evaluation regime",
        "positive control",
        "author_input_needed",
        "todo",
        "tbd",
    )
    for phrase in banned:
        assert phrase not in text


def test_vo_and_mean_correlation_boundaries_are_explicit():
    text = _package_text().lower()

    assert "target-informed" in text
    assert "does not support out-of-sample generalization" in text
    assert "shared positive affine transformation" in text
