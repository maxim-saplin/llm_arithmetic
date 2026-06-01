import os
import json
from datetime import datetime, timezone
import csv
import time
import re

def run(model: str, trials_per_cell: int, depths, output_dir: str, reasoning_effort: str = None, resume_file: str = None, retries: int = 5, retry_delay: float = 5.0, model_alias: str = None, litellm_params: dict = None, extra_context: int = 0, system_prompt: str = None, timeout_sec: int = 600):
    """
    Execute the evaluation for the specified model, number of trials per cell, and digit depths.
    :param reasoning_effort: optional reasoning effort level ('low', 'medium', 'high')
    :param litellm_params: optional dictionary of parameters to pass directly to litellm.completion

    Writes per-trial JSONL into output_dir
    """
    # Delayed imports to avoid circular issues or expensive LLM import
    from decimal import Decimal
    import litellm
    from litellm import completion
    from llm_arithmetic import gen, prompt, parse, types, io as io_
    from llm_arithmetic.progress import RunProgress

    litellm.set_verbose = False
    if hasattr(litellm, "suppress_debug_info"):
        litellm.suppress_debug_info = True

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load extra context messages if any
    extra_context_messages = []
    if extra_context and extra_context > 0:
        dialog_path = os.path.join(os.getcwd(), "data", f"dialog_{extra_context}k.json")
        try:
            with open(dialog_path) as dc:
                data = json.load(dc)
                extra_context_messages = data.get("messages", [])
        except Exception:
            extra_context_messages = []

    # Load pricing metadata
    metadata_file = os.path.join(os.getcwd(), "data/models_metadata.csv")
    model_prices = {}
    try:
        with open(metadata_file) as mf:
            reader = csv.DictReader(mf)
            for row in reader:
                m = row['model']
                try:
                    p_prompt = float(row['1m_prompt'])
                except Exception as _:
                    p_prompt = 0.0
                try:
                    p_completion = float(row['1m_completion'])
                except Exception as _:
                    p_completion = 0.0
                model_prices[m] = (p_prompt, p_completion)
    except FileNotFoundError:
        model_prices = {}
    # Determine display model for logs and pricing lookup
    display_model = model_alias if model_alias else model
    # Pricing based on alias if provided, else actual model
    if model_alias:
        prompt_price_per_m, completion_price_per_m = model_prices.get(display_model, model_prices.get(model, (0.0, 0.0)))
    else:
        prompt_price_per_m, completion_price_per_m = model_prices.get(model, (0.0, 0.0))

    # Prepare file paths and stats container (resume or new)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
    sanitized_model = model.replace("/", "_")
    if resume_file:
        trial_file = resume_file
    else:
        trial_file = os.path.join(output_dir, f"{sanitized_model}_{date}.jsonl")
    stats = {}

    # Initialize stats for each variant and depth
    for variant in types.VARIANTS:
        stats[variant] = {}
        for depth in depths:
            stats[variant][f"depth_{depth}"] = {
                "total_trials": 0,
                "correct_count": 0,
                "nan_count": 0,
                "deviate_count": 0,
                "error_sum": Decimal("0.00"),
                "prompt_tokens_sum": 0,
                "completion_tokens_sum": 0,
                "cost_sum": 0.0
            }

    # Initialize global model-level stats
    global_correct = 0
    global_nan = 0
    global_deviate = 0
    global_error_sum = Decimal("0.00")
    # Track total retries (attempts-1) and total failed replies
    global_total_retries = 0
    global_failed_replies = 0

    # Setup progress bar
    total_tasks = len(types.VARIANTS) * len(depths) * trials_per_cell
    # Initialize accumulated token and cost counters
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_cost = 0.0
    with RunProgress(total=total_tasks) as progress:
        if resume_file and os.path.exists(trial_file):
            trials = io_.read_trials(trial_file)

            if trials:
                last_trial = trials[-1]
                last_trial_model = last_trial.get('model')
                last_trial_extra_context = last_trial.get('extra_context')

                if last_trial_model != display_model:
                    raise ValueError(
                        f"Resuming with a different model/alias. "
                        f"Resume file model: '{last_trial_model}', Current model/alias: '{display_model}'. "
                        f"Please ensure they match or start a new run."
                    )

                current_extra_context = extra_context if extra_context else 0
                resume_extra_context = last_trial_extra_context if last_trial_extra_context is not None else 0
                if resume_extra_context != current_extra_context:
                    raise ValueError(
                        f"Resuming with a different extra_context. "
                        f"Resume file extra_context: {resume_extra_context}k, Current extra_context: {current_extra_context}k. "
                        f"Please ensure they match or start a new run."
                    )

            for rec in trials:
                v = rec.get('variant')
                d = rec.get('depth')
                key = f"depth_{d}"
                cell = stats[v][key]
                cell['total_trials'] += 1
                cls = rec.get('classification')
                if cls == 'Correct':
                    global_correct += 1
                    cell['correct_count'] += 1
                elif cls == 'NaN':
                    global_nan += 1
                    cell['nan_count'] += 1
                else:
                    global_deviate += 1
                    cell['deviate_count'] += 1
                    err = rec.get('error') or '0'
                    cell['error_sum'] += Decimal(err)
                    global_error_sum += Decimal(err)
                toks = rec.get('tokens', {})
                pt = toks.get('prompt_tokens', 0)
                ct = toks.get('completion_tokens', 0)
                cost_val = rec.get('cost', 0.0)
                cell['prompt_tokens_sum'] += pt
                cell['completion_tokens_sum'] += ct
                cell['cost_sum'] += cost_val
                total_prompt_tokens += pt
                total_completion_tokens += ct
                total_cost += cost_val
            loaded = len(trials)
            progress.advance(loaded)
            progress.log(f"Resuming from {trial_file}: loaded {loaded}/{total_tasks} trials.")
            if loaded >= total_tasks:
                progress.log(f"All {total_tasks} trials already completed; nothing to run.")
                return

        for variant in types.VARIANTS:
            typ, op = variant.split("_")
            for depth in depths:
                cell = stats[variant][f"depth_{depth}"]
                remaining = trials_per_cell - cell['total_trials']
                for _ in range(remaining):
                    if typ == "int":
                        lhs, rhs = gen.gen_int_pair(variant, depth)
                    else:
                        lhs, rhs = gen.gen_float_pair(variant, depth)
                    correct = gen.compute_correct(variant, lhs, rhs)
                    op_symbol = prompt.OP_SYMBOLS[op]
                    ptext = prompt.make_prompt(lhs, op_symbol, rhs)
                    delay = retry_delay
                    for attempt in range(retries):
                        try:
                            messages = []
                            if system_prompt:
                                messages.append({"role": "system", "content": system_prompt})
                            if extra_context_messages:
                                messages.extend(extra_context_messages)
                            messages.append({"role": "user", "content": ptext})
                            completion_kwargs = {
                                "model": model,
                                "messages": messages,
                                "timeout": timeout_sec
                            }
                            if reasoning_effort:
                                completion_kwargs["reasoning_effort"] = reasoning_effort
                            if litellm_params:
                                completion_kwargs.update(litellm_params)
                            response = completion(**completion_kwargs)
                            break
                        except Exception as e:
                            progress.log(
                                f"retry {variant}@{depth} ({attempt + 1}/{retries}): {e}"
                            )
                            if attempt == retries - 1:
                                response = None
                            else:
                                delay *= 2
                                time.sleep(delay)
                            continue
                    failed_to_get_reply = (response is None)
                    retries_used = attempt
                    global_total_retries += retries_used
                    if failed_to_get_reply:
                        global_failed_replies += 1
                    if response is None:
                        prompt_tokens = 0
                        completion_tokens = 0
                        raw = ''
                    else:
                        usage = getattr(response, 'usage', {})
                        prompt_tokens = usage.get('prompt_tokens', 0)
                        completion_tokens = usage.get('completion_tokens', 0)
                        try:
                            raw = response.choices[0].message.content.strip()
                            raw = re.sub(
                                r"<think>.*?</think>",
                                "",
                                raw,
                                flags=re.DOTALL,
                            )
                        except Exception:
                            raw = ''
                    cost = (prompt_tokens / 1_000_000) * prompt_price_per_m + (
                        completion_tokens / 1_000_000
                    ) * completion_price_per_m
                    parsed, classification, error = parse.parse_response(raw, correct, variant)
                    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    attempts_taken = attempt + 1
                    trial = types.Trial(
                        model=display_model,
                        variant=variant,
                        depth=depth,
                        operands=[lhs, rhs],
                        correct=correct,
                        raw_response=raw,
                        parsed=parsed,
                        classification=classification,
                        error=error,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        cost=cost,
                        timestamp=timestamp,
                        attempts=attempts_taken,
                        failed_to_get_reply=failed_to_get_reply,
                        extra_context=extra_context
                    )
                    io_.write_trial(trial, trial_file)
                    cell['total_trials'] += 1
                    if classification == 'Correct':
                        global_correct += 1
                        cell['correct_count'] += 1
                    elif classification == 'NaN':
                        global_nan += 1
                        cell['nan_count'] += 1
                    else:
                        global_deviate += 1
                        cell['deviate_count'] += 1
                        cell['error_sum'] += Decimal(error)
                        global_error_sum += Decimal(error)
                    cell['prompt_tokens_sum'] += prompt_tokens
                    cell['completion_tokens_sum'] += completion_tokens
                    cell['cost_sum'] += cost
                    total_prompt_tokens += prompt_tokens
                    total_completion_tokens += completion_tokens
                    total_cost += cost
                    progress.tick(
                        prompt_tokens=total_prompt_tokens,
                        completion_tokens=total_completion_tokens,
                        cost=total_cost,
                    )