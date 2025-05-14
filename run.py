import argparse
from llm_arithmetic.runner import run
from dotenv import load_dotenv
import os
import json
load_dotenv()

MODEL = os.getenv("MODEL")
TRIALS = 10 # Default 10
DEPTHS = list(range(2, 11)) # Default 2-10
OUTPUT_DIR = "results" # Default results directory
REASONING_EFFORT = None # None, "low", "medium", "high"
RESUME_FILE = None # Default None
RETRIES = 20 # Default 3
RETRY_DELAY = 1 # Default 1
MODEL_ALIAS = "gemini-2.5-flash-preview-04-17-no-thinking" # Default None alias for logs and pricing
# LITELLM_PARAMS = None # Default None
# LITELLM_PARAMS = {"thinking": {"type": "enabled", "budget_tokens": 1024}}
LITELLM_PARAMS = {"thinking": { "type":"enabled", "budget_tokens": 0 }} # By default thinking is enabled for Google models supporting it

def main():
    # Parse litellm_params from global var
    litellm_params = None
    if LITELLM_PARAMS:
        if isinstance(LITELLM_PARAMS, str):
            try:
                litellm_params = json.loads(LITELLM_PARAMS)
            except json.JSONDecodeError:
                raise ValueError("DEFAULT_LITELLM_PARAMS must be a valid JSON string")
        else:
            litellm_params = LITELLM_PARAMS

    if not MODEL:
        raise ValueError("the following arguments are required: --model (or set MODEL in .env)")

    run(
        model=MODEL,
        trials_per_cell=TRIALS,
        depths=DEPTHS,
        output_dir=OUTPUT_DIR,
        reasoning_effort=REASONING_EFFORT,
        resume_file=RESUME_FILE,
        retries=RETRIES,
        retry_delay=RETRY_DELAY,
        model_alias=MODEL_ALIAS,
        litellm_params=litellm_params
    )

if __name__ == "__main__":
    main()
