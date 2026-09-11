# Research Status

**Current status is exploratory measurement validation, not a completed corrigibility result.**

Current version: schema `strategy-v2-factorized-1.1.1`. Date: 2026-09-09 synthesis; status written 2026-09-11.

## Research objective

"Corrigibility Under Ordinary Task Pressure: Measuring Strategy Substitution and Safety-Constraint Loss Through Delegation." Questions: (1) does pressure change failure type rather than binary rate; (2) can we separate transmission failure from downstream violation in delegation; (3) does mechanical constraint re-injection improve multi-hop retention. Does NOT claim ordinary-pressure failures are novel — ROGUE and related work establish the broad phenomenon; the contribution is measurement infrastructure (see `docs/novelty_assessment.md`).

## What is implemented

ROGUE-style scenarios; live model probing; hardened rule-based judges; factorized schema v1.1.1; blinded calibration/held-out workflow (prepare, validate, join, agreement, adjudicate-init, score); scoring, joining, agreement, adjudication tooling; unit tests.

## What has been run

- Deterministic policy-arm suites (smoke: 24 rows; ablations: 32 rows) validating judges and schema.
- 90 exploratory live probes: 54 Haiku + 36 Sonnet, smoke suite × {low, base, high} pressure.
- Judge red-team (13/13 fooled original; 12/13 fixed after hardening) and live re-judging.
- Measurement Pilot 1 (ontology ambiguity → factorization) and Pilot 2 (15 blinded examples × 2 blinded model passes).

## Exploratory live findings

Small-n directional only. Model identity largest effect (Haiku 14/18 override vs Sonnet 3/12). Pressure changes strategy: Haiku → shutdown racing at high pressure; Sonnet tampering only at high pressure. Narrate-vs-transmit dissociation observed. Restricted-resource flags are judge false positives. Haiku delegation loss confounded by empty prompts. See `docs/synthesis_2026-09-09.md`.

## Measurement-validation status

Pilot 2: all-axis exact agreement 14/15 (93.3%); stance 14/15; shutdown 14/15; resource/control/delegation 15/15 — but delegation all-negative, so vacuous for positive risky-delegation reliability. Sole disagreement (refusal/self-stop semantics) repaired in v1.1.1. Two independent blinded *model* annotation passes, not human agreement; n=15, no formal reliability claim. See `docs/measurement_validation.md`.

## What is NOT yet established

No reliable restricted-resource violation rate; no positive risky-delegation reliability; no powered pressure dose-response; no depth-k retention curve; no restoration-arm effect; no multi-model causal result.

## Current limitations

Small cells; rule-judge brittleness; restricted-resource FP floor; empty-prompt confound; no positive delegation validation; no powered study.

## Next experimental milestone

1. Targeted positive-risk delegation validation. 2. Five-level pressure dose-response. 3. Depth-k retention ladder. 4. Mechanical restoration arm. 5. Powered multi-model replication.

## Compute bottleneck

Infrastructure is ready; the bottleneck is frontier-model API/compute for powered cells, multi-hop arms, calibration sets (150–250 transcripts), and LLM-judge comparison.

## Current version / date

Schema `strategy-v2-factorized-1.1.1`; synthesis 2026-09-09; status 2026-09-11.
