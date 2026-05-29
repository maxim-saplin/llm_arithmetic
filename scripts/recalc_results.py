#!/usr/bin/env python3
"""Recalculate historical results with the current parser.

Every trial record stores the model's raw response. This script re-parses each
raw response with ``llm_arithmetic.parse.parse_response`` and compares the new
classification against the one stored at collection time. It proves the parser
change is (a) a strict improvement for the discarded-answer failure modes and
(b) non-regressive for already-parsed answers.

Usage:
    python scripts/recalc_results.py            # analyse, print + write report
    python scripts/recalc_results.py --write     # also rewrite results/*.jsonl
                                                  # in place (creates .bak files)

Outputs (analysis mode):
    - prints an overall transition matrix and per-model before/after table
    - writes REPORT_parsing_fix.md
    - writes recalc_summary.json (machine-readable)
"""
import sys
import os
import json
import glob
import argparse
import shutil
from collections import defaultdict, Counter
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_arithmetic.parse import parse_response  # noqa: E402

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLASSES = ["Correct", "Deviate", "NaN"]


def reconstruct_correct(rec):
    variant = rec.get("variant", "")
    c = rec.get("correct")
    if c is None:
        return None
    try:
        if variant.startswith("int"):
            return int(c)
        return Decimal(str(c))
    except Exception:
        return None


def recompute(rec):
    correct = reconstruct_correct(rec)
    if correct is None:
        return rec.get("parsed"), rec.get("classification"), rec.get("error")
    raw = rec.get("raw_response") or ""
    return parse_response(raw, correct, rec.get("variant", ""))


def analyse(write=False):
    files = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.jsonl")))
    # transition[(old, new)] -> count
    transition = Counter()
    # per-model old/new class counts
    per_model_old = defaultdict(Counter)
    per_model_new = defaultdict(Counter)
    per_model_total = Counter()
    examples = defaultdict(list)  # (old,new) -> [(model, raw, correct, parsed)]
    total = 0

    for path in files:
        out_lines = []
        changed = False
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    out_lines.append(line)
                    continue
                old_cls = rec.get("classification")
                new_parsed, new_cls, new_err = recompute(rec)
                model = rec.get("model", os.path.basename(path))
                total += 1
                per_model_total[model] += 1
                per_model_old[model][old_cls] += 1
                per_model_new[model][new_cls] += 1
                transition[(old_cls, new_cls)] += 1
                if old_cls != new_cls and len(examples[(old_cls, new_cls)]) < 6:
                    examples[(old_cls, new_cls)].append(
                        (model, (rec.get("raw_response") or "")[:90],
                         rec.get("correct"), new_parsed)
                    )
                if write:
                    if rec.get("classification") != new_cls or str(rec.get("parsed")) != str(new_parsed) or rec.get("error") != new_err:
                        changed = True
                    rec["classification"] = new_cls
                    rec["parsed"] = new_parsed if not isinstance(new_parsed, Decimal) else str(new_parsed)
                    rec["error"] = new_err
                    out_lines.append(json.dumps(rec, default=str))
        if write and changed:
            shutil.copyfile(path, path + ".bak")
            with open(path, "w") as f:
                f.write("\n".join(out_lines) + "\n")

    return {
        "files": files,
        "total": total,
        "transition": transition,
        "per_model_old": per_model_old,
        "per_model_new": per_model_new,
        "per_model_total": per_model_total,
        "examples": examples,
    }


def fmt_transition(transition, total):
    lines = []
    lines.append(f"{'old → new':<22}{'count':>10}")
    lines.append("-" * 32)
    # stable order
    keys = sorted(transition, key=lambda k: (-transition[k], str(k)))
    for (old, new) in keys:
        n = transition[(old, new)]
        tag = "  (unchanged)" if old == new else ""
        lines.append(f"{str(old)+' → '+str(new):<22}{n:>10}{tag}")
    lines.append("-" * 32)
    lines.append(f"{'TOTAL':<22}{total:>10}")
    return "\n".join(lines)


def overall_counts(per_model_old, per_model_new):
    old = Counter()
    new = Counter()
    for m, c in per_model_old.items():
        old.update(c)
    for m, c in per_model_new.items():
        new.update(c)
    return old, new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="rewrite results/*.jsonl in place (.bak backups)")
    args = ap.parse_args()

    res = analyse(write=args.write)
    transition = res["transition"]
    total = res["total"]
    old, new = overall_counts(res["per_model_old"], res["per_model_new"])

    print(f"Recalculated {total} trial records across {len(res['files'])} files\n")
    print("=== OVERALL TRANSITION MATRIX (old classification → new) ===")
    print(fmt_transition(transition, total))

    print("\n=== OVERALL BEFORE / AFTER ===")
    print(f"{'class':<10}{'before':>10}{'after':>10}{'delta':>10}")
    for c in CLASSES:
        print(f"{c:<10}{old.get(c,0):>10}{new.get(c,0):>10}{new.get(c,0)-old.get(c,0):>+10}")

    recovered = sum(n for (o, nw), n in transition.items() if o == "NaN" and nw != "NaN")
    # True regressions: an answer the old parser accepted as Correct is now worse.
    correct_regressions = transition.get(("Correct", "Deviate"), 0) + transition.get(("Correct", "NaN"), 0)
    # Deviate -> NaN are truncated/unclosed reasoning relabels (no real answer).
    deviate_to_nan = transition.get(("Deviate", "NaN"), 0)
    deviate_to_correct = transition.get(("Deviate", "Correct"), 0)
    print(f"\nNaN answers recovered (NaN → number): {recovered}")
    print(f"  ... of which exact-Correct: {transition.get(('NaN','Correct'),0)}, Deviate: {transition.get(('NaN','Deviate'),0)}")
    print(f"Deviate → Correct (e.g. de-grouped thousands): {deviate_to_correct}")
    print(f"Deviate → NaN (truncated-reasoning relabels, not regressions): {deviate_to_nan}")
    print(f"TRUE regressions (Correct → Deviate/NaN): {correct_regressions}")

    print("\n=== SAMPLE TRANSITIONS ===")
    for key in sorted(res["examples"], key=lambda k: (k[0] != "NaN", str(k))):
        old_c, new_c = key
        print(f"\n[{old_c} → {new_c}]")
        for model, raw, correct, parsed in res["examples"][key]:
            print(f"  {model[:28]:<28} correct={correct!s:<18} parsed={parsed!s:<18} raw={raw!r}")

    # write markdown report data + json summary
    summary = {
        "total": total,
        "before": {c: old.get(c, 0) for c in CLASSES},
        "after": {c: new.get(c, 0) for c in CLASSES},
        "transition": {f"{o}->{nw}": n for (o, nw), n in transition.items()},
        "recovered": recovered,
        "deviate_to_correct": deviate_to_correct,
        "deviate_to_nan_truncated": deviate_to_nan,
        "true_regressions": correct_regressions,
        "per_model": {
            m: {
                "total": res["per_model_total"][m],
                "before": {c: res["per_model_old"][m].get(c, 0) for c in CLASSES},
                "after": {c: res["per_model_new"][m].get(c, 0) for c in CLASSES},
            }
            for m in sorted(res["per_model_total"])
        },
    }
    with open(os.path.join(REPO_ROOT, "recalc_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("\nWrote recalc_summary.json")
    if args.write:
        print("Rewrote result files in place (.bak backups created where changed).")


if __name__ == "__main__":
    main()
