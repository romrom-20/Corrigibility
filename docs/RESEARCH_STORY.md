# Before we can measure resistance to correction, we have to measure execution

*A research notebook in prose, through 18 September 2026. The experiments below
are exploratory and concern one pinned model configuration on small artificial
tasks. This account separates observed outputs, software checks, and hypotheses.
Sections 1-11 cover work through 16 September; sections 12-13 report the
completed instrument-qualification runs of 17-18 September.*

We started with a question about what happens after an objective changes. A model
has been asked to optimize for A. It has publicly worked on that objective, perhaps
explaining and defending a recommendation. Then the user explicitly replaces A
with B. Does the earlier work continue to pull the model toward A's preferred
answer, even when it can state that B now governs?

That is still the research question. But the most important thing we have learned
so far is how easily a much simpler failure can look like the answer to it.
A model can choose the old optimum because it miscompares two numbers. It can
name the new rule while applying its filter incorrectly. It can select the correct
final label while omitting eligible options from its explanation. And asking it
to show more structure can introduce new errors rather than certify the answer.

We have not established normative hysteresis. We have accumulated evidence about
why the measurement is difficult, narrowed several failure modes, and reached a
more informative next experiment. This is progress in diagnosis, not a steadily
rising capability curve.

## 1. What would count as the phenomenon?

The [original brief](original_research_brief.md) defines a demanding target:
residual influence of a superseded objective, beyond ordinary text exposure,
factual-update inertia and useful information reuse. Merely getting a new task
wrong does not meet that definition. Neither does repeating an earlier answer.

The design therefore needs multiple comparisons. A fresh-B condition measures
errors when the model has no earlier A assignment. Descriptive A exposure asks
whether the earlier information alone matters. Reasoning for another planner
helps distinguish an ownership interpretation from generic exposure to arguments.
A factual-update control asks whether any persistence is specific to objectives
rather than difficulty replacing information generally. Planning depth probes
whether additional public work changes the contrast, although turn count is not
itself a clean measure of psychological commitment.

There are also two different things we must track: selecting the *true old optimum*
and repeating the model's *actual earlier recommendation*. If the model's original
A plan was wrong, these need not be the same option. A model that repeats an
incorrect shortcut has not thereby demonstrated persistence of the objective it
was supposed to optimize.

Even the current-rule probe has a limit. In these experiments, a state-report
response and a decision response can be separate branches from the same context.
A correct report in one branch does not prove that the other branch represented
or used the rule correctly. The conjunction is an observable measurement, not a
window into the model's internal goals.

## 2. The first smoke: an apparently interesting result with a broken foundation

The [original smoke audit](audits/smoke-001-20260913/review.md) covered 32 shipping
trajectories. Objective choices were correct in only 2/24 cases; factual choices
were correct in 8/8; current-instruction uptake passed 32/32. Nine responses chose
the old objective's optimum. Read superficially, that combination could sound
like a model stating the new instruction while refusing to move on.

The controls undermined that interpretation. Fresh B was correct in 0/6 trials.
All nine old-option choices belonged to one label/order variant. Self-justification
and other-planner justification made the same semantic choices in every matched
variant/depth cell. Self-justification residue was 1/2 at each depth, rather than
increasing with public investment. There was no ownership contrast to explain.

The transcripts were more informative than the final labels. Some wrong choices
were ineligible fastest-overall options; others were slower eligible options.
Three of the ten correct final choices still contained substantive planning or
rationale errors. Being right at the endpoint was already an inadequate measure
of executing the task faithfully.

Then a separate software issue appeared. Checkpoint generation defaults could
override the requested greedy settings, and the old backend recorded the requested
configuration rather than necessarily the effective one. The
[runtime addendum](audits/smoke-001-20260913/runtime_addendum.md) records that finding.
The backend was changed to disable model-default substitution, check effective
settings, and record what generation actually used.

This mattered for provenance: the old run could not be called verified greedy
inference. It did not erase its responses, make their annotations meaningless,
or establish that every subsequent mistake was a backend bug. The later experiments
used the corrected policy. We must resist carrying one real early software failure
forward as an untested explanation for all later behavioral failures.

