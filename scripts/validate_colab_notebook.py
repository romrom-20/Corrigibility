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
import zipfile

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = nbformat.read(ROOT / "notebooks/normative_hysteresis_diagnostic_colab.ipynb", as_version=4)
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
        "# OFFLINE VALIDATION — SYNTHETIC TEST DOUBLE ONLY\nNo GPU or real model inference. Tests extraction, scientific invariants, closed gate, repeated fixture approval, full synthetic pilot, analysis and exports.")]
    validation.cells += [select("from pathlib import Path"), select("import unittest"), select("from corrigibility_bench.normative_hysteresis")]
    validation.cells.append(nbformat.v4.new_code_cell(
        "from test_normative_hysteresis import RecordingBackend\nbackend = RecordingBackend()\nRESULTS_ROOT = PROJECT_ROOT / 'synthetic-results'\n"))
    validation.cells += [select(prefix) for prefix in (
        "from corrigibility_bench.runner import run_experiment", "from corrigibility_bench.analysis import analyze_run",
        "from scripts.notebook_workflow import ensure_smoke_approval", "RUN_PILOT = False", "if pilot_run is not None:",
        "from datetime import datetime, timezone")]
    validation.cells.append(nbformat.v4.new_code_cell('''
assert pilot_run is None, "Default notebook path must leave pilot closed"
assert not list(RESULTS_ROOT.glob('raw/normative_hysteresis/pilot-*'))
# SOFTWARE FIXTURE ONLY: this does not approve any real smoke or model result.
from corrigibility_bench.runner import review_template
fixture = review_template(smoke_run)
fixture.update(reviewer="SYNTHETIC NOTEBOOK TEST ONLY", task_comprehension_acceptable=True, approve_pilot=True)
for annotation in fixture['trajectories'].values():
    annotation.update(reviewed=True, notes="Synthetic software fixture, not a human research judgment.")
fixture_path = RESULTS_ROOT / 'synthetic-review.json'
fixture_path.write_text(json.dumps(fixture))
'''))
    approved = select("from scripts.notebook_workflow import ensure_smoke_approval")
    approved.source = approved.source.replace('REVIEW_FILE = ""', 'REVIEW_FILE = str(fixture_path)')
    validation.cells += [copy.deepcopy(approved), copy.deepcopy(approved)]
    pilot = select("RUN_PILOT = False")
    pilot.source = pilot.source.replace("RUN_PILOT = False", "RUN_PILOT = True")
    validation.cells += [pilot, select("if pilot_run is not None:"), select("from datetime import datetime, timezone")]
    validation.cells.append(nbformat.v4.new_code_cell('''
from corrigibility_bench.runner import read_json, raw_digest
assert read_json(pilot_run / 'complete.json')['calls'] == 1440
assert read_json(pilot_run / 'complete.json')['raw_digest'] == raw_digest(pilot_run)
assert len(backend.calls) == 480 + 1440
'''))
    # The same production cell intentionally runs twice; each test copy needs its own ID.
    for index, code_cell in enumerate(validation.cells):
        code_cell.id = f"validation-{index}"
    NotebookClient(validation, timeout=180, kernel_name="python3", resources={"metadata": {"path": str(work)}}).execute()
    output = work / "offline_integration_executed.ipynb"
    nbformat.write(validation, output)
    extracted = work / ("nh-diagnostic-src-" + source.metadata.source_bundle_sha256[:12])
    bundle = json.loads((extracted / "bundle_provenance.json").read_text())
    assert bundle["git_commit"]
    for directory, pattern in (("corrigibility_bench", "*.py"), ("tests", "*.py"), ("configs", "*.yaml")):
        for path in (ROOT / directory).glob(pattern):
            assert path.read_bytes() == (extracted / path.relative_to(ROOT)).read_bytes(), f"Stale notebook payload: {path}"
    assert len(list(extracted.glob("synthetic-results/raw/normative_hysteresis/pilot-*/complete.json"))) == 1
    archives = list(extracted.glob("synthetic-results/exports/*.zip"))
    assert len(archives) == 2
    pilot_counts = []
    for archive in archives:
        with zipfile.ZipFile(archive) as zipped:
            assert zipped.testzip() is None
            names = zipped.namelist()
            assert "source/scripts/notebook_workflow.py" in names
            assert "source/docs/EXPERIMENT_GUIDE.md" in names
            pilot_records = [name for name in names if "/pilot-diagnostic-001/records/" in name]
            pilot_counts.append(len(pilot_records))
            if pilot_records:
                assert "results/raw/normative_hysteresis/smoke-diagnostic-001/review_approval.json" in names
    assert sorted(pilot_counts) == [0, 1440]
    print("PASS: notebook schema, embedded-source tests, synthetic smoke, closed pilot gate, reusable fixture approval, full synthetic pilot, analysis and both ZIP exports.")
    print("Evidence:", output)


if __name__ == "__main__":
    main()
