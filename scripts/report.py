#!/usr/bin/env python3
import json
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from enum import Enum

class SortBy(Enum):
    MODEL = 'model'
    CORRECT = 'accuracy'
    NAN = 'nan_rate'
    DEV = 'deviate_rate'

# Sort field for the overview table: MODEL sorts ascending; metrics sort descending
SORT_BY = SortBy.MODEL

# Configuration parameters - set these globals at the top instead of using CLI arguments
MODEL = None  # Model name to filter (string) or None for last record
RESULTS_DIR = os.path.join(os.getcwd(), "results")
MIN_DEPTH = 5  # Minimum digit depth to include in report (integer) or None to include all

def load_results():
    """
    Load raw trial records from JSONL files in the results directory and aggregate by model run.
    """
    recs = []
    for fname in sorted(os.listdir(RESULTS_DIR)):
        if not fname.endswith('.jsonl'):
            continue
        fpath = os.path.join(RESULTS_DIR, fname)
        trials = []
        try:
            with open(fpath) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        trials.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            continue
        if not trials:
            continue
        # Group trials by variant and depth
        cells = {}
        for tr in trials:
            variant = tr.get('variant')
            depth = tr.get('depth')
            key = f'depth_{depth}'
            cells.setdefault(variant, {}).setdefault(key, []).append(tr)
        # Compute stats per cell
        cells_stats = {}
        for variant, depth_dict in cells.items():
            cells_stats[variant] = {}
            for depth_key, tlist in depth_dict.items():
                t = len(tlist)
                correct = sum(1 for tr in tlist if tr.get('classification') == 'Correct')
                nan_ct = sum(1 for tr in tlist if tr.get('classification') == 'NaN')
                dev_ct = sum(1 for tr in tlist if tr.get('classification') == 'Deviate')
                error_sum = sum(float(tr.get('error') or 0) for tr in tlist if tr.get('classification') == 'Deviate')
                avg_error = error_sum / dev_ct if dev_ct > 0 else 0.0
                sum_prompt = sum(tr.get('tokens', {}).get('prompt_tokens', 0) for tr in tlist)
                sum_completion = sum(tr.get('tokens', {}).get('completion_tokens', 0) for tr in tlist)
                avg_prompt = sum_prompt / t if t > 0 else 0.0
                avg_completion = sum_completion / t if t > 0 else 0.0
                total_cost = sum(tr.get('cost') or 0 for tr in tlist)
                cells_stats[variant][depth_key] = {
                    'total_trials': t,
                    'correct_count': correct,
                    'nan_count': nan_ct,
                    'deviate_count': dev_ct,
                    'accuracy': correct / t if t > 0 else 0.0,
                    'nan_rate': nan_ct / t if t > 0 else 0.0,
                    'deviate_rate': dev_ct / t if t > 0 else 0.0,
                    'avg_error': f"{avg_error:.2f}",
                    'avg_prompt_tokens': avg_prompt,
                    'avg_completion_tokens': avg_completion,
                    'total_cost': total_cost
                }
        # Include raw trial count to identify incomplete runs
        recs.append({
            'model': trials[0].get('model', ''),
            'date': os.path.splitext(fname)[0],
            'cells': cells_stats,
            'raw_trial_count': len(trials)
        })
    return recs

