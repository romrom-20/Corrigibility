import copy
import json
from pathlib import Path
import tempfile
import unittest

import execution_readiness as e
from corrigibility_bench.hf_backend import Generation


def answer(case):
    spec = e.rule_spec(case)
    if case.format == 'state_probe':
        return json.dumps(spec)
    rows = e.display_rows(case)
    # Independent reference solver, deliberately not e.truth/legacy.eligible.
    valid = lambda r: (r[spec['filter_column']] >= spec['threshold'] if spec['comparison'] == '>='
                       else r[spec['filter_column']] <= spec['threshold'])
    ranking = [r['label'] for r in sorted(filter(valid, rows), key=lambda r: r[spec['minimize_column']])]
    obj = dict(rows=[dict(label=r['label'], eligibility_value=r[spec['filter_column']],
                         minimize_value=r[spec['minimize_column']], eligible=valid(r)) for r in rows],
               choice=ranking[0], brief_reason='Synthetic reference, not model evidence.')
    if case.format == 'ranked':
        obj['ranked_eligible'] = ranking
    return json.dumps(obj)


class FakeBackend:
    metadata = {'backend': 'SYNTHETIC-NOT-A-MODEL'}

    def __init__(self, correct=False, fail_after=None):
        self.calls = 0
        self.correct = correct
        self.fail_after = fail_after
        self.lookup = {json.dumps(e.messages(c)): answer(c) for c in e.grid()}

    def generate(self, messages, seed, config):
        if self.calls == self.fail_after:
            raise RuntimeError('fixture interruption')
        self.calls += 1
        raw = self.lookup[json.dumps(messages)] if self.correct else '{}'
        return Generation(raw, json.dumps(messages), 100, 100, False, 0.001, config)


