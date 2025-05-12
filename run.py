#!/usr/bin/env python3
import argparse
from llm_arithmetic.runner import run
from dotenv import load_dotenv
import os
load_dotenv()

DEFAULT_MODEL = os.getenv("MODEL")
DEFAULT_TRIALS = 10 # Default 10
DEFAULT_DEPTHS = list(range(2, 11)) # Default 2-10
DEFAULT_OUTPUT_DIR = "results" # Default results directory
DEFAULT_REASONING_EFFORT = None # None, "low", "medium", "high"
DEFAULT_RESUME_FILE = None # Default None
DEFAULT_RETRIES = 3 # Default 3

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
    parser.add_argument(
        "--resume_file", default=DEFAULT_RESUME_FILE,
        help="Path to existing trial JSONL file to resume from"
    )
    parser.add_argument(
        "--retries", type=int, default=DEFAULT_RETRIES,
        help="Number of retries for failed LLM calls"
    )
    args = parser.parse_args()
    if not args.model:
        parser.error("the following arguments are required: --model (or set MODEL in .env)")
    run(
        model=args.model,
        trials_per_cell=args.trials,
        depths=args.depths,
        output_dir=args.output_dir,
        reasoning_effort=args.reasoning_effort,
        resume_file=args.resume_file,
        retries=args.retries
    )

if __name__ == "__main__":
    main() 