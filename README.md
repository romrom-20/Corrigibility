# Normative hysteresis — instrument qualification

**Status: instrument qualified (2026-09-18). No experimental result yet.**

This project tests whether prior objective-directed reasoning leaves residual
behavioral influence after an explicit, authorized objective replacement
("normative hysteresis"), using frozen models and neutral table-selection tasks.

## What is established

Two consecutive component runs under the frozen backend (Qwen3-8B, revision
`b968826d`, bf16, no quantization, thinking enabled, A100) passed every
preregistered gate criterion:

| Component | Run ID | Cases | Valid | Accuracy | Balance |
|---|---|---|---|---|---|
| Eligibility | `ablation-bf16-think-1024-003` | 384 | 384/384 | 1.000 (all 6 boundary relations) | rotation 192/192 |
| Comparison (ranking/selection) | `comparison-bf16-think-1024-001` | 288 | 288/288 | 1.000 (labeled, named, numeric) | reverse 144/144, rotation 144/144 |

Gate: `require_all_valid`, `max_truncated: 0`, `min_accuracy: 1.0`,
`require_exact_balance` — PASS on all criteria.

Reference points: the same eligibility cases under the prior backend
(NF4, non-thinking, `context-002`) scored 76.8%. An earlier pilot failed all
24 objective-choice trials and was rejected without scaling.

## What this does NOT establish

Nothing here is evidence for or against normative hysteresis. Qualification
certifies the measuring stick — constrained eligibility and ranking under the
deployed configuration — not the measurement. No A-history treatment arm has
run under the qualified instrument.

## Reproduce / audit

Pipeline notebook: [notebooks/nh_instrument_qualification_pipeline.ipynb](notebooks/nh_instrument_qualification_pipeline.ipynb)

The notebook fetches the source bundle from Drive `source_snapshots/` by
SHA-256 (`d09345e35fbd…`) and verifies it. Two files added 2026-09-18 are
pinned individually by the hashes recorded in the passing run's manifest:

- `comparison_qualification_v1.py` — sha256 `c536e9bfec6565d7a1aac4ae1221df767f39c464c284591417b5fa9d8f76c616`
- `configs/comparison_qualification_thinking_v1.json` — sha256 `fae80555aa960cb15f582c1c11842ff75fde6bd74a9198cff136d10220033ed3`

Export: `results/exports/nh-instrument-qualification-8bc1e1a9.zip`
(737 files: source, raw records, derived summaries, preserved manifest).

## Next

1. Expand from prototype scenarios to 12+ solver-verified neutral scenario
   families; calibrate difficulty without inspecting treatment effects.
2. Preregister: estimands, factorial contrasts, sample sizes, stopping rules,
   kill criteria.
3. Full fresh-B smoke test under a **new run ID**, frozen backend, reverse
   counterbalancing enabled on every arm. Freeze prompts, parser, scoring,
   and exclusion criteria before launch; no edits after.

## Rules that got us here

All real inference stays in hosted Colab; no model weights on the Mac.
Fresh run IDs only — reusing a completed run ID silently returns old records.
Preserve historical sources, notebooks, raw results, and failed runs.
Invalid/truncated outputs remain failures. Unreadable manifests are preserved,
never regenerated. Execution errors are not relabeled resistance to correction.

## History

- [Detailed research story](docs/RESEARCH_STORY.md)
- [Experiment history index](docs/EXPERIMENT_HISTORY.md)
- [Ablation bf16+thinking rescore report (2026-09-18)](docs/ABLATION_BF16_THINKING_002_RESCORED_20260918.md)
- [Run handoff](docs/RUN_HANDOFF.md)
