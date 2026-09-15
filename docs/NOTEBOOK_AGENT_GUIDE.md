# Agent runbook — nh-v2-diagnostic in Colab

Read this file, `EXPERIMENT_GUIDE.md`, and `RUN_HANDOFF.md` before operating the
notebook. This runbook supersedes the old mixed-notebook A–E instructions.

The user authorized implementing the revision and preparing it for another agent
to run in Colab. Perform setup, smoke, diagnostics, review preparation and export
without redundant permission questions when asked to execute. Once the human has
approved this exact new smoke and requested scaling, continue D, analysis and E.
Do not interpret the current preparation request as human approval of unseen data.

## Boundaries and current status

- Every model download, model load and real inference call belongs in Colab.
  The laptop is for source, offline tests and small result artifacts. Do not
  install `requirements-colab.txt` or run the inference CLI on the Mac.
- Use **`notebooks/normative_hysteresis_diagnostic_colab.ipynb`**. It is self-contained;
  upload that single file. The older `normative_hysteresis_shortlist_colab.ipynb`, `normative_hysteresis_v0_colab.ipynb` and
  historical live notebook contain different source and are not this protocol.
- Version must be `nh-v2-diagnostic`. Defaults are `smoke-diagnostic-001` and
  `pilot-diagnostic-001`. No real run of this revision was performed during preparation.
- Human decisions for old smoke runs remain unchanged. They cannot approve this
  changed prompt/schema/design. Do not repair an old rejected review into approval.
- Read experiment meaning, controls, predictions, metrics and limitations in
  `EXPERIMENT_GUIDE.md`. In particular, the scaffold itself changes the estimand.

## Prepare the portable notebook

If you change source, tests, config or current docs, rebuild from canonical files:

```sh
.venv/bin/python -m unittest discover -s tests -v
python3 scripts/build_colab_notebook.py
.venv/bin/python scripts/validate_colab_notebook.py
```

The validator runs a **synthetic** smoke and full pilot through notebook cells,
checks the initially closed gate, reuses a fixture approval twice, analyzes and
exports both. That is software validation, never human approval or model evidence.
It creates an executed notebook under `.context/validation/`.

Freeze all experiment changes before real smoke. A commit is useful, but exact
source hashes and the notebook bundle are the provenance even with uncommitted
edits. Do not alter source after smoke and expect its approval to transfer.
Do not hand-edit the notebook's compressed payload.

## A — Extract, check, freeze settings and mount Drive (sections 1–5)

1. Open the new notebook in Colab and choose a GPU. The completed v1 pilot used
   Tesla T4. NF4 is intended for a T4-class 16 GB device or larger, with actual memory
   checked on the assigned GPU. Keep the same GPU/library metadata through pilot.
   Do not connect Colab to the laptop as a local runtime.
2. Run extraction. It prints `BUNDLE_SHA256` and creates
   `/content/nh-diagnostic-src-<bundle hash prefix>`. It rejects a different already
   imported package and refuses to overwrite edited files. If needed, restart the
   session and extract again; do not bypass these checks.
3. Run dependency installation and software tests. If installation changes an
   already imported library, restart and rerun. Tests must have no failures/skips.
4. Freeze settings. Both config and notebook pin Qwen/Qwen3-8B to
   `b968826d9c46dd6066d109eabc6255188de91218`, non-thinking, NF4. Keep seed 20260913,
   context limit 4096, planning/behavior/uptake caps **384/384/160**. Changing these
   requires a separate experiment; do not silently shrink token budgets after OOM.
5. Set the smoke and pilot IDs before generating. Use the same ID only to resume
   exactly matching outputs; use a fresh ID for an actual protocol/config change.
6. Mount Drive using the user's existing account. Reuse the existing HF secret or
   login without printing credentials. Default `RESULTS_ROOT` is
   `/content/drive/MyDrive/normative-hysteresis-v0/results`; this historical parent
   name is retained, but the protocol and new run IDs distinguish these experiments.
7. The storage cell backs up every embedded source file to
   `RESULTS_ROOT.parent/source_snapshots/<BUNDLE_SHA256>` before inference and prints
   `SOURCE_BACKUP`. It checks an existing smoke manifest's source/config/revision
   before model loading. Save these paths in the run handoff.

## B — Load and verify decoding (section 6)

Run model loading only on Colab. The cell prints backend metadata and verifies
six effective generation configurations: smoke/pilot x planning/behavior/uptake.
Require `DECODING_CHECK_PASSED`. Both stages must have do_sample=True,
temperature 0.7, top_p 0.8, top_k 20; caps are 384/384/160. The backend disables
checkpoint-default overrides. The historical smoke metadata bug is not fixed
merely by seeing a requested do_sample value; inspect effective recorded settings.

The cell saves a unique JSON report to `RESULTS_ROOT/runtime_checks/` containing
bundle hash, config and backend metadata. These configuration checks do not
perform inference and do not establish that the new prompt works.

## C — Smoke and audit (sections 7–8)

Run `smoke-diagnostic-001` (or the explicitly chosen new ID) once. Expect **144
trajectories and 480 raw calls** (192 planning, 288 terminal). Use the same ID after interruption; the runner
resumes saved calls. Verify `complete.json`, actual record count and raw digest.
Analyze and open `transcript_audit.html`. All 144 trajectories must be inspected,
including planning and both sibling branches, before a human scaling decision.

