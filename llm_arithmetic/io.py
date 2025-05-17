import json
from typing import Any, Dict
from llm_arithmetic.types import Trial, Aggregate


def write_trial(trial: Trial, path: str):
    """
    Append a single trial record to a JSONL file.
    """
    record: Dict[str, Any] = {
        "model": trial.model,
        "variant": trial.variant,
        "depth": trial.depth,
        "operands": trial.operands,
        "correct": trial.correct,
        "raw_response": trial.raw_response,
        "parsed": trial.parsed,
        "classification": trial.classification,
        "error": trial.error,
        "tokens": {
            "prompt_tokens": trial.prompt_tokens,
            "completion_tokens": trial.completion_tokens
        },
        "cost": trial.cost,
        "timestamp": trial.timestamp,
        "attempts": trial.attempts,
        "failed_to_get_reply": trial.failed_to_get_reply,
        "extra_context": trial.extra_context
    }
    with open(path, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")


def write_aggregate(aggregate: Aggregate, path: str):
    """
    Append an aggregate summary record to a JSONL file.
    """
    record: Dict[str, Any] = {
        "model": aggregate.model,
        "date": aggregate.date,
        "trials_per_cell": aggregate.trials_per_cell,
        "extra_context": aggregate.extra_context,
        "overall": aggregate.overall,
        "per_category": aggregate.per_category,
        "cells": aggregate.cells
    }
    with open(path, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")


def read_trials(path: str) -> list[dict]:
    """
    Read all trial records from a JSONL file and return as a list of dicts.
    """
    records = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    records.append(rec)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass
    return records 