## 3. Shortlists made intermediate errors visible

The [shortlist v1 pilot](history/PILOT_SHORTLIST_20260915.md) completed 432
trajectories and 1,440 calls on a T4. It expanded beyond shipping and required a
more explicit account of eligible options. Across the mixed tasks, final choices
were correct in 318/432 cases, but only 223/432 decisions were fully verified.
Those pooled numbers describe the run; they are not an estimate of hysteresis.

The scenario-level differences explain why. Compute fresh B managed only 2/18
correct choices. Venue fresh B got 18/18 final choices right, but 0/18 complete,
verified shortlists. Shipping objective conditions were correct in all 72 cases,
with no old-optimum choices. Production self-justification fell to 10/18 correct,
but none of those self errors chose the true old optimum. A degradation after
history is not automatically persistence of A.

There were only five objective old-optimum choices in the pilot. The two self
cases occurred at depth one and shared a variant; both earlier public artifacts
had recommended a different option from the eventual old optimum. At depth three,
there was no objective residue. That is not the pattern we would want to label
increasing entrenchment.

The factual controls were also not clean. Shipping and compute fresh Y each
scored 8/18. Venue fresh Y chose correctly in 18/18 cases, while 15/18 uptake
responses incorrectly said the previous fact still governed. The mismatch suggested
that the probe itself needed investigation, in addition to task performance.

The lesson was methodological: a smoke covering one scenario under one decoding
regime cannot establish competence for a more varied sampled pilot. And a final
label can conceal a failed operation that happens not to change that label.

## 4. The diagnostic smoke: correct copying is not correct filtering

The [v2 diagnostic smoke](history/DIAGNOSTIC_V2_20260915.md) contained 144
trajectories and 480 responses. It made the original planning more structured
and examined those intermediate outputs. Objective choices were correct in 67/96
cases, but only 43/96 were fully verified. There were zero observed objective
old optima, despite substantial task failure. Factual choices were correct in
35/48 cases, with three old-option choices, two of them in fresh Y.

Compute was particularly revealing. Fresh B was correct in 0/6 cases. Initial
self-justification A choices were correct in 0/8. The model could copy runtime 28
correctly, retain that option under a runtime<=22 condition, and then minimize
over the wrong set. A correct copied number did not demonstrate that the relevant
comparison had been performed.

Venue again produced correct final labels with incomplete sets: 6/6 fresh-B
choices, 0/6 verified shortlists. Structured planning across the run was correct
in 60/96 choices and fully verified in only 40/96. No reported truncation explained
these failures. Increasing the output budget was therefore not the obvious next
intervention supported by this evidence.

This stage also exposed collisions in the tasks. If the unrestricted minimum is
already the correct B answer, a model can ignore the eligibility rule and still
look successful. In a factual shipping task, stale-X minimization and completely
unfiltered minimization could select the same option. These are different problems:
one hides a failure inside an apparent success; the other makes two erroneous
processes observationally indistinguishable. Future tables needed distinct traps.

The uptake probe had its own recurring pattern. All 24 fresh-fact responses named
Y yet said the previous fact still governed; all 24 changed-fact probes passed.
Possible explanations included a misleading presupposition about a previous fact,
confusion between an unchanged objective and a replaced fact, and a template-driven
response habit. The observations did not choose between those explanations.

## 5. Calibration: simplify the operations before interpreting the behavior

The [272-call calibration](history/CALIBRATION_V1_20260915.md) moved to isolated
fresh tasks on an A100. It compared the original shortlist, a small wording change,
a rowwise classification format, computer-filtered ranking, and state probes.

The original shortlist achieved 17/48 fully correct outputs. Rewording achieved
22/48. Rowwise classification achieved 37/48, with all copied values correct and
42/48 eligibility masks correct. The improvement was useful but incomplete:
five correct-mask responses still selected the wrong minimum.

Computer-filtered ranking achieved 46/48. That simplified task removed both
filtering and irrelevant columns, so its success could not establish that the
original full task was repaired. It did, however, motivate separating operations
instead of continuing to add instructions to the combined problem.

