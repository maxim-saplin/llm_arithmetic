import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm_arithmetic.progress import (
    RunProgress,
    format_stats,
    terminal_width,
    truncate_postfix,
)


def test_format_stats_compact():
    s = format_stats(3844, 465000, 1.23)
    assert "prompt_tokens" not in s
    assert "completion_tokens" not in s
    assert "tok=" in s
    assert "$1.2300" in s
    assert len(s) < 40


def test_truncate_postfix_max_length():
    s = truncate_postfix("tok=468.8k $1.2300 extra noise here", 30)
    assert len(s) <= 30


def test_terminal_width_clamped(monkeypatch):
    import shutil

    monkeypatch.setattr(
        shutil, "get_terminal_size", lambda fallback=None: type("S", (), {"columns": 10})()
    )
    assert terminal_width() == 40

    monkeypatch.setattr(
        shutil, "get_terminal_size", lambda fallback=None: type("S", (), {"columns": 500})()
    )
    assert terminal_width() == 200


def test_run_progress_narrow_terminal_no_duplicate_desc(monkeypatch, capfd):
    monkeypatch.setattr(
        "llm_arithmetic.progress.terminal_width", lambda: 60
    )
    monkeypatch.setattr(
        "llm_arithmetic.progress._plain_disabled", lambda: False
    )

    with RunProgress(total=5) as progress:
        for i in range(5):
            progress.tick(
                prompt_tokens=1000 * (i + 1),
                completion_tokens=465000,
                cost=0.04 * (i + 1),
            )

    captured = capfd.readouterr().err
    for line in captured.splitlines():
        assert len(re.findall(r"trials", line)) <= 1


def test_run_progress_plain_mode(monkeypatch, capfd):
    monkeypatch.setenv("TQDM_DISABLE", "1")
    monkeypatch.setattr("llm_arithmetic.progress._plain_disabled", lambda: True)

    with RunProgress(total=3) as progress:
        for i in range(3):
            progress.tick(prompt_tokens=10, completion_tokens=20, cost=0.01 * (i + 1))

    captured = capfd.readouterr().err
    assert "trials" in captured
    assert "tok=" in captured
