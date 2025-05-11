#!/usr/bin/env python3
import argparse
import json
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def load_aggregates(path):
    """
    Load aggregate records from a JSONL file.
    """
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


def main():
    parser = argparse.ArgumentParser(
        description="Show a terminal summary of LLM arithmetic results"
    )
    parser.add_argument(
        "--model", help="Model name to filter (default: last record)",
        default=None
    )
    parser.add_argument(
        "--file", help="Path to aggregate JSONL file",
        default=os.path.join(os.getcwd(), "aggregate.jsonl")
    )
    args = parser.parse_args()

    recs = load_aggregates(args.file)
    if not recs:
        print(f"No aggregate records found in {args.file}")
        return
    console = Console()
    # If a model is specified, show detailed report for that model
    if args.model:
        filtered = [r for r in recs if r.get('model') == args.model]
        if not filtered:
            print(f"No records for model {args.model}")
            return
        record = filtered[-1]
    # If no model and multiple records, show overview table
    elif len(recs) > 1:
        table = Table(title="Models Overview")
        table.add_column("Model", style="cyan")
        table.add_column("Date", style="magenta")
        table.add_column("Trials", justify="right")
        table.add_column("Accuracy", justify="right")
        table.add_column("NaN %", justify="right")
        table.add_column("Dev %", justify="right")
        table.add_column("Cost", justify="right")
        table.add_column("Avg Error", justify="right")
        # Populate rows for each model
        for r in recs:
            o = r.get('overall', {})
            table.add_row(
                r.get('model', ''),
                r.get('date', ''),
                str(o.get('total_trials', '')),
                f"{o.get('accuracy',0)*100:.2f}%",
                f"{o.get('nan_rate',0)*100:.2f}%",
                f"{o.get('deviate_rate',0)*100:.2f}%",
                f"${o.get('total_cost',0):.6f}",
                o.get('avg_error', '')
            )
        console.print(table)
        # Detailed per-model cards
        for record in recs:
            overall = record.get('overall', {})
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
            per_cat = record.get('per_category', {})
            if per_cat:
                detail_table = Table(title=f"Per-Variant Summary ({record.get('model')})")
                detail_table.add_column("Variant", style="cyan", no_wrap=True)
                detail_table.add_column("Trials", justify="right")
                detail_table.add_column("Accuracy", justify="right")
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

    overall = record.get('overall', {})

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

    # Build per-category table
    per_cat = record.get('per_category', {})
    if per_cat:
        table = Table(title="Per-Variant Summary")
        table.add_column("Variant", style="cyan", no_wrap=True)
        table.add_column("Trials", justify="right")
        table.add_column("Accuracy", justify="right")
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