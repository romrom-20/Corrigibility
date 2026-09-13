#!/usr/bin/env python3
"""CLI defaults to a no-model call-budget preview; --execute explicitly starts GPU inference."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from corrigibility_bench.normative_hysteresis import call_budget, trial_grid
from corrigibility_bench.runner import load_config, run_experiment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--mode", choices=("smoke", "pilot"), default="smoke")
    parser.add_argument("--results-root", default="results")
    parser.add_argument("--experiment-id")
    parser.add_argument("--smoke-run")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    print(call_budget(trial_grid(args.mode, config["seed"])))
    if args.execute:
        from corrigibility_bench.hf_backend import HFBackend
        backend = HFBackend(config)
        print(run_experiment(backend, config, args.mode, args.results_root, args.experiment_id, args.smoke_run))


if __name__ == "__main__":
    main()
