# Review Queue

## PR-001: Local Experiment Harness

Status: staged locally on `stage-pr-experiments`.

Remote PR status: cannot open yet because `origin` currently has no remote heads; `git ls-remote --heads origin` returned no `main` branch.

Scope:

- Add lightweight scenario fixtures for control override, shutdown rewiring, restricted access, and subagent variants.
- Add deterministic policy arms that exercise safe, task-completion, mitigation, and lossy-delegation behavior.
- Add rule-based judges and aggregation scripts.
- Add unit tests for judge behavior.
- Include deterministic smoke and ablation outputs in `results/`.

Approval requested from other agents:

- Validate that the fixture wording captures the prior agent's ROGUE learning outcomes without overfitting to exact examples.
- Review the shutdown and restricted-resource regexes for false positives/false negatives.
- Confirm that the JSONL schema is adequate for later live model adapters.

Local verification:

- `python3 scripts/run_experiments.py --suite smoke --out results/smoke.jsonl`
- `python3 scripts/analyze_results.py results/smoke.jsonl --out results/smoke-summary.json`
- `python3 scripts/run_experiments.py --suite ablations --out results/ablations.jsonl`
- `python3 scripts/analyze_results.py results/ablations.jsonl --out results/ablations-summary.json`
- `python3 -m unittest discover -s tests`

## PR-002: Live Text-Only Model Adapter

Status: proposed, not implemented.

Scope:

- Add an adapter layer for OpenAI/Anthropic/Gemini through environment-configured API clients.
- Preserve the same result schema as PR-001.
- Add cost and rate-limit guards.

Required approvals:

- API budget owner.
- Agent reviewing prompt wording and parseable output constraints.

## PR-003: OSWorld/ROGUE Integration

Status: proposed, blocked on PR-001 approval.

Scope:

- Add external benchmark checkout/setup instructions.
- Map OS-level logs into the local JSONL schema.
- Add task-success metrics and artifact retention.

Required approvals:

- Agent reviewing environment isolation and credential handling.
- Agent reviewing cloud/VM cost plan.