Start with all 24 FRESH_B trials across the four scenarios, depths and variants. Check the actual
eligible rows, copied numbers, chosen minimum and brief_reason. Then inspect all
remaining conditions. Include failures even when B_success=1 or uptake_correct=1.
The new indicators separate set, numerical, membership and ranking errors;
`decision_verified` does not validate free-form prose. Compare variants and
conditions before aggregates. Smoke covers all four scenarios, but only one sample
per cell. It is a diagnostic screen, not a precise estimate of competence.

Read baseline_diagnostics.csv and diagnostic_readiness.json, then planning_steps.csv
and planning_summary.csv. Audit whether recommendations are initially correct and
fully verified under A/X. In trials.csv compare final_repeats_last_recommendation
with A_residue; do not confuse the actual recommendation with the true old optimum.
Smoke uses replication 0 and pilot uses 1–3, so sampled trajectories do not overlap.

If systematic fresh-B failure remains, report that the proposed repair failed.
Preserve raw records and source; do not silently retry, relabel, remove failures,
or tune for a desired residue effect. A changed prompt requires a new ID/smoke.

Save AI audit notes separately from the human review. Do not use an AI reviewer's
name as if a human had inspected the outputs. Export this smoke using E even if
review rejects scaling or is pending; E works without running D.

## Human review and sign-off (section 9)

Analysis creates `smoke_review.json` with the correct ID/digest and default false
flags. A new analysis creates a new timestamped directory and a new template;
do not lose track of the human's existing signed file. Record the exact path.

The human must judge comprehension and scaling, enter their name, and review/note
every trajectory. Only when their actual judgment approves both decisions should
`task_comprehension_acceptable` and `approve_pilot` be true. Keep the real digest;
never leave a placeholder or replace it merely to make mismatched notes validate.

Set `REVIEW_FILE` to that completed file and run section 9. The helper validates
all fields and creates immutable `review_approval.json` under the raw smoke folder.
If this approval already exists, an empty path validates and reuses it. If an
explicit supplied review differs from the saved one, preserve both and resolve
the discrepancy. Identical reruns do not overwrite approval or ask for another
review. The saved human decision is sufficient; do not add an agent veto or
invent an automatic accuracy threshold after the human has approved the exact run.

## D — Pilot and selected-transcript audit (section 10)

After approval and authorization to scale, set `RUN_PILOT=True`. Run D using the
same source/config/model/runtime and the fixed new pilot ID. Expect **432
trajectories and 1,440 calls**: 288 objective and 144 factual trajectories. Do not
expand the grid automatically. The runner validates the actual loaded backend
against the approved smoke before pilot inference.

Run the pilot analysis cell. Inspect `audit_selection.json` and every selected
trajectory: all old choices, wrong choices, incorrect/invalid uptake, malformed
responses, truncations, unverified decisions, incorrect/unverified initial planning
and the random correct-choice sample.
Record arithmetic and rationale errors even in nominally successful trials.
Compare every scenario/variant, then NH, ownership, justification, FH, specificity
and the actual depth changes. Keep all trials in estimators.

## E — Export (section 11, implemented in the new notebook)

Run E after smoke and again after pilot. It writes a unique ZIP in
`RESULTS_ROOT/exports/` containing selected raw/derived runs, approvals if present,
the exact source bundle and the smoke-associated live runtime-check reports.
It excludes weights, caches and HF credentials. Set `DOWNLOAD_ARCHIVE=True` only
when a local artifact copy is useful. Save an executed `.ipynb` with cell outputs
using Colab File → Download → .ipynb, and retain the live notebook URL in the handoff.

## Cold-runtime recovery without a repeat review

Use the exact notebook used for that run, not a later rebuild. If necessary,
recover its source from the printed Drive backup. Restore the exact saved config
from the smoke manifest (including resolved revision) before model loading.
Run setup/storage/load, then rerun C under the same ID; completed calls are reused.
If smoke is complete, C returns it without generation. Reuse the existing approval
in section 9, then resume D under the same pilot ID. Analysis may be rerun into a
new directory; signed reviews and raw approval remain attached to the raw run.

Never combine old A–E globals with the new notebook's `backend`, `config`,
`smoke_run` and `pilot_run`. Missing globals after a disconnect are a restoration
problem, not evidence that the user must review the same transcripts again.

If the GPU/library metadata differs, the runner will reject resume/approval.
Inspect the specific differences and restore the recorded environment when
possible. If it cannot be reproduced, explain the incompatibility and preserve
the run; do not weaken provenance checks or quietly change model/precision.
A stale `.runner-lock` can be removed only after verifying no runner for that ID
is active, and only if it is the empty lock directory. Do not delete raw records,
manifest, completion or approval to get past an error. Corruption is preserved.

## Report and hand off

Update `RUN_HANDOFF.md` with the live notebook URL, protocol/bundle hash, source
backup, exact smoke/pilot IDs, completed counts and digest checks, model/runtime,
review path and actual human decisions, runtime-check JSON, derived/audit paths,
export ZIP, executed notebook and any deviations. State separately what was
implemented, what was tested synthetically, and what actually ran on the GPU.
Record the exact failing predicate and next action if incomplete. Never report
“pilot completed” merely because the code and notebook were prepared.