def filter_record_by_depth(record, min_depth):
    """
    Return (overall, per_category) metrics for the record filtered by min_depth.
    """
    cells = record.get('cells', {})
    total_trials = total_correct = total_nan = total_dev = 0
    total_error_sum = 0.0
    total_prompt_tokens = total_completion_tokens = total_cost = 0.0
    new_per_cat = {}
    for variant, depth_dict in cells.items():
        var_total_trials = var_correct = var_nan = var_dev = 0
        var_error_sum = var_prompt_tokens = var_completion_tokens = var_cost = 0.0
        for key, stats in depth_dict.items():
            try:
                depth = int(key.split('_')[1])
            except Exception as _:
                continue
            if depth < min_depth:
                continue
            t = stats.get('total_trials', 0)
            c = stats.get('correct_count', 0)
            n = stats.get('nan_count', 0)
            d = stats.get('deviate_count', 0)
            avg_error = float(stats.get('avg_error', "0"))
            error_sum = d * avg_error
            var_total_trials += t
            var_correct += c
            var_nan += n
            var_dev += d
            var_error_sum += error_sum
            var_prompt_tokens += stats.get('avg_prompt_tokens', 0.0) * t
            var_completion_tokens += stats.get('avg_completion_tokens', 0.0) * t
            var_cost += stats.get('total_cost', 0.0)
        if var_total_trials > 0:
            per_accuracy = var_correct / var_total_trials
            per_nan_rate = var_nan / var_total_trials
            per_dev_rate = var_dev / var_total_trials
            per_avg_error = var_error_sum / var_dev if var_dev > 0 else 0.0
            new_per_cat[variant] = {
                'total_trials': var_total_trials,
                'correct_count': var_correct,
                'nan_count': var_nan,
                'deviate_count': var_dev,
                'accuracy': per_accuracy,
                'nan_rate': per_nan_rate,
                'deviate_rate': per_dev_rate,
                'avg_error': f"{per_avg_error:.2f}",
                'total_cost': var_cost
            }
            total_trials += var_total_trials
            total_correct += var_correct
            total_nan += var_nan
            total_dev += var_dev
            total_error_sum += var_error_sum
            total_prompt_tokens += var_prompt_tokens
            total_completion_tokens += var_completion_tokens
            total_cost += var_cost
    overall_accuracy = total_correct / total_trials if total_trials > 0 else 0.0
    overall_nan_rate = total_nan / total_trials if total_trials > 0 else 0.0
    overall_dev_rate = total_dev / total_trials if total_trials > 0 else 0.0
    overall_avg_error = total_error_sum / total_dev if total_dev > 0 else 0.0
    new_overall = {
        'total_trials': total_trials,
        'accuracy': overall_accuracy,
        'nan_rate': overall_nan_rate,
        'deviate_rate': overall_dev_rate,
        'total_prompt_tokens': total_prompt_tokens,
        'total_completion_tokens': total_completion_tokens,
        'total_cost': total_cost,
        'avg_error': f"{overall_avg_error:.2f}"
    }
    return new_overall, new_per_cat

