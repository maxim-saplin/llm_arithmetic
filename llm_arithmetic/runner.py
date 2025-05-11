import os
from datetime import datetime
def run(model: str, trials_per_cell: int, depths, output_dir: str):
    """
    Execute the evaluation for the specified model, number of trials per cell, and digit depths.

    Writes per-trial JSONL into output_dir and updates aggregate.jsonl in project root.
    """
    # Delayed imports to avoid circular issues or expensive LLM import
    from decimal import Decimal
    from litellm import completion
    from llm_arithmetic import gen, prompt, parse, types, io as io_

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Prepare file paths and stats container
    date = datetime.utcnow().strftime("%Y-%m-%d")
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
                "completion_tokens_sum": 0
            }

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
                    timestamp=timestamp
                )
                io_.write_trial(trial, trial_file)
                # Update stats
                cell['total_trials'] += 1
                if classification == 'Correct':
                    cell['correct_count'] += 1
                elif classification == 'NaN':
                    cell['nan_count'] += 1
                else:
                    cell['deviate_count'] += 1
                    # error is string; convert to Decimal
                    cell['error_sum'] += Decimal(error)
                cell['prompt_tokens_sum'] += prompt_tokens
                cell['completion_tokens_sum'] += completion_tokens

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
                'avg_completion_tokens': avg_completion
            }

    # Write aggregate to root-level aggregate.jsonl
    aggregate = types.Aggregate(
        model=model,
        date=date,
        trials_per_cell=trials_per_cell,
        cells=formatted_cells
    )
    agg_file = "aggregate.jsonl"
    io_.write_aggregate(aggregate, agg_file) 