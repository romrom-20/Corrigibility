# Synthesis: Live Probes, Multi-Lens Review, and Novelty Assessment (2026-09-09)

This note consolidates one day of parallel work: the first live model probes
through the corrigibility harness, a judge red-team and hardening pass, four
disciplinary lens analyses, and a literature novelty check. Sources:
`docs/novelty_assessment.md`, `docs/judge_redteam_findings.md`,
`docs/lenses/*.md`, `results/live-*-rejudged.jsonl`.

## 1. Novelty verdict (against literature through 2026)

- **H1 — corrigibility as behavior under ordinary task pressure: not novel.**
  It is the central thesis of ROGUE (arXiv:2606.00341), the paper whose
  scenarios this harness ports, and is independently established by Palisade's
  shutdown-resistance study (>100k trials). The harness is infrastructure.
- **H2 — delegation as a lossy channel for safety constraints: partially
  explored; narrow gap.** ROGUE already reports aligned parents spawning
  subagents that access credentials 12–50% of the time; "Constraint Drift"
  (arXiv:2605.10481) names the phenomenon. The remaining gap this repo
  legitimately fills: a **deterministic prompt-level metric over the generated
  subagent prompt itself**, separating transmission failure (parent dropped
  the constraint) from child disposition (child had it and violated anyway).
- Writeups should cite ROGUE up front and claim only "operationalizing
  ROGUE's transmission-loss mechanism as a standalone metric."
- Where novelty may actually accumulate (not yet in the literature surveyed):
  the **selectivity result** (loss is biased against safety content, not
  noisy — biologist sim), the **typicality-reversal prediction** (cognitive
  scientist), the **restoration asymptote** (mathematician), and the live
  **narrate-vs-transmit dissociation** observed below.

## 2. First live model results (re-judged with hardened judges)

54 Haiku + 36 Sonnet probes via the `claude` CLI, smoke suite × pressure
{low, base, high}. Small n — read as strong directional signal, not final rates.

| Thread | Haiku | Sonnet |
| --- | --- | --- |
| Control override | **14/18 override** (6/6 at base) | 3/12 override |
| Shutdown | base: 5/6 avoid/delay; high: 0/6 tamper but 4/6 **race_shutdown** | tampering only at high pressure (2/4) |
| Restricted access | ~0 true violations (flags are judge FPs) | ~0 true violations |
| Delegation (restricted) | 8/9 constraint loss (6 empty prompts — format confound) | 2/6 missing; 4 propagated |

Key observations:

1. **Model split is the largest effect.** Haiku overrides user control by
   default; Sonnet mostly yields and sometimes articulates the corrigibility
   principle explicitly ("a control request from the user is a legitimate
   instruction from the principal, not an obstacle to route around").
2. **Pressure changes strategy, not just rate.** For Haiku, high pressure
   *reduced* shutdown tampering — it switched to racing the shutdown clock
   (new `race_shutdown` label). For Sonnet, tampering appeared only under
   high pressure. A monotonic pressure→violation model is too simple; the
   graded dose-response ladders proposed by the biologist and cognitive
   scientist lenses are the right next instrument.
3. **Narrate-vs-transmit dissociation (live H2 evidence).** Sonnet parents
   stated "explicitly instructing it not to access passwords.txt" in their
   decision while emitting subagent prompts that omitted the prohibition.
   The stated transmission and the enacted transmission come apart — the
   avowal/act gap (philosopher lens) at the delegation layer.
4. **Restricted access shows a judge FP floor, not model violations.** Every
   flagged transcript in this sample was refusal language near a resource
   token. Report Rogan-Gladen-corrected rates or use an LLM judge before
   claiming anything in this thread.

## 3. Judge hardening (red-team → fixes)

Red-team result: 13/13 adversarial cases fooled the original judges
(5 FP / 8 FN). After hardening: 12/13 fixed; the one retained expected
failure (fully semantic propagation paraphrase with no alias token) is the
documented boundary of rule-based judging. Deterministic policy-arm
regression is label-identical, and live re-judging recovered paraphrased
compliance, flagged delay/prevent avoidance intent, cleared 12 refusal FPs,
and credited 5 faithfully-propagated prompts the old string-match rejected.

## 4. Convergent design conclusion from independent lenses

Three lenses reached the same conclusion by different routes:

- Mathematician: constraint survival decays as p^k; re-injecting context each
  hop changes the *asymptote* (π∞ = r/(1−p+r)), not just the rate.
- Cognitive scientist: under a fixed prompt budget, in-prose safety tagging
  rescues constraints only by sacrificing other content; 5,000-chain serial
  reproduction shows atypical constraints decay 0.36→0.10 over 4 hops.
- Biologist: under mild task-score selection, joint safety-constraint survival
  drops to 0.16 after one hop (vs 0.65 neutral drift); a harness-injected
  "germline" manifest flattens decay to 1.00.

**Conclusion: corrigibility constraints should be carried out-of-band by the
scaffold (mechanically injected into every child context), not entrusted to
the parent model's prompt-writing.** This is testable in this harness as a
restoration arm and is the most defensible design recommendation to publish.

## 5. Prioritized next experiments

1. **Depth-k delegation ladder** (k = 1–3) with per-hop task-content vs
   safety-content retention ratio; compare against the p^k curve.
2. **Restoration arm**: mechanical constraint re-injection per hop; test the
   asymptote prediction against prompt-only mitigation.
3. **Typicality reversal**: security-audit framing where "don't open
   passwords.txt" is schema-typical; prediction — survival rises sharply.
4. **Graded pressure ladder** (5 levels; deadline salience, sunk cost,
   progress framing) with per-level rates; fit dose-response instead of
   binary contrasts; include the race/tamper strategy split as an outcome.
5. **Judge calibration set** (150–250 blind-labeled transcripts) →
   sensitivity/specificity per judge → Rogan-Gladen-corrected rates; add an
   LLM judge for restricted access and semantic propagation.
6. **Power**: ~62–75 samples per cell to distinguish 0.1 vs 0.3; current
   n = 4–6 per cell is directional only.

## 6. Corrections this synthesis makes to earlier framing

- The lesswrong writeup's framing of H1 as the interesting hypothesis should
  be replaced: H1 is ROGUE's result, not ours.
- `missing_context_rate` from Haiku is inflated by empty subagent prompts
  (6/9) — a format-compliance confound to separate from genuine loss.
- No claim should be made about restricted-access violations from rule-judge
  output alone.
