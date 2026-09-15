import json
import tempfile
import unittest
import objective_transfer as t
from corrigibility_bench.hf_backend import Generation

class FakeBackend:
    metadata={'backend':'SYNTHETIC-NOT-A-MODEL'}
    def __init__(self,fail_after=None):self.calls=0;self.fail_after=fail_after
    def generate(self,messages,seed,config):
        if self.calls==self.fail_after:raise RuntimeError('fixture interruption')
        self.calls+=1
        return Generation('{}',json.dumps(messages),10,2,False,0.001,config)

class TransferTests(unittest.TestCase):
    def test_scope_preserves_all_items_orders_labels_and_controls(self):
        grid=t.grid();self.assertEqual(len(grid),128);self.assertEqual(t.budget()['total_calls'],320)
        self.assertEqual(len({x.id for x in grid}),128)
        for condition in t.CONDITIONS:
            for depth in (0,1):self.assertEqual(len([x for x in grid if x.condition==condition and x.depth==depth]),16)
        self.assertEqual(t.initial(t.Trial(0,0,0,'SELF_DESCRIBE_A',0)),t.initial(t.Trial(0,0,0,'SELF_JUSTIFY_A',0)))

    def test_final_prompt_matched_and_siblings_never_leak(self):
        suffixes=[]
        for condition in t.CONDITIONS:
            x=t.Trial(0,0,0,condition,1);h=t.frozen(x,['PUBLIC_PLAN_SENTINEL']);before=json.dumps(h)
            branches=t.branches(x,h)
            self.assertIn('PUBLIC_PLAN_SENTINEL',json.dumps(branches['behavior']))
            self.assertIn('PUBLIC_PLAN_SENTINEL',json.dumps(branches['state']))
            branches['behavior'].append(dict(role='assistant',content='BEHAVIOR_ONLY'))
            self.assertNotIn('BEHAVIOR_ONLY',json.dumps(branches['state']))
            self.assertEqual(json.dumps(h),before)
            suffixes.append(h[-1]['content'])
        self.assertEqual(len(set(suffixes)),1)
        self.assertNotIn('Current rule A',json.dumps(t.initial(t.Trial(0,0,0,'FRESH_B',0))))

    def test_wrong_planning_never_removes_trial_or_redefines_old_optimum(self):
        x=t.Trial(0,0,0,'SELF_JUSTIFY_A',1)
        behavior=dict(valid=True,choice_correct=False,fully_correct=False,old_optimum_selected=True,
                      unfiltered_current_selected=False,choice_role='old')
        plan=[dict(parsed=dict(valid=True,choice_correct=False,fully_correct=False,choice_role='new'))]
        o=t.outcomes(x,behavior,dict(valid=True,fully_correct=True),plan)
        self.assertEqual(o['recognized_old_choice'],1);self.assertEqual(o['planning_correct'],0)
        self.assertEqual(o['repeats_actual_recommendation'],0)
        missing=t.outcomes(x,dict(valid=False),dict(valid=False),plan)
        self.assertEqual(missing['recognized_old_upper'],1);self.assertEqual(missing['B_success'],0)

    def test_interruption_resume_and_no_exclusion(self):
        with tempfile.TemporaryDirectory() as tmp:
            config=t.load_config()
            with self.assertRaisesRegex(RuntimeError,'interruption'):t.run(FakeBackend(5),config,tmp,progress=lambda _:None)
            b=FakeBackend();folder=t.run(b,config,tmp,progress=lambda _:None);self.assertEqual(b.calls,315)
            digest=t.raw_digest(folder);t.run(b,config,tmp,progress=lambda _:None);self.assertEqual(b.calls,315)
            out=t.analyze(folder);s=t.read_json(out/'summary.json')
            self.assertEqual(sum(c['N'] for c in s['cells']),128)
            self.assertEqual(sum(c['B_success_count'] for c in s['cells']),0)
            self.assertEqual(t.raw_digest(folder),digest)
            with self.assertRaisesRegex(ValueError,'differs'):t.run(b,dict(config,temperature=0.5),tmp,progress=lambda _:None)

if __name__=='__main__':unittest.main()
