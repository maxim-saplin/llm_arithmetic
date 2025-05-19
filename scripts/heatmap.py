import json
import os
from colorsys import hls_to_rgb
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.style import Style
# Configuration (set at top)
# Use None to include all models
MODEL_FILTER = None  # e.g. "claude-3-7-sonnet-20250219"
# Metrics to include in heatmaps
METRICS = ["accuracy", "deviate_rate", "nan_rate"]
# Path to raw logs directory
RESULTS_DIR = os.path.join(os.getcwd(), 'results')

def load_logs(results_dir):
    logs = []
    for fname in os.listdir(results_dir):
        if not fname.endswith('.jsonl'):
            continue
        path = os.path.join(results_dir, fname)
        try:
            with open(path) as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    logs.append(rec)
        except FileNotFoundError:
            continue
    return logs

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
    # Sort categories lexicographically then apply custom order
    ordered = []
    for prefix in ["int", "float"]:
        for op in ["add", "sub", "mul", "div"]:
            col = f"{prefix}_{op}"
            if col in categories:
                ordered.append(col)
    for col in categories:
        if col not in ordered:
            ordered.append(col)
    categories = ordered
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
                # highlight best cases: accuracy == 100% or rate metrics == 0%
                if metric == "accuracy" and val == 1.0:
                    text = Text(f"{display_pct:.1f}%", style=Style(bold=True))
                elif metric != "accuracy" and val == 0.0:
                    text = Text(f"{display_pct:.1f}%", style=Style(bold=True))
                else:
                    # shading: darker reds to brighter greens based on hue_val
                    lightness = 0.3 + 0.4 * hue_val
                    r, g, b = hls_to_rgb(hue/360, lightness, 1)
                    bg = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
                    text = Text(f"{display_pct:.1f}%", style=Style(color="white", bgcolor=bg))
                row.append(text)
        table.add_row(*row)
    return table


def main():
    # Load logs from configured directory
    logs = load_logs(RESULTS_DIR)
    if not logs:
        print(f"No log records found in {RESULTS_DIR}")
        return

    # Filter logs if a model is specified
    recs = logs
    if MODEL_FILTER:
        recs = [r for r in logs if r.get('model') == MODEL_FILTER]
        if not recs:
            print(f"No log records for model {MODEL_FILTER}")
            return

    console = Console()
    # Determine complete vs incomplete models based on variant-depth coverage
    # Group logs by model
    grouped = {}
    for rec in recs:
        m = rec.get("model", "")
        grouped.setdefault(m, []).append(rec)
    # Compute distinct variant-depth combos and trial counts per model
    variant_depth_count = {}
    trial_count = {}
    for m, rec_list in grouped.items():
        combos = set()
        for rec in rec_list:
            variant = rec.get("variant", "")
            depth = rec.get("depth")
            if depth is None:
                continue
            combos.add((variant, depth))
        variant_depth_count[m] = len(combos)
        trial_count[m] = len(rec_list)
    # Determine complete models (max combos) and list incomplete ones
    expected_combos = max(variant_depth_count.values()) if variant_depth_count else 0
    complete_models = [m for m, count in variant_depth_count.items() if count == expected_combos]
    incomplete_models = [m for m, count in variant_depth_count.items() if count < expected_combos]
    if incomplete_models:
        console.print("[bold yellow]Ignored incomplete models:[/bold yellow]")
        for m in sorted(incomplete_models):
            console.print(f" - {m}: {trial_count[m]} trials")
    # Only include complete models in overall aggregation
    recs_overall = [rec for rec in recs if rec.get("model", "") in complete_models]
    # Build and display heatmaps for each requested metric
    for metric in METRICS:
        # aggregate raw logs into per-category per-depth statistics (complete models only)
        agg_stats = {}
        for rec in recs_overall:
            cat = rec.get('variant', '')
            depth = rec.get('depth')
            if depth is None:
                continue
            key = f"depth_{depth}"
            agg_stats.setdefault(cat, {})
            agg_stats[cat].setdefault(key, {"total": 0, "correct": 0, "deviate": 0, "nan": 0})
            stats = agg_stats[cat][key]
            stats["total"] += 1
            if rec.get("classification") == "Correct":
                stats["correct"] += 1
            else:
                if rec.get("error") or rec.get("failed_to_get_reply"):
                    stats["nan"] += 1
                else:
                    stats["deviate"] += 1
        # prepare cells for overall heatmap
        cells = {}
        for cat, depths in agg_stats.items():
            cells[cat] = {}
            for key, st in depths.items():
                total = st.get("total", 0)
                if metric == "accuracy":
                    val = st.get("correct", 0) / total if total else 0
                elif metric == "deviate_rate":
                    val = st.get("deviate", 0) / total if total else 0
                elif metric == "nan_rate":
                    val = st.get("nan", 0) / total if total else 0
                else:
                    val = 0
                cells[cat][key] = {metric: val}
        console.print("\n\n")
        console.rule(f"[bold yellow]{metric.replace('_', ' ').title()} Heatmap[/bold yellow]")
        console.print("\n")
        console.print(build_heatmap(
            cells,
            f"Overall {metric.replace('_', ' ').title()} Heatmap",
            metric
        ))
        # per-model heatmaps
        models = sorted(set(r.get("model", "") for r in recs))
        for model in models:
            model_recs = [r for r in recs if r.get('model') == model]
            # Include trial count in model title
            trial_count = len(model_recs)

            agg_stats = {}
            for rec in model_recs:
                cat = rec.get("variant", "")
                depth = rec.get("depth")
                if depth is None:
                    continue
                key = f"depth_{depth}"
                agg_stats.setdefault(cat, {})
                agg_stats[cat].setdefault(key, {"total": 0, "correct": 0, "deviate": 0, "nan": 0})
                stats = agg_stats[cat][key]
                stats["total"] += 1
                if rec.get("classification") == "Correct":
                    stats["correct"] += 1
                else:
                    if rec.get("error") or rec.get("failed_to_get_reply"):
                        stats["nan"] += 1
                    else:
                        stats["deviate"] += 1
            cells = {}
            for cat, depths in agg_stats.items():
                cells[cat] = {}
                for key, st in depths.items():
                    total = st.get("total", 0)
                    if metric == "accuracy":
                        val = st.get("correct", 0) / total if total else 0
                    elif metric == "deviate_rate":
                        val = st.get("deviate", 0) / total if total else 0
                    elif metric == "nan_rate":
                        val = st.get("nan", 0) / total if total else 0
                    else:
                        val = 0
                    cells[cat][key] = {metric: val}
            console.print(build_heatmap(
                cells,
                f"{model} ({trial_count} trials) {metric.replace('_', ' ').title()} Heatmap",
                metric
            ))

if __name__ == "__main__":
    main() 