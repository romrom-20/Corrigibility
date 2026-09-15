# Next run handoff — 2026-09-15

**Ready for a new Colab smoke; no real nh-v1-shortlist run has been performed.**
This task implements the previously proposed shortlist clarification, scoring,
position counterbalancing, notebook recovery/export and the next-agent instructions.
Whether these changes improve model comprehension remains to be tested.

Read [NOTEBOOK_AGENT_GUIDE.md](NOTEBOOK_AGENT_GUIDE.md) for execution and
[EXPERIMENT_GUIDE.md](EXPERIMENT_GUIDE.md) for the research question, every
condition, controls, metrics, experimental changes and interpretation limits.

- Upload `notebooks/normative_hysteresis_shortlist_colab.ipynb` alone to Colab.
- Required protocol: `nh-v1-shortlist`.
- Defaults: `smoke-shortlist-001` then, if that smoke is approved, `pilot-shortlist-001`.
- First real run: 32 shipping trajectories / 108 calls. Pilot: 432 trajectories /
  1,440 calls. The notebook contains implemented C, D and E sections.
- Model: Qwen/Qwen3-8B pinned to `b968826d9c46dd6066d109eabc6255188de91218`,
  non-thinking, NF4. Caps: planning 144, behavior 384, uptake 160.
- Default Drive results parent remains
  `/content/drive/MyDrive/normative-hysteresis-v0/results`.
- Extracted source is identified by the printed bundle hash and backed up to
  `RESULTS_ROOT.parent/source_snapshots/<BUNDLE_SHA256>` before inference.
- Use only Colab for models/GPU work. No weights were downloaded on the laptop.

The old live notebook at
https://colab.research.google.com/drive/117HBfMbsEcOQUzAMeVzD13eDarLVCVs6
is historical. Its repaired D cell is not a deployment of this revised protocol.
Do not run its old C/D or its mixed source cells for the new experiment. The new
notebook has not been uploaded or executed in the user's Colab during preparation.
Record the new live URL after upload.

The latest historical smoke (`smoke-separated-002`) failed all 24 objective
choices, passed 8 factual choices, and has a signed rejection of comprehension
and scaling. That result motivates the revision; it does not validate or approve
it. Its source used fixed row order, whereas this revision restores reversal.
All old files remain intact. The detailed historical operational record is
[history/RUN_HANDOFF_20260914.md](history/RUN_HANDOFF_20260914.md) in the repository.
It is an archive, not current execution guidance.

Validation during preparation: **34 unit tests passed**. The notebook integration
completed the synthetic smoke, repeated fixture approval, full 432-trajectory
synthetic pilot, analysis and smoke/pilot exports. No real weights were used.

To reproduce: run the unit suite, rebuild the notebook, then execute
`scripts/validate_colab_notebook.py`. The validator includes a synthetic full pilot,
reused fixture approval, analysis and smoke/pilot ZIP export. Its outputs are
explicitly synthetic and cannot be used as research results or human approval.

Next agent: execute A/B/C, audit the actual smoke and prepare its correctly bound
human review. If the exact new smoke is approved and scaling authorized, proceed
through D, selected-transcript audit and E without a redundant permission loop.
If comprehension still fails, preserve and export the failure and state that the
proposed repair did not work; do not keep rerunning identical greedy smoke.
