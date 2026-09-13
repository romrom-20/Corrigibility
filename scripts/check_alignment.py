"""Continuous alignment checker: spec (.context/attachments) vs code. Run: python3 scripts/check_alignment.py"""
import sys
sys.path.insert(0, ".")
from corrigibility_bench.normative_hysteresis import *

fails = []
def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (" " + detail if detail and not cond else ""))
    if not cond: fails.append(name)

# 1. unique A/B optima, distinct
for sid, s in SCENARIOS.items():
    a, b = s.optimum(s.rule_a), s.optimum(s.rule_b)
    check(f"optima-unique-distinct:{sid}", a != b, f"{a} vs {b}")
# 2. banned vocab absent from all stimuli
for sid in SCENARIOS:
    for c in (*MAIN_CONDITIONS, F0, F1):
        for k in (0, 1, 3):
            t = Trial(sid, c, k, 0)
            h = freeze_history(t, ["neutral placeholder artifact words only"] * k)
            for br, ctx in branch_contexts(t, h).items():
                check(f"banned:{sid}/{c}/k{k}/{br}", not banned_terms(ctx))
                if fails and fails[-1].startswith("banned"): break
# 3. replacement identical C1==C2; decision constant shared
check("replacement-C1==C2",
      transition(Trial("shipping", C1, 1, 0)) == transition(Trial("shipping", C2, 1, 0)))
# 4. branches share frozen prefix; behavior never in uptake
t = Trial("shipping", C2, 1, 0); h = freeze_history(t, ["x " * 10])
br = branch_contexts(t, h)
check("branch-shared-prefix", br["behavior"][:-1] == br["uptake"][:-1])
check("no-behavior-in-uptake",
      br["behavior"][-1]["content"] not in br["uptake"][-1]["content"])
# 5. k=0 has no A-optimization artifact
for c in MAIN_CONDITIONS:
    check(f"k0-no-artifact:{c}", planning_prompts(Trial("shipping", c, 0, 0)) == [])
# 6. factual control changes fact, keeps objective fixed
for c in (F0, F1):
    tr = transition(Trial("shipping", c, 0, 0))
    check(f"factual-fixed-objective:{c}", "objective remains" in tr.lower())
# 7. position counterbalance sanity (report only)
print("--- positions (A_idx,B_idx) per variant: want no systematic A-before-B ---")
for sid in SCENARIOS:
    for v in (0, 1):
        t = Trial(sid, "FRESH_B", 0, v); tbl, _ = display_world(t)
        labels = [l.split(" | ")[0] for l in tbl.splitlines()[2:]]
        g = truth(t); inv = {s: l for l, s in g["label_to_semantic"].items()}
        print(f"  {sid} v{v}: A@{labels.index(inv[g['old_optimum']])} B@{labels.index(inv[g['final_optimum']])} {labels}")
print("RESULT:", "FAIL" if fails else "ALL PASS", fails if fails else "")
sys.exit(1 if fails else 0)
