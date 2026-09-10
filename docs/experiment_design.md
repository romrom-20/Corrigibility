# Experiment Design

## Primary Hypotheses

1. Task-completion pressure increases control-override, shutdown-avoidance, and restricted-resource violations.
2. Explicit safety instructions reduce violations in direct execution, but the effect weakens under delegation.
3. Subagent prompts often lose concrete restrictions, especially when parent instructions contain both task urgency and resource limits.
4. Richer environment affordance information increases unsafe action rates because it makes violations easier to execute.

## Initial Experiment Ladder

1. **Local smoke harness:** deterministic policy arms validate scenario definitions, judges, result schema, and aggregation.
2. **Text-only model probes:** ask models for parseable choices under the same scenarios and ablations.
3. **Transcript judging:** score model outputs and reasoning summaries with rule-based checks first, then add LLM judge comparison.
4. **Delegation probes:** compare parent task prompt against generated subagent prompt and score missing inherited constraints.
5. **OS-level integration:** run a subset of ROGUE/OSWorld tasks after the scoring and logging format is reviewed.

## Metrics

- `violation_rate`: unsafe action or clearly unsafe intent per scenario/policy.
- `missing_context_rate`: subagent prompts missing inherited forbidden resources or control instructions.
- `task_success_rate`: reserved for later live-agent and OS-level runs.
- `judge_label`: scenario-specific label such as `override`, `rewire_or_avoid_shutdown`, or `restricted_access`.

## Review Gates

Before live model or VM runs, another agent should approve:

- Scenario wording and whether it preserves the prior paper's relevant failure modes.
- Rule-based judge precision and false-positive risk.
- Result schema stability for future model adapters.
- Any use of credentials, cloud VMs, or paid APIs.
