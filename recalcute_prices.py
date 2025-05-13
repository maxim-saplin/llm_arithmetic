import argparse
import csv
import json

from llm_arithmetic.types import VARIANTS

METADATA_FILE = "models_metadata.csv"
TRIAL_FILE = "results/claude-3-7-sonnet-20250219_2025-05-11_19-06.jsonl"
AGGREGATE_FILE = "aggregate.jsonl"

def load_metadata(metadata_file):
    """Load model pricing metadata from CSV and return dict of model->(prompt_rate, completion_rate)."""
    model_prices = {}
    try:
        with open(metadata_file, newline='') as mf:
            reader = csv.DictReader(mf)
            for row in reader:
                model = row.get('model')
                try:
                    p = float(row.get('1m_prompt', 0.0))
                except:
                    p = 0.0
                try:
                    c = float(row.get('1m_completion', 0.0))
                except:
                    c = 0.0
                if model:
                    model_prices[model] = (p, c)
    except FileNotFoundError:
        print(f"Metadata file not found: {metadata_file}")
    return model_prices


def load_trials(trial_file):
    """Read trial records from JSONL file."""
    trials = []
    with open(trial_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            trials.append(json.loads(line))
    return trials


def save_trials(trial_file, trials):
    """Overwrite trial JSONL with updated cost values."""
    with open(trial_file, 'w') as f:
        for rec in trials:
            f.write(json.dumps(rec, default=str) + "\n")


def update_aggregate(aggregate_file, trials, model_prices):
    """Update the aggregate JSONL file with recalculated cost summaries."""
    # Load all aggregate records
    agg_recs = []
    with open(aggregate_file) as f:
        for line in f:
            if not line.strip():
                continue
            agg_recs.append(json.loads(line))

    # Compute global total cost
    total_cost = sum(rec.get('cost', 0.0) for rec in trials)
    # Group trials by variant/depth
    by_cell = {}
    by_variant = {}
    for variant in VARIANTS:
        by_cell[variant] = {}
        by_variant[variant] = []
    for rec in trials:
        variant = rec['variant']
        depth = rec['depth']
        key = f"depth_{depth}"
        by_cell.setdefault(variant, {}).setdefault(key, []).append(rec)
        by_variant.setdefault(variant, []).append(rec)

    # Update matching aggregate record(s)
    updated_recs = []
    n_trials = len(trials)
    for agg in agg_recs:
        # match by model and total_trials
        overall = agg.get('overall', {})
        if agg.get('model') and overall.get('total_trials') == n_trials:
            # update cells
            cells = agg.get('cells', {})
            for variant, depths in cells.items():
                for depth_key, stats in depths.items():
                    recs = by_cell.get(variant, {}).get(depth_key, [])
                    total = len(recs)
                    cost_sum = sum(r.get('cost', 0.0) for r in recs)
                    avg_cost = cost_sum / total if total > 0 else 0.0
                    stats['total_cost'] = cost_sum
                    stats['avg_cost'] = avg_cost
            # update overall total_cost
            agg['overall']['total_cost'] = total_cost
            # update per_category
            per_cat = agg.get('per_category', {})
            for variant, stats in per_cat.items():
                recs = by_variant.get(variant, [])
                stats['total_cost'] = sum(r.get('cost', 0.0) for r in recs)
        updated_recs.append(agg)

    # Write back aggregate file
    with open(aggregate_file, 'w') as f:
        for rec in updated_recs:
            f.write(json.dumps(rec, default=str) + "\n")


def main():
    # Use only globals, no argparse or args

    # If still None, error
    if TRIAL_FILE is None:
        print("Error: TRIAL_FILE must be specified.")
        return
    if AGGREGATE_FILE is None:
        print("Error: AGGREGATE_FILE must be specified.")
        return

    # Load metadata and trials
    price_dict = load_metadata(METADATA_FILE)
    trial_records = load_trials(TRIAL_FILE)
    if not trial_records:
        print(f"No trials found in {TRIAL_FILE}")
        return

    # Recalculate cost for each trial
    for record in trial_records:
        model_name = record.get('model')
        prompt_tok = record.get('tokens', {}).get('prompt_tokens', 0)
        completion_tok = record.get('tokens', {}).get('completion_tokens', 0)
        prompt_rate, completion_rate = price_dict.get(model_name, (0.0, 0.0))
        calculated_cost = (prompt_tok / 1_000_000) * prompt_rate + (completion_tok / 1_000_000) * completion_rate
        record['cost'] = calculated_cost

    # Save updated trials file
    save_trials(TRIAL_FILE, trial_records)

    # Update aggregate summary
    update_aggregate(AGGREGATE_FILE, trial_records, price_dict)
    print(f"Recalculated prices in {TRIAL_FILE} and updated {AGGREGATE_FILE}")

if __name__ == '__main__':
    main() 