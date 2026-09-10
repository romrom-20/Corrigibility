#!/usr/bin/env python3
"""Statistical utilities for the corrigibility benchmark.

Stdlib-only (numpy optional, not required):
  - Wilson score interval for a binomial proportion.
  - Two-proportion z-test (pooled), with power/sample-size helpers.
  - Rogan-Gladen correction for judge false-positive/false-negative rates.
  - Monte Carlo simulation of constraint survival through a delegation chain,
    checked against the analytic geometric-survival formula.

Run `python3 scripts/stats_utils.py` for a small demo table.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Normal distribution helpers (stdlib only)
# ---------------------------------------------------------------------------


def normal_cdf(x: float) -> float:
    """Standard normal CDF via math.erf."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def normal_ppf(q: float, tol: float = 1e-10) -> float:
    """Standard normal quantile by bisection (adequate for tail probs >= 1e-12)."""
    if not 0.0 < q < 1.0:
        raise ValueError("q must be in (0, 1)")
    lo, hi = -12.0, 12.0
    while hi - lo > tol:
        mid = (lo + hi) / 2.0
        if normal_cdf(mid) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# ---------------------------------------------------------------------------
# (a) Wilson score interval
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Interval:
    point: float
    lo: float
    hi: float

    def __str__(self) -> str:
        return f"{self.point:.3f} [{self.lo:.3f}, {self.hi:.3f}]"


def wilson_interval(successes: int, n: int, confidence: float = 0.95) -> Interval:
    """Wilson score interval for a binomial proportion.

    Preferred over the Wald interval because it has near-nominal coverage at
    small n and never escapes [0, 1] — both of which matter here, where
    per-cell n is small and rates sit at the 0/1 boundary.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= successes <= n:
        raise ValueError("successes must be in [0, n]")
    z = normal_ppf(1.0 - (1.0 - confidence) / 2.0)
    phat = successes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (phat + z2 / (2.0 * n)) / denom
    half = (z / denom) * math.sqrt(phat * (1.0 - phat) / n + z2 / (4.0 * n * n))
    return Interval(phat, max(0.0, center - half), min(1.0, center + half))


# ---------------------------------------------------------------------------
# (b) Two-proportion z-test and power / sample-size planning
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TwoPropResult:
    p1: float
    p2: float
    diff: float
    z: float
    p_value: float  # two-sided


def two_proportion_test(x1: int, n1: int, x2: int, n2: int) -> TwoPropResult:
    """Two-sided two-proportion z-test with pooled variance.

    Null: both samples share one violation rate. Use for arm-vs-arm or
    condition-vs-condition comparisons of violation counts.
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError("sample sizes must be positive")
    p1, p2 = x1 / n1, x2 / n2
    pooled = (x1 + x2) / (n1 + n2)
    se = math.sqrt(pooled * (1.0 - pooled) * (1.0 / n1 + 1.0 / n2))
    if se == 0.0:
        # Both rates identical at 0 or 1: no evidence against the null.
        return TwoPropResult(p1, p2, p2 - p1, 0.0, 1.0)
    z = (p2 - p1) / se
    p_value = 2.0 * (1.0 - normal_cdf(abs(z)))
    return TwoPropResult(p1, p2, p2 - p1, z, p_value)


def required_n_per_arm(
    p1: float, p2: float, alpha: float = 0.05, power: float = 0.80
) -> int:
    """Sample size per arm to detect p1 vs p2, two-sided level-alpha z-test."""
    if p1 == p2:
        raise ValueError("p1 and p2 must differ")
    z_a = normal_ppf(1.0 - alpha / 2.0)
    z_b = normal_ppf(power)
    pbar = (p1 + p2) / 2.0
    num = z_a * math.sqrt(2.0 * pbar * (1.0 - pbar)) + z_b * math.sqrt(
        p1 * (1.0 - p1) + p2 * (1.0 - p2)
    )
    return math.ceil((num / (p2 - p1)) ** 2)


