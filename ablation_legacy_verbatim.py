"""Legacy-verbatim ablation: the same 384 eligibility cases that make up
context_diagnostic_v2's `legacy_verbatim` arm, re-run under whatever
backend you load (bf16 weights, thinking enabled, or both) and a run_id
you choose -- never 'context-002'.

Why this exists: context_diagnostic_v2.run() checks
`if (folder / 'complete.json').exists(): return folder` before it ever
inspects the backend argument. Passing a new backend with an old,
already-complete run_id silently returns the OLD records -- which is
exactly what the screenshot showed happening. There is no code fix for
that inside context_diagnostic_v2 that wouldn't change its frozen
behavior for the run that already completed; the fix is procedural
(always use a fresh run_id) and this module makes the procedural fix the
only available path, by not accepting 'context-002' at all.

Design choice: this module reuses context_diagnostic_v2.Case objects
directly rather than redefining them. Case.id hashes in v2.VERSION (a
module-level global looked up at call time, not bound to whichever module
holds the reference), so every record produced here has the SAME case_id
as its counterpart in context-002. That makes the two runs directly
joinable by case_id for a matched comparison -- see compare_to_context002
-- while living in a completely separate run_id folder that cannot
short-circuit against context-002's saved records.

The ablation config pins the same seed as context_diagnostic_v2's config
(20260918), so any difference between a context-002 record and its
ablation counterpart is attributable to the backend (quantization,
thinking, or both -- whatever you changed at load time), not to a
different sampling seed. Record-level provenance (actual quantization,
enable_thinking, GPU) comes from backend.metadata in the manifest, not
from this module's config file -- check manifest.model after the run,
don't assume it from the run_id you chose.
"""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
from collections import Counter
import csv
import hashlib
import html
import json
import re
import uuid

import context_diagnostic_v2 as v2
from component_diagnostic import owned_lock, recover_lock, differences
from corrigibility_bench.normative_hysteresis import digest, derived_seed
from corrigibility_bench.runner import read_json, write_new_json, raw_digest, now

ROOT = Path(__file__).resolve().parent
VERSION = 'nh-ablation-legacy-verbatim-v1'  # this module's own config/provenance only; case IDs use v2.VERSION
FORBIDDEN_RUN_IDS = {'context-002', 'ablation-bf16-thinking-001', 'ablation-bf16-thinking-002'}

messages = v2.messages
expected_answer = v2.expected_answer
candidate_policies = v2.candidate_policies
def strip_thinking(raw):
    """Non-thinking backends never emit '</think>'; this is a no-op for
    them, so it's safe to apply unconditionally. Verified against the
    'ablation-bf16-thinking-002' upload: exactly one '</think>' tag in
    all 384 records, and the tail after it parses as strict JSON in all
    384 -- the model's answers were fine all along; the harness's
    strict_json call on the raw (unstripped) string was rejecting the
    <think> preamble, not the answer."""
    idx = raw.rfind('</think>')
    return raw[idx + len('</think>'):].strip() if idx != -1 else raw


def score(c, raw): return v2.score(c, strip_thinking(raw))


def settings(config, c):
    """Overrides v2.settings: max_new_tokens is config-controlled here, not
    hardcoded, because a thinking-enabled backend needs far more budget to
    reach its final JSON past the <think> block. Using v2's fixed 160-token
    cap with thinking enabled produces 0% valid responses -- every
    generation is truncated mid-reasoning before it ever emits an answer.
    That is a token-budget bug, not a behavioral result; it happened on
    run 'ablation-bf16-thinking-001' (382/384 records truncated at exactly
    160 tokens, 384/384 invalid) and is why this override exists."""
    base = v2.settings(config, c)
    return dict(base, max_new_tokens=config.get('max_new_tokens', 160))


def grid():
    cases = [c for c in v2.grid() if c.family == 'eligibility' and c.variant == 'legacy_verbatim']
    assert len(cases) == 384
    return cases


def load_config(name='ablation_legacy_verbatim_v1.json'): return read_json(ROOT / 'configs' / name)


def frozen_configs():
    return [load_config('ablation_legacy_verbatim_v1.json'), load_config('ablation_legacy_verbatim_thinking_v1.json')]


