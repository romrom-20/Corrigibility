#!/usr/bin/env python3
"""Execute the notebook's offline path in a fresh kernel using a labeled test double.

Needs nbformat, nbclient, ipykernel, numpy, pandas, matplotlib; never loads HF weights.
Writes validation evidence under .context/validation (gitignored).
"""
import ast
import copy
import json
from pathlib import Path
import uuid

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = nbformat.read(ROOT / "notebooks/normative_hysteresis_v0_colab.ipynb", as_version=4)
    nbformat.validate(source)
    for i, cell in enumerate(source.cells):
        if cell.cell_type == "code":
            ast.parse(cell.source, filename=f"cell-{i}")
            assert cell.execution_count is None and not cell.outputs, "Delivery notebook must have no fabricated run output"
    # Select by source anchors so unrelated markdown edits cannot move the wrong cells into validation.
    def select(prefix):
        matches = [c for c in source.cells if c.cell_type == "code" and c.source.startswith(prefix)]
        assert len(matches) == 1, prefix
        return copy.deepcopy(matches[0])

    work = ROOT / ".context/validation" / uuid.uuid4().hex[:8]
    work.mkdir(parents=True)
    validation = nbformat.v4.new_notebook()
    validation.metadata = copy.deepcopy(source.metadata)
    validation.cells = [nbformat.v4.new_markdown_cell(
        "# OFFLINE VALIDATION — SYNTHETIC TEST DOUBLE ONLY\nNo GPU or real model inference. Tests notebook extraction, scientific invariants, data plumbing, analysis, closed pilot gate and export.")]
    validation.cells += [select("from pathlib import Path"), select("import unittest"), select("from corrigibility_bench.normative_hysteresis")]
    validation.cells.append(nbformat.v4.new_code_cell(
        "from test_normative_hysteresis import RecordingBackend\nbackend = RecordingBackend()\nRESULTS_ROOT = PROJECT_ROOT / 'synthetic-results'\n"))
    validation.cells += [select(prefix) for prefix in (
        "from corrigibility_bench.runner import run_experiment", "from corrigibility_bench.analysis import analyze_run",
        "from scripts.notebook_workflow import ensure_smoke_approval", "RUN_PILOT = False", "if pilot_run is not None:",
        "from datetime import datetime, timezone")]
    NotebookClient(validation, timeout=180, kernel_name="python3", resources={"metadata": {"path": str(work)}}).execute()
    output = work / "offline_integration_executed.ipynb"
    nbformat.write(validation, output)
    extracted = work / "normative-hysteresis-v0-src"
    bundle = json.loads((extracted / "bundle_provenance.json").read_text())
    assert bundle["git_commit"]
    for directory, pattern in (("corrigibility_bench", "*.py"), ("tests", "*.py"), ("configs", "*.yaml")):
        for path in (ROOT / directory).glob(pattern):
            assert path.read_bytes() == (extracted / path.relative_to(ROOT)).read_bytes(), f"Stale notebook payload: {path}"
    assert not list(extracted.glob("synthetic-results/raw/normative_hysteresis/pilot-*")), "Pilot must remain gated"
    archives = list(extracted.glob("synthetic-results/exports/*.zip"))
    assert len(archives) == 1
    print("PASS: notebook schema, cell compilation, embedded-source tests, synthetic smoke, analysis, closed pilot gate, and ZIP export.")
    print("Evidence:", output)


if __name__ == "__main__":
    main()
