#!/usr/bin/env python3
import argparse
from llm_arithmetic.runner import run
from dotenv import load_dotenv
import os
load_dotenv()

DEFAULT_MODEL = os.getenv("MODEL")
DEFAULT_TRIALS = 10
DEFAULT_DEPTHS = list(range(2, 11))
DEFAULT_OUTPUT_DIR = "results"
DEFAULT_REASONING_EFFORT = "high" # None, "low", "medium", "high"

def main():
    parser = argparse.ArgumentParser(
        description="LLM Arithmetic Evaluation Harness"
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help="Model name, e.g. openai/gpt-4o"
    )
    parser.add_argument(
        "--trials", type=int, default=DEFAULT_TRIALS,
        help="Number of trials per variant-depth cell"
    )
    parser.add_argument(
        "--depths", nargs='+', type=int,
        default=DEFAULT_DEPTHS,
        help="List of digit depths to test"
    )
    parser.add_argument(
        "--output_dir", default=DEFAULT_OUTPUT_DIR,
        help="Directory to store per-trial result files"
    )
    parser.add_argument(
        "--reasoning_effort", choices=["low","medium","high"],
        default=DEFAULT_REASONING_EFFORT,
        help="Reasoning effort level passed to LLM (low, medium, high)"
    )
    args = parser.parse_args()
    if not args.model:
        parser.error("the following arguments are required: --model (or set MODEL in .env)")
    run(
        model=args.model,
        trials_per_cell=args.trials,
        depths=args.depths,
        output_dir=args.output_dir,
        reasoning_effort=args.reasoning_effort
    )

if __name__ == "__main__":
    main() 