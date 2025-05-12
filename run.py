import argparse
from llm_arithmetic.runner import run
from dotenv import load_dotenv
import os
import json
load_dotenv()

DEFAULT_MODEL = os.getenv("MODEL")
DEFAULT_TRIALS = 10 # Default 10
DEFAULT_DEPTHS = list(range(2, 11)) # Default 2-10
DEFAULT_OUTPUT_DIR = "results" # Default results directory
DEFAULT_REASONING_EFFORT = None # None, "low", "medium", "high"
DEFAULT_RESUME_FILE = None # Default None
DEFAULT_RETRIES = 3 # Default 3
DEFAULT_RETRY_DELAY = 1 # Default 1
DEFAULT_MODEL_ALIAS = None # Default None alias for logs and pricing
DEFAULT_LITELLM_PARAMS = None # Default None
# DEFAULT_LITELLM_PARAMS = {"thinking": {"type": "enabled", "budget_tokens": 1024}}
# DEFAULT_LITELLM_PARAMS = {"thinking": {"type": "disabled"}} # By default thinking is enabled for Google models supporting it

def main():
    # Parse litellm_params from global var
    litellm_params = None
    if DEFAULT_LITELLM_PARAMS:
        if isinstance(DEFAULT_LITELLM_PARAMS, str):
            try:
                litellm_params = json.loads(DEFAULT_LITELLM_PARAMS)
            except json.JSONDecodeError:
                raise ValueError("DEFAULT_LITELLM_PARAMS must be a valid JSON string")
        else:
            litellm_params = DEFAULT_LITELLM_PARAMS

    if not DEFAULT_MODEL:
        raise ValueError("the following arguments are required: --model (or set MODEL in .env)")

    run(
        model=DEFAULT_MODEL,
        trials_per_cell=DEFAULT_TRIALS,
        depths=DEFAULT_DEPTHS,
        output_dir=DEFAULT_OUTPUT_DIR,
        reasoning_effort=DEFAULT_REASONING_EFFORT,
        resume_file=DEFAULT_RESUME_FILE,
        retries=DEFAULT_RETRIES,
        retry_delay=DEFAULT_RETRY_DELAY,
        model_alias=DEFAULT_MODEL_ALIAS,
        litellm_params=litellm_params
    )

if __name__ == "__main__":
    main()
