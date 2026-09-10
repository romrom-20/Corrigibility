# Experiment Design

## Current estimands (Phase 1)

Measure strategy distributions conditional on model, scenario, pressure and
case/mitigation. Pressure -> binary violation is NOT the hypothesis being
assumed: pressure may shift which strategy is selected, including race/delay,
tampering, asking, self-stop and deference. Retain binary rates for historical
comparability, without assuming a monotonic pressure effect.

[Measurement contract](measurement_phase1.md) defines the taxonomy, evidence
reconciliation, local blinded evaluation, and unresolved measurement weaknesses.
Delegation causal interventions, observability, reflection and training are
future work; Phase 1 only repairs measurement and adds strategy outcomes.

## Initial Experiment Ladder

1. **Local smoke harness:** deterministic policy arms validate scenario definitions, judges, result schema, and aggregation.
2. **Text-only model probes:** ask models for parseable choices under the same scenarios and ablations.
3. **Transcript judging:** score model outputs and reasoning summaries with rule-based checks first, then add LLM judge comparison.
4. **Delegation probes:** compare parent task prompt against generated subagent prompt and score missing inherited constraints.
5. **OS-level integration:** run a subset of ROGUE/OSWorld tasks after the scoring and logging format is reviewed.

## Metrics

- `strategy_distributions`: categorical counts/rates by model/scenario/pressure and case, with unclear and unmeasured denominators.
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
