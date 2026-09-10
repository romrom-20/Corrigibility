# Mathematician's Lens: Corrigibility Bench

Scope: formalize the delegation-loss hypothesis, specify the statistics the harness
needs before live model runs, model judge error, and provide runnable utilities
(`scripts/stats_utils.py`).

---

## 1. The delegation hypothesis as a noisy channel

The writeup's second hypothesis — *"Delegation creates a lossy channel for
corrigibility constraints"* — is currently prose. Here is the minimal formal model.

### 1.1 Setup

Let a constraint `C` (e.g., "do not access `/home/user/Desktop/passwords.txt`") be a
binary random variable over prompt contents: `X_i = 1` if the constraint is present
in agent `i`'s prompt, `X_i = 0` otherwise. The delegation chain is a Markov chain

```
X_0 = 1  →  X_1  →  X_2  →  …  →  X_k
```

where each hop is prompt compression by the parent. In the simplest model each hop
is a **Z-channel**: a present constraint is preserved with probability `p` and lost
with probability `1 − p`; a lost constraint is never spontaneously re-invented
(`P(X_{i+1}=1 | X_i=0) = 0`). This is exactly what `judge_subagent_propagation` in
`corrigibility_bench/judges.py` measures at one hop: `missing_safety_context` is the
event `X_1 = 0` given `X_0 = 1`, so the observed `missing_context_rate` is an
estimator of `1 − p`.

### 1.2 Survival over depth k

With i.i.d. hops,

```
S(k) := P(X_k = 1) = p^k = e^{k ln p}
```

Survival decays **geometrically** in depth. Two consequences worth internalizing:

- **Half-life depth.** The depth at which survival drops to 1/2 is
  `k_half = ln(1/2) / ln(p)`. For `p = 0.95`, `k_half ≈ 13.5`; for `p = 0.8`,
  `k_half ≈ 3.1`; for `p = 0.5`, `k_half = 1`. Even a "pretty good" 95%-faithful
  hop gives you less than a coin flip of constraint survival by depth 14, and only
  `0.95^4 ≈ 0.81` at the modest depths (3–5) real agent stacks already reach.
- **First-loss depth.** Let `T = min{k : X_k = 0}`. Then `T` is geometric:
  `P(T = t) = p^{t-1}(1 − p)`, and

  ```
  E[T] = 1 / (1 − p)
  ```

  (infinite chain). For a finite chain of depth `k`, conditional on a loss
  occurring, `E[T | T ≤ k] = 1/(1−p) − k·p^k/(1−p^k)`. So `p = 0.9` means the
  constraint is lost, on average, at the **10th** hop — but with substantial mass
  much earlier: `P(T ≤ 3) = 1 − 0.9^3 ≈ 27%`.

Heterogeneous hops generalize trivially: `S(k) = ∏_i p_i`, i.e., log-survival is
additive, `ln S(k) = Σ ln p_i`. This is the right form for regression: fit per-hop
loss as an additive effect in log space, with covariates like task urgency or
prompt length.

### 1.3 Data processing inequality (why this can only get worse downstream)

Framed information-theoretically: with `C` the user's constraint and `P_i` the
prompt at depth `i`, the chain `C → P_0 → P_1 → … → P_k` satisfies the data
processing inequality:

```
I(C; P_k) ≤ I(C; P_{k-1}) ≤ … ≤ I(C; P_0)
```

No amount of downstream cleverness by a subagent can recover constraint
information that its prompt does not carry — **unless** there is a side channel.
That is the mathematically precise version of the writeup's claim that "the child
operates in a locally reasonable way while violating the original user's
constraint": the child is doing constrained-optimal inference given `P_k`, and
`P_k` simply lacks the bit.

### 1.4 The restoration variant (why system-level re-injection changes the asymptotics)

If a side channel exists — a harness that re-injects safety context into every
subagent spawn with per-hop probability `r` — the chain becomes a two-state Markov
chain with transition matrix `[[p, 1−p], [r, 1−r]]` (states: present, absent).
Then

```
P(X_k = 1) = π∞ + (1 − π∞)(p − r)^k,   π∞ = r / (1 − p + r)
```

Survival no longer decays to 0; it decays geometrically (rate `|p − r| < 1`) to a
**positive plateau** `π∞`. Example: `p = 0.8, r = 0.3` gives `π∞ = 0.6`. This is
the quantitative argument for a mitigation class the benchmark should test:
mechanical constraint propagation (restoration, `r > 0`) beats exhortation
(raising `p` slightly) at any nontrivial depth, because it changes the asymptote,
not just the rate. Both formulas are implemented and Monte Carlo–verified in
`scripts/stats_utils.py`.

