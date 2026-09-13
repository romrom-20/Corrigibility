"""Backend regressions without loading weights or depending on CUDA."""
import copy
from contextlib import nullcontext
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from corrigibility_bench.hf_backend import HFBackend
from corrigibility_bench.runner import generation_settings, load_config


class TokenArray:
    shape = (1, 3)

    def to(self, device):
        return self


class FakeConfig(SimpleNamespace):
    def __init__(self, **kwargs):
        super().__init__(**dict(dict(do_sample=False, temperature=1.0, bos_token_id=None), **kwargs))

    def to_dict(self):
        return vars(self).copy()


class BackendGenerationTests(unittest.TestCase):
    def make_backend(self, drift=False):
        backend = HFBackend.__new__(HFBackend)
        backend.context_limit = 4096
        backend.tokenizer = SimpleNamespace(
            apply_chat_template=lambda *a, **k: 'rendered prompt',
            eos_token_id=9, pad_token_id=0,
            decode=lambda *a, **k: '{"choice":"MAPLE","brief_reason":"fixture"}')
        class Tokenizer:
            def __call__(self, *a, **k):
                return {'input_ids': TokenArray()}
        tokenizer = Tokenizer()
        tokenizer.__dict__.update(backend.tokenizer.__dict__)
        backend.tokenizer = tokenizer
        class Output:
            def __getitem__(self, item):
                return [8, 9]
        calls = []
        def prepare(gc, use_model_defaults=None):
            effective = copy.deepcopy(gc)
            effective.bos_token_id = 7
            # Model the library behavior that broke the smoke run.
            if use_model_defaults is not False or drift:
                effective.do_sample = True
                effective.temperature = 0.6
            calls.append(('prepare', use_model_defaults))
            return effective, {}
        def generate(**kwargs):
            effective, _ = prepare(kwargs['generation_config'], kwargs.get('use_model_defaults'))
            calls.append(('generate', effective.to_dict()))
            return Output()
        backend.model = SimpleNamespace(device='fixture', generation_config=SimpleNamespace(eos_token_id=[9]),
                                        _prepare_generation_config=prepare, generate=generate)
        backend.torch = SimpleNamespace(inference_mode=nullcontext, cuda=SimpleNamespace(synchronize=lambda: None))
        return backend, calls

    def test_effective_smoke_and_pilot_settings_are_preserved_and_recorded(self):
        module = SimpleNamespace(GenerationConfig=FakeConfig, set_seed=lambda seed: None)
        for mode in ('smoke', 'pilot'):
            with self.subTest(mode=mode), patch.dict(sys.modules, {'transformers': module}):
                backend, calls = self.make_backend()
                settings = generation_settings(load_config(), mode, 'behavior')
                result = backend.generate([], 123, settings)
                actual = next(config for kind, config in calls if kind == 'generate')
                self.assertEqual(result.generation_config, actual)
                self.assertEqual(result.generation_config['bos_token_id'], 7)
                self.assertTrue(all(value is False for kind, value in calls if kind == 'prepare'))
                for key, value in settings.items():
                    self.assertEqual(actual[key], value)
                self.assertFalse(result.truncated)

    def test_unexpected_effective_setting_change_stops_before_inference(self):
        module = SimpleNamespace(GenerationConfig=FakeConfig, set_seed=lambda seed: None)
        with patch.dict(sys.modules, {'transformers': module}):
            backend, calls = self.make_backend(drift=True)
            with self.assertRaisesRegex(RuntimeError, 'Generation setting changed'):
                backend.generate([], 123, generation_settings(load_config(), 'smoke', 'behavior'))
            self.assertFalse(any(kind == 'generate' for kind, _ in calls))


if __name__ == '__main__':
    unittest.main()
