"""Verify installed Transformers config resolution without running model inference."""

def verify_generation_policy(backend, config, old_record=None):
    from transformers import GenerationConfig
    from corrigibility_bench.runner import generation_settings
    report = {'checks': [], 'model_revision': backend.metadata['model_revision'],
              'generation_policy': backend.metadata['generation_policy']}
    keys = ('do_sample', 'temperature', 'top_p', 'top_k', 'num_beams', 'repetition_penalty', 'max_new_tokens')
    if old_record is not None:
        recorded = GenerationConfig.from_dict(old_record['generation_config'])
        replayed, _ = backend.model._prepare_generation_config(recorded)
        report['old_smoke_config_resolution'] = {
            'trajectory_id': old_record['trajectory_id'],
            'recorded': {k: getattr(recorded, k) for k in keys},
            'resolved_by_installed_library': {k: getattr(replayed, k) for k in keys},
            'note': 'Reconstruction from the saved config and matching live model/library, not a new completion.'}
    for mode in ('smoke', 'pilot'):
        for branch in ('planning', 'behavior', 'uptake'):
            expected = generation_settings(config, mode, branch)
            requested = GenerationConfig(**expected, eos_token_id=backend.model.generation_config.eos_token_id,
                                         pad_token_id=backend.tokenizer.pad_token_id, use_cache=True)
            actual, _ = backend.model._prepare_generation_config(requested, use_model_defaults=False)
            repeated, _ = backend.model._prepare_generation_config(actual, use_model_defaults=False)
            assert actual.to_dict() == repeated.to_dict(), 'Effective config is not idempotent'
            for k, value in expected.items():
                assert getattr(actual, k) == value, (mode, branch, k, value, getattr(actual, k))
            report['checks'].append({'mode': mode, 'branch': branch, 'passed': True,
                                     'effective': {k: getattr(actual, k) for k in keys}})
    report['passed'] = True
    return report