def main():
    recs = load_results()
    if not recs:
        print(f"No records found in {RESULTS_DIR}")
        return
    console = Console()
    # If a model is specified, show detailed report for that model
    if MODEL:
        filtered = [r for r in recs if r.get('model') == MODEL]
        if not filtered:
            print(f"No records for model {MODEL}")
            return
        record = filtered[-1]
    # If no model and multiple records, show overview table
    elif len(recs) > 1:
        # Move incomplete runs to bottom; otherwise sort by accuracy descending
        expected_trials = max(r.get('raw_trial_count', 0) for r in recs)
        def _sort_key(rec):
            overall_vals, _ = (filter_record_by_depth(rec, MIN_DEPTH)
                               if MIN_DEPTH is not None else (rec.get('overall', {}), {}))
            acc = overall_vals.get('accuracy', 0.0)
            incomplete = rec.get('raw_trial_count', 0) < expected_trials
            return (incomplete, -acc)
        sorted_recs = sorted(recs, key=_sort_key)
        table = Table(title="Models Overview")
        table.add_column("Model", style="cyan")
        table.add_column("Date", style="magenta")
        table.add_column("Trials", justify="right")
        table.add_column("Correct %", justify="right")
        table.add_column("NaN %", justify="right")
        table.add_column("Dev %", justify="right")
        table.add_column("Comp. Tok.", justify="right")
        table.add_column("Cost", justify="right")
        table.add_column("Avg Error", justify="right")
        # Populate rows for each model (sorted)
        for r in sorted_recs:
            if MIN_DEPTH is not None:
                o, _ = filter_record_by_depth(r, MIN_DEPTH)
            else:
                o = r.get('overall', {})
            table.add_row(
                r.get('model', ''),
                r.get('date', ''),
                str(o.get('total_trials', '')),
                f"{o.get('accuracy',0)*100:.2f}%",
                f"{o.get('nan_rate',0)*100:.2f}%",
                f"{o.get('deviate_rate',0)*100:.2f}%",
                f"{o.get('total_completion_tokens',0):.2f}",
                f"${o.get('total_cost',0):.6f}",
                o.get('avg_error', '')
            )
        console.print(table)
        # Verification table: count per‐variant trials and check consistency
        verif_table = Table(title="Verification")
        verif_table.add_column("File", style="cyan")
        verif_table.add_column("Model", style="cyan")
        # gather all variants across all runs
        categories = sorted({v for rec in recs for v in rec.get('cells', {})})
        for cat in categories:
            verif_table.add_column(cat, justify="right")
        verif_table.add_column("Verification", justify="center")
        # one row per run
        for rec in sorted_recs:
            file = rec.get('date', '')
            model = rec.get('model', '')
            cells = rec.get('cells', {})
            # total trials per category
            counts = [
                str(sum(stats.get('total_trials', 0)
                        for stats in cells.get(cat, {}).values()))
                for cat in categories
            ]
            # valid if all counts equal
            verification = "Valid" if len(set(counts)) == 1 else "Invalid"
            verif_table.add_row(file, model, *counts, verification)
        console.print(verif_table)
        # Detailed per-model cards (sorted)
        for record in sorted_recs:
            if MIN_DEPTH is not None:
                overall, per_cat = filter_record_by_depth(record, MIN_DEPTH)
            else:
                overall = record.get('overall', {})
                per_cat = record.get('per_category', {})
            # Build overall summary panel for each model
            overall_lines = []
            for key in [
                'total_trials', 'accuracy', 'nan_rate', 'deviate_rate',
                'total_prompt_tokens', 'total_completion_tokens',
                'total_cost', 'avg_error'
            ]:
                if key not in overall:
                    continue
                val = overall[key]
                if key in ('accuracy', 'nan_rate', 'deviate_rate'):
                    val_str = f"{val*100:.2f}%"
                elif 'cost' in key:
                    val_str = f"${val:.6f}"
                else:
                    val_str = str(val)
                overall_lines.append(f"[bold]{key.replace('_', ' ').title()}: [/bold]{val_str}")
            panel = Panel("\n".join(overall_lines), title=f"Overall ({record.get('model')} @ {record.get('date')})")
            console.print(panel)
            # Per-variant table for each model
            if per_cat:
                detail_table = Table(title=f"Per-Variant Summary ({record.get('model')})")
                detail_table.add_column("Variant", style="cyan", no_wrap=True)
                detail_table.add_column("Trials", justify="right")
                detail_table.add_column("Correct %", justify="right")
                detail_table.add_column("NaN %", justify="right")
                detail_table.add_column("Dev %", justify="right")
                detail_table.add_column("Avg Error", justify="right")
                detail_table.add_column("Cost", justify="right")
                for variant, stats in per_cat.items():
                    detail_table.add_row(
                        variant,
                        str(stats.get('total_trials', '')),
                        f"{stats.get('accuracy',0)*100:.2f}%",
                        f"{stats.get('nan_rate',0)*100:.2f}%",
                        f"{stats.get('deviate_rate',0)*100:.2f}%",
                        stats.get('avg_error',''),
                        f"${stats.get('total_cost',0):.6f}"
                    )
                console.print(detail_table)
        return
    else:
        record = recs[-1]

    # Apply depth filtering if requested
    if MIN_DEPTH is not None:
        overall, per_cat = filter_record_by_depth(record, MIN_DEPTH)
    else:
        overall = record.get('overall', {})
        per_cat = record.get('per_category', {})

    # Build overall summary panel
    overall_lines = []
    for key in [
        'total_trials', 'accuracy', 'nan_rate', 'deviate_rate',
        'total_prompt_tokens', 'total_completion_tokens',
        'total_cost', 'avg_error'
    ]:
        if key not in overall:
            continue
        val = overall[key]
        if key in ('accuracy', 'nan_rate', 'deviate_rate'):
            val_str = f"{val*100:.2f}%"
        elif 'cost' in key:
            val_str = f"${val:.6f}"
        else:
            val_str = str(val)
        overall_lines.append(f"[bold]{key.replace('_', ' ').title()}: [/bold]{val_str}")
    panel = Panel("\n".join(overall_lines), title=f"Overall ({record.get('model')} @ {record.get('date')})")
    console.print(panel)

    # Build per-category table (filtered if min-depth is set)
    if per_cat:
        table = Table(title="Per-Variant Summary")
        table.add_column("Variant", style="cyan", no_wrap=True)
        table.add_column("Trials", justify="right")
        table.add_column("Correct %", justify="right")
        table.add_column("NaN %", justify="right")
        table.add_column("Dev %", justify="right")
        table.add_column("Avg Error", justify="right")
        table.add_column("Cost", justify="right")
        for variant, stats in per_cat.items():
            table.add_row(
                variant,
                str(stats.get('total_trials', '')),  
                f"{stats.get('accuracy',0)*100:.2f}%",
                f"{stats.get('nan_rate',0)*100:.2f}%",
                f"{stats.get('deviate_rate',0)*100:.2f}%",
                stats.get('avg_error',''),
                f"${stats.get('total_cost',0):.6f}"
            )
        console.print(table)

if __name__ == "__main__":
    main() 