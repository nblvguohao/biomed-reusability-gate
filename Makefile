.PHONY: setup lint typecheck test smoke inventory pin-upstreams \
        profile-nichetrans gate-nichetrans profile-squidiff gate-squidiff \
        profile-cmonge gate-cmonge decide selected-tier0 selected-report \
        selected-tier1 selected-figures audit-all-candidates

VENV := .venv
PYTHON := $(VENV)/Scripts/python.exe

setup:
	uv venv --python 3.11
	uv pip install -e ".[dev]"

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy src

test:
	$(PYTHON) -m pytest tests/unit -v

smoke:
	$(PYTHON) -m pytest tests/ -m "not integration and not gpu and not slow" -v

inventory:
	$(PYTHON) -m reuse_gate.cli inventory

pin-upstreams:
	$(PYTHON) -m reuse_gate.cli data

profile-nichetrans:
	$(PYTHON) -m reuse_gate.cli gate --candidate nichetrans

gate-nichetrans:
	$(PYTHON) -m reuse_gate.cli gate --candidate nichetrans

profile-squidiff:
	$(PYTHON) -m reuse_gate.cli gate --candidate squidiff

gate-squidiff:
	$(PYTHON) -m reuse_gate.cli gate --candidate squidiff

profile-cmonge:
	$(PYTHON) -m reuse_gate.cli gate --candidate cmonge

gate-cmonge:
	$(PYTHON) -m reuse_gate.cli gate --candidate cmonge

decide:
	$(PYTHON) -m reuse_gate.cli decide

selected-tier0:
	$(PYTHON) -m reuse_gate.cli run-selected --tier 0

selected-report:
	$(PYTHON) -m reuse_gate.cli report

selected-tier1:
	$(PYTHON) -m reuse_gate.cli run-selected --tier 1

selected-figures:
	@echo "Figures: not yet implemented"

audit-all-candidates:
	@echo "Warning: This runs all three candidate gates for audit purposes."
	@echo "It must never automatically trigger all three Tier 1 branches."
	$(PYTHON) -m reuse_gate.cli gate --candidate nichetrans
	$(PYTHON) -m reuse_gate.cli gate --candidate squidiff
	$(PYTHON) -m reuse_gate.cli gate --candidate cmonge