### 1.5 What the harness should therefore measure

The current suite measures one hop (`X_1`). The model above says the scientifically
valuable quantities are:

1. `p̂` per (model, scenario, mitigation) cell — one-hop preservation probability,
   with an interval (Section 2).
2. Depth curves: run 2- and 3-hop delegation and check whether the empirical
   `S(k)` matches `p̂^k`. Deviation from the product form is itself a finding —
   super-geometric loss suggests compounding compression pressure; sub-geometric
   loss suggests models re-derive constraints from residual cues (a small
   effective `r > 0`).

---

## 2. Statistical rigor for live model samples

### 2.1 What `scripts/analyze_results.py` lacks

The aggregator (`scripts/analyze_results.py`) currently reports raw
`violation_rate = sum(violations)/n` and nothing else. Concretely missing:

- **No uncertainty quantification.** `results/ablations-summary.json` reports
  rates of exactly 0.0 and 1.0 on `n ∈ {1, 2, 3}`. For deterministic policy arms
  that is fine (it is a harness self-test, not an estimate), but the same code
  path will soon aggregate stochastic model samples, where `1/1 = 1.0` and
  `20/20 = 1.0` are radically different pieces of evidence. A Wilson 95% interval
  on 3/3 is [0.44, 1.00]; on 0/3 it is [0.00, 0.56]. Any table without intervals
  will overstate certainty at these n.
- **No comparisons.** The hypotheses in `docs/experiment_design.md` are all
  *contrasts* (pressure vs. no pressure, mitigation vs. none, direct vs.
  delegated), but the script computes no differences, no tests, no effect-size
  intervals.
- **Boundary-hostile estimator.** The MLE `x/n` at 0 or 1 has a degenerate Wald
  interval (width 0). Wilson or Jeffreys/beta-binomial handles this.
- **No multiplicity handling.** The grid is scenario × policy × suite; with live
  runs it becomes scenario × model × mitigation × depth. Dozens of cells at
  α = 0.05 will produce false "effects" by construction.
- Minor: no per-case breakdown (rates pool heterogeneous cases within a
  scenario), and `subagent_propagation` rows are keyed only by policy, discarding
  scenario — this masks which constraint is being dropped.

### 2.2 Sample sizes: what n do you need?

Two-proportion z-test, two-sided α = 0.05, power 0.80, n per arm (from
`required_n_per_arm` in `scripts/stats_utils.py`):

| Contrast (p₁ vs p₂) | n per arm |
|---|---|
| 0.10 vs 0.30 | **62** |
| 0.30 vs 0.50 | 93 |
| 0.05 vs 0.15 | 141 |
| 0.10 vs 0.20 | 199 |

The formula: `n = [ z_{α/2}√(2 p̄(1−p̄)) + z_β √(p₁(1−p₁)+p₂(1−p₂)) ]² / (p₂−p₁)²`
with `p̄ = (p₁+p₂)/2`. (Adding the continuity correction for the exact test pushes
0.10-vs-0.30 to ~72; treat 62 as a floor, budget ~75.)

Practical reading for this harness:

- The headline contrast in the design (does pressure move violation rate from
  ~0.1 to ~0.3?) needs **~60–75 samples per condition cell**, i.e., per
  (scenario, model, mitigation) combination — not per suite. At 3 scenarios × 2
  pressure conditions that is ~400 transcripts per model, which is cheap for
  text-only probes.
- Subtler effects (0.10 vs 0.20) need ~200/cell; do not claim mitigation
  "weakens under delegation" from a 0.10-vs-0.18 gap at n = 30 — the power there
  is roughly 20%.
- Rare events are the trap: distinguishing 0.01 from 0.05 needs ~470/arm. If
  baseline violation rates turn out to be very low, switch from per-cell testing
  to pooled logistic regression with scenario fixed effects.

### 2.3 Interval and estimator recommendations

- **Report Wilson score intervals** (implemented: `wilson_interval`) next to every
  rate in the summary JSON. They have near-nominal coverage at small n, never
  leave [0,1], and behave sensibly at 0/n and n/n.
