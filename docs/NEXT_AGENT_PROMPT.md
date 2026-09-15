# Assignment for the next Colab agent

Run the diagnostic smoke for `nh-v2-diagnostic` and assess whether the task is
understood well enough to justify another pilot. Read NOTEBOOK_AGENT_GUIDE.md,
EXPERIMENT_GUIDE.md, RUN_HANDOFF.md and history/PILOT_SHORTLIST_20260915.md first.
All weights, loading and inference must stay in hosted Google Colab. The Mac is
only for source, small artifacts and offline checks.

1. Upload `notebooks/normative_hysteresis_diagnostic_colab.ipynb` as a new notebook.
   Preserve historical notebooks/exports. Choose the GPU before smoke; record its
   identity rather than assuming A100. Run setup, tests, Drive source backup and
   effective-decoding verification. Use the existing HF secret without printing it.
2. Run C with `smoke-diagnostic-001` (144 trajectories, 480 calls). Both stages use
   temperature 0.7, top_p 0.8, top_k 20. Planning/behavior/uptake caps: 384/384/160.
   Resume matching saved calls under the same ID. Never retry a bad model answer.
3. Generate analysis and inspect all smoke trajectories. Start with fresh B/Y by
   scenario and variant, then initial A/X planning, final decision and independent
   uptake. Use baseline_diagnostics.csv, planning_steps.csv, planning_summary.csv,
   diagnostic_readiness.json and trials.csv. Read the actual brief reasons too.
4. Answer these questions in separate AI notes: Does compute still ignore runtime?
   Does venue still omit eligible rows despite correct choices? Does production
   switch the wrong attribute? Does fresh-fact uptake confuse the unchanged
   objective with the previous fact? Are A/X recommendations initially correct?
   Does any final old-option choice actually repeat a prior recommendation? Are
   failures confined to one paired label/order variant? Are outputs truncated?
5. Preserve all primary denominators and failed cases. Do not silently change
   conditions, discard scenarios or filter to initially correct planning. No fixed
   numerical accuracy threshold was preregistered; report failures clearly and
   prepare the human review without fabricating a human decision or signature.
6. Export E after smoke even if scaling is rejected or pending. Save the live URL,
   executed notebook, exact hashes, runtime-check report, AI notes and export ZIP.
   Provide the human a concise recommendation with per-scenario evidence.
7. Only if that exact v2 smoke is human-approved and the user requests the pilot,
   reuse the saved approval and run D (`pilot-diagnostic-001`, 432/1,440). Continue
   analysis, selected-transcript audit and export without asking again for an
   already-authorized step. Smoke replication 0 and pilot replications 1–3 differ.

If comprehension remains poor, preserve the result and propose one explicitly
versioned next intervention, rather than changing prompts mid-run. A model or
precision change is a new experimental condition. Do not treat a larger GPU as
evidence that accuracy improves. No mechanism or positive effect is assumed.

On a workflow stop, report the actual exception and failed predicate. Restore
missing globals/environment from the recorded source; reuse exact approvals.
Do not erase a manifest, relax provenance checks, delete outputs or invent a
human-review requirement beyond the documented procedure. A stale empty lock
may be removed only after establishing that its runner has stopped.
