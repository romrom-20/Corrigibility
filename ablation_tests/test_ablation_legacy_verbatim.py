import json
from pathlib import Path
import tempfile
import unittest

import ablation_legacy_verbatim as a
import context_diagnostic_v2 as v2
from corrigibility_bench.hf_backend import Generation


class FakeBackend:
    def __init__(self, metadata, mode='correct'):
        self.metadata = metadata
        self.mode = mode
        self.lookup = {digest_msgs: v2.expected_answer(case) for case in a.grid()
                       for digest_msgs in [v2.digest(v2.messages(case))]}

    def generate(self, messages, seed, config):
        answer = self.lookup[v2.digest(messages)]
        if self.mode == 'always_true':
            answer = {'eligible': True}
        return Generation(json.dumps(answer), json.dumps(messages), 10, 10, False, 0.001, config)


NF4_META = {'backend': 'FIXTURE', 'quantization': 'nf4', 'enable_thinking': False, 'gpu': 'fixture'}
BF16_META = {'backend': 'FIXTURE', 'quantization': 'none', 'enable_thinking': True, 'gpu': 'fixture'}


class AblationTests(unittest.TestCase):
    def test_grid_is_the_384_legacy_verbatim_cases_from_v2(self):
        cases = a.grid()
        self.assertEqual(len(cases), 384)
        self.assertTrue(all(c.family == 'eligibility' and c.variant == 'legacy_verbatim' for c in cases))
        v2_ids = {c.id for c in v2.grid() if c.family == 'eligibility' and c.variant == 'legacy_verbatim'}
        self.assertEqual({c.id for c in cases}, v2_ids)

    def test_forbidden_run_id_rejected(self):
        with self.assertRaises(ValueError):
            a.run(None, a.load_config(), '/tmp', run_id='context-002')

    def test_poisoned_ablation_run_ids_rejected(self):
        # 001 was truncated at 160 tokens; 002 was scored with the pre-fix
        # scorer. Neither may be reused -- rerun under a fresh run_id.
        for run_id in ('ablation-bf16-thinking-001', 'ablation-bf16-thinking-002'):
            with self.assertRaises(ValueError):
                a.run(None, a.load_config(), '/tmp', run_id=run_id)

    def test_strip_thinking_extracts_json_after_think_tag(self):
        case = a.grid()[0]
        answer = json.dumps(v2.expected_answer(case))
        raw = f'<think>\nSome reasoning about quality vs threshold...\n</think>\n\n{answer}'
        self.assertEqual(a.strip_thinking(raw), answer)
        result = a.score(case, raw)
        self.assertTrue(result['valid'])
        self.assertTrue(result['fully_correct'])

    def test_strip_thinking_is_a_noop_for_non_thinking_output(self):
        case = a.grid()[0]
        answer = json.dumps(v2.expected_answer(case))
        self.assertEqual(a.strip_thinking(answer), answer)

    def test_design_audit_seed_matches_v2(self):
        audit = a.design_audit()
        self.assertEqual(audit['calls'], 384)
        self.assertEqual(audit['max_new_tokens'], 160)

    def test_thinking_config_has_larger_token_budget_and_is_accepted(self):
        thinking_config = a.load_config('ablation_legacy_verbatim_thinking_v1.json')
        audit = a.design_audit(thinking_config)
        self.assertEqual(audit['max_new_tokens'], 1024)
        sample = a.grid()[0]
        self.assertEqual(a.settings(thinking_config, sample)['max_new_tokens'], 1024)
        self.assertEqual(a.settings(a.load_config(), sample)['max_new_tokens'], 160)

    def test_unfrozen_config_rejected(self):
        bad = dict(a.load_config(), max_new_tokens=99999)
        with self.assertRaises(ValueError):
            a.design_audit(bad)
        with self.assertRaises(ValueError):
            a.run(None, bad, '/tmp', run_id='some-new-run')

    def test_run_resume_analyze_and_compare(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # First, populate a fake context-002 (all wrong: always_true backend).
            base_folder = v2.Path(root) / 'raw/context_diagnostic_v2/context-002'
            # Reuse v2's own run() with a full-grid fake backend restricted for speed
            # would take too long here; instead build a matching subset manually.
            base_folder.mkdir(parents=True)
            # Build a legit context-002-shaped run using v2.run with a lightweight
            # fake backend, but only assert on the ablation compare logic using
            # a hand-built base to keep the test fast.
            base_records_dir = base_folder / 'records'
            base_records_dir.mkdir()
            from corrigibility_bench.runner import write_new_json, raw_digest
            cases = v2.grid()
            for c in cases:
                seed = v2.derived_seed(v2.load_config()['seed'], v2.VERSION, c.id)
                expected = v2.expected_answer(c)
                raw = json.dumps(expected)
                prompt = v2.messages(c)
                record = dict(case=json.loads(json.dumps(v2.asdict(c))), messages=prompt, prompt_hash=v2.digest(prompt),
                              seed=seed, requested_generation_config=v2.settings(v2.load_config(), c),
                              raw_text=raw, rendered_prompt=json.dumps(prompt), input_tokens=1, output_tokens=1,
                              truncated=False, elapsed_seconds=0.001, generation_config=v2.settings(v2.load_config(), c),
                              model=NF4_META, timestamp='fixture', rendered_prompt_hash=v2.digest(json.dumps(prompt)),
                              parsed=v2.score(c, raw))
                write_new_json(base_records_dir / (c.id + '.json'), record)
            write_new_json(base_folder / 'manifest.json', dict(version=v2.VERSION, run_id='context-002', config=v2.load_config(),
                           model=NF4_META, sources=v2.sources(), cases=[json.loads(json.dumps(v2.asdict(c))) for c in cases]))
            write_new_json(base_folder / 'complete.json', dict(calls=len(cases), raw_digest=raw_digest(base_folder), completed_at='fixture'))

            # Now run the ablation with a backend that always says True -- fixes
            # nothing (legacy_verbatim's true-answer cells were already right,
            # ineligible cells still wrong), but proves the plumbing end to end.
            ablation_folder = a.run(FakeBackend(BF16_META, 'always_true'), a.load_config(), root, run_id='ablation-bf16-001')
            derived = a.analyze(ablation_folder)
            summary = json.loads((derived / 'summary.json').read_text())
            self.assertEqual(summary['N'], 384)

            comparison = a.compare_to_context002(base_folder, ablation_folder)
            self.assertEqual(comparison['N'], 384)
            self.assertEqual(comparison['context002_model']['quantization'], 'nf4')
            self.assertEqual(comparison['ablation_model']['quantization'], 'none')
            # base (context-002) was fully correct by construction; always_true
            # ablation harms every ineligible case and fixes none.
            self.assertEqual(comparison['fixed'], 0)
            self.assertGreater(comparison['harmed'], 0)

            # Resuming a complete ablation run must not require a backend.
            a.run(None, a.load_config(), root, run_id='ablation-bf16-001')


if __name__ == '__main__':
    unittest.main()