The strongest warning against a premature hysteresis claim came from compute
rowwise B. It scored 0/4. In two trials, the numbers and eligibility mask were
correct, yet the model chose quartz, the old A optimum, rather than jade. There
had been no A assignment or prior planning in those fresh calls. An old-optimum
choice with correct filtering can arise without objective history at all.

The new state probe correctly reported the current label and numeric limit in
40/40 cases and all fields in 37/40. The older probe achieved only 26/40 fully
correct, with all 14 failures in the previous-fact Boolean in fresh contexts.
This supported changing future measurement rather than retroactively forgiving
old failures. A new probe gets a new protocol; earlier primary scores stay frozen.

## 6. Fresh readiness and a deliberately narrower transition test

The [192-call readiness test](history/READINESS_V1_20260915.md) constructed clearer
error traps, crossed labels and row order independently, and compared full tables
with relevant-column views. Focused A achieved 15/16 fully verified and focused B
16/16. Full A and B achieved 9/16 and 10/16 fully verified. Reducing irrelevant
attributes looked useful for these objective tasks.

The factual rules remained weak. Focused X and Y each achieved only 5/16 fully
verified; full X and Y achieved 3/16 and 1/16. The model often omitted faster rows
that satisfied the limit even when it copied their times correctly. The focused
view was a candidate scaffold, not a universal cure.

We then tried a bounded objective-only transition feasibility test, explicitly
setting aside any objective-versus-factual specificity claim. The
[transfer run](history/OBJECTIVE_TRANSFER_V1_20260915.md) completed 128 trajectories
and 320 calls. All 128 final responses copied values and marked eligibility
correctly, all state reports were correct, and 117/128 decisions selected B's
optimum. The remaining errors were ten old optima and one unfiltered trap.

At depth zero, old choices were fresh 0/16, describe 2/16, self 1/16, other 2/16.
At depth one, they were fresh 1/16, describe 1/16, self 2/16, other 1/16.
The self-minus-fresh excess was one case at both depths. Eight of ten old choices
shared one row order, and nine selected NORI. This made presentation sensitivity
at least as pressing an explanation to investigate as prior self-directed work.

## 7. Replication: the suspected history pattern did not strengthen

The [512-trajectory replication](history/OBJECTIVE_REPLICATION_V1_20260916.md)
expanded label rotations and seed replicates and added an explicit-comparison
sibling. It completed 1,536 calls. Baseline decisions were verified in 487/512
cases; all 512 current-state reports were correct. Every failed baseline answer
had correct copied values and eligibility masks but selected the wrong minimum.

Of the 25 errors, 23 chose the old optimum and two chose the unfiltered trap.
Twenty-four errors shared label rotation one; 22 selected NORI. That clustering
is descriptive evidence of presentation sensitivity, not proof of a specific
label mechanism. The depth pattern again did not support a clean entrenchment
story. Self old-choice counts decreased from 4/64 at depth zero to 3/64 at depth
one. At depth one, each control had 2/64 old choices. One extra self case is not
a convincing ownership-and-investment pattern in this setting.

Asking for an explicit comparison did not reliably rescue execution. On the
matched subset, success moved from 245/256 to 243/256: three fixes and five harms.
Some explanations named the correct smaller number or label while the final
choice named something else. Other explanations contained false comparisons.
Because siblings used separate sampled draws, each fix or harm is not a causal
story about that individual response. At the experiment level, this was still a
failed candidate repair.

## 8. The ranked certificate made things worse

The [768-call execution screen](history/EXECUTION_READINESS_V1_20260916.md)
returned to fresh tasks and restored the factual rules. It tested a prospectively
chosen ranked-output candidate against rowwise classification and state reporting.
The hope was that an ordered eligible list would expose or stabilize minimum
selection. The candidate failed.

