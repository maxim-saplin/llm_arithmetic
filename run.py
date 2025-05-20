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
RESUME_FILE = None #"results/azure_o4-mini-2025-04-16_2025-05-17_07-47.jsonl" # Default None
EXTRA_CONTEXT = 0 # Default 0: number of k tokens of dialog to include as extra context, files in data/dialog_{EXTRA_CONTEXT}k.json
RETRIES = 3 # Default 3
RETRY_DELAY = 5 # Default 5
MODEL_ALIAS = None # Default None alias for logs and pricing
LITELLM_PARAMS = None # Default None
# LITELLM_PARAMS = {"thinking": {"type": "enabled", "budget_tokens": 1024}}
# LITELLM_PARAMS = {"thinking": { "type":"enabled", "budget_tokens": 0 }} # By default thinking is enabled for Google models supporting it

def main():
    
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

    print_params()

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
        litellm_params=litellm_params,
        extra_context=EXTRA_CONTEXT
    )

def print_params():
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text

    console = Console()

    # Define default values for comparison
    defaults = {
        "MODEL": None,
        "TRIALS": 10,
        "DEPTHS": list(range(2, 11)),
        "OUTPUT_DIR": "results",
        "REASONING_EFFORT": None,
        "RESUME_FILE": None,
        "EXTRA_CONTEXT": 0,
        "RETRIES": 3,
        "RETRY_DELAY": 5,
        "MODEL_ALIAS": None,
        "LITELLM_PARAMS": None,
    }

    # Gather current settings
    current_settings = {
        "MODEL": MODEL,
        "TRIALS": TRIALS,
        "DEPTHS": DEPTHS,
        "OUTPUT_DIR": OUTPUT_DIR,
        "REASONING_EFFORT": REASONING_EFFORT,
        "RESUME_FILE": RESUME_FILE,
        "EXTRA_CONTEXT": EXTRA_CONTEXT,
        "RETRIES": RETRIES,
        "RETRY_DELAY": RETRY_DELAY,
        "MODEL_ALIAS": MODEL_ALIAS,
        "LITELLM_PARAMS": LITELLM_PARAMS,
    }

    # Prepare table
    table = Table(title="Run Parameters", show_header=True, header_style="bold magenta")
    table.add_column("Parameter", style="bold")
    table.add_column("Value", style="")

    for key, val in current_settings.items():
        default_val = defaults[key]
        # For lists, compare as lists
        is_default = (val == default_val)
        # Special handling for MODEL, which is required
        if key == "MODEL" and val is not None:
            is_default = False  # Always highlight MODEL
        # Format value for display
        if isinstance(val, list):
            val_str = str(val)
        elif val is None:
            val_str = "None"
        else:
            val_str = str(val)
        # Highlight if not default
        if not is_default:
            value_text = Text(val_str, style="bold yellow")
        else:
            value_text = Text(val_str, style="dim")
        table.add_row(key, value_text)

    console.print(table)

if __name__ == "__main__":
    main()