def sources():
    paths = [ROOT / p for p in ('ablation_legacy_verbatim.py', 'context_diagnostic_v2.py', 'component_diagnostic.py',
             'execution_readiness.py', 'readiness_bench.py', 'calibration_bench.py',
             'configs/ablation_legacy_verbatim_v1.json', 'configs/ablation_legacy_verbatim_thinking_v1.json',
             'configs/context_diagnostic_v2.json', 'requirements-colab.txt')]
    paths += sorted((ROOT / 'corrigibility_bench').glob('*.py'))
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def design_audit(config=None):
    config = config or load_config()
    if config not in frozen_configs():
        raise ValueError('Use one of the frozen ablation configs (v1 or thinking_v1)')
    cases = grid()
    assert len(cases) == len({c.id for c in cases}) == 384
    assert config['seed'] == v2.load_config()['seed'], 'Ablation must reuse context_diagnostic_v2 seed to isolate the backend as the only changed variable'
    seeds = [expected_record(c, config)['seed'] for c in cases]
    assert len(set(seeds)) == len(seeds)
    return dict(version=VERSION, calls=len(cases), case_version=v2.VERSION, max_new_tokens=config.get('max_new_tokens', 160),
                interpretation=('Same 384 legacy_verbatim cases as context-002 (identical case_id per case). '
                                 'Compare by joining on case_id via compare_to_context002; the actual backend '
                                 'that produced this run is recorded in manifest.model, not in this run_id. Use '
                                 'the thinking_v1 config (max_new_tokens=1024) for any thinking-enabled backend -- '
                                 'the 160-token default truncates every response mid-reasoning (see '
                                 "'ablation-bf16-thinking-001': 382/384 truncated, 384/384 invalid)."))


def expected_record(c, config):
    prompt = messages(c)
    return dict(case=json.loads(json.dumps(asdict(c))), messages=prompt, prompt_hash=digest(prompt),
                seed=derived_seed(config['seed'], v2.VERSION, c.id), requested_generation_config=settings(config, c))


def validate_record(r, c, config, model):
    if (any(r.get(k) != v for k, v in expected_record(c, config).items()) or r['model'] != model
            or r['rendered_prompt_hash'] != digest(r['rendered_prompt']) or r['parsed'] != score(c, r['raw_text'])
            or any(r['generation_config'].get(k) != v for k, v in settings(config, c).items())):
        raise ValueError('Saved record/context/settings/score mismatch: ' + c.id)


def checked_records(folder):
    folder = Path(folder); m = read_json(folder / 'manifest.json'); cases = grid()
    if (m['version'] != VERSION or m['sources'] != sources() or m['config'] not in frozen_configs()
            or m['cases'] != [json.loads(json.dumps(asdict(c))) for c in cases]):
        raise ValueError('Restore frozen sources/config/design for analysis')
    complete = read_json(folder / 'complete.json')
    if (complete['calls'] != len(cases) or complete['raw_digest'] != raw_digest(folder)
            or {p.name for p in (folder / 'records').glob('*.json')} != {c.id + '.json' for c in cases}):
        raise ValueError('Completed records/digest mismatch')
    records = []
    for c in cases:
        r = read_json(folder / 'records' / (c.id + '.json')); validate_record(r, c, m['config'], m['model']); records.append(r)
    return m, records


def run(backend, config, root, run_id, progress=print):
    if run_id in FORBIDDEN_RUN_IDS or not re.fullmatch(r'[A-Za-z0-9_-]+', run_id):
        raise ValueError(f"Refusing run_id {run_id!r}: choose a new run_id for this ablation, "
                           "never reuse a context_diagnostic_v2 run_id such as 'context-002' "
                           "or a poisoned ablation run_id ('ablation-bf16-thinking-001' was truncated "
                           "at 160 tokens; 'ablation-bf16-thinking-002' was scored with the pre-fix "
                           "scorer that rejected every <think> preamble).")
    if config not in frozen_configs():
        raise ValueError('Use one of the frozen ablation configs (v1 or thinking_v1)')
    design_audit(config); cases = grid(); folder = Path(root) / 'raw/ablation_legacy_verbatim' / run_id
    folder.mkdir(parents=True, exist_ok=True)
    if (folder / 'complete.json').exists():
        checked_records(folder); return folder
    if backend is None: raise ValueError('Incomplete run: load matching hosted backend to resume')
    manifest = dict(version=VERSION, run_id=run_id, config=config, model=backend.metadata, sources=sources(),
                     cases=[json.loads(json.dumps(asdict(c))) for c in cases])
    if (folder / 'manifest.json').exists():
        delta = differences(read_json(folder / 'manifest.json'), manifest)
        if delta: raise ValueError('Resume mismatch; preserve saved calls. Differences: ' + json.dumps(delta))
    with owned_lock(folder) as assert_owner:
        if (folder / 'manifest.json').exists():
            if read_json(folder / 'manifest.json') != manifest: raise ValueError('Manifest changed while acquiring lock')
        else: write_new_json(folder / 'manifest.json', manifest)
        for i, c in enumerate(cases):
            assert_owner(); path = folder / 'records' / (c.id + '.json')
            if path.exists(): validate_record(read_json(path), c, config, backend.metadata)
            else:
                generated = backend.generate(messages(c), expected_record(c, config)['seed'], settings(config, c))
                assert_owner()
                record = dict(**expected_record(c, config), **asdict(generated), model=backend.metadata, timestamp=now(),
                              rendered_prompt_hash=digest(generated.rendered_prompt), parsed=score(c, generated.raw_text))
                validate_record(record, c, config, backend.metadata); write_new_json(path, record)
            progress(f'{i+1}/384: {c.id} (backend: {backend.metadata.get("quantization")}, '
                     f'thinking={backend.metadata.get("enable_thinking")})')
        assert_owner()
        if {p.name for p in (folder / 'records').glob('*.json')} != {c.id + '.json' for c in cases}:
            raise ValueError('Unexpected record set')
        write_new_json(folder / 'complete.json', dict(calls=len(cases), raw_digest=raw_digest(folder), completed_at=now()))
    return folder


