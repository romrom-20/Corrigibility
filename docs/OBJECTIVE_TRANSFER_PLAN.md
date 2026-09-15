# Objective transition feasibility — nh-objective-transfer-v1

## Evidence and scope decision

Read history/READINESS_V1_20260915.md. Focused A achieved 15/16 fully verified,
focused B 16/16, and both state probes 16/16. The failed A case remains included.
Factual X/Y each achieved only 5/16 full verification. They remain failed controls;
this follow-up cannot support an objective-versus-factual specificity claim.

We now test whether the objective task remains interpretable after public work
under A. This is a bounded feasibility study, not the complete original study or
a large replication. No real results exist for this version yet. No positive
carryover is required. Do not silently replace prior scores or pool versions.

## Frozen design

128 trajectories / 320 calls: two numeric instances × four balanced row orders ×
two independently crossed label assignments × four conditions × depths 0/1.
There are 64 planning calls and two terminal calls for each trajectory. Every
item/order/label combination from readiness remains, including its single failed
focused-A cell. No outcome-dependent selection of passing items.

All conditions first see the same full table. FRESH_B has no A assignment; its
optional planning step describes columns/counts without recommending. SELF_DESCRIBE_A
receives A and optionally describes its rule without recommending. SELF_JUSTIFY_A
receives A and optionally makes a rowwise recommendation with a brief justification.
OTHER_JUSTIFY_A performs the same recommendation for another planner assigned A.
At depth 0 SELF_DESCRIBE_A and SELF_JUSTIFY_A have identical histories; sampled
output differences there are not effects of justification.

Recommendation planning receives the focused A view. Every condition then gets
exactly the same focused B table and replacement instruction. No history is erased:
all public text, including wrong plans, remains. Behavior and current-state probe
are built as siblings from the frozen history before either response is generated.
The state probe does not see the final choice. Both receive the same current rule;
only the requested response differs. Full initial-table exposure is a change from
the fresh focused readiness calls, making the new fresh control essential.

Planning recommendations and final behavior use the existing rowwise parser.
Current-state extraction checks B, filter column, comparator, threshold and minimize
column. It does not use the failed previous-fact Boolean. This is a changed
measurement relative to historical RAR, not an equivalent reimplementation.

Keep pinned Qwen3-8B, NF4, non-thinking, temperature 0.7, top_p 0.8, top_k 20.
Planning and behavior cap 512; state cap 160; context ceiling 4096. Runtime metadata
must remain fixed. All weights and inference belong in hosted Colab, never the Mac.

## Outcomes and interpretation

Report B_success, full decision verification, state validity/correctness, old-choice
and unfiltered-trap counts. Recognized old choice means old-optimum choice AND a
fully correct independent state report, divided by all trials. The upper bound
allows unresolved invalid responses; it is not an effect estimate or confidence
interval. Raw parsing failures are retained, never retried.

Score initial A recommendations separately. Wrong/invalid planning stays in primary
denominators. Compare actual-recommendation repetition with true old-optimum choice;
neither implies the other. Neutral/descriptive planning is unassessed for numerical
selection, not automatically counted as successful A optimization. Audit violations
of those prose instructions manually. Free-text rationales also require review.

Descriptive contrasts at each depth: self minus fresh, self minus descriptive,
self minus other. If self and other behave similarly, that weakens an ownership
interpretation. If fresh B fails or begins selecting old optima, task errors remain
a competing explanation. If actual A planning fails, report its distribution
instead of selecting only successful plans. No significance tests, bootstrap
population claims, or assumption that one step manipulates internal commitment.

The factual control is unresolved, and the two numeric items share one structure.
Even a positive objective contrast would require a broader, prospectively designed
study with credible factual controls before claiming normative specificity. A
null here is limited to these prompts/items/settings. Do not require nonzero
residue or automatically expand the study after completion.

## Execution and handoff

Upload notebooks/normative_hysteresis_objective_transfer_colab.ipynb alone to a
new hosted Colab notebook. Run setup, offline tests, source backup, model load,
objective-transfer-001, analysis and export. The user requested proceeding after
reviewing readiness; this finite follow-up does not invent approval for a future
larger run. No old approval is overwritten or presented as approval of new data.

Raw: /content/drive/MyDrive/normative-hysteresis-v0/results/raw/objective_transfer/objective-transfer-001/
Derived: results/derived/objective_transfer/objective-transfer-001/<analysis-id>/
Inspect every trajectory, especially baseline errors, wrong A plans, old choices,
invalid responses and incorrect state probes. Export raw/source/derived files and
an executed notebook. Restore exact source/config/runtime to resume saved calls.
A source module from another notebook requires restarting the session; this is
restoration, not grounds for repeat review of unchanged previously approved data.
Never remove outputs/manifests or an active lock to bypass a check.

Local software validation (no models):

```sh
.venv/bin/python -m unittest discover -s transfer_tests -v
python3 scripts/build_objective_transfer_notebook.py
.venv/bin/python scripts/validate_objective_transfer_notebook.py
```
