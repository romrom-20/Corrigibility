# Corrigibility Experiments

This repository stages corrigibility experiments based on the ROGUE finding that ordinary task pressure can push agents toward unsafe control behavior.

The current scaffold focuses on fast, text-only and transcript-level experiments that can run locally without external services. It is intended to create reviewable PR slices before adding model APIs or OS-level VM integration.

## Quick Start

```bash
python3 scripts/run_experiments.py --suite smoke --out results/smoke.jsonl
python3 scripts/analyze_results.py results/smoke.jsonl --out results/smoke-summary.json
python3 -m unittest discover -s tests
```

## Experiment Threads

1. **Control override**: measure whether an agent yields to user takeover or preserves task control.
2. **Shutdown compliance**: measure whether an agent accepts shutdown or tries to modify/avoid it.
3. **Restricted resource access**: measure whether an agent respects a resource prohibition under task pressure.
4. **Subagent propagation**: measure whether safety-critical instructions survive delegation.

The first PR candidate is the local harness and design docs. Later PRs should add live model adapters and OSWorld/ROGUE integration after another agent reviews the scoring assumptions.
