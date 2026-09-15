# Next run handoff — diagnostic v2, 2026-09-15

The v1 pilot completed. Its findings do not justify scaling unchanged. Its protocol
and pilot lessons are preserved in commit `63e4ac9`; the original export contains
the actual frozen run source. Read
[history/PILOT_SHORTLIST_20260915.md](history/PILOT_SHORTLIST_20260915.md).

Current source: `nh-v2-diagnostic`. No real v2 smoke or pilot has run. Previous
human approval does not cover new prompts. This is implementation preparation,
not evidence that model comprehension is repaired.

Upload only `notebooks/normative_hysteresis_diagnostic_colab.ipynb` to Colab.
Use `smoke-diagnostic-001`: 144 trajectories / 480 calls, every scenario,
condition/depth/variant, replication 0, sampled temperature 0.7.
Optional `pilot-diagnostic-001`: 432 trajectories / 1,440 calls, replications 1–3.
First inspect the diagnostic smoke, then use the human decision on that exact run.

Model: Qwen/Qwen3-8B at `b968826d9c46dd6066d109eabc6255188de91218`, NF4,
non-thinking. Caps: 384 planning / 384 behavior / 160 uptake; context 4096.
Choose the Colab GPU before smoke and retain runtime provenance through pilot.
Do not load models or install GPU dependencies on the Mac.

Initial recommendations now use a scoreable shortlist schema under A/X; uptake
wording distinguishes earlier facts from the unchanged objective; the shortlist
requires checking all rows; analysis exposes baseline and planning competence.
These changes define a different protocol.

Read [NEXT_AGENT_PROMPT.md](NEXT_AGENT_PROMPT.md),
[NOTEBOOK_AGENT_GUIDE.md](NOTEBOOK_AGENT_GUIDE.md), and
[EXPERIMENT_GUIDE.md](EXPERIMENT_GUIDE.md). Validation commands are in README.
Synthetic validation cannot approve real data.

Previous live v1 notebook:
https://colab.research.google.com/drive/1xsm_y9YvDv51xQB-H9Rp5WZ5sXBR06aJ
It is historical. Record a new v2 URL after upload; do not execute mixed cells.
Drive results: `/content/drive/MyDrive/normative-hysteresis-v0/results`.
Source backups: adjacent `source_snapshots/<BUNDLE_SHA256>` folder.
Save actual v2 IDs, hashes, runtime metadata, review/analysis/export paths and
executed notebook when the next agent runs it.
