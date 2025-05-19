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

# Minimum digit depth to include in metrics (None to include all)
MIN_DEPTH = 6
# Maximum digit depth to include in metrics (None to include all)
MAX_DEPTH = 10

# Path to raw logs directory
RESULTS_DIR = os.path.join(os.getcwd(), 'results')

def load_logs(results_dir, min_depth, max_depth):
    stats = {}
    for fname in os.listdir(results_dir):
        if not fname.endswith('.jsonl'):
            continue
        path = os.path.join(results_dir, fname)
        with open(path) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                depth = rec.get('depth')
                if depth is None:
                    continue
                if min_depth is not None and depth < min_depth:
                    continue
                if max_depth is not None and depth > max_depth:
                    continue
                model = rec.get('model', '')
                variant = rec.get('variant', '')
                classification = rec.get('classification', '')
                cost = rec.get('cost', 0.0)
                stats.setdefault(model, {})
                stats[model].setdefault(variant, {'trials': 0, 'correct': 0, 'cost': 0.0})
                stats[model][variant]['trials'] += 1
                if classification == 'Correct':
                    stats[model][variant]['correct'] += 1
                stats[model][variant]['cost'] += cost
    data = []
    categories = set()
    for model, var_stats in stats.items():
        total_trials = sum(v['trials'] for v in var_stats.values())
        total_correct = sum(v['correct'] for v in var_stats.values())
        total_cost = sum(v['cost'] for v in var_stats.values())
        overall_acc = total_correct / total_trials if total_trials > 0 else 0.0
        per_cat = {}
        for variant, v in var_stats.items():
            trials = v['trials']
            per_cat[variant] = v['correct'] / trials if trials > 0 else 0.0
            categories.add(variant)
        overall = {'accuracy': overall_acc, 'total_trials': total_trials, 'total_cost': total_cost}
        data.append({'model': model, 'overall': overall, 'per_cat': per_cat})
    return data, categories

def build_heatmap(data, categories):
    """
    Build and print heatmap table of accuracy for each model (rows) and category (columns).
    """
    console = Console()
    console.print(f"\n[bold]Min Depth: {MIN_DEPTH if MIN_DEPTH is not None else 'all'}[/bold]")
    console.print(f"[bold]Max Depth: {MAX_DEPTH if MAX_DEPTH is not None else 'all'}[/bold]")
    # Sort and prepare categories
    categories = sorted(categories)

    # Order columns: int then float with ops add, sub, mul, div
    ordered = []
    for prefix in ['int', 'float']:
        for op in ['add', 'sub', 'mul', 'div']:
            col = f"{prefix}_{op}"
            if col in categories:
                ordered.append(col)
    # include any other categories afterwards
    for col in categories:
        if col not in ordered:
            ordered.append(col)
    categories = ordered

    # Sort records
    if SORT_BY == SortBy.MODEL:
        data.sort(key=lambda x: x['model'].lower())
    else:
        # put complete logs first, then incomplete logs, each sorted by accuracy descending
        total_cats = len(categories)
        data.sort(key=lambda x: (len(x['per_cat']) < total_cats, -x['overall'].get('accuracy', 0.0)))

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
                # highlight perfect scores distinctly
                if val == 1.0:
                    text = Text(f"{val*100:.1f}%", style=Style(bold=True))
                else:
                    # enhance contrast: darker reds for low accuracy, brighter greens for high accuracy
                    hue = val * 120
                    lightness = 0.3 + 0.4 * val  # range from 0.3 to 0.7
                    r, g, b = hls_to_rgb(hue/360, lightness, 1)
                    bg = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
                    text = Text(f"{val*100:.1f}%", style=Style(color="white", bgcolor=bg))
                row.append(text)
        table.add_row(*row)
    console.print(table)

def main():
    data, categories = load_logs(RESULTS_DIR, MIN_DEPTH, MAX_DEPTH)
    if not data:
        print(f"No log records found in {RESULTS_DIR}")
        return
    build_heatmap(data, categories)

if __name__ == '__main__':
    main() 