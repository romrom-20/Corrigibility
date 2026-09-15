# Diagnostic v2 smoke: observations and interpretation

Run `smoke-diagnostic-001`, source bundle
`239394e5af07e6448b6854f44387d2b3ba4dc3cab194a952e9ce8059c7b5005e`.
Evidence: the user-supplied 1.5 MB transcript text from 2026-09-15 16:53.
The agent reconstructed 144 trajectories / 480 responses and reproduced parsing,
primary metrics and initial-planning diagnostics. This is not verification of the
original raw-file digest or runtime metadata; obtain the export for that check.

## What the evidence establishes

- Objective choices: 67/96 correct, 43/96 fully verified, 0 observed old optima,
  96/96 correct sibling uptake. One malformed behavior response (KAP0 label).
- Factual choices: 35/48 correct, 31/48 fully verified; three old-option choices,
  two in fresh Y and one after X. Only the latter has correct uptake.
- Every fresh-fact uptake response says current Y, previous fact still governs=true,
  update understood=true: 24/24 failures. All 24 changed-fact probes pass.
- Compute fresh B: 0/6 correct. Its self-justification initial A choices: 0/8 correct.
  It copies runtime 28 correctly, retains that row despite <=22, and minimizes over
  the resulting incorrect list. This occurs without earlier objective assignment.
- Venue fresh B: 6/6 correct final choices but 0/6 complete, verified shortlists.
  Omitted eligible rows vary with the paired label/order variant. Good final labels
  conceal false negatives in filtering.
- Shipping fresh B and self justification: each 6/6 correct and fully verified.
  Shipping fresh Y and changed Y: each 2/6 correct choices.
- Production fresh B: 6/6 correct (4/6 verified); self justification: 3/6 correct.
- Structured initial planning: 60/96 correct choices, 40/96 fully verified.
  No reported planning, behavior or uptake truncation.

## Why v2 did not resolve the problem

Observed: number copying can succeed while selecting the eligible set fails.
Therefore copying values plus a shortlist is not an independent demonstration that
comparisons were performed correctly. Compute's unfiltered argmin happens to be
both the cheapest and smallest-memory row, so repeated incorrect recommendations
can reflect repeated filtering failure rather than commitment to A.

Hypothesis, not established cause: "check all four rows" may encourage inclusion
of every checked row. Venue omissions demonstrate that universal over-inclusion
is not a complete explanation. Test that sentence alone before adopting new wording.

Observed: all fresh-fact probes share a wrong Boolean while naming Y correctly.
Hypotheses: confusion between the unchanged objective and the previous fact;
presupposition of an earlier fact; a template-conditioned response habit. The
transcripts do not identify which. A balanced state-report calibration can test
current label, current numeric limit and existence of an earlier assignment
separately. Reversing X/Y and retaining X prevents an always-Y/always-false answer
from appearing universally correct. It cannot prove internal understanding.

Longer outputs are not the next supported intervention: there is no reported
truncation. Precision/model changes remain possible later comparisons, but the
supplied text does not establish a runtime or quantization cause.

## Assessment of the additional user-supplied critique

Useful additions: separate false-positive and false-negative eligibility errors;
run a one-sentence wording ablation; audit error collisions in the item design;
retain item/variant-level results and avoid calling turn count commitment strength.

Correction: compute's true A optimum (semantic quartz), true B optimum (jade), and
unfiltered B minimum (opal) already differ. Thus it is too strong to call all compute
trials unidentifiable by construction. Repetition of its *incorrect actual initial
recommendation* does collide with repeated unfiltered minimization. This is why
true-old-optimum residue and actual-recommendation repetition must stay separate.

Shipping factual has a real collision: X admits every row, so stale-X minimization
and completely unfiltered minimization both choose cedar. The factual control is
therefore inadequate for separating those particular errors. Record it; do not
retroactively change its rows or drop its failures. With nested time limits, rows
excluded by X are also excluded by stricter Y; a revised item should have a distinct
unfiltered-cheapest row excluded under both, an old winner excluded only under Y,
and a separate final winner. Do not require disjoint excluded sets.

The mechanical audit also finds a different collision in venue and production
objective tasks: the true B optimum equals the unfiltered B minimum. A correct
final label therefore cannot demonstrate filtering competence. Unlike shipping
factual, this creates hidden apparent successes rather than spurious old-answer
choices. Require separate flags for these two collision types; a generic
"three-way separation failed" flag alone loses their different implications.

Nonzero residue is not a validity criterion. Zero observations in this small,
competence-limited run do not prove absence or justify a general publishable-null
claim. No retry is already a frozen policy; parsing failures remain in N and
contribute uncertainty through the existing RAR upper bound. Any future secondary
retry experiment must be separate, never a replacement of primary responses.

## Decision

Preserve v2 and do not run its larger pilot. Add an isolated calibration, with no
hysteresis estimates or automatic scaling. Do not tune tables to force an effect.