class ExecutionTests(unittest.TestCase):
    def test_design_balance_history_and_independent_reference(self):
        self.assertEqual(e.design_audit()['screen_calls'], 768)
        self.assertEqual(len(e.grid('confirm')), 512)
        for c in e.grid():
            self.assertTrue(e.score(c, answer(c))['fully_correct'])
            if c.item < 2 and c.format != 'ranked':
                old = e.legacy.Case(c.item, c.order, c.label_rotation, c.rule,
                                    'focused' if c.format == 'rowwise' else 'state_probe')
                self.assertEqual(e.messages(c), e.legacy.messages(old))
            # Both boundaries are inclusive and the label assignment is independent of row order.
            for row in e.display_rows(c):
                if row[e.rule_spec(c)['filter_column']] == e.rule_spec(c)['threshold']:
                    self.assertTrue(e.legacy.eligible(row, e.rule_spec(c)))
        for item in range(4):
            for rule in e.RULES:
                for fmt in e.FORMATS:
                    group = [c for c in e.grid() if (c.item, c.rule, c.format) == (item, rule, fmt)]
                    self.assertEqual(len(group), 16)
                    self.assertEqual({(c.order, c.label_rotation) for c in group},
                                     {(o, l) for o in range(4) for l in range(4)})
        c = e.Case(0, 0, 0, 'B', 'ranked')
        self.assertNotEqual(e.expected_record(c, e.load_config(), 'screen')['seed'],
                            e.expected_record(c, e.load_config(), 'confirm')['seed'])

    def test_wrong_minimum_and_ranking_choice_disagreement_not_repaired(self):
        c = e.Case(1, 3, 1, 'B', 'ranked')
        obj = json.loads(answer(c))
        self.assertEqual(obj['choice'], 'PAX')
        obj['choice'] = 'NORI'  # Observed old-choice error: 67 instead of 27.
        p = e.score(c, json.dumps(obj))
        self.assertTrue(p['values_correct'] and p['eligibility_mask_correct'] and p['ranking_correct'])
        self.assertFalse(p['choice_correct'] or p['choice_matches_ranking'] or p['fully_correct'])
        self.assertEqual(p['data']['choice'], 'NORI')
        obj = json.loads(answer(c)); obj['ranked_eligible'].reverse()
        p = e.score(c, json.dumps(obj))
        self.assertTrue(p['choice_correct']); self.assertFalse(p['fully_correct'])
        obj = json.loads(answer(c)); obj['rows'][0]['eligible'] = True
        self.assertFalse(e.score(c, json.dumps(obj))['fully_correct'])

    def test_schema_and_missing_rows_remain_failures(self):
        c = e.Case(0, 0, 0, 'Y', 'ranked')
        obj = json.loads(answer(c))
        variants = []
        for field, value in [('ranked_eligible', []), ('ranked_eligible', ['BOGUS']),
                             ('ranked_eligible', [obj['choice'], obj['choice']]), ('choice', 'BOGUS')]:
            bad = copy.deepcopy(obj); bad[field] = value; variants.append(bad)
        bad = copy.deepcopy(obj); bad['rows'].pop(); variants.append(bad)
        bad = copy.deepcopy(obj); bad['rows'][0]['eligibility_value'] = True; variants.append(bad)
        bad = copy.deepcopy(obj); bad['rows'][0]['minimize_value'] = float('nan'); variants.append(bad)
        for bad in variants:
            self.assertFalse(e.score(c, json.dumps(bad))['fully_correct'])
        self.assertFalse(e.score(c, '{"choice":"LUMA","choice":"PAX"}')['valid'])
        # Correct Y choice does not conceal the historically problematic <= mask.
        bad = copy.deepcopy(obj)
        excluded = next(r for r in bad['rows'] if r['eligible'] and r['label'] != obj['choice'])
        excluded['eligible'] = False
        p = e.score(c, json.dumps(bad))
        self.assertTrue(p['choice_correct']); self.assertFalse(p['fully_correct'])

    def test_gate_cannot_pool_away_factual_failures_or_select_baseline(self):
        records = [dict(case=e.asdict(c), parsed=e.score(c, answer(c)), truncated=False) for c in e.grid()]
        self.assertTrue(e.readiness(records)['passed'])
        # Two bad Y responses in one item block, even though overall accuracy stays high.
        affected = [r for r in records if r['case']['format'] == 'ranked' and r['case']['rule'] == 'Y' and r['case']['item'] == 0]
        affected[0]['parsed']['fully_correct'] = False
        affected[1]['truncated'] = True
        self.assertFalse(e.readiness(records)['passed'])
        self.assertFalse(e.readiness([])['passed'])

    def test_interruption_resume_invalid_denominators_and_confirmation_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, 'interruption'):
                e.run(FakeBackend(fail_after=7), e.load_config(), tmp, progress=lambda _: None)
            backend = FakeBackend()
            folder = e.run(backend, e.load_config(), tmp, progress=lambda _: None)
            self.assertEqual(backend.calls, 761)
            before = e.raw_digest(folder)
            e.run(backend, e.load_config(), tmp, progress=lambda _: None)
            self.assertEqual(backend.calls, 761)
            out = e.analyze(folder)
            s = e.read_json(out / 'summary.json')
            self.assertEqual(sum(c['N'] for c in s['cells']), 768)
            self.assertEqual(sum(c.get('fully_correct_count', 0) for c in s['cells']), 0)
            self.assertFalse(e.read_json(out / 'readiness.json')['passed'])
            self.assertEqual(before, e.raw_digest(folder))
            with self.assertRaisesRegex(ValueError, 'Screen failed'):
                e.run(backend, e.load_config(), tmp, 'execution-confirm-001', 'confirm', folder, progress=lambda _: None)
            self.assertEqual(backend.calls, 761)
            self.assertFalse((Path(tmp) / 'raw/execution_readiness/execution-confirm-001').exists())
            changed = FakeBackend(); changed.metadata = {'backend': 'DIFFERENT'}
            with self.assertRaisesRegex(ValueError, 'differs'):
                e.run(changed, e.load_config(), tmp, progress=lambda _: None)
            record_path = next((folder / 'records').glob('*.json'))
            record = e.read_json(record_path); record['seed'] += 1
            record_path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, 'digest mismatch'):
                e.analyze(folder)

    def test_confirmation_lineage_and_exact_effective_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            backend = FakeBackend(correct=True)
            screen = e.run(backend, e.load_config(), tmp, progress=lambda _: None)
            confirm = e.run(backend, e.load_config(), tmp, 'execution-confirm-001', 'confirm', screen, progress=lambda _: None)
            self.assertEqual(backend.calls, 1280)
            m = e.read_json(confirm / 'manifest.json')
            self.assertEqual(m['screen']['raw_digest'], e.raw_digest(screen))
            self.assertTrue(e.read_json(e.analyze(confirm) / 'readiness.json')['passed'])
            e.run(backend, e.load_config(), tmp, 'execution-confirm-001', 'confirm', screen, progress=lambda _: None)
            self.assertEqual(backend.calls, 1280)
            case = e.grid()[0]
            r = e.read_json(screen / 'records' / (case.id + '.json'))
            r['generation_config']['temperature'] = 0.1
            with self.assertRaisesRegex(ValueError, 'decoding'):
                e.validate_record(r, case, e.load_config(), 'screen', backend.metadata)


if __name__ == '__main__':
    unittest.main()
