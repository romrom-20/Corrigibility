#!/usr/bin/env python3
"""Execute the portable calibration path with an explicitly invalid synthetic backend."""
import ast
import copy
from pathlib import Path
import uuid
import zipfile
import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]
source=nbformat.read(ROOT/'notebooks/normative_hysteresis_calibration_colab.ipynb',as_version=4)
nbformat.validate(source)
for cell in source.cells:
    if cell.cell_type=='code':
        ast.parse(cell.source)
        assert not cell.outputs and cell.execution_count is None

def select(prefix):
    matches=[c for c in source.cells if c.cell_type=='code' and c.source.startswith(prefix)]
    assert len(matches)==1,prefix
    return copy.deepcopy(matches[0])

work=ROOT/'.context/validation'/('calibration-'+uuid.uuid4().hex[:8]);work.mkdir(parents=True)
nb=nbformat.v4.new_notebook(metadata=copy.deepcopy(source.metadata))
nb.cells=[nbformat.v4.new_markdown_cell('# SYNTHETIC SOFTWARE VALIDATION ONLY\nNo model loaded; deliberately invalid responses remain in every denominator.'),
          select('from pathlib import Path'),select('import unittest'),
          nbformat.v4.new_code_cell("from test_calibration import FakeBackend\nbackend=FakeBackend()\nRESULTS_ROOT=PROJECT_ROOT/'synthetic-results'"),
          select("RUN_ID ="),select("RUN_ID ="),select('derived ='),select('import zipfile, uuid'),
          nbformat.v4.new_code_cell("assert backend.calls==272\nassert cal.read_json(run_dir/'complete.json')['calls']==272\nassert cal.read_json(run_dir/'complete.json')['raw_digest']==cal.raw_digest(run_dir)\nsummary=cal.read_json(derived/'summary.json')\nassert sum(c['N'] for c in summary['cells'])==272\nassert sum(c['fully_correct_count'] for c in summary['cells'])==0")]
for i,c in enumerate(nb.cells):c.id=f'validation-{i}'
NotebookClient(nb,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(work)}}).execute()
evidence=work/'executed.ipynb';nbformat.write(nb,evidence)
extracted=work/('nh-calibration-src-'+source.metadata.source_bundle_sha256[:12])
for name in ['calibration_bench.py','configs/calibration_v1.json','calibration_tests/test_calibration.py']:
    assert (ROOT/name).read_bytes()==(extracted/name).read_bytes()
archives=list(extracted.glob('synthetic-results/exports/*.zip'));assert len(archives)==1
with zipfile.ZipFile(archives[0]) as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if '/records/' in n])==272
    assert 'source/calibration_bench.py' in z.namelist()
    assert any(n.endswith('/design_audit.json') for n in z.namelist())
print('PASS: portable sources, offline tests, 272 saved synthetic failures, completed resume without generation, analysis and export.')
print('Evidence:',evidence)
