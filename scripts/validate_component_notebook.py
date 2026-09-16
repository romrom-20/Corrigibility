"""Execute portable diagnostic end to end with synthetic successes and failures."""
import ast
import copy
from pathlib import Path
import uuid
import zipfile
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]
source=nbformat.read(ROOT/'notebooks/normative_hysteresis_component_diagnostic_colab.ipynb',as_version=4)
nbformat.validate(source)
for cell in source.cells:
    if cell.cell_type=='code':
        ast.parse(cell.source)
        assert not cell.outputs and cell.execution_count is None

def select(prefix):
    cells=[c for c in source.cells if c.cell_type=='code' and c.source.startswith(prefix)]
    assert len(cells)==1,prefix
    return copy.deepcopy(cells[0])

for correct in (False,True):
    work=ROOT/'.context/validation'/('components-'+str(correct)+'-'+uuid.uuid4().hex[:8]);work.mkdir(parents=True)
    nb=nbformat.v4.new_notebook(metadata=copy.deepcopy(source.metadata))
    nb.cells=[nbformat.v4.new_markdown_cell('# SYNTHETIC ONLY — no empirical model results'),
        select('from pathlib import Path'),select('import unittest'),
        nbformat.v4.new_code_cell(f"from test_components import FakeBackend\nbackend=FakeBackend(correct={correct})\nRESULTS_ROOT=PROJECT_ROOT/'synthetic-results'\nrun_folder=RESULTS_ROOT/'raw/component_diagnostic'/RUN_ID"),
        select('run_dir ='),select('backend = None'),select('run_dir ='),select('derived ='),select('import zipfile, uuid'),
        nbformat.v4.new_code_cell(f"assert backend is None\nassert cal.read_json(run_dir/'complete.json')['calls']==480\ns=cal.read_json(derived/'summary.json')\nassert sum(c['N'] for c in s['cells'])==480\nassert sum(c['verified'] for c in s['cells'])=={480 if correct else 0}\nassert len(cal.read_json(derived/'matched_pairs.json'))==288")]
    for i,c in enumerate(nb.cells):c.id=f'validation-{i}'
    NotebookClient(nb,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(work)}}).execute()
    evidence=work/'executed.ipynb';nbformat.write(nb,evidence)
    extracted=work/('nh-component-diagnostic-src-'+source.metadata.source_bundle_sha256[:12])
    for name in ('component_diagnostic.py','docs/NEXT_AGENT_PROMPT.md','component_tests/test_components.py'):
        assert (ROOT/name).read_bytes()==(extracted/name).read_bytes()
    archives=list(extracted.glob('synthetic-results/exports/*.zip'));assert len(archives)==1
    with zipfile.ZipFile(archives[0]) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if '/records/' in n])==480
        assert any(n.endswith('/matched_pairs.json') for n in z.namelist())
    print('PASS',correct,': 480 synthetic records, no-model completed resume, analysis and export.',evidence)
