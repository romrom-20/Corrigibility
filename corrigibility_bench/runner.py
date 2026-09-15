"""Immutable per-call records, resumable trajectories, and a smoke-review gate."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import uuid

from .normative_hysteresis import (
    VERSION, Trial, append_request, banned_terms, branch_contexts, call_budget, canonical_json,
    derived_seed, digest, freeze_history, initial_history, parse_response, planning_prompts,
    trial_grid, truth,
)

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_METADATA = {
    "experiment_id", "experiment_version", "scenario_id", "condition", "investment_depth",
    "order_variant", "replication", "trajectory_id", "branch", "model_id", "model_revision",
    "backend", "temperature", "seed", "generation_config", "prompt_hash", "history_hash",
    "git_commit", "timestamp", "raw_text", "parsed",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_config(path=None) -> dict:
    # JSON is a valid YAML subset. Keep configuration readable without adding a YAML runtime dependency.
    config = json.loads(Path(path or ROOT / "configs/normative_hysteresis_v0.yaml").read_text())
    if config["experiment_version"] != VERSION:
        raise ValueError("Unsupported experiment version")
    return config


def source_snapshot() -> dict:
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "corrigibility_bench").glob("*.py"))}


def git_state() -> dict:
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
        return {"git_commit": commit, "git_dirty": dirty}
    except (subprocess.CalledProcessError, FileNotFoundError):
        embedded = ROOT / "bundle_provenance.json"
        provenance = json.loads(embedded.read_text()) if embedded.exists() else {}
        return {"git_commit": provenance.get("git_commit", "unavailable"),
                "git_dirty": provenance.get("git_dirty", True), "source": "embedded_notebook"}


def write_new_json(path: Path, value: dict):
    """Exclusive creation: existing raw outputs, manifests and approvals are never replaced."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as file:
        file.write(canonical_json(value) + "\n")
        file.flush()
        os.fsync(file.fileno())


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (ValueError, OSError) as exc:
        raise RuntimeError(f"Unreadable record {path}; preserve it and start a new run, do not silently regenerate") from exc


def raw_digest(run_dir: Path) -> str:
    return digest({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((run_dir / "records").glob("*.json"))})


def generation_settings(config: dict, mode: str, branch: str) -> dict:
    temperature = config[f"{mode}_temperature"]
    settings = {"max_new_tokens": config[f"max_new_tokens_{branch}"], "do_sample": temperature > 0,
                "num_beams": 1, "repetition_penalty": 1.0}
    if temperature > 0:
        settings.update(temperature=temperature, top_p=config["top_p"], top_k=config["top_k"], min_p=0.0)
    return settings


def review_template(run_dir: Path) -> dict:
    manifest = read_json(run_dir / "manifest.json")
    if not (run_dir / "complete.json").exists():
        raise ValueError("Finish smoke before reviewing")
    return {"smoke_experiment_id": manifest["experiment_id"], "raw_digest": raw_digest(run_dir),
            "reviewer": "", "task_comprehension_acceptable": False,
            "approve_pilot": False,
            "trajectories": {t["trajectory_id"]: {"reviewed": False, "notes": ""} for t in manifest["trials"]}}


def validate_review(smoke_dir: Path, review: dict, config: dict, backend_metadata: dict):
    manifest = read_json(smoke_dir / "manifest.json")
    completion = read_json(smoke_dir / "complete.json")
    ids = {t["trajectory_id"] for t in manifest["trials"]}
    annotations = review.get("trajectories", {})
    if manifest["mode"] != "smoke" or manifest["config"] != config:
        raise ValueError("Review must cover a smoke run with the same configuration")
    if manifest["sources"] != source_snapshot() or manifest["model"] != backend_metadata:
        raise ValueError("Source/model/runtime changed since smoke; rerun smoke and review")
    fingerprint = raw_digest(smoke_dir)
    if (review.get("smoke_experiment_id") != manifest["experiment_id"] or
            review.get("raw_digest") != fingerprint or completion["raw_digest"] != fingerprint):
        raise ValueError("Review does not match these immutable smoke outputs")
    if not (review.get("approve_pilot") is True and review.get("task_comprehension_acceptable") is True
            and isinstance(review.get("reviewer"), str) and review["reviewer"].strip()):
        raise ValueError("A named human reviewer must approve comprehension and scaling")
    if not isinstance(annotations, dict) or set(annotations) != ids or not all(isinstance(item, dict)
                                        and item.get("reviewed") is True and isinstance(item.get("notes"), str) and item["notes"].strip()
                                        for item in annotations.values()):
        raise ValueError("Every smoke trajectory needs a review and a note, including all planning artifacts")


def approve_smoke(smoke_dir: Path, review_path: Path):
    """Validate a completed human-authored review and save its immutable approval record."""
    smoke_dir = Path(smoke_dir)
    manifest = read_json(smoke_dir / "manifest.json")
    review = read_json(Path(review_path))
    validate_review(smoke_dir, review, manifest["config"], manifest["model"])
    write_new_json(smoke_dir / "review_approval.json", {**review, "approved_at": now()})