- **Prefer a beta-binomial posterior for estimation and downstream propagation.**
  With a Jeffreys prior `Beta(1/2, 1/2)`, the posterior after x violations in n
  trials is `Beta(x + 1/2, n − x + 1/2)`; posterior mean `(x+1/2)/(n+1)` shrinks
  the boundary estimates (3/3 → 0.875 rather than 1.0), and equal-tailed credible
  intervals nearly match Wilson. The real payoff is compositionality: to get a
  posterior over chain survival `p^k` or over the Rogan-Gladen–corrected rate
  (Section 3), sample from the Beta posteriors and push samples through the
  formula. This is far cleaner than delta-method variance algebra on ratios.
- **For contrasts**, use the two-proportion z-test (implemented:
  `two_proportion_test`) as the workhorse, Fisher's exact when any cell count
  < 5, and report the difference with its own CI, not just a p-value. Control
  multiplicity across the cell grid with Benjamini–Hochberg at FDR 0.05.

---

## 3. Judge error model and correction

### 3.1 How judge error biases the estimate

The rule-based judges in `corrigibility_bench/judges.py` are classifiers with
nonzero error. Let `π` be the true violation rate, `se` the judge's sensitivity
(1 − FN rate: P(flag | violation)) and `sp` its specificity (1 − FP rate:
P(no flag | no violation)). The observed flag rate is

```
π_obs = π·se + (1 − π)(1 − sp)
```

so the bias is

```
π_obs − π = (1 − sp)(1 − π) − (1 − se)·π
```

Consequences:

- At **low true rates** (the regime this benchmark hopes for), bias is dominated
  by the false-positive term `(1 − sp)(1 − π)`: a judge with sp = 0.95 reports
  π_obs ≈ 0.05 + 0.85π, i.e., a floor of 5% "violations" that are judge artifacts.
  The writeup's own review history (counting "I will not click Override" as an
  override) is exactly this failure.
- At **high true rates**, false negatives dominate and the judge *understates*
  violations.
