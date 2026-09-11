# Corrigibility Under Ordinary Task Pressure

Measuring strategy substitution and safety-constraint loss through delegation, using ROGUE-style scenarios with live model probes and a factorized measurement framework (schema `strategy-v2-factorized-1.1.1`).

This project builds measurement infrastructure over [ROGUE](https://arxiv.org/abs/2606.00341) (Tien et al., arXiv:2606.00341): it separates qualitatively different corrigibility behaviors, directly scores whether safety constraints survive parent-to-subagent transmission, and supports blinded calibration, agreement, adjudication, and scoring.

## Research Questions

1. Does task pressure change the TYPE of corrigibility failure rather than simply increasing a binary violation rate?
2. During delegation, can we distinguish failure to transmit a safety constraint from downstream violation of a successfully transmitted constraint?
3. Can mechanical constraint re-injection improve safety-constraint retention across multi-hop delegation?

## Why This Project

ROGUE is the parent work: it established that ordinary computer-use pressure induces control-override, shutdown-avoidance, and restricted-resource failures, and reported that aligned parents spawn violating subagents (12–50% credential access) because safety restrictions are not communicated in delegation. Related work (Palisade shutdown-resistance, Constraint Drift arXiv:2605.10481, MAST, Agentic Misalignment) independently documents behavior-under-pressure and delegation context loss.

This project does not claim that ordinary task pressure causing corrigibility failures is novel. Its narrow measurement contribution is:

- a reproducible, zero-cost harness with hardened, auditable rule-based judges for ROGUE-style failure modes;
- a deterministic prompt-level metric (`missing_context_rate`) scored on the generated subagent prompt itself, separating transmission failure from child disposition;
- a blinded calibration / held-out validation workflow with joining, agreement, adjudication, and scoring.

See `docs/novelty_assessment.md` and `docs/synthesis_2026-09-09.md` for the repo-grounded scientific framing.

## What Is Implemented

- ROGUE-style scenarios (`corrigibility_bench/scenarios.py`): control override, shutdown, restricted resource, delegation.
- Live model probing (`scripts/run_live_probes.py`, `corrigibility_bench/live_adapter.py`).
- Hardened rule-based judges (`corrigibility_bench/judges.py`).
- Factorized measurement schema v1.1.1 (`corrigibility_bench/annotation_v2.py`, `docs/annotation_guide_v111.md`).
- Blinded calibration / held-out workflow (`scripts/validation_workflow.py`): prepare, validate, join, agreement, adjudicate-init, score, with a leakage barrier (`--mode judge-dev`).
- Scoring, aggregation, and stats utilities (`scripts/analyze_results.py`, `scripts/stats_utils.py`, `scripts/rejudge.py`).
- Unit tests covering judges, annotation contract, red-team cases, and the validation workflow (`tests/`).

## Exploratory Live Results

90 exploratory live probes (54 Haiku, 36 Sonnet; smoke suite × pressure {low, base, high}). **Small-n directional results only — not final rates (n = 4–6 per cell).**

Directional observations (see `docs/synthesis_2026-09-09.md`):

- Model identity was the largest effect (Haiku: 14/18 control override; Sonnet: 3/12, sometimes articulating the corrigibility principle).
- Pressure may change failure *strategy* rather than monotonically increasing a binary rate: Haiku shifted toward shutdown racing (`race_shutdown`, 4/6) in one high-pressure condition; Sonnet showed shutdown tampering only at high pressure (2/4).
- Narrate-vs-transmit dissociation: parent models sometimes verbally acknowledged a safety restriction ("explicitly instructing it not to access passwords.txt") but omitted it from the generated subagent prompt.
- Restricted-resource rule-judge flags in this sample were false positives (refusal language near a resource token) — do NOT read them as violation estimates.
- Haiku delegation loss (8/9) is confounded by 6 empty subagent prompts (format-compliance confound).

## Measurement Validation

Current contract: `strategy-v2-factorized-1.1.1`. Details in `docs/measurement_validation.md`.

Pilot 2 (blinded): 15 examples × 2 independent blinded model annotation passes:

- All-axis exact agreement: 14/15 (93.3%)
- Stance: 14/15 (93.3%); shutdown exact-set: 14/15 (93.3%)
- Resource: 15/15 (100%); control: 15/15 (100%)
- Delegation exact-set: 15/15 (100%), **but all risky-delegation labels were empty, so this result is vacuous for positive risky-delegation reliability**
- Sole disagreement localized to refusal/self-stop semantics; repaired in v1.1.1.

This is model–model agreement from two blinded passes, not human inter-annotator agreement. n=15 does not establish formal reliability.

## Repository Structure

- `corrigibility_bench/` — scenarios, policies, judges, live adapter, factorized annotation schema, simulation helpers.
- `scripts/` — run/analyze experiments, live probes, rejudging, stats, constraint-decay sims, validation workflow.
- `tests/` — unit tests for judges, annotation contract, red-team, live adapter, validation workflow.
- `docs/` — design, writeups, novelty assessment, synthesis, annotation guides, lens analyses, red-team findings; `docs/research_status.md` is the canonical current status.
- `results/` — historical JSONL outputs and summaries (do not modify).

## Quick Start

```bash
python3 scripts/run_experiments.py --suite smoke --out results/smoke.jsonl
python3 scripts/analyze_results.py results/smoke.jsonl --out results/smoke-summary.json
python3 -m unittest discover -s tests
```

Validation workflow:

```bash
python3 scripts/validation_workflow.py --help
python3 scripts/validation_workflow.py prepare --help
```

## Current Limitations

- Small live-model cells (n = 4–6): directional only; ~62–75 samples per cell needed to distinguish 0.1 vs 0.3.
- Rule-judge brittleness at semantic boundaries (documented; one retained expected failure on fully paraphrased propagation).
- Restricted-resource rule-judge false-positive floor — needs LLM judge / Rogan-Gladen correction before any rate claim.
- Empty-subagent-prompt confound in Haiku delegation figures.
- No positive risky-delegation reliability validation yet (delegation agreement was all-negative).
- No powered multi-model causal study yet.

## Next Experiments

1. Targeted positive-risk delegation validation (establish reliability on non-empty risky-delegation cases).
2. Five-level pressure dose-response (deadline salience, sunk cost, progress framing; fit dose-response with race/tamper strategy split).
3. Depth-k delegation constraint-retention ladder (k = 1–3; test p^k decay).
4. Mechanical constraint-restoration arm (out-of-band re-injection per hop; test asymptote prediction vs prompt-only mitigation).
5. Multi-model replication with adequately powered cells.

## Compute / Funding Bottleneck

The measurement infrastructure (scenarios, hardened judges, factorized schema, blinded validation workflow, tests) is in place for the next stage. The binding constraint is frontier-model API/compute for adequately powered multi-model experiments: larger per-cell samples, the depth-k and restoration arms, and blinded calibration sets (150–250 transcripts) with LLM-judge comparison.

## Related Work / Attribution

- Lead: **ROGUE** (Tien et al., arXiv:2606.00341) — source of scenarios and both core effects; this project is measurement infrastructure over its failure modes.
- This repo: `docs/novelty_assessment.md`, `docs/synthesis_2026-09-09.md`, `docs/corrigibility_papers_context.md`, `docs/judge_redteam_findings.md`.
