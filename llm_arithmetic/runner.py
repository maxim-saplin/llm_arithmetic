import os
from datetime import datetime
import csv

def run(model: str, trials_per_cell: int, depths, output_dir: str):
    """
    Execute the evaluation for the specified model, number of trials per cell, and digit depths.

    Writes per-trial JSONL into output_dir and updates aggregate.jsonl in project root.
    """
    # Delayed imports to avoid circular issues or expensive LLM import
    from decimal import Decimal
    from litellm import completion
    from llm_arithmetic import gen, prompt, parse, types, io as io_
    from tqdm import tqdm

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load pricing metadata
    metadata_file = os.path.join(os.getcwd(), "models_metadata.csv")
    model_prices = {}
    try:
        with open(metadata_file) as mf:
            reader = csv.DictReader(mf)
            for row in reader:
                m = row['model']
                try:
                    p_prompt = float(row['1m_prompt'])
                except:
                    p_prompt = 0.0
                try:
                    p_completion = float(row['1m_completion'])
                except:
                    p_completion = 0.0
                model_prices[m] = (p_prompt, p_completion)
    except FileNotFoundError:
        model_prices = {}
    # Pricing for this model
    prompt_price_per_m, completion_price_per_m = model_prices.get(model, (0.0, 0.0))

    # Prepare file paths and stats container
    date = datetime.utcnow().strftime("%Y-%m-%d_%H-%M")
    sanitized_model = model.replace("/", "_")
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

    # Setup progress bar
    total_tasks = len(types.VARIANTS) * len(depths) * trials_per_cell
    # Initialize accumulated token and cost counters
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_cost = 0.0
    pbar = tqdm(total=total_tasks, desc=f"Model: {model}", unit="trial")

    # Run trials
    for variant in types.VARIANTS:
        typ, op = variant.split("_")
        for depth in depths:
            cell = stats[variant][f"depth_{depth}"]
            for _ in range(trials_per_cell):
                # Generate operands
                if typ == "int":
                    lhs, rhs = gen.gen_int_pair(variant, depth)
                else:
                    lhs, rhs = gen.gen_float_pair(variant, depth)
                # Compute correct answer
                correct = gen.compute_correct(variant, lhs, rhs)
                # Build prompt
                op_symbol = prompt.OP_SYMBOLS[op]
                ptext = prompt.make_prompt(lhs, op_symbol, rhs)
                # Call model
                response = completion(
                    model=model,
                    messages=[{"role": "user", "content": ptext}]
                )
                # Extract response details
                usage = getattr(response, 'usage', {})
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)
                # Compute cost for this trial
                cost = (prompt_tokens / 1_000_000) * prompt_price_per_m + (completion_tokens / 1_000_000) * completion_price_per_m
                # Extract model output
                raw = None
                try:
                    raw = response.choices[0].message.content.strip()
                except Exception:
                    raw = ''
                # Parse and classify
                parsed, classification, error = parse.parse_response(raw, correct, variant)
                # Timestamp
                timestamp = datetime.utcnow().isoformat() + "Z"
                # Build trial record and write
                trial = types.Trial(
                    model=model,
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
                    timestamp=timestamp
                )
                io_.write_trial(trial, trial_file)
                # Update stats
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
                    # error is string; convert to Decimal
                    cell['error_sum'] += Decimal(error)
                    global_error_sum += Decimal(error)
                cell['prompt_tokens_sum'] += prompt_tokens
                cell['completion_tokens_sum'] += completion_tokens
                # Update stats cost sum
                cell['cost_sum'] += cost
                # Update accumulated token and cost counters and display
                total_prompt_tokens += prompt_tokens
                total_completion_tokens += completion_tokens
                total_cost += cost
                pbar.set_postfix({
                    'prompt_tokens': total_prompt_tokens,
                    'completion_tokens': total_completion_tokens,
                    'total_tokens': total_prompt_tokens + total_completion_tokens,
                    'cost': total_cost
                })
                pbar.update(1)

    pbar.close()

    # Compute aggregated metrics
    formatted_cells = {}
    for variant in types.VARIANTS:
        formatted_cells[variant] = {}
        for depth in depths:
            key = f"depth_{depth}"
            cell = stats[variant][key]
            # Compute averages
            total = cell['total_trials']
            dev_count = cell['deviate_count']
            avg_error = (cell['error_sum'] / dev_count) if dev_count > 0 else Decimal("0.00")
            avg_prompt = cell['prompt_tokens_sum'] / total if total > 0 else 0
            avg_completion = cell['completion_tokens_sum'] / total if total > 0 else 0
            formatted_cells[variant][key] = {
                'total_trials': total,
                'correct_count': cell['correct_count'],
                'nan_count': cell['nan_count'],
                'deviate_count': dev_count,
                'avg_error': str(avg_error.quantize(Decimal("0.00"))),
                'avg_prompt_tokens': avg_prompt,
                'avg_completion_tokens': avg_completion,
                'total_cost': cell['cost_sum'],
                'avg_cost': (cell['cost_sum'] / total) if total > 0 else 0.0
            }

    # Compute model-level overall summary
    overall = {
        'total_prompt_tokens': total_prompt_tokens,
        'total_completion_tokens': total_completion_tokens,
        'total_cost': total_cost,
        'correct_count': global_correct,
        'nan_count': global_nan,
        'deviate_count': global_deviate,
        'avg_error': str((global_error_sum / global_deviate).quantize(Decimal("0.00"))) if global_deviate > 0 else "0.00"
    }
    # Compute per-category (variant) aggregates across depths
    per_category = {}
    for variant in types.VARIANTS:
        var_stats = stats[variant]
        # sums across depths
        prompt_sum = sum(var_stats[f"depth_{d}"]['prompt_tokens_sum'] for d in depths)
        completion_sum = sum(var_stats[f"depth_{d}"]['completion_tokens_sum'] for d in depths)
        cost_sum = sum(var_stats[f"depth_{d}"]['cost_sum'] for d in depths)
        correct_sum = sum(var_stats[f"depth_{d}"]['correct_count'] for d in depths)
        nan_sum = sum(var_stats[f"depth_{d}"]['nan_count'] for d in depths)
        dev_sum = sum(var_stats[f"depth_{d}"]['deviate_count'] for d in depths)
        error_sum = sum(var_stats[f"depth_{d}"]['error_sum'] for d in depths)
        per_category[variant] = {
            'total_prompt_tokens': prompt_sum,
            'total_completion_tokens': completion_sum,
            'total_cost': cost_sum,
            'correct_count': correct_sum,
            'nan_count': nan_sum,
            'deviate_count': dev_sum,
            'avg_error': str((error_sum / dev_sum).quantize(Decimal("0.00"))) if dev_sum > 0 else "0.00"
        }
    # Build aggregate record and append to a single aggregate.jsonl at project root
    aggregate = types.Aggregate(
        model=model,
        date=date,
        trials_per_cell=trials_per_cell,
        cells=formatted_cells,
        overall=overall,
        per_category=per_category
    )
    # Always append to one aggregate file
    agg_file = os.path.join(os.getcwd(), "aggregate.jsonl")
    io_.write_aggregate(aggregate, agg_file) 