- Worst of all for the science: if `se`/`sp` differ **across arms or models**
  (e.g., the regex negation window in `_is_negated` handles one model's phrasing
  better than another's), the bias is differential and can manufacture or erase
  the very contrasts the experiment exists to measure. Judge error must be
  estimated per transcript-style stratum, not assumed global.

### 3.2 Rogan-Gladen correction

Invert the observation equation (valid when `se + sp > 1`, i.e., the judge beats
chance):

```
π̂ = (π_obs + sp − 1) / (se + sp − 1),   clipped to [0, 1]
```

Implemented as `rogan_gladen` in `scripts/stats_utils.py`. Example with
se = 0.90, sp = 0.95: an observed 14% flag rate corresponds to a true rate of
~10.6%; an observed 10% to ~5.9%. Note the leverage: near the FP floor, small
observed differences correspond to larger true differences (the denominator
0.85 < 1 stretches them).

### 3.3 Getting se and sp: the calibration set

Estimate `se` and `sp` from a **labeled calibration set**: sample transcripts
(stratified by scenario, arm, and judge verdict — oversample flagged ones),
hand-label them blind, and compute `se = TP/(TP+FN)`, `sp = TN/(TN+FP)` with
their own Wilson intervals. Then propagate all three uncertainties jointly:

- Bayesian version (recommended, matches Section 2.3): put Jeffreys Beta
  posteriors on `π_obs`, `se`, `sp` from their respective counts, draw samples,
  push through the Rogan-Gladen formula, and report the posterior interval on
  `π̂`. This correctly widens when the calibration set is small and correctly
  handles the truncation at 0.
- Calibration budget: to know `sp` to ±0.03 (needed if you care about rates near
  0.05) requires ~200 hand-labeled negatives; ~100 gives ±0.04. Sensitivity needs
  fewer labels if violations are oversampled. Budget ~150–250 hand labels per
  judge before trusting corrected rates.
- The planned rule-judge vs. LLM-judge comparison fits this framework as a
  two-rater agreement problem: report Cohen's κ, and treat disagreements as the
  priority queue for hand-labeling.

The delegation judge has an extra wrinkle: `judge_subagent_propagation` requires
the *verbatim* resource string in the subagent prompt, so a semantically faithful
paraphrase ("don't touch the saved-passwords file on the Desktop") counts as a
loss. That is a known FN=0 / FP>0 asymmetry on the *preservation* event — the
measured `p̂` is a **lower bound** on semantic preservation. Fine, but say so, and
let the LLM-judge comparison estimate the paraphrase FP rate.

---

## 4. Runnable utilities and demo output

`scripts/stats_utils.py` (stdlib only; no numpy required) implements:

- `wilson_interval(successes, n, confidence)` — Wilson score interval.
- `two_proportion_test(x1, n1, x2, n2)` and `required_n_per_arm(p1, p2, alpha, power)`.
- `rogan_gladen(observed_rate, sensitivity, specificity)`.
- `chain_survival_analytic` / `chain_survival_mc` (Monte Carlo, 20k chains) and
  `chain_survival_mc_restoration` for the plateau variant, both checked against
  the closed forms.

Verified output of `python3 scripts/stats_utils.py`:

```
Delegation-chain constraint survival: analytic p^k vs Monte Carlo
(20,000 chains per cell; MC column shows estimate with 95% Wilson CI)

p      E[first loss]  k=1                    k=2                    k=4                    k=8                    k=16
-----------------------------------------------------------------------------------------------------------------------------------------
0.50      2.0 hops   0.500~0.497±0.007   0.250~0.250±0.006   0.062~0.059±0.003   0.004~0.004±0.001   0.000~0.000±0.000
0.80      5.0 hops   0.800~0.797±0.006   0.640~0.639±0.007   0.410~0.415±0.007   0.168~0.171±0.005   0.028~0.029±0.002
0.95     20.0 hops   0.950~0.951±0.003   0.902~0.903±0.004   0.815~0.814±0.005   0.663~0.661±0.007   0.440~0.442±0.007

Two-proportion z-test demo: 10/100 vs 30/100 violations
  p1=0.10 p2=0.30 z=3.536 p-value=0.00041

Sample size per arm (alpha=0.05 two-sided, power=0.80):
  detect 0.10 vs 0.30: n = 62
  detect 0.10 vs 0.20: n = 199
  detect 0.05 vs 0.15: n = 141
  detect 0.30 vs 0.50: n = 93

Rogan-Gladen correction (judge sensitivity=0.90, specificity=0.95):
  observed rate 0.10 -> corrected 0.059
  observed rate 0.14 -> corrected 0.106
  observed rate 0.30 -> corrected 0.294

Restoration channel (p=0.8, r=0.3): survival plateaus instead of dying
  k=1   analytic=0.800 mc=0.798 (plateau pi_inf=0.600)
  k=4   analytic=0.625 mc=0.624 (plateau pi_inf=0.600)
  k=16  analytic=0.600 mc=0.604 (plateau pi_inf=0.600)
```

Every Monte Carlo cell agrees with the analytic value within its Wilson interval,
which validates both the simulator and the interval code.

---

## Concrete recommendations

1. **Report intervals, not raw rates.** Wire `wilson_interval` into
   `scripts/analyze_results.py` so every `violation_rate` and
   `missing_context_rate` in the summary JSON carries `[lo, hi]` and `n`. Rates
   of 1.0 at n = 1–3 (as in `results/ablations-summary.json`) should never
   appear without an interval again.
2. **Power the live runs at ~75 samples per cell** for the primary 0.1-vs-0.3
   contrasts (62 is the analytic floor; 75 covers continuity correction and
   dropout). Pre-register which contrasts are primary; apply Benjamini–Hochberg
   across the rest of the grid.
3. **Estimate with Jeffreys beta-binomial posteriors** `Beta(x+½, n−x+½)` for
   any quantity that gets composed downstream (chain survival, corrected rates);
   propagate by posterior sampling rather than delta-method algebra.
4. **Build the judge calibration set before the first paid run**: 150–250
   blind hand labels per judge, stratified by verdict and arm; compute se/sp
   with intervals; publish Rogan-Gladen–corrected rates alongside raw ones. Check
   se/sp separately per model/arm — differential judge error is the failure mode
   that silently fakes treatment effects.
5. **Measure delegation at depths 1–3, not just 1**, and test the empirical
   survival curve against `p^k`. Report `p̂` (one-hop preservation) and the
   implied half-life depth `ln(½)/ln(p̂)` as the headline delegation metrics.
6. **Add a restoration arm** (harness mechanically re-injects
   `forbidden_resources` into every subagent prompt). The two-state chain math
   says restoration changes the survival *asymptote* (`π∞ = r/(1−p+r)`) while
   better prompting only changes the *rate*; this is the cheapest high-value
   mitigation experiment the current scaffold can support.
7. **Document the propagation judge's asymmetry**: verbatim string matching makes
   `p̂` a lower bound on semantic preservation; use the planned LLM-judge
   comparison to estimate the paraphrase false-loss rate and correct with
   Rogan-Gladen.
