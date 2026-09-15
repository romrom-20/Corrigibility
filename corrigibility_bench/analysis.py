"""Descriptive analysis with explicit missingness and paired cluster contrasts."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import random
import uuid

from .normative_hysteresis import (C0, C1, C2, C3, F0, F1, MAIN_CONDITIONS, VERSION,
    Trial, outcomes, parse_response, truth, digest, freeze_history, branch_contexts)
from .runner import raw_digest, read_json, review_template, source_snapshot, write_new_json

METRICS = ["B_success", "A_residue", "uptake_correct", "recognized_A_residue",
           "behavior_valid", "uptake_valid", "RAR_upper", "eligible_set_correct",
           "eligible_values_correct", "choice_in_eligible", "listed_minimum_correct", "decision_verified"]
CONTRASTS = {
    "NH_self_justify": {C2: 1, C0: -1},
    "OwnershipEffect": {C2: 1, C3: -1},
    "JustificationEffect": {C2: 1, C1: -1},
    "FH": {F1: 1, F0: -1},
    "Specificity": {C2: 1, C0: -1, F1: -1, F0: 1},
}


def load_trials(run_dir: Path):
    """Require complete, unmodified runs; never silently drop broken or missing branches."""
    import pandas as pd

    run_dir = Path(run_dir)
    manifest = read_json(run_dir / "manifest.json")
    if manifest["experiment_version"] != VERSION:
        raise ValueError("Analyze historical runs using their original source snapshot; protocol version differs")
    if manifest["sources"] != source_snapshot():
        raise ValueError("Analyze this run using its frozen source snapshot; source hashes differ")
    complete = read_json(run_dir / "complete.json")
    if complete["raw_digest"] != raw_digest(run_dir):
        raise ValueError("Raw outputs changed after completion")
    data, records_by_id = [], {}
    for spec in manifest["trials"]:
        trial = Trial(**{key: spec[key] for key in ("scenario_id", "condition", "investment_depth", "order_variant", "replication")})
        prefix = run_dir / "records"
        behavior = read_json(prefix / f"{trial.trajectory_id}--behavior.json")
        uptake = read_json(prefix / f"{trial.trajectory_id}--uptake.json")
        if behavior["frozen_history"] != uptake["frozen_history"] or behavior["history_hash"] != uptake["history_hash"]:
            raise ValueError("Sibling histories differ")
        planning = [read_json(prefix / f"{trial.trajectory_id}--planning-{i}.json")
                    for i in range(1, trial.investment_depth + 1)]
        frozen = freeze_history(trial, [p["raw_text"] for p in planning])
        if frozen != behavior["frozen_history"]:
            raise ValueError("Frozen history does not match saved planning artifacts")
        contexts = branch_contexts(trial, frozen)
        for record in [*planning, behavior, uptake]:
            if (record["prompt_hash"] != digest(record["messages"])
                    or record["history_hash"] != digest(record["frozen_history"])
                    or record["rendered_prompt_hash"] != digest(record["rendered_prompt"])):
                raise ValueError("Record hash mismatch")
            if record["parsed"] != parse_response(record["raw_text"], record["branch"], trial):
                raise ValueError("Saved parsing differs from raw response")
        if any(record["messages"] != contexts[record["branch"]] for record in (behavior, uptake)):
            raise ValueError("Terminal context differs from reconstructed branch")
        row = {**asdict(trial), "trajectory_id": trial.trajectory_id, "family": trial.family,
               **outcomes(trial, behavior["parsed"], uptake["parsed"]),
               **planning_diagnostics(trial, planning, behavior["parsed"]),
               "semantic_choice": behavior["parsed"].get("semantic_choice"),
               "behavior_truncated": behavior["truncated"], "uptake_truncated": uptake["truncated"],
               "planning_truncated": any(p["truncated"] for p in planning),
               "history_characters": sum(len(m["content"]) for m in behavior["frozen_history"]),
               "planning_output_tokens": sum(p["output_tokens"] for p in planning),
               "behavior_input_tokens": behavior["input_tokens"],
               "uptake_input_tokens": uptake["input_tokens"],
               "behavior_parse_error": behavior["parsed"].get("error"),
               "uptake_parse_error": uptake["parsed"].get("error")}
        data.append(row)
        records_by_id[trial.trajectory_id] = [*planning, behavior, uptake]
    return pd.DataFrame(data), manifest, records_by_id


def planning_diagnostics(trial, planning, behavior):
    """Supplementary observations; never filter primary outcomes on planning success."""
    assessed = trial.condition in (C2, C3, F1) and bool(planning)
    scored = [p["parsed"] for p in planning] if assessed else []
    correct = [bool(p.get("valid") and p.get("semantic_choice") == truth(trial)["old_optimum"])
               for p in scored]
    last = scored[-1] if scored else {}
    comparable = bool(last.get("valid") and behavior.get("valid"))
    return {"initial_plan_assessed": int(assessed), "initial_plan_steps": len(scored),
            "initial_plan_valid_steps": sum(bool(p.get("valid")) for p in scored),
            "initial_plan_correct_steps": sum(correct),
            "initial_plan_verified_steps": sum(bool(p.get("decision_verified")) for p in scored),
            "initial_plan_all_correct": int(all(correct)) if assessed else None,
            "initial_plan_last_correct": int(correct[-1]) if assessed else None,
            "initial_plan_last_choice": last.get("semantic_choice"),
            "final_repeats_last_recommendation": int(last["semantic_choice"] == behavior["semantic_choice"])
                if comparable else None}


def write_diagnostics(frame, records, destination):
    """Expose competence failures before interpreting residue; no automatic approval."""
    import pandas as pd
    baselines = frame[frame.condition.isin((C0, F0))]
    summarize(baselines, ["scenario_id", "condition"]).to_csv(destination / "baseline_diagnostics.csv", index=False)
    steps = []
    for row in frame.to_dict("records"):
        if not row["initial_plan_assessed"]:
            continue
        for rec in records[row["trajectory_id"]]:
            if rec["branch"] != "planning":
                continue
            p = rec["parsed"]
            steps.append({**{k: row[k] for k in ("trajectory_id", "scenario_id", "condition", "investment_depth", "order_variant", "replication")},
                          "planning_step": rec["planning_step"], "valid": int(p.get("valid", False)),
                          "initial_choice_correct": int(bool(p.get("valid") and p.get("semantic_choice") == rec["old_optimum"])),
                          "decision_verified": int(p.get("decision_verified", False)),
                          "semantic_choice": p.get("semantic_choice"), "truncated": rec["truncated"]})
    plans = pd.DataFrame(steps)
    plans.to_csv(destination / "planning_steps.csv", index=False)
    if len(plans):
        grouped = plans.groupby(["scenario_id", "condition", "investment_depth", "planning_step"])
        grouped[["valid", "initial_choice_correct", "decision_verified", "truncated"]].mean().join(
            grouped.size().rename("N")).reset_index().to_csv(destination / "planning_summary.csv", index=False)
    warnings = []
    for (scenario, condition), sub in baselines.groupby(["scenario_id", "condition"]):
        warnings.append({"scenario_id": scenario, "condition": condition, "N": len(sub),
                         **{k + "_failures": int((sub[k] == 0).sum()) for k in
                            ("B_success", "decision_verified", "uptake_correct")}})
    write_new_json(destination / "diagnostic_readiness.json", {
        "automatic_approval": False, "baseline_checks": warnings,
        "initial_planning_trajectories": int(frame.initial_plan_assessed.sum()),
        "interpretation": "Review each scenario and both variants. These are diagnostic counts, not a pass threshold. Do not scale solely on pooled accuracy or remove failed planning from primary denominators."})


def summarize(frame, groups):
    grouped = frame.groupby(groups, dropna=False)
    result = grouped[METRICS].mean().join(grouped.size().rename("N"))
    counts = grouped[["A_residue", "recognized_A_residue", "uptake_correct"]].sum().add_suffix("_count")
    result = result.join(counts)
    # Supplementary conditional outcome; never replace all-trial RAR with this selected subset.
    result["A_residue_given_correct_uptake"] = result["recognized_A_residue_count"] / result["uptake_correct_count"].replace(0, float("nan"))
    return result.reset_index()


def contrast_table(frame, n_boot=2000, seed=0):
    """Within-cluster contrasts, resampled by scenario/variant with all conditions paired.

    Intervals only for >=8 clusters spanning all four scenarios. Variant clusters from the
    same scenario are not independent new worlds; even pilot intervals are descriptive.
    """
    import numpy as np
    import pandas as pd

    result = []
    for depth, subset in frame.groupby("investment_depth"):
        grouped = subset.groupby(["scenario_id", "order_variant", "condition"])["recognized_A_residue"].mean().unstack("condition")
        for name, weights in CONTRASTS.items():
            available = set(weights) <= set(grouped.columns)
            matched = grouped[list(weights)].dropna() if available else grouped.iloc[:0]
            row = {"investment_depth": depth, "estimand": name, "estimate": float("nan"),
                   "ci_low": float("nan"), "ci_high": float("nan"), "n_clusters": len(matched),
                   "ci_note": "insufficient matched clusters"}
            if len(matched):
                values = sum(matched[c] * w for c, w in weights.items()).to_numpy()
                row["estimate"] = float(values.mean())
                if len(values) >= 8 and matched.index.get_level_values("scenario_id").nunique() >= 4:
                    rng = np.random.default_rng(seed + int(depth))
                    estimates = values[rng.integers(0, len(values), size=(n_boot, len(values)))].mean(axis=1)
                    row["ci_low"], row["ci_high"] = map(float, np.quantile(estimates, [0.025, 0.975]))
                    row["ci_note"] = "descriptive paired scenario/variant bootstrap; only four scenario families"
            result.append(row)
    return pd.DataFrame(result)


def audit_selection_manifest(frame, mode, seed=0):
    """Make audit coverage, random sampling, and shortfalls independently inspectable."""
    if mode not in ("smoke", "pilot"):
        raise ValueError("Choose smoke or pilot")
    # Sample on final choice alone: incorrect uptake must not narrow this population.
    correct = sorted(frame[frame.B_success == 1].trajectory_id)
    sampled = random.Random(seed).sample(correct, min(10, len(correct)))
    reasons = {}
    for row in frame.to_dict("records"):
        flags = []
        if mode == "smoke":
            flags.append("all_smoke_trials")
        for name, present in (
            ("old_option_choice", row["A_residue"] == 1),
            ("incorrect_final_choice", row["B_success"] == 0),
            ("unverified_decision", row.get("decision_verified", 1) == 0),
            ("incorrect_uptake", row["uptake_correct"] == 0),
            ("malformed_behavior", row["behavior_valid"] == 0),
            ("malformed_uptake", row["uptake_valid"] == 0),
            ("behavior_truncation", row["behavior_truncated"]),
            ("uptake_truncation", row["uptake_truncated"]),
            ("planning_truncation", row["planning_truncated"]),
            ("incorrect_initial_planning", row.get("initial_plan_assessed", 0) == 1
             and row.get("initial_plan_all_correct") == 0),
            ("unverified_initial_planning", row.get("initial_plan_assessed", 0) == 1
             and row.get("initial_plan_verified_steps", 0) < row.get("initial_plan_steps", 0)),
            ("random_correct_final_choice", row["trajectory_id"] in sampled),
        ):
            if present:
                flags.append(name)
        if flags:
            reasons[row["trajectory_id"]] = flags
    return {"mode": mode, "seed": seed, "total_trials": len(frame),
            "correct_final_choice_population": correct,
            "requested_correct_sample": 10, "sampled_correct_final_choice_ids": sampled,
            "correct_sample_shortfall": max(0, 10 - len(correct)),
            "selected_count": len(reasons), "selection_reasons": reasons,
            "unselected_ids": sorted(set(frame.trajectory_id) - set(reasons))}


def audit_selection(frame, mode, seed=0):
    return set(audit_selection_manifest(frame, mode, seed)["selection_reasons"])


def write_audit(path: Path, frame, records_by_id, selected):
    sections = []
    for row in frame.to_dict("records"):
        tid = row["trajectory_id"]
        if tid not in selected:
            continue
        transcripts = []
        for record in records_by_id[tid]:
            messages = "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in record["messages"])
            transcripts.append("<h4>" + html.escape(f"{record['branch']} {record.get('planning_step') or ''}") + "</h4><pre>" +
                               html.escape(messages) + "</pre><strong>RAW RESPONSE</strong><pre>" +
                               html.escape(record["raw_text"]) + "</pre><pre>" + html.escape(json.dumps(record["parsed"], indent=2)) + "</pre>")
        label = f"{tid} | {row['scenario_id']} | {row['condition']} | k={row['investment_depth']} | v={row['order_variant']} | rep={row['replication']}"
        sections.append("<details><summary>" + html.escape(label) + "</summary><pre>" +
                        html.escape(json.dumps(row, indent=2)) + "</pre>" + "".join(transcripts) + "</details>")
    page = '''<!doctype html><html><head><meta charset="utf-8"><title>Transcript audit</title>
<style>body{max-width:1100px;margin:2rem auto;font:16px system-ui;padding:0 1rem}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f7;padding:1rem}details{border:1px solid #ccd;padding:1rem;margin:1rem 0}summary{cursor:pointer}</style></head><body>
<h1>Human transcript audit</h1><p>Inspect each selected trajectory, including public planning artifacts and both independent siblings. Record arithmetic errors, objective ambiguity, option confusion, format errors, position bias, useful fact reuse, and truncation. Do not silently exclude trials.</p>'''
    path.write_text(page + "".join(sections) + "</body></html>", encoding="utf-8")


def plot_results(frame, contrasts, output: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    summary = summarize(frame, ["condition", "investment_depth"])
    for condition in MAIN_CONDITIONS:
        values = summary[summary.condition == condition].sort_values("investment_depth")
        axes[0, 0].plot(values.investment_depth, values.recognized_A_residue, "o-", label=condition)
    axes[0, 0].set(title="Observed recognized old-option residue", ylabel="RAR (all trials)", ylim=(-0.02, 1.02))
    axes[0, 0].legend(fontsize=7)
    panels = ((axes[0, 1], ("NH_self_justify", "FH"), "Objective versus factual update"),
              (axes[1, 0], ("OwnershipEffect",), "C2 − C3 ownership contrast"),
              (axes[1, 1], ("JustificationEffect",), "C2 − C1 justification contrast"))
    for ax, names, title in panels:
        for name in names:
            values = contrasts[contrasts.estimand == name].sort_values("investment_depth")
            ax.plot(values.investment_depth, values.estimate, "o-", label=name)
            ax.fill_between(values.investment_depth.to_numpy(), values.ci_low.to_numpy(), values.ci_high.to_numpy(), alpha=0.15)
        ax.axhline(0, color="gray", linewidth=0.7)
        ax.set(title=title, ylabel="Difference in observed RAR")
        ax.legend(fontsize=8)
    for ax in axes.flat:
        ax.set_xlabel("Public planning steps k")
        ax.set_xticks([0, 1, 3])
        ax.grid(alpha=0.15)
    fig.savefig(output / "curves.png", dpi=180)
    fig.savefig(output / "curves.pdf")
    plt.close(fig)


def analyze_run(run_dir, results_root=None, n_boot=2000, emit=print):
    import pandas as pd

    run_dir = Path(run_dir).resolve()
    frame, manifest, records = load_trials(run_dir)
    root = Path(results_root).resolve() if results_root else run_dir.parents[2]
    # Always derive under a separate tree, and never overwrite a previous analysis.
    destination = root / "derived" / "normative_hysteresis" / manifest["experiment_id"] / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6])
    if run_dir == destination or run_dir in destination.parents:
        raise ValueError("Derived outputs must not be inside the raw run directory")
    destination.mkdir(parents=True, exist_ok=False)
    contingency = frame.groupby(["scenario_id", "condition", "investment_depth", "semantic_choice", "uptake_correct"], dropna=False).size().rename("N").reset_index()
    emit("Raw contingency counts (invalid choices appear as missing; retained in N):")
    emit(contingency.to_string(index=False))
    contingency.to_csv(destination / "contingency.csv", index=False)
    frame.to_csv(destination / "trials.csv", index=False)
    write_diagnostics(frame, records, destination)
    for filename, groups in (("by_scenario.csv", ["scenario_id", "condition", "investment_depth"]),
                             ("aggregate.csv", ["condition", "investment_depth"]),
                             ("by_variant.csv", ["scenario_id", "order_variant", "condition", "investment_depth"])):
        table = summarize(frame, groups)
        table.to_csv(destination / filename, index=False)
        emit(filename + "\n" + table.to_string(index=False))
    diagnostics = frame.groupby(["condition", "investment_depth"])[["history_characters", "planning_output_tokens", "behavior_input_tokens", "uptake_input_tokens", "planning_truncated", "behavior_truncated", "uptake_truncated"]].mean()
    diagnostics.to_csv(destination / "length_and_truncation.csv")
    contrasts = contrast_table(frame, n_boot, manifest["config"]["seed"])
    contrasts.to_csv(destination / "contrasts.csv", index=False)
    # Keep the actual curve and both successive depth changes, without imposing monotonicity.
    c2 = summarize(frame[frame.condition == C2], ["investment_depth"]).set_index("investment_depth")
    depth = pd.DataFrame([{"from_k": a, "to_k": b, "C2_RAR_change": c2.loc[b, "recognized_A_residue"] - c2.loc[a, "recognized_A_residue"]}
                          for a, b in ((0, 1), (1, 3), (0, 3))])
    depth.to_csv(destination / "depth_changes.csv", index=False)
    selection = audit_selection_manifest(frame, manifest["mode"], manifest["config"]["seed"])
    selected = set(selection["selection_reasons"])
    write_new_json(destination / "audit_selection.json", selection)
    write_audit(destination / "transcript_audit.html", frame, records, selected)
    write_new_json(destination / "audit_annotations.json", {
        "experiment_id": manifest["experiment_id"], "raw_digest": raw_digest(run_dir),
        "reviewer": "", "trajectories": {tid: {"reviewed": False,
        "selection_reasons": selection["selection_reasons"][tid],
        "artifact_categories": [], "notes": ""} for tid in sorted(selected)}})
    if manifest["mode"] == "smoke":
        write_new_json(destination / "smoke_review.json", review_template(run_dir))
    plot_results(frame, contrasts, destination)
    write_new_json(destination / "analysis_manifest.json", {"raw_run": str(run_dir), "raw_digest": raw_digest(run_dir),
        "bootstrap_samples": n_boot, "bootstrap_seed": manifest["config"]["seed"], "selected_audit_count": len(selected),
        "interpretation": "Descriptive exploratory pilot. Inspect transcripts before interpreting aggregate metrics. No significance tests."})
    emit("Derived artifacts: " + str(destination))
    return destination
