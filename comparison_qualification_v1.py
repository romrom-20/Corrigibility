"""Comparison-only qualification under a frozen thinking backend.
Built from the evidenced context_diagnostic_v2 run/validate/analyze patterns.
"""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
from collections import Counter
import csv, hashlib, html, json, re, uuid
import context_diagnostic_v2 as v2
from ablation_legacy_verbatim import strip_thinking
from component_diagnostic import owned_lock, recover_lock, differences
from corrigibility_bench.normative_hysteresis import digest, derived_seed
from corrigibility_bench.runner import read_json, write_new_json, raw_digest, now

ROOT = Path(__file__).resolve().parent
VERSION = 'nh-comparison-qualification-v1'
CONFIG_NAME = 'comparison_qualification_thinking_v1.json'
FORBIDDEN_RUN_IDS = {'context-002', 'ablation-bf16-think-1024-003'}

def grid():
    cases = [c for c in v2.grid() if c.family == 'comparison']
    assert len(cases) == len({c.id for c in cases})
    return cases

def load_config(): return read_json(ROOT / 'configs' / CONFIG_NAME)

def settings(config, c):
    return dict(v2.settings(config, c), max_new_tokens=config['max_new_tokens'])

def score(c, raw): return v2.score(c, strip_thinking(raw))
def messages(c): return v2.messages(c)
def expected_answer(c): return v2.expected_answer(c)

def sources():
    paths = [ROOT / p for p in ('comparison_qualification_v1.py', 'context_diagnostic_v2.py',
             'ablation_legacy_verbatim.py', 'component_diagnostic.py', 'execution_readiness.py',
             'readiness_bench.py', 'calibration_bench.py', 'configs/' + CONFIG_NAME,
             'configs/context_diagnostic_v2.json', 'requirements-colab.txt')]
    paths += sorted((ROOT / 'corrigibility_bench').glob('*.py'))
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def design_audit(config=None):
    config = config or load_config(); cases = grid()
    assert config == load_config()
    assert len(cases) == len({c.id for c in cases})
    strata = Counter((c.variant, c.rotation, c.reverse, c.decoding) for c in cases)
    assert set(c.reverse for c in cases) == {0,1}
    assert set(c.rotation for c in cases) == {0,1}
    for variant in ('numeric','named','labeled'):
        for decoding in ('sampled','greedy'):
            n0 = sum(1 for c in cases if c.variant==variant and c.decoding==decoding and c.reverse==0)
            n1 = sum(1 for c in cases if c.variant==variant and c.decoding==decoding and c.reverse==1)
            r0 = sum(1 for c in cases if c.variant==variant and c.decoding==decoding and c.rotation==0)
            r1 = sum(1 for c in cases if c.variant==variant and c.decoding==decoding and c.rotation==1)
            assert n0 == n1 and r0 == r1
    seeds = [expected_record(c, config)['seed'] for c in cases]
    assert len(set(seeds)) == len(seeds)
    return dict(version=VERSION, calls=len(cases), families={'comparison': len(cases)},
                variants=dict(Counter(c.variant for c in cases)),
                decoding=dict(Counter(c.decoding for c in cases)),
                reverse=dict(Counter(c.reverse for c in cases)),
                rotation=dict(Counter(c.rotation for c in cases)),
                max_new_tokens=config['max_new_tokens'], automatic_followup=False)

def expected_record(c, config):
    prompt = messages(c)
    return dict(case=json.loads(json.dumps(asdict(c))), messages=prompt, prompt_hash=digest(prompt),
                seed=derived_seed(config['seed'], v2.VERSION, c.id),
                requested_generation_config=settings(config, c))

def validate_record(r, c, config, model):
    if (any(r.get(k) != val for k,val in expected_record(c,config).items()) or r['model'] != model
        or r['rendered_prompt_hash'] != digest(r['rendered_prompt'])
        or r['parsed'] != score(c, r['raw_text'])
        or any(r['generation_config'].get(k) != val for k,val in settings(config,c).items())):
        raise ValueError('Saved record/context/settings/score mismatch: ' + c.id)

def checked_records(folder):
    folder=Path(folder); m=read_json(folder/'manifest.json'); cases=grid()
    if (m['version'] != VERSION or m['sources'] != sources() or m['config'] != load_config()
        or m['cases'] != [json.loads(json.dumps(asdict(c))) for c in cases]):
        raise ValueError('Restore frozen sources/config/design for analysis')
    complete=read_json(folder/'complete.json')
    if (complete['calls'] != len(cases) or complete['raw_digest'] != raw_digest(folder)
        or {p.name for p in (folder/'records').glob('*.json')} != {c.id+'.json' for c in cases}):
        raise ValueError('Completed records/digest mismatch')
    records=[]
    for c in cases:
        r=read_json(folder/'records'/(c.id+'.json')); validate_record(r,c,m['config'],m['model']); records.append(r)
    return m,records

