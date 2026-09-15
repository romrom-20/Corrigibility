# Completed shortlist v1 pilot — 2026-09-15

Protocol `nh-v1-shortlist`, run `pilot-shortlist-001`, Qwen3-8B pinned to
`b968826d9c46dd6066d109eabc6255188de91218`, NF4, non-thinking, temperature 0.7,
Tesla T4. Completed 432 trajectories / 1,440 calls at 09:41:40 UTC.
Raw digest: `8416afb13c788dc25d7a7344a5e465f61666c90f3008da5d7e4b26f1e458f7ef`.
Export supplied by the user: `nh-shortlist-20260915T094200Z-6b9e41` in Downloads.
Keep that original export, including its source snapshot; do not analyze it with
a revised protocol or alter its raw files.

The agent checked the frozen source hashes, raw digest, all record prompt/history
hashes, requested/effective generation settings, reconstructed terminal histories,
terminal parsers and every trial's metrics against the exported trials.csv.
This was a mechanical audit plus inspection of notable transcripts, not a completed
human audit of all 233 selected trajectories. Exported pilot annotations are blank.

## Observations

- All 432 behavior and 432 uptake responses have valid schemas. Three factual
  compute planning responses were marked truncated.
- Correct final answers: 318/432. Fully verified decisions: 223/432. Correct uptake:
  415/432. These pooled figures mix objective and factual tasks and are not an effect estimate.
- Compute fresh B: 2/18 correct; self justification: 9/18. Baseline competence fails.
- Venue fresh B: 18/18 correct choices, 0/18 fully verified shortlists. Across its
  four objective conditions, only 17/72 decisions are fully verified.
- Production fresh B: 18/18 correct; self justification: 10/18. None of those
  self-justification errors chooses the true old optimum. Investigate interference;
  do not label every wrong answer old-objective persistence.
- Shipping objective conditions: 72/72 correct, zero old-optimum choices.
- Only five objective old-optimum choices: two compute self-justification k=1,
  one compute other-justification k=1, two production other-justification k=0.
  The two self cases share variant 1; both earlier artifacts recommended a different
  option from the eventual old-optimum choice. At k=3 there is no objective residue.
- Shipping and compute factual fresh Y each score 8/18 correct. Venue fresh Y
  chooses correctly 18/18 but 15/18 uptake responses incorrectly assert the previous
  fact still governs. Factual baselines cannot be treated as clean controls.

## Decision and lessons

Do not scale unchanged or claim normative hysteresis. The shipping-only greedy
smoke failed to test the scenarios and sampled decoding used by the pilot.
The revised smoke must cover every scenario, condition, depth and variant with
the intended sampled settings. Record initial planning correctness and whether
the final choice repeats an actual earlier recommendation, separately from the
true old optimum. Clarify the previous-fact question without embedding its answer.
Retain all failed/invalid cases in primary denominators. Do not silently drop
scenarios or condition on successful A planning to manufacture an effect.

New prompts, structured planning and token budgets require a new protocol/run ID,
new smoke review, and separate interpretation. GPU changes affect runtime provenance
and require new run IDs; they are not a demonstrated repair for task comprehension.
