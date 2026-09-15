"""Known-answer analysis tests; inputs are explicitly synthetic fixtures."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

from corrigibility_bench.normative_hysteresis import *

HAS_ANALYSIS = all(importlib.util.find_spec(p) for p in ("numpy", "pandas", "matplotlib"))


@unittest.skipUnless(HAS_ANALYSIS, "Install analysis dependencies to run artifact and estimator tests")
class AnalysisTests(unittest.TestCase):
    def test_audit_covers_failures_and_samples_choice_without_uptake_filter(self):
        import pandas as pd
        from corrigibility_bench.analysis import audit_selection_manifest
        baseline = dict(decision_verified=1, A_residue=0, B_success=1, uptake_correct=1, behavior_valid=1,
                        uptake_valid=1, behavior_truncated=False, uptake_truncated=False,
                        planning_truncated=False)
        data = [dict(baseline, trajectory_id=f"correct-{i}") for i in range(10)]
        data[0]["uptake_correct"] = 0
        for field, value in (("A_residue", 1), ("uptake_correct", 0), ("behavior_valid", 0),
                             ("uptake_valid", 0), ("behavior_truncated", True),
                             ("uptake_truncated", True), ("planning_truncated", True)):
            data.append(dict(baseline, trajectory_id=field, B_success=0, **{field: value}))
        data.append(dict(baseline, trajectory_id="other_wrong_choice", B_success=0))
        data.append(dict(baseline, trajectory_id="correct_but_unverified", decision_verified=0))
        frame = pd.DataFrame(data)
        audit = audit_selection_manifest(frame, "pilot", seed=42)
        self.assertEqual(len(audit["sampled_correct_final_choice_ids"]), 10)
        self.assertIn("unverified_decision", audit["selection_reasons"]["correct_but_unverified"])
        self.assertIn("correct-0", audit["correct_final_choice_population"])
        self.assertEqual(audit["correct_sample_shortfall"], 0)
        mandatory = set(frame[frame.B_success == 0].trajectory_id) | {"correct-0", "correct_but_unverified"}
        expected = mandatory | set(audit["sampled_correct_final_choice_ids"])
        self.assertEqual(set(audit["selection_reasons"]), expected)
        self.assertEqual(audit["selected_count"], len(expected))
        self.assertEqual(set(audit["unselected_ids"]), set(frame.trajectory_id) - expected)
        for field in ("behavior", "uptake", "planning"):
            self.assertIn(field + "_truncation", audit["selection_reasons"][field + "_truncated"])
        self.assertIn("incorrect_final_choice", audit["selection_reasons"]["other_wrong_choice"])
        self.assertEqual(audit, audit_selection_manifest(frame.iloc[::-1], "pilot", seed=42))
        short = audit_selection_manifest(frame.iloc[:3], "pilot", seed=42)
        self.assertEqual(short["correct_sample_shortfall"], 7)
        smoke = audit_selection_manifest(frame, "smoke", seed=42)
        self.assertTrue(all("all_smoke_trials" in r for r in smoke["selection_reasons"].values()))

    def test_known_nonzero_paired_contrasts(self):
        import pandas as pd
        from corrigibility_bench.analysis import contrast_table
        data = []
        values = {C0: [0, 0, 0], C1: [1, 0, 0], C2: [1, 1, 1], C3: [1, 1, 0], F0: [0, 0, 0], F1: [1, 0, 0]}
        for scenario in SCENARIOS:
            for variant in (0, 1):
                for condition, samples in values.items():
                    for replication, value in enumerate(samples):
                        data.append(dict(scenario_id=scenario, order_variant=variant, condition=condition,
                                         investment_depth=3, replication=replication, recognized_A_residue=value))
        table = contrast_table(pd.DataFrame(data), n_boot=100).set_index("estimand")
        expected = {"NH_self_justify": 1, "OwnershipEffect": 1/3, "JustificationEffect": 2/3, "FH": 1/3, "Specificity": 2/3}
        for name, value in expected.items():
            self.assertAlmostEqual(table.loc[name, "estimate"], value)
            self.assertEqual(table.loc[name, "n_clusters"], 8)
            self.assertAlmostEqual(table.loc[name, "ci_low"], value)
        small = contrast_table(pd.DataFrame(data[:18]), n_boot=100)
        self.assertTrue(small.ci_low.isna().all())

    def test_end_to_end_analysis_keeps_raw_immutable(self):
        from corrigibility_bench.analysis import analyze_run, load_trials
        from corrigibility_bench.runner import load_config, raw_digest, run_experiment
        from test_normative_hysteresis import RecordingBackend
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            run = run_experiment(RecordingBackend(), load_config(), results_root=root, experiment_id="fixture", progress=lambda _: None)
            fingerprint = raw_digest(run)
            derived = analyze_run(run, n_boot=100, emit=lambda _: None)
            self.assertTrue(derived.is_relative_to(root / "derived"))
            self.assertFalse(derived.is_relative_to(run))
            self.assertEqual(raw_digest(run), fingerprint)
            for name in ("contingency.csv", "aggregate.csv", "by_scenario.csv", "by_variant.csv", "contrasts.csv", "depth_changes.csv", "trials.csv", "curves.png", "curves.pdf", "transcript_audit.html", "smoke_review.json", "audit_selection.json", "baseline_diagnostics.csv", "planning_steps.csv", "planning_summary.csv", "diagnostic_readiness.json"):
                self.assertTrue((derived / name).stat().st_size > 0, name)
            frame, _, _ = load_trials(run)
            self.assertEqual(len(frame), 144)
            self.assertEqual(frame.behavior_valid.sum(), 144)
            second = analyze_run(run, n_boot=100, emit=lambda _: None)
            self.assertNotEqual(derived, second)


if __name__ == "__main__":
    unittest.main()
