"""Terminal progress bar for evaluation runs (tqdm wrapper with width-safe postfix)."""

import os
import signal
import sys
import time
from typing import Optional

from tqdm import tqdm


def terminal_width() -> int:
    import shutil
    cols = shutil.get_terminal_size(fallback=(120, 24)).columns
    return max(40, min(200, cols))


def _humanize_count(n: int) -> str:
    if n >= 1_000_000:
        s = f"{n / 1_000_000:.1f}"
        if s.endswith(".0"):
            s = s[:-2]
        return f"{s}M"
    if n >= 1000:
        s = f"{n / 1000:.1f}"
        if s.endswith(".0"):
            s = s[:-2]
        return f"{s}k"
    return str(n)


def format_stats(prompt_tokens: int, completion_tokens: int, cost: float) -> str:
    total_tokens = prompt_tokens + completion_tokens
    return f"tok={_humanize_count(total_tokens)} ${cost:.4f}"


def truncate_postfix(s: str, max_len: int) -> str:
    if max_len <= 0:
        return ""
    if len(s) <= max_len:
        return s
    if max_len == 1:
        return s[:1]
    return s[: max_len - 1] + "…"


def _plain_disabled() -> bool:
    return os.environ.get("TQDM_DISABLE") == "1" or not sys.stderr.isatty()


class RunProgress:
    """Context manager: tqdm bar on stderr, or plain lines when disabled / non-TTY."""

    def __init__(self, total: int):
        self.total = total
        self._n = 0
        self._disable = _plain_disabled()
        self._pbar: Optional[tqdm] = None
        self._start_time: float = 0.0
        self._sigwinch = None

    def __enter__(self) -> "RunProgress":
        self._start_time = time.monotonic()
        if self._disable:
            return self
        self._pbar = tqdm(
            total=self.total,
            desc="trials",
            unit="trial",
            file=sys.stderr,
            dynamic_ncols=True,
            mininterval=0.5,
            leave=True,
            disable=False,
        )
        if hasattr(signal, "SIGWINCH"):
            def _on_resize(signum, frame):
                if self._pbar is not None:
                    self._pbar.refresh()

            self._sigwinch = _on_resize
            try:
                signal.signal(signal.SIGWINCH, _on_resize)
            except (ValueError, OSError):
                self._sigwinch = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._pbar is not None:
            self._pbar.close()
            self._pbar = None
        if self._sigwinch is not None:
            try:
                signal.signal(signal.SIGWINCH, signal.SIG_DFL)
            except (ValueError, OSError):
                pass
            self._sigwinch = None

    def _max_postfix_len(self) -> int:
        return max(8, terminal_width() - 55)

    def _postfix_for_tick(
        self, prompt_tokens: int, completion_tokens: int, cost: float
    ) -> str:
        stats = format_stats(prompt_tokens, completion_tokens, cost)
        return truncate_postfix(stats, self._max_postfix_len())

    def _plain_interval(self) -> int:
        return 10 if self.total > 100 else 1

    def _maybe_plain_line(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float,
        *,
        force: bool = False,
    ) -> None:
        if not self._disable:
            return
        interval = self._plain_interval()
        if not force and self._n % interval != 0 and self._n != self.total:
            return
        elapsed = time.monotonic() - self._start_time
        per_trial = elapsed / self._n if self._n else 0.0
        stats = format_stats(prompt_tokens, completion_tokens, cost)
        parts = [f"{self._n}/{self.total} trials", stats]
        if per_trial > 0:
            parts.append(f"{per_trial:.1f}s/trial")
        print(" | ".join(parts), file=sys.stderr)

    def advance(self, n: int) -> None:
        if n <= 0:
            return
        self._n += n
        if self._pbar is not None:
            self._pbar.update(n)

    def tick(
        self,
        *,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float,
    ) -> None:
        self._n += 1
        if self._pbar is not None:
            self._pbar.set_postfix_str(
                self._postfix_for_tick(prompt_tokens, completion_tokens, cost)
            )
            self._pbar.update(1)
        else:
            self._maybe_plain_line(prompt_tokens, completion_tokens, cost)

    def log(self, message: str) -> None:
        if self._pbar is not None:
            self._pbar.write(message)
        else:
            print(message, file=sys.stderr)
