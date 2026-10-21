# Normative hysteresis — research status

**Status through 2026-10-13:**

- **Component gates passed, 2026-09-18:** constrained eligibility and ranking.
- **Full instrument qualification under the pre-Oct-6 design did not pass:**
  the Oct 2–3 diagnostics failed predeclared gates.
- **Assay redesigned, 2026-10-06:** transfer tables, a 5 percentage point minimum
  meaningful effect, and the unconditional behavioral contrast as primary.
- **Labeled 64-instance smoke pilot completed, 2026-10-13:** 832/832 records
  saved and hash-verified, zero errors, all arms behaving as designed.
- **Descriptive read:** a ceiling-level null at pilot resolution. No evidence
  for or against normative hysteresis; no experimental result on NH exists.

This project tests whether prior objective-directed reasoning leaves residual
behavioral influence after an explicit, authorized objective replacement
("normative hysteresis"), using frozen models and neutral table-selection tasks.

## Component gates — 2026-09-18

Two consecutive component runs under the frozen backend (Qwen3-8B, revision
`b968826d`, bf16, no quantization, thinking enabled, A100) passed every
preregistered gate criterion:

| Component | Run ID | Cases | Valid | Accuracy | Balance |
|---|---|---|---|---|---|
| Eligibility | `ablation-bf16-think-1024-003` | 384 | 384/384 | 1.000 (all 6 boundary relations) | rotation 192/192 |
| Comparison (ranking/selection) | `comparison-bf16-think-1024-001` | 288 | 288/288 | 1.000 (labeled, named, numeric) | reverse 144/144, rotation 144/144 |

Gate: `require_all_valid`, `max_truncated: 0`, `min_accuracy: 1.0`,
`require_exact_balance` — PASS on all criteria.

These are component gates for constrained eligibility and ranking, not full
instrument qualification. Full qualification never passed under the pre-Oct-6
design; the [experiment history](docs/EXPERIMENT_HISTORY.md) preserves the
Oct 2–3 failures.

Reference points: the same eligibility cases under the prior backend
(NF4, non-thinking, `context-002`) scored 76.8%. An earlier pilot failed all
24 objective-choice trials and was rejected without scaling.

## 2026-10-13 milestone

After an external audit on 2026-10-06, further prompt repair was replaced with
the transfer-table assay. On each new instance, the old answer (X), the old rule
applied to the new task (Z), and the correct update (Y) make different predictions.
This separates hysteresis as rule persistence from copying the old answer. The
minimum meaningful effect was fixed at 5 percentage points (5pp), with the
unconditional behavioral contrast primary.

A labeled 64-instance smoke pilot (32 cells × 2 instances) ran on Modal across
five arms on 2026-10-12–13 and completed on 2026-10-13: **832/832 records saved
and hash-verified, zero errors**. This was explicitly a smaller smoke design;
its 95% interval widens to about ±34pp and cannot settle the 5pp effect.

Every arm behaved as designed, with 128/128 strict-correct per arm:

| Arm | Observed choices |
|---|---|
| `fresh_A` | A-optimal answer, 128/128 |
| `A_no_change` | A-optimal answer, 128/128 |
| `A_to_B` | B-correct answer, 128/128 |
| `describe_to_B` | B-correct answer, 128/128 |
| `fresh_B` | B-correct answer, 128/128 |

The two A-history switch arms chose B in all 256 slots: zero old-rule carryover.
The descriptive effect read is a **ceiling-level null, with zero variance between
arms at pilot resolution**. The assay as configured showed no detectable
hysteresis pressure. Discrimination may have been too easy: `fresh_B` alone
solved the current tables perfectly.

Disclosed caveats: the pilot spanned three invocations (restart history; every
record individually hash-valid); six `describe_to_B` planning records hit the
1024-token cap; Modal spend was unsettled at report time. The token-cap condition
remains part of the report alongside the strict-correct choice counts.

The Oct 6–13 run records, evidence pack, Modal worker source, and environment/
pyenv pins are not yet in this repository. This milestone reports the owner's
verified facts; those artifacts are not available here for a repository audit.

## What this does NOT establish

Nothing here is evidence for or against normative hysteresis. The September
component gates certify constrained eligibility and ranking under the deployed
configuration, not the composed full task. The October pilot establishes the
reported instrument behavior on this smoke design, not an NH finding. The
measuring stick and the measurement remain distinct.

Perfect choices and zero old-rule carryover in this pilot do not establish that
normative hysteresis does not exist, or that it does. The smaller smoke design's
approximately ±34pp 95% interval cannot resolve the fixed 5pp minimum meaningful
effect. No experimental result on NH exists.

## Reproduce / audit

September component pipeline notebook:
[notebooks/nh_instrument_qualification_pipeline.ipynb](notebooks/nh_instrument_qualification_pipeline.ipynb)

The notebook fetches the source bundle from Drive `source_snapshots/` by
SHA-256 (`d09345e35fbd…`) and verifies it. Two files added 2026-09-18 are
pinned individually by the hashes recorded in the passing run's manifest:

- `comparison_qualification_v1.py` — sha256 `c536e9bfec6565d7a1aac4ae1221df767f39c464c284591417b5fa9d8f76c616`
- `configs/comparison_qualification_thinking_v1.json` — sha256 `fae80555aa960cb15f582c1c11842ff75fde6bd74a9198cff136d10220033ed3`

Export: `results/exports/nh-instrument-qualification-8bc1e1a9.zip`
(737 files: source, raw records, derived summaries, preserved manifest;
referenced archive, not checked into this repository).

## Next

The owner's next steps are a full 128-instance pilot of the same design, then a
powered held-out run. A harder-discrimination redesign is under consideration
because `fresh_B` alone solves the current tables.

## Rules that got us here

The earlier component work used hosted Colab; the October smoke pilot used Modal.
No model weights on the Mac.
Fresh run IDs only — reusing a completed run ID silently returns old records.
Preserve historical sources, notebooks, raw results, and failed runs.
Invalid/truncated outputs remain failures. Unreadable manifests are preserved,
never regenerated. Execution errors are not relabeled resistance to correction.

## History

- [Detailed research story](docs/RESEARCH_STORY.md)
- [Experiment history index](docs/EXPERIMENT_HISTORY.md)
- Historical ablation bf16+thinking rescore report (2026-09-18):
  `docs/ABLATION_BF16_THINKING_002_RESCORED_20260918.md` (not present in this repository).
- [Historical replication handoff](docs/RUN_HANDOFF.md)
