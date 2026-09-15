# Next agent assignment: diagnose before another hysteresis run

Read `history/DIAGNOSTIC_V2_20260915.md` and `CALIBRATION_PLAN.md` before acting.
The v2 smoke completed and did not repair the core failures. Do not run v2 D.
The current task is isolated `nh-calibration-v1`, not a new hysteresis pilot.

1. Upload `notebooks/normative_hysteresis_calibration_colab.ipynb` to a new hosted
   Colab notebook. All weights/loading/inference stay there. Preserve v1/v2 source,
   notebooks, raw outputs and human decisions. Do not use a laptop runtime.
2. Run extraction, tests, Drive/source backup and model loading. Keep the pinned
   model/configuration; record the actual GPU and runtime. Use the existing HF
   secret without printing it. If resuming, match the recorded environment.
3. Run `calibration-001`: 272 calls. There is no prior-smoke approval gate for this
   isolated calibration. Save every response, including errors, without retry.
4. Analyze and inspect all responses. First compare the one-sentence shortlist
   ablation. Then distinguish false-positive and false-negative rows, correct
   copies with incorrect masks, and incorrect minima despite correct masks.
   Compare ranking-only capability, acknowledging that its supplied rows are
   filtered by the computer. Compare probe current labels, numeric limits and
   earlier-state answers separately, especially fresh and reversed-label contexts.
5. Use design_audit.json to distinguish true old optima from unfiltered minima.
   Compute's true three-way separation passes, but its repeated erroneous choices
   can still reflect filtering failure. Shipping factual fails separation and must
   be redesigned before a future hysteresis experiment. Venue/production objective
   tasks instead have correct B = unfiltered B minimum, hiding filtering failures
   behind correct final labels. Review both collision flags. No nonzero effect is
   required; do not tune tasks until residue appears.
6. Export raw records, source, all derived files and an executed notebook. Report
   actual completed calls, runtime, hashes/paths, error patterns and the next
   intervention justified by the comparisons. Keep AI notes distinct from human
   review. This calibration does not authorize or automatically start a larger run.

If calibration is inconclusive, say which comparison is unresolved. Do not silently
change model, precision, prompt or table mid-run. Do not merge the outcomes with
old results, drop failing items, overwrite bad responses or change the primary
no-retry policy. Restore missing notebook globals instead of requesting another
review of an unchanged already-approved run. State the exact failed predicate if
execution stops. See CALIBRATION_PLAN.md for paths and recovery details.
