#!/usr/bin/env python3
"""Build a self-contained Colab notebook from canonical reviewed source files."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import textwrap
import zlib

ROOT = Path(__file__).resolve().parents[1]


def cell(kind, source, **metadata):
    result = {"cell_type": kind, "metadata": metadata, "source": textwrap.dedent(source).strip() + "\n"}
    result["id"] = hashlib.sha256(result["source"].encode()).hexdigest()[:12]
    if kind == "code":
        result.update(execution_count=None, outputs=[])
    return result


def build():
    files = [*ROOT.glob("corrigibility_bench/*.py"), *ROOT.glob("configs/*.yaml"),
             *ROOT.glob("tests/*.py"), *ROOT.glob("docs/*.md"), ROOT / "README.md", ROOT / "requirements-colab.txt",
             ROOT / "scripts/run_normative_hysteresis.py", ROOT / "scripts/analyze_normative_hysteresis.py",
             ROOT / "scripts/verify_generation_runtime.py"]
    bundle = {str(p.relative_to(ROOT)): p.read_text() for p in sorted(files)}
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    bundle["bundle_provenance.json"] = json.dumps({"git_commit": commit, "git_dirty": dirty,
        "note": "Exact embedded source hashes are the provenance for uncommitted implementation changes."}, indent=2)
    packed = json.dumps(bundle, sort_keys=True).encode()
    encoded = base64.b64encode(zlib.compress(packed, 9)).decode()
    fingerprint = hashlib.sha256(packed).hexdigest()
    chunks = "\n".join(f'    "{encoded[i:i+100]}"' for i in range(0, len(encoded), 100))
    bootstrap = '''
from pathlib import Path
import base64, hashlib, json, os, sys, zlib

# This is a generated, readable-on-extraction snapshot of the repository sources.
# It contains no credentials or weights. Source changes require rebuilding the notebook.
PROJECT_ROOT = (Path("/content") if Path("/content").exists() else Path.cwd()) / "normative-hysteresis-v0-src"
SOURCE_BUNDLE = (
CHUNKS
)
BUNDLE_SHA256 = "FINGERPRINT"
payload = zlib.decompress(base64.b64decode(SOURCE_BUNDLE))
assert hashlib.sha256(payload).hexdigest() == BUNDLE_SHA256, "Source bundle checksum mismatch"
embedded_sources = json.loads(payload)
# Validate all destinations before writing anything; never overwrite edited sources.
for relative, content in embedded_sources.items():
    destination = PROJECT_ROOT / relative
    assert not Path(relative).is_absolute() and ".." not in Path(relative).parts
    if destination.exists() and destination.read_text() != content:
        raise RuntimeError(f"Existing source differs: {destination}. Preserve edits and use a fresh source directory.")
for relative, content in embedded_sources.items():
    destination = PROJECT_ROOT / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        destination.write_text(content)
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
print(f"Extracted {len(embedded_sources)} files to {PROJECT_ROOT}")
print("Source bundle SHA256:", BUNDLE_SHA256)
'''.replace("CHUNKS", chunks).replace("FINGERPRINT", fingerprint)
    cells = [
        cell("markdown", r'''
        # Normative Hysteresis v0 — an exploratory Colab pilot

        **Question:** Does previous public optimization for objective A leave residual influence after
        objective B explicitly replaces it, beyond other-planner reasoning and generic update inertia?

        This direction is worth testing because it separates **accepting an updated objective in words**
        from **acting according to it**, with controls that can undermine the hypothesis. A clear null
        or a generic-priming explanation is a useful result. This is not a benchmark or established
        evidence about corrigibility. Model weights remain fixed throughout; this is inference only.

        The notebook is self-contained. Upload this `.ipynb` alone to Colab. The source, deterministic
        tests, configuration, original protocol, and run handoff are embedded below. **No real model
        results are included.** The synthetic test backend is only for software verification.

        Main conditions: C0 fresh B; C1 own A with factual analysis; C2 own A with public justification;
        C3 reason for another planner assigned A, then receive B. Public-step depths are 0, 1, and 3.
        Four neutral scenarios use canonical semantic choices with two label/order variants.

        Behavior and uptake are generated as independent siblings from the same frozen transcript.
        A correct sibling probe does not prove internal understanding in the behavior branch.
        '''),
        cell("markdown", '''
        ## 1. Start a GPU runtime and extract the source

        In Colab select **Runtime → Change runtime type → GPU**. Default loading uses 4-bit NF4,
        one GPU, batch size one, and a 4,096-token context ceiling. It is intended for a T4-class
        16 GB GPU or larger; actual memory/runtime must be checked on the assigned GPU.
        The backend selects FP16 or BF16 computation according to GPU support.

        Your existing `HF_TOKEN` Colab secret or Hugging Face login is reused. Never paste or print
        your token in the notebook. Public weights may work without authentication.

        The folded cell below extracts a checksum-verified source bundle. You can inspect the
        resulting `.py` files in Colab's Files pane. It refuses to replace files you have edited.
        '''),
        cell("code", bootstrap, cellView="form"),
        cell("markdown", '''
        ## 2. Install the inference and analysis libraries

        Use a fresh runtime. This keeps Colab's CUDA-compatible PyTorch installation. If any listed
        library was already imported and its installed version changes, restart the session and rerun
        from the top. The backend records the exact loaded environment with every run.
        '''),
        cell("code", '''
        import importlib.metadata
        import subprocess
        import sys
        assert sys.version_info >= (3, 10), "The GPU stack requires Python 3.10+"
        tracked = {"transformers": "transformers", "accelerate": "accelerate", "bitsandbytes": "bitsandbytes",
                   "huggingface-hub": "huggingface_hub", "numpy": "numpy", "pandas": "pandas", "matplotlib": "matplotlib"}
        imported_before = {package: getattr(sys.modules[module], "__version__", None)
                           for package, module in tracked.items() if module in sys.modules}
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(PROJECT_ROOT / "requirements-colab.txt")], check=True)
        changed_loaded = [package for package, version in imported_before.items()
                          if version != importlib.metadata.version(package)]
        if changed_loaded:
            raise RuntimeError(f"Restart the Colab session and rerun from the top; loaded packages changed: {changed_loaded}")
        print({package: importlib.metadata.version(package) for package in tracked})
        '''),
        cell("markdown", '''
        ## 3. Run deterministic software checks — no weights required

        These verify mechanical optima, the 432-trial pilot design, prompt matching, counterbalancing,
        sibling isolation, JSON parsing, immutable records, interrupted resumption, the review gate,
        and known-answer contrasts. The synthetic outputs used here are not experimental data.
        '''),
        cell("code", '''
        import unittest
        suite = unittest.defaultTestLoader.discover(str(PROJECT_ROOT / "tests"))
        test_result = unittest.TextTestRunner(verbosity=2).run(suite)
        assert test_result.wasSuccessful() and not test_result.skipped, "All software checks must pass without skips"
        '''),
        cell("markdown", '''
        ## 4. Freeze settings and preview the compute budget

        Set the model revision before the first smoke if you want an explicit Hugging Face commit.
        `main` is resolved to an immutable commit for loading and logging. Resume rejects changed
        source, config, resolved model, quantization, or runtime metadata. Keep one model/precision
        throughout v0. The default backend requires an explicit non-thinking template switch.

        Smoke is greedy: **24 main + 8 factual trajectories = 108 calls including planning**.
        The manually enabled pilot is temperature 0.7: **288 main + 144 factual trajectories =
        1,440 calls including planning**. The pilot adds no automatic extra replications.
        '''),
        cell("code", '''
        from corrigibility_bench.normative_hysteresis import call_budget, trial_grid, Trial, C2, initial_history, planning_prompts, transition
        from corrigibility_bench.runner import load_config

        config = load_config()
        MODEL_ID = "Qwen/Qwen3-8B"  # @param {type:"string"}
        MODEL_REVISION = "main"  # @param {type:"string"}
        QUANTIZATION = "nf4"  # @param ["nf4", "none"]
        config.update(model_id=MODEL_ID, model_revision=MODEL_REVISION, quantization=QUANTIZATION)
        SMOKE_ID = "smoke-001"  # @param {type:"string"}
        PILOT_ID = "pilot-001"  # @param {type:"string"}
        print("Smoke:", call_budget(trial_grid("smoke", config["seed"])))
        print("Pilot:", call_budget(trial_grid("pilot", config["seed"])))
        example = Trial("shipping", C2, 3, 0)
        print("\\nExample static stimuli (no model outputs):")
        print(initial_history(example)[-1]["content"])
        print(*planning_prompts(example), sep="\\n")
        print(transition(example))
        '''),
        cell("markdown", '''
        ## 5. Select durable output storage

        Drive is recommended so completed calls survive runtime disconnects. The model cache stays
        on the Colab runtime disk. If you opt out of Drive, download the export ZIP before ending the
        runtime. Reuse the same run ID to resume; use a new ID for a separate experiment.
        '''),
        cell("code", '''
        USE_GOOGLE_DRIVE = True  # @param {type:"boolean"}
        if USE_GOOGLE_DRIVE:
            from google.colab import drive
            drive.mount("/content/drive")
            RESULTS_ROOT = Path("/content/drive/MyDrive/normative-hysteresis-v0/results")
        else:
            RESULTS_ROOT = PROJECT_ROOT / "results"
        RESULTS_ROOT.mkdir(parents=True, exist_ok=True)
        print("Results:", RESULTS_ROOT)
        '''),
        cell("markdown", '''
        ## 6. Load the Hugging Face model

        This cell downloads weights on the first run and uses the existing HF token without displaying
        it. It never trains or uploads the model. Non-thinking mode uses `enable_thinking=False` as
        documented in the [Qwen3-8B model card](https://huggingface.co/Qwen/Qwen3-8B).
        Quantization follows [Hugging Face's bitsandbytes integration](https://huggingface.co/docs/transformers/quantization/bitsandbytes).

        If GPU memory runs out, preserve the error and start a fresh runtime using the NF4 default.
        Do not switch precision or shrink token ceilings midway through an experiment.
        '''),
        cell("code", '''
        import gc
        import torch
        from corrigibility_bench.hf_backend import HFBackend
        if "backend" in globals():
            del backend
            gc.collect()
            torch.cuda.empty_cache()
        backend = HFBackend(config)
        print(json.dumps(backend.metadata, indent=2))  # No credentials in metadata
        '''),
        cell("markdown", '''
        ## 7. Run only the smoke experiment

        Each public artifact and each sibling response is saved immediately as its own JSON record.
        Full prompts, rendered prompt hashes, frozen histories, seeds, model revision, token counts,
        timing, parse errors, and truncation flags are retained. No malformed response is silently
        regenerated. Completion here means the code finished, not that scientific smoke review passed.

        After an abrupt disconnect, an empty `.runner-lock` directory may remain in the run folder.
        Confirm the old runner is stopped before removing that lock and resuming. Unreadable partial
        raw files must be preserved; start a new run rather than overwriting them.
        '''),
        cell("code", '''
        from corrigibility_bench.runner import run_experiment
        smoke_run = run_experiment(backend, config, mode="smoke", results_root=RESULTS_ROOT, experiment_id=SMOKE_ID)
        print("Smoke raw outputs:", smoke_run)
        '''),
        cell("markdown", r'''
        ## 8. Generate descriptive artifacts and inspect every smoke transcript

        The first output is the raw contingency table, followed by per-scenario and aggregate rates.
        Open the HTML transcript report and inspect all 32 trajectories before interpreting summaries.

        [
        RAR=I(	ext{old-optimal choice AND correct sibling uptake}),quad
        NH=C2-C0,quad FH=F_{	ext{self}}-F_{	ext{fresh}}.
        ]

        Ownership is C2−C3; justification is C2−C1; specificity is NH−FH. Invalid JSON remains in
        the denominator; validity rates and `RAR_upper` expose unresolved outcomes. No significance
        tests run. Two smoke clusters are insufficient for bootstrap intervals, and smoke has no
        factual k=1 cell. The plots show the actual depth curve without enforcing monotonicity.
        '''),
        cell("code", '''
        from corrigibility_bench.analysis import analyze_run
        from IPython.display import display, Image, HTML
        smoke_derived = analyze_run(smoke_run, n_boot=config["bootstrap_samples"])
        display(Image(filename=str(smoke_derived / "curves.png")))
        display(HTML((smoke_derived / "transcript_audit.html").read_text()))
        print("Edit the human review file:", smoke_derived / "smoke_review.json")
        print("Read research interpretation notes:", PROJECT_ROOT / "docs/RESEARCH_NOTES.md")
        '''),
        cell("markdown", '''
        ## 9. Human smoke review — deliberate stopping point

        Your protocol requires a human to inspect every raw smoke transcript before scaling. Edit
        the generated `smoke_review.json`: enter the reviewer's name, add a note for every trajectory,
        mark each reviewed, and set `task_comprehension_acceptable` and `approve_pilot` to true only
        if the human reviewer judges scaling appropriate. Preserve its digest and experiment ID.
        An agent should not fill this out as if a human inspected the transcripts.

        Leave `REVIEW_FILE` empty until review is complete. The next cell then does nothing. Approval
        is tied to the exact raw data, config, source, resolved model, and runtime. Prompt changes
        require a new smoke and review. No automatic threshold decides task comprehension for you.
        '''),
        cell("code", '''
        from corrigibility_bench.runner import approve_smoke
        REVIEW_FILE = ""  # @param {type:"string"}
        if REVIEW_FILE.strip():
            approve_smoke(smoke_run, Path(REVIEW_FILE))
            print("Recorded human review approval:", smoke_run / "review_approval.json")
        else:
            print("Pilot remains gated. Complete the human transcript review before setting REVIEW_FILE.")
        '''),
        cell("markdown", '''
        ## 10. Optional v0 pilot — off by default

        The pilot requires the saved human approval. Enabling the switch runs only the frozen v0
        grid, with no automatic expansion. The four scenario families and two variants provide only
        limited generalization; bootstrap intervals are descriptive, with just eight scenario/variant
        clusters. Generated histories have matched turns and word ceilings, not exact content or
        token matching. Inspect length diagnostics and useful-fact reuse before attributing an effect
        to objective ownership.
        '''),
        cell("code", '''
        RUN_PILOT = False  # @param {type:"boolean"}
        pilot_run = None
        if RUN_PILOT:
            pilot_run = run_experiment(backend, config, mode="pilot", results_root=RESULTS_ROOT,
                                       experiment_id=PILOT_ID, smoke_run=smoke_run)
        else:
            print("Pilot not requested; no pilot inference calls made.")
        '''),
        cell("code", '''
        if pilot_run is not None:
            pilot_derived = analyze_run(pilot_run, n_boot=config["bootstrap_samples"])
            display(Image(filename=str(pilot_derived / "curves.png")))
            print("Audit every selected trajectory before interpreting aggregates:", pilot_derived / "transcript_audit.html")
            print("Record manual annotations:", pilot_derived / "audit_annotations.json")
        '''),
        cell("markdown", '''
        ## 11. Export and preserve the handoff

        This ZIP includes the selected raw runs, their derived artifacts, and the exact source bundle.
        It excludes weights, HF tokens, and caches. Save an executed copy of this notebook too.
        If using Drive, the archive remains there; set the download switch to also download it.
        '''),
        cell("code", '''
        from datetime import datetime, timezone
        import uuid, zipfile
        export_dir = RESULTS_ROOT / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        archive = export_dir / ("nh-v0-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6] + ".zip")
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as zipped:
            for relative in embedded_sources:
                zipped.write(PROJECT_ROOT / relative, "source/" + relative)
            selected_runs = [smoke_run] + ([pilot_run] if pilot_run is not None else [])
            for run in selected_runs:
                for tree in (run, RESULTS_ROOT / "derived/normative_hysteresis" / run.name):
                    if tree.exists():
                        for file in sorted(tree.rglob("*")):
                            if file.is_file():
                                zipped.write(file, "results/" + str(file.relative_to(RESULTS_ROOT)))
        print("Export:", archive)
        DOWNLOAD_ARCHIVE = False  # @param {type:"boolean"}
        if DOWNLOAD_ARCHIVE:
            from google.colab import files
            files.download(str(archive))
        '''),
        cell("markdown", '''
        ## How to decide whether this direction deserves another experiment

        Inspect all old-option choices, incorrect uptake, malformed responses, truncations, and at
        least ten randomly selected correct-final-choice pilot trials. Record artifacts; never silently
        exclude them. Compare each scenario and variant before drawing an aggregate conclusion.

        Demote the objective-specific explanation if C2≈C3, objective effects resemble factual
        inertia, uptake failures explain the observation, order changes remove it, one scenario drives
        it, or depth adds no consistent effect. A null can be a reason to stop. A promising pattern
        should be replicated with another model before mechanistic work.

        The strongest appropriate v0 claim is narrowly about residual influence under these synthetic
        conditions relative to the matched controls. It does not establish scheming, self-preservation,
        mechanistic entrenchment, or a general corrigibility failure. See the embedded
        `docs/RESEARCH_NOTES.md`, `docs/RUN_HANDOFF.md`, and original protocol for the full handoff.
        '''),
    ]
    notebook = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"}, "accelerator": "GPU",
        "colab": {"name": "normative_hysteresis_v0_colab.ipynb", "provenance": [], "toc_visible": True},
        "source_bundle_sha256": fingerprint}, "nbformat": 4, "nbformat_minor": 5}
    destination = ROOT / "notebooks/normative_hysteresis_v0_colab.ipynb"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
    print(f"Built {destination} ({len(cells)} cells; {len(bundle)} bundled files)")


if __name__ == "__main__":
    build()
