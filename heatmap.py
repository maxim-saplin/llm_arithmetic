import argparse
import json
import os
from colorsys import hls_to_rgb
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.style import Style

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


def build_heatmap(cells, title, metric="accuracy"):
    # Determine categories and depth levels
    categories = sorted(cells.keys())
    depth_nums = set()
    for depths in cells.values():
        for key in depths.keys():
            if key.startswith("depth_"):
                try:
                    depth_nums.add(int(key.split("_")[1]))
                except ValueError:
                    pass
    depth_nums = sorted(depth_nums)
    # Prepare table
    table = Table(title=title)
    table.add_column("Category", style="bold")
    for n in depth_nums:
        table.add_column(f"Depth {n}", justify="right")
    # Populate rows
    for cat in categories:
        row = [cat]
        for n in depth_nums:
            stats = cells.get(cat, {}).get(f"depth_{n}")
            if not stats:
                row.append(Text("-", style="dim"))
            else:
                val = stats.get(metric, 0)
                display_pct = val * 100
                # Choose hue: high good for accuracy, low good for rates, with progressive scale for nan_rate
                if metric == "accuracy":
                    hue_val = val
                elif metric == "nan_rate":
                    # power mapping for nan_rate: steep initial shading, flatten near high values
                    exponent = 0.3
                    hue_val = 1 - (val ** exponent)
                else:
                    hue_val = 1 - val
                hue = hue_val * 120  # 0 to 120 degrees
                r, g, b = hls_to_rgb(hue/360, 0.5, 1)
                bg = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
                text = Text(f"{display_pct:.1f}%", style=Style(color="white", bgcolor=bg))
                row.append(text)
        table.add_row(*row)
    return table


def main():
    parser = argparse.ArgumentParser(
        description="Show heatmaps of LLM arithmetic accuracies"
    )
    parser.add_argument(
        "--file", help="Path to aggregate JSONL file",
        default=os.path.join(os.getcwd(), "aggregate.jsonl")
    )
    parser.add_argument(
        "--model", help="Model name to filter (default: all models)",
        default=None
    )
    parser.add_argument(
        "--metrics", help="Metrics to plot (choices: accuracy, deviate_rate, nan_rate)",
        nargs="+", choices=["accuracy", "deviate_rate", "nan_rate"],
        default=["accuracy", "deviate_rate", "nan_rate"]
    )
    args = parser.parse_args()

    records = load_aggregates(args.file)
    if not records:
        print(f"No records found in {args.file}")
        return

    # Filter records if a model is specified
    recs = records
    if args.model:
        recs = [r for r in records if r.get('model') == args.model]
        if not recs:
            print(f"No records for model {args.model}")
            return

    console = Console()
    # Build and display heatmaps for each requested metric
    for metric in args.metrics:
        # aggregate selected metric across records

        console.print("\n\n")
        console.rule(f"[bold yellow]{metric.replace('_', ' ').title()} Heatmap[/bold yellow]")
        console.print("\n")
        
        agg = {}
        for r in recs:
            cells = r.get('cells', {})
            for cat, depths in cells.items():
                if cat not in agg:
                    agg[cat] = {}
                for k, stats in depths.items():
                    val = stats.get(metric, 0)
                    if k not in agg[cat]:
                        agg[cat][k] = {'sum': val, 'count': 1}
                    else:
                        agg[cat][k]['sum'] += val
                        agg[cat][k]['count'] += 1
        # compute averages
        avg_cells = {}
        for cat, depths in agg.items():
            avg_cells[cat] = {}
            for k, vs in depths.items():
                avg_cells[cat][k] = {metric: vs['sum'] / vs['count']}
        # overall heatmap
        overall_table = build_heatmap(
            avg_cells,
            f"Overall {metric.replace('_', ' ').title()} Heatmap",
            metric
        )
        console.print(overall_table)
        # per-model heatmaps
        for r in recs:
            cells = r.get('cells', {})
            table = build_heatmap(
                cells,
                f"{r.get('model')} {metric.replace('_', ' ').title()} Heatmap",
                metric
            )
            console.print(table)

if __name__ == "__main__":
    main() 