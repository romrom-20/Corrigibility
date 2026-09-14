"""Offline regressions for notebook sign-off and interrupted pilot recovery."""
import json
from pathlib import Path
import tempfile
import unittest

from corrigibility_bench.runner import load_config, read_json, review_template, run_experiment
from scripts.notebook_workflow import ensure_smoke_approval
from test_normative_hysteresis import RecordingBackend


class NotebookWorkflowTests(unittest.TestCase):
    def test_approval_reuse_and_pilot_resume_preserve_records(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_config()
            smoke = run_experiment(RecordingBackend(), config, results_root=root,
                                   experiment_id="smoke", progress=lambda _: None)
            review = review_template(smoke)
            review.update(reviewer="SYNTHETIC TEST FIXTURE", task_comprehension_acceptable=True, approve_pilot=True)
            for note in review["trajectories"].values():
                note.update(reviewed=True, notes="Synthetic fixture, not a real review.")
            edit = root / "review.json"
            edit.write_text(json.dumps(review))
            approval = ensure_smoke_approval(smoke, edit)
            before = approval.read_bytes()
            self.assertEqual(ensure_smoke_approval(smoke, edit), approval)
            self.assertEqual(ensure_smoke_approval(smoke), approval)
            self.assertEqual(approval.read_bytes(), before)
            pilot_args = dict(mode="pilot", results_root=root, experiment_id="pilot",
                              smoke_run=smoke, progress=lambda _: None)
            with self.assertRaisesRegex(RuntimeError, "simulated"):
                run_experiment(RecordingBackend(fail_after=5), config, **pilot_args)
            records = root / "raw/normative_hysteresis/pilot/records"
            saved = {p.name: p.read_bytes() for p in records.glob("*.json")}
            backend = RecordingBackend()
            pilot = run_experiment(backend, config, **pilot_args)
            self.assertEqual(len(backend.calls), 1435)
            self.assertEqual(read_json(pilot / "complete.json")["calls"], 1440)
            for name, content in saved.items():
                self.assertEqual((records / name).read_bytes(), content)
            review["trajectories"][next(iter(review["trajectories"]))]["notes"] = "Different judgment"
            edit.write_text(json.dumps(review))
            with self.assertRaisesRegex(ValueError, "differs from saved"):
                ensure_smoke_approval(smoke, edit)
            review["approve_pilot"] = False
            edit.write_text(json.dumps(review))
            with self.assertRaises(ValueError):
                ensure_smoke_approval(smoke, edit)
            self.assertEqual(approval.read_bytes(), before)

    def test_signed_rejection_explains_block_without_writing_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            smoke = run_experiment(RecordingBackend(), load_config(), results_root=root,
                                   experiment_id="smoke", progress=lambda _: None)
            review = review_template(smoke)
            review["reviewer"] = "SYNTHETIC TEST FIXTURE"
            edit = root / "review.json"
            edit.write_text(json.dumps(review))
            with self.assertRaisesRegex(ValueError, "approve_pilot=False"):
                ensure_smoke_approval(smoke, edit)
            self.assertFalse((smoke / "review_approval.json").exists())


if __name__ == "__main__":
    unittest.main()
