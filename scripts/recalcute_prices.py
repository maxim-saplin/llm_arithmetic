import csv
import json

METADATA_FILE = "data/models_metadata.csv"
TRIAL_FILE = "results/claude-3-7-sonnet-20250219_2025-05-11_19-06.jsonl"

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
                except Exception as _:
                    p = 0.0
                try:
                    c = float(row.get('1m_completion', 0.0))
                except Exception as _:
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

def main():
    # If still None, error
    if TRIAL_FILE is None:
        print("Error: TRIAL_FILE must be specified.")
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

if __name__ == '__main__':
    main() 