def run(backend, config, root, run_id, progress=print):
    if config != load_config() or not re.fullmatch(r'[A-Za-z0-9_-]+',run_id) or run_id in FORBIDDEN_RUN_IDS:
        raise ValueError('Use frozen config and a fresh valid run ID')
    design_audit(config); cases=grid(); folder=Path(root)/'raw/comparison_qualification_v1'/run_id
    folder.mkdir(parents=True,exist_ok=True)
    if (folder/'complete.json').exists(): checked_records(folder); return folder
    if backend is None: raise ValueError('Incomplete run: load matching hosted backend to resume')
    manifest=dict(version=VERSION,run_id=run_id,config=config,model=backend.metadata,sources=sources(),
                  cases=[json.loads(json.dumps(asdict(c))) for c in cases])
    if (folder/'manifest.json').exists():
        delta=differences(read_json(folder/'manifest.json'),manifest)
        if delta: raise ValueError('Resume mismatch; preserve saved calls. Differences: '+json.dumps(delta))
    with owned_lock(folder) as assert_owner:
        if (folder/'manifest.json').exists():
            if read_json(folder/'manifest.json') != manifest: raise ValueError('Manifest changed while acquiring lock')
        else: write_new_json(folder/'manifest.json',manifest)
        for i,c in enumerate(cases):
            assert_owner(); path=folder/'records'/(c.id+'.json')
            if path.exists(): validate_record(read_json(path),c,config,backend.metadata)
            else:
                generated=backend.generate(messages(c),expected_record(c,config)['seed'],settings(config,c))
                assert_owner()
                record=dict(**expected_record(c,config),**asdict(generated),model=backend.metadata,timestamp=now(),
                            rendered_prompt_hash=digest(generated.rendered_prompt),parsed=score(c,generated.raw_text))
                validate_record(record,c,config,backend.metadata); write_new_json(path,record)
            progress(f'{i+1}/{len(cases)}: comparison {c.variant} reverse={c.reverse} rotation={c.rotation} {c.id}')
        assert_owner()
        if {p.name for p in (folder/'records').glob('*.json')} != {c.id+'.json' for c in cases}: raise ValueError('Unexpected record set')
        write_new_json(folder/'complete.json',dict(calls=len(cases),raw_digest=raw_digest(folder),completed_at=now()))
    return folder

def summarize(rows):
    n=len(rows); verified=sum(r['verified'] for r in rows)
    return dict(N=n,valid=sum(r['valid'] for r in rows),verified=verified,
                invalid=sum(not r['valid'] for r in rows),truncated=sum(r['truncated'] for r in rows),
                accuracy=verified/n if n else None)

def analyze(folder, context002_folder=None):
    folder=Path(folder); manifest,records=checked_records(folder)
    out=folder.parents[2]/'derived/comparison_qualification_v1'/manifest['run_id']/uuid.uuid4().hex[:8]
    out.mkdir(parents=True)
    rows=[]
    for r in records:
        c=v2.from_spec(r['case']); p=r['parsed']
        rows.append(dict(r['case'],case_id=c.id,valid=int(p['valid']),correct=int(p['fully_correct']),
                         verified=int(p['fully_correct'] and not r['truncated']),truncated=int(r['truncated']),
                         expected=json.dumps(expected_answer(c)),response=json.dumps(p['data']),error=p['error'],
                         provenance='historical_anchor' if c.item<3 else 'new',
                         digit_width='same' if len(str(v2.PAIRS[c.item][0]))==len(str(v2.PAIRS[c.item][1])) else 'different'))
    with (out/'cases.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=sorted({k for r in rows for k in r}));w.writeheader();w.writerows(rows)
    cells=[];strata=[]
    for variant in sorted({r['variant'] for r in rows}):
        g=[r for r in rows if r['variant']==variant];cells.append(dict(variant=variant,**summarize(g)))
        for field in ('item','reverse','rotation','decoding','provenance','digit_width'):
            for value in sorted({r[field] for r in g},key=str):
                strata.append(dict(variant=variant,field=field,value=value,**summarize([r for r in g if r[field]==value])))
    matched_summary=None; matched=[]
    if context002_folder is not None:
        _,base_records=v2.checked_records(context002_folder)
        base={v2.from_spec(r['case']).id:r for r in base_records if r['case']['family']=='comparison'}
        cur={v2.from_spec(r['case']).id:r for r in records}
        if set(cur) != set(base): raise ValueError('Expected exactly the 192 shared comparison case IDs')
        for cid in sorted(cur):
            b_ok=base[cid]['parsed']['fully_correct'] and not base[cid]['truncated']
            n_ok=cur[cid]['parsed']['fully_correct'] and not cur[cid]['truncated']
            c=v2.from_spec(cur[cid]['case'])
            matched.append(dict(case_id=cid,variant=c.variant,reverse=c.reverse,rotation=c.rotation,
                                fixed=int(n_ok and not b_ok),harmed=int(b_ok and not n_ok),
                                both_correct=int(n_ok and b_ok),both_wrong=int(not n_ok and not b_ok)))
        matched_summary=dict(N=len(matched),fixed=sum(x['fixed'] for x in matched),harmed=sum(x['harmed'] for x in matched),
                             both_correct=sum(x['both_correct'] for x in matched),both_wrong=sum(x['both_wrong'] for x in matched))
        write_new_json(out/'matched_vs_context002.json',matched)
    balance=dict(reverse=dict(Counter(r['reverse'] for r in rows)),rotation=dict(Counter(r['rotation'] for r in rows)))
    summary=dict(version=VERSION,raw_digest=raw_digest(folder),model=manifest['model'],overall=summarize(rows),
                 cells=cells,strata=strata,balance=balance,matched_vs_context002=matched_summary,
                 interpretation='All invalid and truncated answers remain failures. Review per-strata results and every transcript; no pooled headline replaces the qualification gate.')
    write_new_json(out/'summary.json',summary);write_new_json(out/'design_audit.json',design_audit())
    write_new_json(out/'failures.json',[r for r in rows if not r['verified']])
    (out/'transcripts.html').write_text('<html><meta charset="utf-8"><style>pre{white-space:pre-wrap}</style><h1>Comparison qualification: every raw response</h1>'+''.join('<details><summary>'+html.escape(str(r['case']))+'</summary><pre>'+html.escape(json.dumps(r,indent=2))+'</pre></details>' for r in records)+'</html>')
    return out