Fully verified rowwise A/B/X/Y scores were 59/64, 64/64, 24/64 and 23/64.
Ranked scores were 54/64, 45/64, 2/64 and 15/64. Across matched cases, ranking
fixed eight and harmed 62 verified outcomes. The prospectively planned confirmation
was not warranted by that result; substituting the passing rowwise B slice after
seeing the screen would change the question.

Ranked B copied and classified every row correctly, yet reversed 17 eligible
pairs. Fourteen resulting choices followed the wrong order; three choices were
correct despite contradicting the order. Two additional rankings omitted an
eligible label. More requested structure had created new failure opportunities,
not an independent proof of a reliable computation.

Factual eligibility was even more revealing. Across X/Y formats, 114 eligible
rows were falsely excluded. All were strictly inside the time limit, not equality
cases. An explanation that only fixes the meaning of <= cannot account for that
pattern. The high-cost eligible row was disproportionately omitted, making a
mix-up between eligibility and desirability a plausible hypothesis. It remained
a hypothesis: multi-row load and column binding could also contribute.

State reporting showed a different kind of problem. All eleven failed X reports
copied the literal string “A or B or X or Y” from the example schema. Every
numerical, column and operator field was correct in all 256 state probes. The
frozen exact scorer properly counted the identifier as wrong, but the error does
not say the model reported the wrong threshold. Treating all failures as one
undifferentiated lack of understanding would discard useful information.

A runtime interruption also illustrated why recovery needs care. A saved T4 run
correctly refused to resume with A100 metadata. After T4 was restored, all 768
records completed, but missing-lock cleanup obscured successful completion.
Subsequent runner work made ownership explicit, preserved primary exceptions and
allowed completed-run validation without reloading a model. That is a software
reliability improvement, separate from any behavioral result.

## 9. The latest component run: context changes even the direction of errors

The [component diagnostic](history/COMPONENT_DIAGNOSTIC_V1_20260916.md) is the
latest completed run: 480 independent fresh calls on recorded T4 metadata. Unlike
several earlier pasted-transcript reviews, this inspection had the source snapshot,
manifest, raw records and completion digest. All 480 records validate against the
frozen constructors and scorer; all headline summary counts reproduce. There are
no invalid responses or reported truncations. The supplied directory does not
include an executed notebook, so artifact consistency remains distinct from
independent verification of the actual runtime.

The design asked three smaller questions: can the model evaluate an individual
eligibility predicate, choose between two numbers, and report rule state without
copying the schema's alternatives?

Bare numerical eligibility was correct in 64/64 calls. The contextual version,
which showed one option's attributes and the filtering-plus-optimization rule,
was correct in only 49/64. Crucially, all 15 contextual errors were false positives.
The model accepted 15/28 ineligible options while correctly accepting all 36 eligible
ones. For example, it returned true for quality
20 under quality>=90, and true for time30 under time<=10. Every PAX row under
A and B was wrongly accepted in these four tables, but PAX was tied to the same
semantic role; that cannot isolate a label preference.

This differs from the previous full-table screen, where the dominant factual
problem was omitting eligible rows. We should not compress both observations
into “the model is too strict,” “the model says true,” or “it mishandles equality.”
The observed error direction depends on the task context. And one-row failures
mean that processing a full table is not necessary for eligibility errors to arise.

The old numeric/context contrast changes several things together: extra columns,
option naming, rule wording and an optimization instruction. It demonstrates a
performance gap between those complete prompts. It does not tell us which added
feature caused the gap. Nor does a perfect 64-call bare-predicate sample establish
universal arithmetic competence; some nominal predicates were repeated.

Pairwise comparison was strong but imperfect: numeric 94/96, named 95/96, labeled
95/96. Numeric responses sometimes selected 90 instead of 10, or 187 instead of
27. The named format also selected cost90 over cost10 once. A labeled response
selected NORI(time12) instead of PAX(time2). All four failures shared the reverse
presentation direction in this grid. That is a reason to counterbalance order
prospectively, not enough evidence to declare a general positional or digit-width
mechanism.