def run_experiment(backend, config: dict, mode="smoke", results_root="results", experiment_id=None,
                   smoke_run=None, progress=print) -> Path:
    if config.get("experiment_version") != VERSION:
        raise ValueError("Configuration protocol version differs from loaded experiment source")
    trials = trial_grid(mode, config["seed"])
    results_root = Path(results_root).expanduser().resolve()
    experiment_id = experiment_id or f"{mode}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}"
    if not re.fullmatch(r"[A-Za-z0-9_-]+", experiment_id):
        raise ValueError("experiment_id must contain only letters, digits, underscores, or hyphens")
    review = None
    if mode == "pilot":
        if smoke_run is None:
            raise ValueError("Pilot requires a completed and approved smoke run")
        smoke_run = Path(smoke_run)
        review = read_json(smoke_run / "review_approval.json")
        validate_review(smoke_run, review, config, backend.metadata)
    run_dir = results_root / "raw" / "normative_hysteresis" / experiment_id
    spec = {
        "experiment_id": experiment_id, "experiment_version": VERSION, "mode": mode,
        "config": config, "model": backend.metadata, "sources": source_snapshot(),
        "trials": [{**asdict(t), "trajectory_id": t.trajectory_id, "family": t.family, **truth(t)} for t in trials],
        "call_budget": call_budget(trials), "review_approval": review,
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    lock = run_dir / ".runner-lock"
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise RuntimeError(f"Run is locked: {lock}. If a Colab disconnect killed the runner, verify it is stopped before removing this directory.") from exc
    try:
        manifest_path = run_dir / "manifest.json"
        if manifest_path.exists():
            manifest = read_json(manifest_path)
            if any(manifest.get(key) != value for key, value in spec.items()):
                raise ValueError("Resume settings/source/model differ from the saved manifest; start a new experiment ID")
        else:
            manifest = {**spec, "created_at": now(), **git_state()}
            write_new_json(manifest_path, manifest)
        if (run_dir / "complete.json").exists():
            if read_json(run_dir / "complete.json")["raw_digest"] != raw_digest(run_dir):
                raise ValueError("Completed run has changed")
            progress(f"Already complete: {run_dir}")
            return run_dir

        def generate_or_resume(trial, branch, messages, history, step=None):
            label = f"planning-{step}" if branch == "planning" else branch
            path = run_dir / "records" / f"{trial.trajectory_id}--{label}.json"
            seed = derived_seed(config["seed"], trial.trajectory_id, label)
            settings = generation_settings(config, mode, branch)
            expected = {"prompt_hash": digest(messages), "history_hash": digest(history),
                        "seed": seed, "requested_generation_config": settings}
            leaked = banned_terms(messages)
            if leaked:
                raise ValueError(f"Forbidden vocabulary in model input: {leaked}. Preserve records and audit this incomplete run.")
            if path.exists():
                record = read_json(path)
                if not REQUIRED_METADATA <= record.keys() or any(record.get(k) != v for k, v in expected.items()):
                    raise ValueError(f"Resume record mismatch: {path}")
                return record
            generated = backend.generate(messages, seed, settings)
            raw = generated.raw_text
            parsed = parse_response(raw, branch, trial)
            record = {
                **asdict(trial), "family": trial.family, "trajectory_id": trial.trajectory_id,
                "experiment_id": experiment_id, "experiment_version": VERSION,
                "branch": branch, "planning_step": step, **backend.metadata,
                "temperature": config[f"{mode}_temperature"], **expected,
                "generation_config": generated.generation_config, "timestamp": now(),
                "git_commit": manifest["git_commit"], "git_dirty": manifest["git_dirty"],
                "raw_text": raw, "parsed": parsed, "messages": messages, "frozen_history": history,
                "rendered_prompt": generated.rendered_prompt,
                "rendered_prompt_hash": digest(generated.rendered_prompt),
                "input_tokens": generated.input_tokens, "output_tokens": generated.output_tokens,
                "truncated": generated.truncated, "elapsed_seconds": generated.elapsed_seconds,
                "output_banned_terms": banned_terms([{"content": raw}]), **truth(trial),
            }
            if not REQUIRED_METADATA <= record.keys():
                raise AssertionError("Missing record metadata")
            write_new_json(path, record)
            return record

        for index, trial in enumerate(trials):
            artifacts = []
            history = initial_history(trial)
            for step, prompt in enumerate(planning_prompts(trial), start=1):
                messages = append_request(history, prompt)
                rec = generate_or_resume(trial, "planning", messages, history, step)
                artifacts.append(rec["raw_text"])
                history = messages + [{"role": "assistant", "content": rec["raw_text"]}]
            frozen = freeze_history(trial, artifacts)
            branches = branch_contexts(trial, frozen)
            # Both contexts are constructed before either sibling is generated.
            for branch in ("behavior", "uptake"):
                generate_or_resume(trial, branch, branches[branch], frozen)
            progress(f"{index + 1}/{len(trials)}: {trial.scenario_id} {trial.condition} k={trial.investment_depth} variant={trial.order_variant} rep={trial.replication}")
        expected_calls = call_budget(trials)["total_calls"]
        if len(list((run_dir / "records").glob("*.json"))) != expected_calls:
            raise ValueError("Raw record count does not match the frozen design")
        write_new_json(run_dir / "complete.json", {"completed_at": now(), "raw_digest": raw_digest(run_dir), "calls": expected_calls})
        return run_dir
    finally:
        lock.rmdir()
