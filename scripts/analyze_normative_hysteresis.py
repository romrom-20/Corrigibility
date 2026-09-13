#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from corrigibility_bench.analysis import analyze_run

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    parser.add_argument("--results-root")
    args = parser.parse_args()
    analyze_run(args.run_dir, args.results_root)
