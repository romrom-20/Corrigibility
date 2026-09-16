#!/usr/bin/env python3
"""Read-only consistency audit of a pasted replication summary + transcript export.

Cannot certify original archive bytes/manifest. Never rewrites historical scores.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import objective_replication as protocol


def audit(path):
    text = Path(path).read_text()
    decoder = json.JSONDecoder()
    summary = json.loads(text.splitlines()[0])
    records = [decoder.raw_decode(text, match.end())[0]
               for match in re.finditer(r'Trial\([^\n]+?\)(?=\{)', text)]
    specs = [protocol.Trial(**r['behavior']['trial']) for r in records]
    if Counter(t.id for t in specs) != Counter(t.id for t in protocol.grid()):
        raise ValueError('Missing, extra or duplicate trial')
    config = protocol.load_config()
    all_outcomes, failures, comparison_rows = [], [], []
    calls = 0
    models = set()
    for t, group in zip(specs, records):
        if set(group) != set(protocol.branch_names(t)):
            raise ValueError('Incorrect branch set')
        h = protocol.frozen(t, [group['planning']['raw_text']] if t.depth else [])
        branches = protocol.branches(t, h)
        for branch, r in group.items():
            calls += 1
            models.add(json.dumps(r['model'], sort_keys=True))
            expected_h = protocol.initial(t) if branch == 'planning' else h
            expected_m = protocol.append(expected_h, protocol.planning_request(t)) if branch == 'planning' else branches[branch]
            if (r['trial'] != protocol.asdict(t) or r['branch'] != branch or r['history'] != expected_h
                    or r['messages'] != expected_m or r['parsed'] != protocol.parse(t, branch, r['raw_text'])
                    or r['seed'] != protocol.derived_seed(config['seed'], protocol.VERSION, t.id, branch)
                    or r['requested_generation_config'] != protocol.settings(config, branch)
                    or any(r['generation_config'].get(k) != v for k, v in protocol.settings(config, branch).items())
                    or r['prompt_hash'] != protocol.digest(expected_m)
                    or r['history_hash'] != protocol.digest(expected_h)
                    or r['rendered_prompt_hash'] != protocol.digest(r['rendered_prompt'])):
                raise ValueError(f'Record mismatch: {t}, {branch}')
        outcome = protocol.outcomes(t, group['behavior']['parsed'], group['state']['parsed'],
                                    [group['planning']] if t.depth else [])
        all_outcomes.append(dict(protocol.asdict(t), **outcome))
        if not group['behavior']['parsed']['choice_correct']:
            failures.append(group['behavior'])
        if t.depth:
            a, b = group['behavior']['parsed'], group['comparison']['parsed']
            comparison_rows.append(dict(condition=t.condition, baseline_success=a['choice_correct'],
                comparison_success=b['choice_correct'], comparison_old=b['old_optimum_selected'],
                comparison_valid=b['valid'], comparison_verified=b['fully_correct'],
                fixed=not a['choice_correct'] and b['choice_correct'], harmed=a['choice_correct'] and not b['choice_correct']))
    for cell in summary['cells']:
        group = [r for r in all_outcomes if (r['condition'], r['depth']) == (cell['condition'], cell['depth'])]
        assert cell['N'] == len(group)
        for key, value in cell.items():
            if key.endswith('_count'):
                assert sum(r[key[:-6]] or 0 for r in group) == value, key
            elif key == 'planning_assessed':
                assert sum(r[key] for r in group) == value
    for cell in summary['comparison_cells']:
        group = [r for r in comparison_rows if r['condition'] == cell['condition']]
        assert len(group) == cell['N']
        for key, value in cell.items():
            if key.endswith('_count'):
                assert sum(r[key[:-6]] for r in group) == value, key
    for cell in summary['strata']:
        group = [r for r in all_outcomes if (r['condition'], r['depth'], r[cell['field']]) ==
                 (cell['condition'], cell['depth'], cell['value'])]
        assert len(group) == cell['N']
        assert sum(r['B_success'] for r in group) == cell['B_success_count']
        assert sum(r['old_choice'] for r in group) == cell['old_choice_count']
    assert len(models) == 1
    return dict(trials=len(records), calls=calls, checks='prompts, history, seeds, decoding, parsing, stored hashes, main/comparison/stratum counts',
        archive_integrity_verified=False, reported_raw_digest=summary['raw_digest'],
        behavior_success=sum(r['B_success'] for r in all_outcomes), state_correct=sum(r['state_correct'] for r in all_outcomes),
        behavior_failures=len(failures), failed_by_rotation=dict(Counter(r['trial']['label_rotation'] for r in failures)),
        failed_chosen_labels=dict(Counter(r['parsed']['data']['choice'] for r in failures)),
        all_failed_values_and_masks_correct=all(r['parsed']['values_correct'] and r['parsed']['eligibility_mask_correct'] for r in failures),
        comparison_fixed=sum(r['fixed'] for r in comparison_rows), comparison_harmed=sum(r['harmed'] for r in comparison_rows),
        truncated=sum(r['truncated'] for group in records for r in group.values()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('attachment', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.attachment), indent=2))