def analyze(folder):
    folder = Path(folder); m, records = checked_records(folder)
    out = folder.parents[2] / 'derived/ablation_legacy_verbatim' / m['run_id'] / uuid.uuid4().hex[:8]
    out.mkdir(parents=True)
    rows = []
    for r in records:
        c = v2.from_spec(r['case']); p = r['parsed']
        rows.append(dict(r['case'], case_id=c.id, valid=int(p['valid']), correct=int(p['fully_correct']),
                         verified=int(p['fully_correct'] and not r['truncated']), truncated=int(r['truncated']),
                         response=json.dumps(p['data']), agreement=json.dumps(p['agreement']) if p['agreement'] else None,
                         error=p['error']))
    with (out / 'cases.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=sorted({k for row in rows for k in row})); writer.writeheader()
        writer.writerows(rows)
    valid = [r for r in rows if r['valid']]
    summary = dict(version=VERSION, raw_digest=raw_digest(folder), model=m['model'], N=len(rows),
                   accuracy=sum(r['verified'] for r in rows) / len(rows),
                   agrees_cost_reader=(sum(json.loads(r['agreement'])['cost_reader'] for r in valid) / len(valid)) if valid else None,
                   by_relation=[dict(relation=rel, N=len(g), accuracy=sum(x['verified'] for x in g) / len(g))
                                for rel in sorted({r['relation'] for r in rows})
                                for g in [[r for r in rows if r['relation'] == rel]]],
                   interpretation='Compare these numbers directly against context-002 legacy_verbatim (76.8% accuracy, agrees_cost_reader climbing with distance). Use compare_to_context002 for the matched, per-case version of this comparison.')
    write_new_json(out / 'summary.json', summary)
    write_new_json(out / 'design_audit.json', design_audit())
    (out / 'transcripts.html').write_text('<html><meta charset="utf-8"><style>pre{white-space:pre-wrap}</style><h1>Legacy-verbatim ablation: every raw response</h1>' + ''.join(
        '<details><summary>' + html.escape(str(r['case'])) + '</summary><pre>' + html.escape(json.dumps(r, indent=2)) + '</pre></details>' for r in records) + '</html>')
    return out


def compare_to_context002(context002_folder, ablation_folder):
    """Matched, per-case comparison: for every one of the 384 shared
    case_ids, did the ablation backend fix, harm, or leave unchanged the
    context-002 (NF4, non-thinking) answer? This is the number that
    actually answers 'did switching backend settings close the gap',
    not just two independent accuracy percentages that could differ for
    unrelated reasons.
    """
    _, base_records = v2.checked_records(context002_folder)
    base = {r['case']['case_id'] if 'case_id' in r['case'] else v2.from_spec(r['case']).id: r for r in base_records}
    base = {v2.from_spec(r['case']).id: r for r in base_records}
    _, ablation_records = checked_records(ablation_folder)
    abl = {v2.from_spec(r['case']).id: r for r in ablation_records}
    shared = set(base) & set(abl)
    if shared != {c.id for c in grid()}:
        raise ValueError('context-002 and the ablation folder do not share exactly the 384 legacy_verbatim case_ids expected')
    fixed = harmed = both_correct = both_wrong = 0
    for cid in shared:
        b_ok = base[cid]['parsed']['fully_correct'] and not base[cid]['truncated']
        a_ok = abl[cid]['parsed']['fully_correct'] and not abl[cid]['truncated']
        fixed += int(a_ok and not b_ok); harmed += int(b_ok and not a_ok)
        both_correct += int(a_ok and b_ok); both_wrong += int(not a_ok and not b_ok)
    return dict(N=len(shared), context002_model=base[next(iter(shared))]['model'],
                ablation_model=abl[next(iter(shared))]['model'],
                fixed=fixed, harmed=harmed, both_correct=both_correct, both_wrong=both_wrong,
                context002_accuracy=(both_correct + harmed) / len(shared), ablation_accuracy=(both_correct + fixed) / len(shared),
                interpretation=('fixed = context-002 got it wrong, ablation got it right. If fixed is large and '
                                 'harmed is small, the backend change (quantization/thinking) is most of the story. '
                                 'If both_wrong stays large regardless, the wording-sensitivity account is what survives.'))
