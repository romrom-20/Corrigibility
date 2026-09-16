#!/usr/bin/env python3
"""Build only the prospective execution notebook; historical bundles stay frozen."""
import base64
import hashlib
import json
from pathlib import Path
import zlib
from build_colab_notebook import cell

ROOT = Path(__file__).resolve().parents[1]


def build():
    paths = [ROOT / p for p in ('component_diagnostic.py', 'execution_readiness.py', 'readiness_bench.py', 'calibration_bench.py',
                               'configs/component_diagnostic_v1.json', 'requirements-colab.txt', 'README.md')]
    paths += sorted((ROOT / 'corrigibility_bench').glob('*.py'))
    paths += sorted((ROOT / 'component_tests').glob('*.py'))
    paths += sorted((ROOT / 'docs').rglob('*.md'))
    bundle = {str(p.relative_to(ROOT)): p.read_text() for p in paths}
    data = json.dumps(bundle, sort_keys=True).encode()
    sha = hashlib.sha256(data).hexdigest()
    encoded = base64.b64encode(zlib.compress(data)).decode()
    bootstrap = '''from pathlib import Path
import base64, hashlib, json, os, sys, zlib
BUNDLE_SHA256 = "__SHA__"
embedded_sources = json.loads(zlib.decompress(base64.b64decode("__DATA__")))
assert hashlib.sha256(json.dumps(embedded_sources, sort_keys=True).encode()).hexdigest() == BUNDLE_SHA256
PROJECT_ROOT = (Path('/content') if Path('/content').exists() else Path.cwd()) / ('nh-component-diagnostic-src-' + BUNDLE_SHA256[:12])
for name, loaded in list(sys.modules.items()):
    if name in ('component_diagnostic', 'execution_readiness', 'readiness_bench', 'calibration_bench') or name == 'corrigibility_bench' or name.startswith('corrigibility_bench.'):
        if loaded is not None and PROJECT_ROOT not in Path(loaded.__file__).resolve().parents:
            raise RuntimeError('Different source already imported. Restart session and run this notebook from the top.')
for name, content in embedded_sources.items():
    assert not Path(name).is_absolute() and '..' not in Path(name).parts
    path = PROJECT_ROOT / name
    if path.exists() and path.read_text() != content:
        raise RuntimeError('Extracted source differs: ' + str(path))
for name, content in embedded_sources.items():
    path = PROJECT_ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists(): path.write_text(content)
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))
print('Source:', PROJECT_ROOT, 'Bundle:', BUNDLE_SHA256)
'''.replace('__SHA__', sha).replace('__DATA__', encoded)
    cells = [cell('markdown', '''# Component diagnostic — understand failure before another pilot

**nh-component-diagnostic-v1: 480 calls, no automatic follow-up.** The execution screen completed and the ranked candidate failed.
This notebook isolates single-row eligibility, two-number selection and state-template copying. It does not run D or retry failed full tasks.
All calls are independent fresh prompts. No computed answer or prior response enters another prompt.
Read docs/COMPONENT_DIAGNOSTIC_PLAN.md and docs/NEXT_AGENT_PROMPT.md after extraction.
Use hosted Colab only; choose and retain one GPU/runtime. No model weights on the Mac.
'''), cell('code', bootstrap), cell('markdown','## Install in hosted Colab only'), cell('code', '''import subprocess
if sys.platform == 'darwin' or not Path('/content').is_dir():
    raise RuntimeError('Use hosted Colab; never install model dependencies on the Mac.')
import google.colab
subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-colab.txt'], check=True)
'''), cell('markdown','## Offline checks and frozen budget'), cell('code','''import unittest
result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover('component_tests'))
assert result.wasSuccessful() and not result.skipped
import component_diagnostic as cal
config = cal.load_config()
RUN_ID = 'components-001'
print(json.dumps(cal.design_audit(), indent=2))
'''), cell('markdown', '''## Mount Drive and preserve sources

Keep the run ID for exact resume. Different source/config/hardware/runtime requires restoration or a new ID.
A leftover lock is never removed automatically. First establish that no other session is running this ID.
Only then use `cal.recover_lock(run_folder, confirmed_stopped=True)` in a separate cell. Never delete records or edit manifests.
'''), cell('code','''from google.colab import drive
drive.mount('/content/drive')
RESULTS_ROOT = Path('/content/drive/MyDrive/normative-hysteresis-v0/results')
backup = RESULTS_ROOT.parent / 'source_snapshots' / BUNDLE_SHA256
for name, content in embedded_sources.items():
    path = backup / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_text() == content, 'Source backup differs'
    else:
        path.write_text(content)
run_folder = RESULTS_ROOT / 'raw/component_diagnostic' / RUN_ID
print('Saved calls:', len(list((run_folder / 'records').glob('*.json'))))
print('Complete:', (run_folder / 'complete.json').exists())
if (run_folder / 'manifest.json').exists():
    saved = cal.read_json(run_folder / 'manifest.json')
    print('Saved runtime:', json.dumps(saved['model'], indent=2))
print('Source backup:', backup)
'''), cell('markdown','''## Load only if calls remain

Fixed Qwen3-8B revision/NF4/non-thinking, temperature 0.7. All variants have 160-token caps.
Use the existing HF secret without printing it. A completed run can be validated/exported without another model load.
For incomplete runs, select the same GPU as the saved runtime. A mismatch lists the exact differing fields.
'''), cell('code','''backend = None
if (run_folder / 'complete.json').exists():
    cal.checked_records(run_folder)
    print('Completed run validated; model loading skipped.')
else:
    if sys.platform == 'darwin' or not Path('/content').is_dir():
        raise RuntimeError('Real inference must run in hosted Colab.')
    from corrigibility_bench.hf_backend import HFBackend
    backend = HFBackend(config)
    print(json.dumps(backend.metadata, indent=2))
'''), cell('markdown','## Run or resume 480 independent calls'),cell('code','''run_dir = cal.run(backend, config, RESULTS_ROOT, RUN_ID)
print('Saved:', run_dir)
'''),cell('markdown','''## Analyze without changing responses

All invalid/truncated answers stay included. Review component/variant counts, rule/item/position strata,
state identifier versus numerical-criteria accuracy, matched fixes AND harms, and raw transcripts.
Some numeric prompts repeat across nominal cases; these are sampled repetitions, not independent task structures.
Simpler tasks omit full-table load. Passing components does not establish full-task competence, factual uptake or hysteresis.
No confirmation or pilot is unlocked by this notebook. Preserve and export every outcome.
'''),cell('code','''derived = cal.analyze(run_dir)
print((derived / 'summary.json').read_text())
print('Derived:', derived)
print('Transcripts:', derived / 'transcripts.html')
'''),cell('markdown','## Export raw records, sources and analysis; save executed notebook separately'),cell('code','''import zipfile, uuid
archive = RESULTS_ROOT / 'exports' / ('nh-components-' + uuid.uuid4().hex[:8] + '.zip')
archive.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
    for name in embedded_sources:
        z.write(PROJECT_ROOT / name, 'source/' + name)
    for folder in (run_dir, derived):
        for path in folder.rglob('*'):
            if path.is_file():
                z.write(path, 'results/' + str(path.relative_to(RESULTS_ROOT)))
print('Export:', archive)
print('Completion:', cal.read_json(run_dir / 'complete.json'))
print('Download ZIP and save the executed notebook with File > Download. No further GPU calls are scheduled.')
''')]
    notebook=dict(cells=cells, nbformat=4, nbformat_minor=5, metadata={
        'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
        'source_bundle_sha256':sha,'accelerator':'GPU',
        'colab':{'name':'normative_hysteresis_component_diagnostic_colab.ipynb'}})
    path=ROOT/'notebooks/normative_hysteresis_component_diagnostic_colab.ipynb'
    path.write_text(json.dumps(notebook,indent=1)+'\n')
    print(path,sha)

if __name__=='__main__':build()
