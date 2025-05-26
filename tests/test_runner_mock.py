import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import re
import json
from decimal import Decimal
import pytest

from llm_arithmetic.runner import run
from llm_arithmetic import io as io_
from llm_arithmetic import types

# A minimal fake response object to mimic litellm completion output
class FakeMessage:
    def __init__(self, content):
        self.content = content

class FakeChoice:
    def __init__(self, message):
        self.message = message

class FakeResponse:
    def __init__(self, content):
        self.choices = [FakeChoice(FakeMessage(content))]
        self.usage = {"prompt_tokens": 0, "completion_tokens": 0}

@pytest.fixture(autouse=True)
def patch_completion(monkeypatch):
    """
    Monkeypatch litellm.completion to parse the prompt expression and return exact correct results.
    """
    def fake_completion(model, messages, reasoning_effort=None, timeout=None, **kwargs):
        # Extract the last line containing the expression
        ptext = messages[-1]["content"].strip()
        # Match two numbers and an operator (+, -, ×, ÷)
        m = re.search(r"(-?\d+(?:\.\d*)?)\s*([+\-×÷])\s*(-?\d+(?:\.\d*)?)$", ptext)
        if not m:
            return FakeResponse("")
        a_str, op, b_str = m.groups()
        a = Decimal(a_str)
        b = Decimal(b_str)
        # Compute according to op and runner's quantization rules
        if op == "+":
            res = a + b
        elif op == "-":
            res = a - b
        elif op == "×":
            res = (a * b).quantize(Decimal("0.0000"))
        elif op == "÷":
            res = (a / b).quantize(Decimal("0.0000"))
        else:
            res = Decimal("0")
        return FakeResponse(str(res))

    monkeypatch.setattr("litellm.completion", fake_completion)
    yield

@pytest.fixture(autouse=True)
def isolate_fs(tmp_path, monkeypatch):
    """Run each test in an isolated temporary directory to avoid writing to project root"""
    monkeypatch.chdir(tmp_path)

def test_runner_all_variants_positive(tmp_path):
    # Prepare a known trial file path to avoid timestamp unpredictability
    trial_file = tmp_path / "trials.jsonl"
    # Run with one trial at depth=2 for all 8 variants
    run(
        model="test-model",
        trials_per_cell=1,
        depths=[2],
        output_dir=str(tmp_path),
        reasoning_effort=None,
        resume_file=str(trial_file),
        retries=1,
        retry_delay=0.0
    )
    # Read back the trial records
    trials = io_.read_trials(str(trial_file))
    # We expect exactly 8 trials (one per variant)
    assert len(trials) == 8
    # All classifications should be Correct with no error
    for rec in trials:
        assert rec.get("classification") == "Correct"
        # error field should be null in JSON -> None in Python
        assert rec.get("error") is None
        # Verify one attempt in default success case
        assert rec.get("attempts") == 1

    # Optionally: verify each variant appears exactly once
    variants = [rec["variant"] for rec in trials]
    assert sorted(variants) == sorted([*"int_add int_sub int_mul int_div float_add float_sub float_mul float_div".split()])

def test_runner_retries_on_failure(tmp_path, monkeypatch):
    # Count how many times completion is called; fail every even call, succeed every odd
    call_count = { 'count': 0 }
    def fake_retryable(model, messages, reasoning_effort=None, timeout=None, **kwargs):
        idx = call_count['count']
        call_count['count'] += 1
        # On even idx (first attempt for each trial), simulate failure
        if idx % 2 == 0:
            raise Exception("simulated failure")
        # On odd idx, compute correct result as usual
        ptext = messages[-1]["content"].strip()
        m = re.search(r"(-?\d+(?:\.\d*)?)\s*([+\-×÷])\s*(-?\d+(?:\.\d*)?)$", ptext)
        if not m:
            return FakeResponse("")
        a_str, op, b_str = m.groups()
        a = Decimal(a_str)
        b = Decimal(b_str)
        if op == "+":
            res = a + b
        elif op == "-":
            res = a - b
        elif op == "×":
            res = (a * b).quantize(Decimal("0.0000"))
        else:
            res = (a / b).quantize(Decimal("0.0000"))
        return FakeResponse(str(res))

    # Override the autouse fixture's completion
    monkeypatch.setattr("litellm.completion", fake_retryable)

    trial_file = tmp_path / "trials.jsonl"
    # Run with retries=2 so each trial attempts twice (fail then succeed)
    run(
        model="test-model",
        trials_per_cell=1,
        depths=[2],
        output_dir=str(tmp_path),
        reasoning_effort=None,
        resume_file=str(trial_file),
        retries=2,
        retry_delay=0.0
    )
    # Should produce 8 trials
    trials = io_.read_trials(str(trial_file))
    assert len(trials) == 8
    # All should be correct
    for rec in trials:
        assert rec.get("classification") == "Correct"
        # Verify attempts logged
        assert rec.get("attempts") == 2
    # Ensure completion was called twice per trial
    assert call_count['count'] == 8 * 2

def test_resume_only_missing(tmp_path, monkeypatch):
    # Simulate an interrupted run: pre-write 4 trials for first 4 variants
    monkeypatch.chdir(tmp_path)
    trial_file = tmp_path / "trials.jsonl"
    # Create 4 partial correct trials
    for variant in types.VARIANTS[:4]:
        trial = types.Trial(
            model="test-model",
            variant=variant,
            depth=2,
            operands=[1, 1],
            correct=2,
            raw_response="2",
            parsed=2,
            classification="Correct",
            error=None,
            prompt_tokens=0,
            completion_tokens=0,
            cost=0.0,
            timestamp="2025-01-01T00:00:00Z",
            attempts=1,
            failed_to_get_reply=False
        )
        io_.write_trial(trial, str(trial_file))
    # Resume the run, which should write the remaining 4 variants
    run(
        model="test-model",
        trials_per_cell=1,
        depths=[2],
        output_dir=str(tmp_path),
        reasoning_effort=None,
        resume_file=str(trial_file),
        retries=1,
        retry_delay=0.0
    )
    # Verify we now have 8 trials total
    trials = io_.read_trials(str(trial_file))
    assert len(trials) == 8
    # Verify variant order matches full list
    variants = [rec["variant"] for rec in trials]
    assert variants == types.VARIANTS 