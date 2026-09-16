#!/usr/bin/env python3
"""Execute both portable notebook routes without a model, CUDA or network."""
import ast
import copy
from pathlib import Path
import uuid
import zipfile

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
source = nbformat.read(ROOT / 'notebooks/normative_hysteresis_execution_readiness_colab.ipynb', as_version=4)
nbformat.validate(source)
for cell in source.cells:
    if cell.cell_type == 'code':
        ast.parse(cell.source)
        assert not cell.outputs and cell.execution_count is None


def select(prefix):
    matches = [c for c in source.cells if c.cell_type == 'code' and c.source.startswith(prefix)]
    assert len(matches) == 1, prefix
    return copy.deepcopy(matches[0])


for correct in (False, True):
    label = 'pass' if correct else 'fail'
    work = ROOT / '.context/validation' / ('execution-' + label + '-' + uuid.uuid4().hex[:8])
    work.mkdir(parents=True)
    nb = nbformat.v4.new_notebook(metadata=copy.deepcopy(source.metadata))
    count = 1280 if correct else 768
    nb.cells = [nbformat.v4.new_markdown_cell('# SYNTHETIC SOFTWARE VALIDATION ONLY\nNo model loaded; not empirical readiness evidence.'),
        select('from pathlib import Path'), select('import unittest'),
        nbformat.v4.new_code_cell(f"from test_execution import FakeBackend\nbackend = FakeBackend(correct={correct})\nRESULTS_ROOT = PROJECT_ROOT / 'synthetic-results'"),
        select('screen_dir ='), select('screen_dir ='),
        select('confirmation_dir ='), select('confirmation_dir ='),
        select('import zipfile, uuid'),
        nbformat.v4.new_code_cell(f'''assert backend.calls == {count}
assert cal.read_json(screen_dir / 'complete.json')['calls'] == 768
assert cal.read_json(screen_dir / 'complete.json')['raw_digest'] == cal.raw_digest(screen_dir)
assert screen_readiness['passed'] is {correct}
assert sum(c['N'] for c in cal.read_json(screen_derived / 'summary.json')['cells']) == 768
assert (confirmation_dir is not None) is {correct}
if confirmation_dir is not None:
    assert cal.read_json(confirmation_dir / 'complete.json')['calls'] == 512
    assert cal.read_json(confirmation_derived / 'readiness.json')['passed']
    assert cal.read_json(confirmation_dir / 'manifest.json')['screen']['raw_digest'] == cal.raw_digest(screen_dir)
''')]
    for i, cell in enumerate(nb.cells):
        cell.id = f'validation-{label}-{i}'
    NotebookClient(nb, timeout=120, kernel_name='python3', resources={'metadata': {'path': str(work)}}).execute()
    evidence = work / 'executed.ipynb'
    nbformat.write(nb, evidence)
    extracted = work / ('nh-execution-readiness-src-' + source.metadata.source_bundle_sha256[:12])
    for name in ('execution_readiness.py', 'configs/execution_readiness_v1.json',
                 'execution_tests/test_execution.py', 'docs/NEXT_AGENT_PROMPT.md'):
        assert (ROOT / name).read_bytes() == (extracted / name).read_bytes()
    archives = list(extracted.glob('synthetic-results/exports/*.zip'))
    assert len(archives) == 1
    with zipfile.ZipFile(archives[0]) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if '/records/' in n]) == count
        for name in ('source/execution_readiness.py', 'source/docs/NEXT_AGENT_PROMPT.md'):
            assert name in z.namelist()
        for artifact in ('readiness.json', 'format_pairs.csv', 'transcripts.html', 'design_audit.json'):
            assert any(n.endswith('/' + artifact) for n in z.namelist())
    print(f'PASS {label}: {count} synthetic records, resume with no new generation, correct confirmation route, complete ZIP.')
    print('Evidence:', evidence)
