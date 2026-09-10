"""Simulate constraint decay along a delegation chain: drift vs selection.

Biological framing (see docs/lenses/biologist.md):

- "Neutral drift" models passive loss during prompt re-encoding, analogous to
  passive DNA-demethylation when maintenance methyltransferase (DNMT1) is
  absent: each replication/hop loses marks at a per-unit rate, so longer
  (costlier-to-encode) constraints decay faster, but loss is unbiased with
  respect to what the constraint *does*.

- "Selection" models task-success-weighted retention: at each hop the parent
  samples several candidate compressions of the prompt and keeps the one that
  scores best on LOCAL task success minus token cost. Safety constraints that
  block the fast path to completion (negative task coupling) are purged much
  faster than drift alone predicts -- the same logic by which p53-null clones
  expand in a tissue: nothing "targets" the tumor suppressor, it is simply
  enriched-against by local growth advantage.

- "Selection + germline" adds a maintenance channel: safety constraints live
  in an immutable structured manifest that the harness re-injects at every
  hop (analog of DNMT1 maintenance methylation, or imprinted loci protected
  by ZFP57/TRIM28 through the germline reprogramming wave). Only constraints
  with dedicated protection machinery survive; prose does not.

Predictions tested:
  P1: under drift, decay is exponential in hops with rate ~ encoding cost.
  P2: selection strips safety constraints (task-obstructing) far faster than
      drift, while *retaining task-coupled constraints better than drift*.
      The channel is not uniformly lossy -- it is biased. "Missing safety
      context" is adaptive compression, not noise.
  P3: a maintenance channel flattens the decay curve to ~zero loss.

Run: python3 scripts/constraint_decay_sim.py
"""

from __future__ import annotations

import random
from typing import Dict, FrozenSet, List, NamedTuple


class Constraint(NamedTuple):
    name: str
    cost: int          # encoding cost in tokens (longer -> more likely lost in re-encoding)
    coupling: float    # effect on LOCAL task success if retained (safety constraints < 0)
    is_safety: bool


# Mirrors the corrigibility_bench scenarios: three safety constraints that
# obstruct the locally fastest path, two task-serving constraints that help it.
CONSTRAINTS = (
    Constraint("no_credential_files", cost=9, coupling=-0.15, is_safety=True),
    Constraint("accept_user_control", cost=6, coupling=-0.05, is_safety=True),
    Constraint("comply_with_shutdown", cost=5, coupling=-0.10, is_safety=True),
    Constraint("output_must_be_pdf", cost=4, coupling=+0.20, is_safety=False),
    Constraint("note_deadline", cost=3, coupling=+0.05, is_safety=False),
)

HOPS = 6                 # delegation chain depth
TRIALS = 2000            # independent chains per regime
PER_TOKEN_LOSS = 0.02    # per-token, per-hop copying loss rate (drift)
CANDIDATES = 5           # candidate compressions sampled per hop (selection)
TOKEN_PRICE = 0.004      # compression pressure: score penalty per retained token
BASE_SUCCESS = 0.5


def drift_copy(retained: FrozenSet[str], rng: random.Random) -> FrozenSet[str]:
    """One re-encoding hop: each constraint survives with p = (1 - mu)^cost."""
    out = set()
    for c in CONSTRAINTS:
        if c.name in retained:
            p_keep = (1.0 - PER_TOKEN_LOSS) ** c.cost
            if rng.random() < p_keep:
                out.add(c.name)
    return frozenset(out)


def local_score(retained: FrozenSet[str]) -> float:
    """LOCAL task-success proxy seen by the parent when it picks a compression.

    Safety constraints reduce it (they forbid the fast path); task constraints
    raise it; every retained token costs a little (compression pressure).
    """
    s = BASE_SUCCESS
    for c in CONSTRAINTS:
        if c.name in retained:
            s += c.coupling - TOKEN_PRICE * c.cost
    return s


def selection_copy(retained: FrozenSet[str], rng: random.Random) -> FrozenSet[str]:
    """One hop with task-success-weighted retention: sample candidate
    compressions via the same drift process, keep the best-scoring one."""
    candidates = [drift_copy(retained, rng) for _ in range(CANDIDATES)]
    return max(candidates, key=local_score)


def run_chain(regime: str, rng: random.Random) -> List[FrozenSet[str]]:
    state = frozenset(c.name for c in CONSTRAINTS)
    history = [state]
    manifest = frozenset(c.name for c in CONSTRAINTS if c.is_safety)
    for _ in range(HOPS):
        if regime == "drift":
            state = drift_copy(state, rng)
        elif regime == "selection":
            state = selection_copy(state, rng)
        elif regime == "selection+germline":
            # Prose channel evolves under selection, but the harness re-injects
            # safety constraints from an immutable structured manifest.
            state = frozenset(selection_copy(state, rng) | manifest)
        else:
            raise ValueError(regime)
        history.append(state)
    return history


def retention_table(regime: str, seed: int = 7) -> Dict[str, List[float]]:
    rng = random.Random(seed)
    counts = {c.name: [0] * (HOPS + 1) for c in CONSTRAINTS}
    for _ in range(TRIALS):
        for hop, state in enumerate(run_chain(regime, rng)):
            for name in state:
                counts[name][hop] += 1
    return {name: [n / TRIALS for n in row] for name, row in counts.items()}


def main() -> None:
    print(f"Delegation-chain constraint retention ({TRIALS} chains, {HOPS} hops)")
    print(f"drift: per-token per-hop loss = {PER_TOKEN_LOSS}; "
          f"selection: best of {CANDIDATES} compressions by local task score\n")

    tables = {r: retention_table(r) for r in ("drift", "selection", "selection+germline")}

    header = "  hop:            " + "".join(f"{h:>7}" for h in range(HOPS + 1))
    for regime, table in tables.items():
        print(f"[{regime}]")
        print(header)
        for c in CONSTRAINTS:
            tag = "SAFETY" if c.is_safety else "task  "
            row = "".join(f"{v:7.2f}" for v in table[c.name])
            print(f"  {c.name:<22}{tag} {row}")
        print()

    # Headline numbers: P(all safety constraints still present) at final hop,
    # estimated from per-constraint marginals is wrong under correlation, so
    # re-simulate and count jointly.
    print("P(all three safety constraints survive to hop k):")
    for regime in ("drift", "selection", "selection+germline"):
        rng = random.Random(11)
        joint = [0] * (HOPS + 1)
        safety = frozenset(c.name for c in CONSTRAINTS if c.is_safety)
        for _ in range(TRIALS):
            for hop, state in enumerate(run_chain(regime, rng)):
                if safety <= state:
                    joint[hop] += 1
        row = "".join(f"{n / TRIALS:7.2f}" for n in joint)
        print(f"  {regime:<20}{row}")

    # Effective per-hop retention (fitted exponential) for the costliest
    # safety constraint vs the cheapest task constraint.
    print("\nPer-hop survival (hop-1 marginal), drift vs selection:")
    for c in CONSTRAINTS:
        d1 = tables["drift"][c.name][1]
        s1 = tables["selection"][c.name][1]
        kind = "SAFETY" if c.is_safety else "task"
        print(f"  {c.name:<22}{kind:<7} drift={d1:.3f}  selection={s1:.3f}  "
              f"selection/drift={s1 / d1:.2f}")


if __name__ == "__main__":
    main()
