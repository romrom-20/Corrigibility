# Execution readiness v1 — completed screen, failed candidate

Evidence: transcripts.html supplied at
.context/attachments/Q1V26N/transcripts.html and summary/readiness output at
.context/attachments/3o5hlK/pasted_text_2026-09-16_18-10-29.txt.
All 768 unique cases reconstructed; prompt/seed/settings/hash/parser validation
and summary cell counts reproduce against execution_readiness.py. Every record
has identical Tesla T4 metadata. No invalid responses or truncation. The supplied
HTML does not independently certify the original archive bytes/manifest digest.
Colab reported successful completed-run validation and raw digest
f5affe6e828b8ac36f276ce84e60b5f7d6b8a84465262d1d86a360be09d6f123.

Verified rowwise A/B/X/Y: 59/64, 64/64, 24/64, 23/64.
Verified ranked A/B/X/Y: 54/64, 45/64, 2/64, 15/64.
Across 256 matched cases ranked fixed 8 and harmed 62 verified outcomes; different
sampled draws mean this is descriptive. Ranked was the prospective candidate and
failed. Do not run confirmation, substitute rowwise post hoc or scale to D.

Ranked B: values and eligibility all correct; 14 wrong choices, plus five correct
choices with incorrect certificates. Seventeen rankings reverse the true pair
(14 wrong choices, three correct choices contradicting the ranking); two omit an
eligible label. Rowwise B was 64/64 correct. The added certificate is not a cure.
For example, item3 rotation2 order0 ranks PAX(time19) before VEX(time12) and
chooses PAX. This fresh response has no prior A planning history.

Across X/Y both formats, 114 eligible rows were incorrectly excluded: all strictly
below the time limit, none on equality. X rowwise excludes the objective-trap role
18 times and new role five; X ranked 30 and 11. Y rowwise/ranked exclude the
objective-trap role 22/28 times. Four false-positive rows also occur in X.
The high-cost eligible row is disproportionately dropped. Conflation of eligibility
with desirability is a hypothesis, not an established cause. Correct masks still
coexist with wrong choices: X rowwise20/ranked31, Y rowwise19/ranked21.
Examples include marking time2 ineligible under time<=12, or choosing cost90 as
minimum among correctly marked costs30/50/90.

State: A/B/Y 64/64; X 53/64 under frozen exact-object scoring. ALL eleven X errors
copy current_rule="A or B or X or Y" from the schema. All numerical/column/operator
fields are correct in all 256 state probes. This is an output-template failure,
not evidence of incorrect numerical criteria. Keep original scores; prospective
probe changes get a new version. State siblings do not prove decision understanding.

Runner incident: 719 saved T4 calls could not resume on A100 (correct provenance
check); after restoring T4, 768 records and complete.json were saved. Missing-lock
cleanup obscured successful completion. Preserve historical code/notebook sources;
future runner cleanup should retain original exceptions, explain manifest differences
and allow completed-run analysis without loading another model.

Next work: frozen component isolation, not another assumed cure. Check individual
predicates, pairwise numeric/name mapping, and template copying independently.
No positive ownership effect or factual-update specificity has been established.
