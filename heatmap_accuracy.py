#!/usr/bin/env python3

import os
import json
from colorsys import hls_to_rgb
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.style import Style
from enum import Enum

class SortBy(Enum):
    MODEL = 'model'
    ACCURACY = 'accuracy'

# Sorting parameter for rows: MODEL sorts ascending; ACCURACY sorts descending
SORT_BY = SortBy.ACCURACY

# Path to aggregate JSONL file
AGGREGATE_FILE = os.path.join(os.getcwd(), 'aggregate.jsonl')

# Minimum digit depth to include in metrics (None to include all)
MIN_DEPTH = 5

def load_aggregates(path):
    records = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        return []
    return records

def filter_record_by_depth(record, min_depth):
    """
    Filter record cells by min_depth and compute per-category accuracy.
    Returns overall metrics and per_category accuracy dict.
    """
    cells = record.get('cells', {})
    total_trials = total_correct = 0
    total_cost = 0.0
    per_cat = {}
    for variant, depth_dict in cells.items():
        var_trials = var_correct = 0
        var_cost = 0.0
        for key, stats in depth_dict.items():
            try:
                depth = int(key.split('_')[1])
            except (IndexError, ValueError):
                continue
            if min_depth is not None and depth < min_depth:
                continue
            t = stats.get('total_trials', 0)
            c = stats.get('correct_count', 0)
            var_trials += t
            var_correct += c
            var_cost += stats.get('total_cost', 0.0)
        if var_trials > 0:
            acc = var_correct / var_trials
            per_cat[variant] = acc
            total_trials += var_trials
            total_correct += var_correct
            total_cost += var_cost
    overall_acc = total_correct / total_trials if total_trials > 0 else 0.0
    overall = {'accuracy': overall_acc, 'total_trials': total_trials, 'total_cost': total_cost}
    return overall, per_cat

def build_heatmap(records):
    """
    Build and print heatmap table of accuracy for each model (rows) and category (columns).
    """
    console = Console()
    console.print(f"[bold]Min Depth:[/bold] {MIN_DEPTH if MIN_DEPTH is not None else 'all'}")
    # Collect all categories
    categories = set()
    data = []
    for rec in records:
        overall, per_cat = filter_record_by_depth(rec, MIN_DEPTH)
        data.append({'model': rec.get('model', ''), 'overall': overall, 'per_cat': per_cat})
        categories.update(per_cat.keys())
    categories = sorted(categories)

    # Sort records
    if SORT_BY == SortBy.MODEL:
        data.sort(key=lambda x: x['model'].lower())
    else:
        # sort by overall accuracy descending
        data.sort(key=lambda x: x['overall'].get('accuracy', 0.0), reverse=True)

    # Build table
    table = Table(title='Accuracy Heatmap')
    table.add_column('Model', style='bold cyan')
    table.add_column('Trials', justify='right')
    table.add_column('Cost', justify='right')
    table.add_column('Avg Acc', justify='right')
    for cat in categories:
        table.add_column(cat, justify='right')

    for item in data:
        row = [item['model'], str(item['overall'].get('total_trials', 0)), f"${item['overall'].get('total_cost', 0):.6f}", f"{item['overall'].get('accuracy', 0)*100:.1f}%"]
        for cat in categories:
            val = item['per_cat'].get(cat)
            if val is None:
                row.append(Text('-', style='dim'))
            else:
                hue = val * 120
                r, g, b = hls_to_rgb(hue/360, 0.5, 1)
                bg = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
                text = Text(f"{val*100:.1f}%", style=Style(color='white', bgcolor=bg))
                row.append(text)
        table.add_row(*row)
    console.print(table)

def main():
    records = load_aggregates(AGGREGATE_FILE)
    if not records:
        print(f"No records found in {AGGREGATE_FILE}")
        return
    build_heatmap(records)

if __name__ == '__main__':
    main() 