from llm_arithmetic.runner import run
from dotenv import load_dotenv
import argparse
import os
import json

load_dotenv()

# Edit these defaults when not passing CLI flags.
DEFAULTS = {
    "trials": 10,
    "depths": "2-10",  # parsed to list(range(2, 11))
    "output_dir": "results",
    "reasoning_effort": None,
    "resume_file": None,
    "extra_context": 0,
    "retries": 3,
    "retry_delay": 5.0,
    "model_alias": None,
    "litellm_params": None,
    "system_prompt": None,
}
# LITELLM_PARAMS examples:
# {"thinking": {"type": "enabled", "budget_tokens": 1024}}
# {"thinking": {"type": "enabled", "budget_tokens": 0}}


def parse_depths(s: str) -> list[int]:
    """Parse depths: '2-10' (inclusive range) or '2,5,8' (explicit list)."""
    s = s.strip()
    if "-" in s and "," not in s:
        start, end = s.split("-", 1)
        return list(range(int(start), int(end) + 1))
    return [int(x.strip()) for x in s.split(",")]


def parse_litellm_params(value):
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise ValueError("--litellm-params must be a valid JSON string")
    return value


def parse_args():
    p = argparse.ArgumentParser(description="Run LLM arithmetic evaluation suite")
    p.add_argument(
        "--model",
        default=os.getenv("MODEL"),
        help="Model id (or set MODEL in .env)",
    )
    p.add_argument("--trials", type=int, default=DEFAULTS["trials"], help="Trials per cell")
    p.add_argument(
        "--depths",
        default=DEFAULTS["depths"],
        help="Digit depths: inclusive range (e.g. 2-10) or comma list (e.g. 2,5,8)",
    )
    p.add_argument("--output-dir", default=DEFAULTS["output_dir"], help="Results directory")
    p.add_argument(
        "--reasoning-effort",
        choices=["low", "medium", "high"],
        default=DEFAULTS["reasoning_effort"],
        help="Reasoning effort level",
    )
    p.add_argument("--resume-file", default=DEFAULTS["resume_file"], help="JSONL file to resume")
    p.add_argument(
        "--extra-context",
        type=int,
        default=DEFAULTS["extra_context"],
        help="k tokens of dialog from data/dialog_{k}k.json",
    )
    p.add_argument("--retries", type=int, default=DEFAULTS["retries"], help="API retries")
    p.add_argument("--retry-delay", type=float, default=DEFAULTS["retry_delay"], help="Retry delay (seconds)")
    p.add_argument("--model-alias", default=DEFAULTS["model_alias"], help="Display/pricing alias")
    p.add_argument(
        "--litellm-params",
        default=DEFAULTS["litellm_params"],
        help="JSON object passed to litellm.completion",
    )
    p.add_argument(
        "--system-prompt",
        default=DEFAULTS["system_prompt"],
        help='System prompt (e.g. "/no_think" for Qwen 3)',
    )
    return p.parse_args()


def build_settings(args) -> dict:
    return {
        "MODEL": args.model,
        "TRIALS": args.trials,
        "DEPTHS": parse_depths(args.depths),
        "OUTPUT_DIR": args.output_dir,
        "REASONING_EFFORT": args.reasoning_effort,
        "RESUME_FILE": args.resume_file,
        "EXTRA_CONTEXT": args.extra_context,
        "RETRIES": args.retries,
        "RETRY_DELAY": args.retry_delay,
        "MODEL_ALIAS": args.model_alias,
        "LITELLM_PARAMS": args.litellm_params,
        "SYSTEM_PROMPT": args.system_prompt,
    }


def default_settings() -> dict:
    return {
        "MODEL": None,
        "TRIALS": DEFAULTS["trials"],
        "DEPTHS": parse_depths(DEFAULTS["depths"]),
        "OUTPUT_DIR": DEFAULTS["output_dir"],
        "REASONING_EFFORT": DEFAULTS["reasoning_effort"],
        "RESUME_FILE": DEFAULTS["resume_file"],
        "EXTRA_CONTEXT": DEFAULTS["extra_context"],
        "RETRIES": DEFAULTS["retries"],
        "RETRY_DELAY": DEFAULTS["retry_delay"],
        "MODEL_ALIAS": DEFAULTS["model_alias"],
        "LITELLM_PARAMS": DEFAULTS["litellm_params"],
        "SYSTEM_PROMPT": DEFAULTS["system_prompt"],
    }


def main():
    args = parse_args()
    settings = build_settings(args)

    if not settings["MODEL"]:
        raise ValueError("the following arguments are required: --model (or set MODEL in .env)")

    litellm_params = parse_litellm_params(settings["LITELLM_PARAMS"])

    print_params(settings)

    run(
        model=settings["MODEL"],
        trials_per_cell=settings["TRIALS"],
        depths=settings["DEPTHS"],
        output_dir=settings["OUTPUT_DIR"],
        reasoning_effort=settings["REASONING_EFFORT"],
        resume_file=settings["RESUME_FILE"],
        retries=settings["RETRIES"],
        retry_delay=settings["RETRY_DELAY"],
        model_alias=settings["MODEL_ALIAS"],
        litellm_params=litellm_params,
        extra_context=settings["EXTRA_CONTEXT"],
        system_prompt=settings["SYSTEM_PROMPT"],
    )


def print_params(settings: dict):
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text

    console = Console()
    defaults = default_settings()

    table = Table(title="Run Parameters", show_header=True, header_style="bold magenta")
    table.add_column("Parameter", style="bold")
    table.add_column("Value", style="")

    for key, val in settings.items():
        default_val = defaults[key]
        is_default = val == default_val
        if key == "MODEL" and val is not None:
            is_default = False
        if isinstance(val, list):
            val_str = str(val)
        elif val is None:
            val_str = "None"
        else:
            val_str = str(val)
        if not is_default:
            value_text = Text(val_str, style="bold yellow")
        else:
            value_text = Text(val_str, style="dim")
        table.add_row(key, value_text)

    console.print(table)


if __name__ == "__main__":
    main()
