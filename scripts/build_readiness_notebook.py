#!/usr/bin/env python3
"""Build the standalone readiness notebook; does not regenerate v2."""
import base64
import hashlib
import json
from pathlib import Path
import zlib
from build_colab_notebook import cell

ROOT = Path(__file__).resolve().parents[1]


def build():
    paths = [ROOT/'readiness_bench.py', ROOT/'calibration_bench.py', ROOT/'configs/readiness_v1.json', ROOT/'requirements-colab.txt',
             *sorted((ROOT/'corrigibility_bench').glob('*.py')),
             *sorted((ROOT/'readiness_tests').glob('*.py')),
             ROOT/'README.md', *sorted((ROOT/'docs').rglob('*.md'))]
    bundle = {str(p.relative_to(ROOT)): p.read_text() for p in paths}
    data = json.dumps(bundle, sort_keys=True).encode(); sha = hashlib.sha256(data).hexdigest()
    encoded = base64.b64encode(zlib.compress(data)).decode()
    bootstrap = '''from pathlib import Path
import base64, hashlib, json, os, sys, zlib
BUNDLE_SHA256 = "__FINGERPRINT__"
embedded_sources = json.loads(zlib.decompress(base64.b64decode("__ENCODED__")))
assert hashlib.sha256(json.dumps(embedded_sources, sort_keys=True).encode()).hexdigest() == BUNDLE_SHA256
PROJECT_ROOT = (Path('/content') if Path('/content').exists() else Path.cwd()) / ('nh-readiness-src-' + BUNDLE_SHA256[:12])
for name in ('readiness_bench', 'calibration_bench', 'corrigibility_bench'):
    loaded = sys.modules.get(name)
    if loaded is not None and PROJECT_ROOT not in Path(loaded.__file__).resolve().parents:
        raise RuntimeError('Different source already imported. Restart session and run this notebook from the top.')
for name, content in embedded_sources.items():
    path = PROJECT_ROOT / name
    assert not Path(name).is_absolute() and '..' not in Path(name).parts
    if path.exists() and path.read_text() != content:
        raise RuntimeError('Existing extracted source differs: ' + str(path))
for name, content in embedded_sources.items():
    path = PROJECT_ROOT / name; path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists(): path.write_text(content)
os.chdir(PROJECT_ROOT); sys.path.insert(0, str(PROJECT_ROOT))
print('Source:', PROJECT_ROOT, 'Bundle:', BUNDLE_SHA256)
'''.replace('__FINGERPRINT__',sha).replace('__ENCODED__',encoded)
    cells = [cell('markdown','''# Constructed-item readiness before carryover testing

This is **nh-readiness-v1**, not a hysteresis pilot. It makes **192 independent calls**:
128 rowwise decisions and 64 state probes. Two numeric instances of one structure,
four row orders, two independently crossed label assignments and four rules. No automatic scaling,
no previous response fed into another call, and no retries for wrong/invalid answers.
Read `docs/READINESS_PLAN.md` after extraction. Use hosted Colab only; never a local runtime.
Choose the GPU before starting, then keep model/precision/runtime fixed throughout.
'''), cell('code',bootstrap), cell('markdown','## Install Colab dependencies'),
        cell('code',"import subprocess\nsubprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-colab.txt'], check=True)"),
        cell('markdown','## Offline checks and frozen call budget'),
        cell('code',"import unittest\nresult = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover('readiness_tests'))\nassert result.wasSuccessful() and not result.skipped\nimport readiness_bench as cal\nconfig = cal.load_config()\nprint('Calls:', len(cal.grid()))\nprint(json.dumps(cal.design_audit(), indent=2))"),
        cell('markdown','## Mount Drive and preserve exact sources'),
        cell('code',"from google.colab import drive\ndrive.mount('/content/drive')\nRESULTS_ROOT = Path('/content/drive/MyDrive/normative-hysteresis-v0/results')\nbackup = RESULTS_ROOT.parent / 'source_snapshots' / BUNDLE_SHA256\nfor name, content in embedded_sources.items():\n    path = backup / name; path.parent.mkdir(parents=True, exist_ok=True)\n    if path.exists():\n        assert path.read_text() == content, 'Source backup differs'\n    else:\n        path.write_text(content)\nprint('Source backup:', backup)"),
        cell('markdown','''## Load the fixed model on Colab

Keep the pinned Qwen3-8B revision, NF4, non-thinking mode and temperature 0.7.
Each call verifies effective decoding. Decision cap is 512 in both table views;
state probe cap is 160. A changed source/config/runtime requires a new ID.
Reuse the existing HF secret. Never print credentials.
'''), cell('code',"from corrigibility_bench.hf_backend import HFBackend\nbackend = HFBackend(config)\nprint(json.dumps(backend.metadata, indent=2))"),
        cell('markdown','''## Run or resume readiness

The default new run ID is `readiness-001`. Completed matching calls are reused.
If the tab disconnects, restore this exact notebook/environment and rerun setup,
load and this cell. Do not launch two runners with the same ID or delete raw files.
There is no smoke-review gate here: these are fresh-only readiness calls, with no investment manipulation.
'''), cell('code',"RUN_ID = 'readiness-001'\nrun_dir = cal.run(backend, config, RESULTS_ROOT, RUN_ID)\nprint('Saved:', run_dir)"),
        cell('markdown','''## Inspect and export

Review summary.json, cases.csv, design_audit.json and all transcripts. Compare
full versus focused tables: every row and trap remains, while the focused view
omits the unused attribute. Output schema and current rule are matched. Inspect
both initial and final rules by label assignment and row position. Distinguish
old-optimum errors from unfiltered traps. State probes report current criteria;
no response feeds another call. No automatic hysteresis pilot follows.
'''), cell('code',"derived = cal.analyze(run_dir)\nfrom IPython.display import display, HTML\nprint((derived / 'summary.json').read_text())\ndisplay(HTML((derived / 'transcripts.html').read_text()))\nprint('Derived:', derived)"),
        cell('code',"import zipfile, uuid\narchive = RESULTS_ROOT / 'exports' / ('nh-readiness-' + uuid.uuid4().hex[:8] + '.zip')\narchive.parent.mkdir(parents=True, exist_ok=True)\nwith zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:\n    for name in embedded_sources:\n        z.write(PROJECT_ROOT / name, 'source/' + name)\n    for folder in (run_dir, derived):\n        for path in folder.rglob('*'):\n            if path.is_file(): z.write(path, 'results/' + str(path.relative_to(RESULTS_ROOT)))\nprint('Export:', archive)\n# Download this ZIP and the executed notebook through Colab when ready.")]
    nb = dict(cells=cells, nbformat=4, nbformat_minor=5, metadata={
        'kernelspec': {'display_name':'Python 3','language':'python','name':'python3'},
        'source_bundle_sha256':sha, 'accelerator':'GPU',
        'colab': {'name':'normative_hysteresis_readiness_colab.ipynb'}})
    path = ROOT/'notebooks/normative_hysteresis_readiness_colab.ipynb'
    path.write_text(json.dumps(nb,indent=1)+'\n'); print(path, sha)


if __name__=='__main__':build()