State reporting was 30/32 for the legacy template and 32/32 for typed instructions.
The two legacy failures again copied the alternative rule identifiers; all numeric
criteria were right in all 64 calls. This makes schema copying a better-supported
interpretation of those particular errors. It does not show that factual updating
works: no earlier fact existed in these fresh calls. With independent sampled
draws and only two observed failures, the apparent format repair needs bounded
interpretation too.

## 10. What has changed in our understanding?

We can now separate at least five observable failure classes: copying a schema
placeholder; misclassifying eligibility; selecting the wrong minimum despite a
correct mask; contradicting an intermediate ranking; and producing a correct final
label despite an incomplete or erroneous intermediate account. They need not share
a cause or respond to the same intervention.

We also have stronger reasons to be cautious about history effects. Fresh calls
can choose an option that happens to be the old optimum. Correct state reports
can coexist with wrong actions. Label/order changes can concentrate errors. More
public reasoning has not produced a convincing growing self-specific excess.
The factual controls have repeatedly failed competence checks. None of these
observations proves hysteresis absent in general; together they prevent a confident
claim that we have detected it here.

The sequence is not a controlled comparison of successive prompts. Some runs used
A100 and others T4; output formats, tables, task scopes and decoding circumstances
changed. We can describe the measurements within a run and why they motivated the
next one. We cannot attribute every cross-run improvement or decline to wording.
NF4, model capacity and decoding remain possible contributors, not diagnosed causes.

Evidence quality also varies. The earliest smoke gained a later runtime audit.
Several middle stages were reconstructed from supplied text rather than original
archive bytes. The latest component export supports source and raw-digest checks.
Those distinctions are recorded in each linked historical note. They should survive
any polished account of the work rather than disappearing behind a single headline.

## 11. The next experiments: distinguish the contextual ingredients

The [new plan](CONTEXT_DIAGNOSTIC_PLAN.md) implements a 1,280-call eligibility
experiment and a 192-call comparison experiment. Neither has run on a real model.

For eligibility, the core is a two-by-two design: relevant attribute only versus
all attributes, crossed with absence versus presence of the optimization sentence.
The Boolean question and the rest of the contextual wording stay fixed. A fifth
bare-numeric format connects the test to the previous component result. New numeric
blocks cover both inequality directions, interior and equality successes, near and
far failures, two option names and repeated independent draws. Each format has
exactly as many true as false expected answers.

If extra attributes hurt without an optimization instruction, that supports
sensitivity to added attribute context. If the optimization sentence hurts with
the row held fixed, it supports interference from the irrelevant selection demand.
If both matter together, the interaction will be reported explicitly. We will
retain the possibility that nothing fails in the new sample. We will also report
what the design does not isolate: distractor magnitudes, column order, all possible
wordings, or a specific internal process. In the relevant-only optimization arm,
cost is absent because optimization is not requested; that limitation is explicit.

For comparison, the design crosses eight numeric pairs with both directions,
three output formats and two label mappings. Three pairs are historical anchors,
five are new. Same-width and different-width numbers are both represented. The
output will separate anchors from new cases and expose fixes and harms, rather
than presenting the best-looking format as a cure. Digit-width classes contain
different pairs, so their contrast is descriptive, not a clean digit-width effect.

All 1,472 calls are fresh and independent; none receives another response or a
computer-generated answer. Invalid and truncated responses remain failures. There
is no automatic next stage or score that unlocks the original pilot. Passing these
components would move the question to composing operations in fresh full tasks,
including factual controls. Failure would give us a more specific reason to reconsider
the model, decoding or task before investing in history-bearing experiments.

The useful outcome is an experiment that distinguishes explanations, including
ones that weaken our original hypothesis. That is the standard the next results
will need to meet.

## 12. The context diagnostic runs, and a scoring bug found by the harness

The experiments prepared in section 11 have now run, and the sequence mattered
as much as the results.

The full context-diagnostic grid first ran as context-002 under the original
deployed configuration (NF4, non-thinking). On the 384 legacy_verbatim
eligibility cases it scored 76.8% (295/384), with cost-reader agreement climbing
from 56% to 77% across the distance relations added specifically to surface that
failure. The other eligibility variants were near ceiling under the same
backend, leaving little headroom to interpret there.