# ---------------------------------------------------------------------------
# Judge-error correction (Rogan-Gladen)
# ---------------------------------------------------------------------------


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed violation rate for judge FP/FN error.

    observed = pi * se + (1 - pi) * (1 - sp)  =>  pi = (obs + sp - 1) / (se + sp - 1)
    Requires se + sp > 1 (judge better than chance). Result clipped to [0, 1].
    """
    denom = sensitivity + specificity - 1.0
    if denom <= 0.0:
        raise ValueError("judge must satisfy sensitivity + specificity > 1")
    return min(1.0, max(0.0, (observed_rate + specificity - 1.0) / denom))


# ---------------------------------------------------------------------------
# (c) Delegation-chain survival: analytic + Monte Carlo
# ---------------------------------------------------------------------------


def chain_survival_analytic(p: float, depth: int) -> float:
    """P(constraint survives k hops) when each hop preserves it i.i.d. w.p. p."""
    return p**depth


def expected_first_loss_depth(p: float) -> float:
    """E[depth of first loss] = 1 / (1 - p) (geometric); inf if p == 1."""
    if p >= 1.0:
        return math.inf
    return 1.0 / (1.0 - p)


def chain_survival_mc(
    p: float, depth: int, trials: int = 20_000, seed: int | None = None
) -> float:
    """Monte Carlo estimate of p**depth: simulate `trials` chains of `depth` hops."""
    rng = random.Random(seed)
    survived = 0
    for _ in range(trials):
        for _hop in range(depth):
            if rng.random() >= p:
                break
        else:
            survived += 1
    return survived / trials


def chain_survival_mc_restoration(
    p: float, r: float, depth: int, trials: int = 20_000, seed: int | None = None
) -> float:
    """Survival at depth k in a two-state chain where a lost constraint can be
    restored (e.g., re-injected by a system prompt) with per-hop probability r.

    Analytic value: pi_inf + (1 - pi_inf) * (p - r)**k with pi_inf = r / (1 - p + r).
    """
    rng = random.Random(seed)
    present_at_depth = 0
    for _ in range(trials):
        present = True
        for _hop in range(depth):
            present = (rng.random() < p) if present else (rng.random() < r)
        if present:
            present_at_depth += 1
    return present_at_depth / trials


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------


def _demo() -> None:
    print("Delegation-chain constraint survival: analytic p^k vs Monte Carlo")
    print("(20,000 chains per cell; MC column shows estimate with 95% Wilson CI)")
    print()
    depths = (1, 2, 4, 8, 16)
    header = "p      E[first loss]  " + "".join(f"k={d:<21}" for d in depths)
    print(header)
    print("-" * len(header))
    trials = 20_000
    for p in (0.5, 0.8, 0.95):
        cells = []
        for d in depths:
            exact = chain_survival_analytic(p, d)
            mc = chain_survival_mc(p, d, trials=trials, seed=hash((p, d)) & 0xFFFF)
            ci = wilson_interval(round(mc * trials), trials)
            cells.append(f"{exact:.3f}~{ci.point:.3f}±{(ci.hi - ci.lo) / 2:.3f}   ")
        efl = expected_first_loss_depth(p)
        print(f"{p:.2f}   {efl:>6.1f} hops   " + "".join(cells))

    print()
    print("Two-proportion z-test demo: 10/100 vs 30/100 violations")
    res = two_proportion_test(10, 100, 30, 100)
    print(f"  p1={res.p1:.2f} p2={res.p2:.2f} z={res.z:.3f} p-value={res.p_value:.5f}")

    print()
    print("Sample size per arm (alpha=0.05 two-sided, power=0.80):")
    for p1, p2 in ((0.10, 0.30), (0.10, 0.20), (0.05, 0.15), (0.30, 0.50)):
        print(f"  detect {p1:.2f} vs {p2:.2f}: n = {required_n_per_arm(p1, p2)}")

    print()
    print("Rogan-Gladen correction (judge sensitivity=0.90, specificity=0.95):")
    for obs in (0.10, 0.14, 0.30):
        print(f"  observed rate {obs:.2f} -> corrected {rogan_gladen(obs, 0.90, 0.95):.3f}")

    print()
    print("Restoration channel (p=0.8, r=0.3): survival plateaus instead of dying")
    pi_inf = 0.3 / (1 - 0.8 + 0.3)
    for d in (1, 4, 16):
        mc = chain_survival_mc_restoration(0.8, 0.3, d, seed=d)
        exact = pi_inf + (1 - pi_inf) * (0.8 - 0.3) ** d
        print(f"  k={d:<3} analytic={exact:.3f} mc={mc:.3f} (plateau pi_inf={pi_inf:.3f})")


if __name__ == "__main__":
    _demo()
