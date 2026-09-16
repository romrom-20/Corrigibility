# Current handoff — isolate components after failed ranking repair

Execution screen COMPLETE: 768 T4 calls, analysis validated; ranked candidate failed.
Preserved implementation and findings: b032fd8. See history/EXECUTION_READINESS_V1_20260916.md.
Do not rerun screen, confirmation or D. Historical source/notebook remains frozen.

Current prepared version nh-component-diagnostic-v1; no real run yet.
Notebook notebooks/normative_hysteresis_component_diagnostic_colab.ipynb.
480 independent calls: eligibility 128, comparison 288, state 64. No automatic next
stage, no readiness gate, no answer feedback. Read COMPONENT_DIAGNOSTIC_PLAN.md
and NEXT_AGENT_PROMPT.md for the actual hypotheses and limits.

All model work on hosted Colab; no Mac weights. Default components-001 under
/content/drive/MyDrive/normative-hysteresis-v0/results/raw/component_diagnostic/.
Prefer T4 for continuity, frozen Qwen3-8B/NF4 config. Preserve exact runtime on resume.
Completed-run analysis needs no model; new runner gives field-level mismatch
reports and retains original exceptions when lock cleanup fails. Remove a stale
lock only after confirming no old runner remains; never alter saved records.

Export source/raw/derived ZIP plus executed notebook and record bundle, hardware,
run ID/digest, URL and Drive paths. Software tests cover exact predicate answers,
reverse comparisons, placeholder errors, interruption/resume, mixed-runtime refusal,
record tampering, lock ownership and missing-lock exception preservation. End-to-end
portable validation uses synthetic successes/failures, not model results.