A process failure came first. Reusing a completed run ID silently returned the
old records rather than running new ones. Nothing was overwritten, but the
incident is why every later stage enforces fresh run IDs and why this account
treats run identity as part of the result.

The first bf16+thinking ablation then exposed a scoring bug rather than a
behavioral one. A thinking backend emits a reasoning preamble before its answer,
and the frozen scorer required the entire raw string to be JSON, marking all 384
responses invalid. Every answer after the preamble parsed cleanly. Rescored
outside the pipeline with the corrected scorer, the same 384 cases went from
76.8% under NF4/non-thinking to 100% under bf16+thinking: 89 cases fixed, 0
harmed, with every previously observed failure corrected and no regressions.
The [rescored ablation report](ABLATION_BF16_THINKING_002_RESCORED_20260918.md)
records why those numbers were provisional: the frozen-state guard correctly
refused to validate records whose manifest no longer matched the changed
scoring code, and it recommended a canonical rerun under a fresh run ID.
That refusal is the discipline working, not an obstacle to it.

Two limits were written down before the canonical rerun. Quantization and
thinking were changed together, so the combination's success does not identify
which factor did the work; single-factor conditions remain available if that
mechanism question ever matters. And the ablation covered only eligibility -
the comparison-family reversals (the deterministic 90-over-10 style errors
under greedy decoding) were a distinct failure mode, untested under the new
backend.

## 13. Qualification: both components pass under the frozen backend

The canonical rerun, ablation-bf16-think-1024-003, repeated the 384
legacy_verbatim cases under the corrected code and the frozen backend (bf16,
no quantization, thinking enabled, pinned model revision, A100), and validated
through the pipeline this time: 384/384 valid, accuracy 1.000 across all six
boundary relations, rotation balanced, zero truncations. During inspection the
run's manifest produced an unreadable-record error; per protocol it was
preserved as raw bytes with its SHA-256 recorded, not regenerated.

Comparison qualification followed as comparison-bf16-think-1024-001. The grid's
comparison family proved to be 288 cases, not the 192 a new wrapper assumed -
the design audit caught the wrong constant before any GPU spend, which is what
the audit is for. Under the same frozen backend, all 288 records were valid and
fully correct: accuracy 1.000 on each of the labeled, named and numeric formats
(96 cases each), with reverse and rotation counterbalancing exactly balanced at
144/144. The reversal failure mode from earlier sections did not appear under
thinking-enabled decoding.

The preregistered gate - all records valid, zero truncated, accuracy 1.0, exact
reverse/rotation balance, frozen backend verified - reported PASS on every
criterion. The export (737 files: sources, raw records, derived summaries, the
preserved manifest) is archived as
results/exports/nh-instrument-qualification-8bc1e1a9.zip.

What this establishes is narrower than it sounds, and worth stating plainly. The
eligibility component moved from 76.8% to 100%, and the comparison component
from a rejected 0/24 pilot to 288/288, under one frozen deployed configuration.
The instrument is qualified for that configuration. Nothing here measures
normative hysteresis: no A-history treatment arm has run under the qualified
instrument, the bf16/thinking confound is accepted rather than resolved (this
is the configuration we intend to deploy, so the combination is the unit), the
evidence covers one model family, and passing components does not by itself
certify the composed full task.

## 14. What comes next

The qualification result changes what is worth building, not what has been
shown. The plan, in order:

1. Expand from the prototype scenarios to at least twelve solver-verified
   neutral scenario families, calibrating difficulty without inspecting
   treatment effects.
2. Preregister the estimands, factorial contrasts, sample sizes, stopping
   rules and kill criteria before any history-bearing run.
3. Run the full fresh-B smoke under a new run ID, on the same frozen backend,
   with reverse counterbalancing enabled on every arm. Prompts, parser,
   scoring rules and exclusion criteria freeze before launch; there are no
   edits afterward, only results.

The standard from section 11 stands: an experiment that distinguishes
explanations, including ones that weaken the original hypothesis. The
instrument now exists to hold the next results to it.
