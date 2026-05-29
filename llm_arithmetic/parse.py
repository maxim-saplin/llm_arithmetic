"""Robust parsing of free-form LLM responses into a single numeric answer.

The evaluation prompt asks models to "reply with just the numeric result", but
real responses vary wildly: LaTeX ``\\boxed{}`` markers, thousands separators,
scientific notation, markdown emphasis, trailing commentary, fractions, etc.

The original parser only accepted a number anchored at the very end of the
string (regex ``(-?\\d+(?:\\.\\d*)?)\\s*$``). That discarded thousands of
legitimate answers as ``NaN``. This module recovers them while remaining
backward-compatible: a response that the old parser accepted is parsed to the
same value here.

Extraction strategy (in priority order):

1. ``\\boxed{...}`` -- the de-facto "final answer" marker used by reasoning
   models. The content of the *last* box wins.
2. Otherwise, the *last* number-like token in the (cleaned) text, matching the
   original "last number in response" philosophy but with a far more capable
   number recognizer.

The classification / error logic (Correct / Deviate / NaN, int vs. float
quantization) is preserved unchanged.
"""

import re
from decimal import Decimal, InvalidOperation

# --- number token --------------------------------------------------------
# sign, an integer part (optionally with a trailing dot like "15.") or a bare
# fraction (".5"), and an optional scientific exponent.
_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
_NUMBER_RE = re.compile(_NUMBER)

# Map unicode superscripts (used in "×10¹⁷") to ASCII so they can be parsed.
_SUPERSCRIPT = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻", "0123456789+-")

# Backward-compatibility regex: the exact behaviour of the original parser.
# Kept so callers/tests can assert that legacy-accepted strings are unchanged.
LEGACY_NUMBER_REGEX = re.compile(r"(-?\d+(?:\.\d*)?)\s*$")
# Public alias retained for any external importers of the old name.
NUMBER_REGEX = LEGACY_NUMBER_REGEX


def _strip_think(s: str) -> str:
    """Remove ``<think>...</think>`` reasoning blocks, including an unclosed
    trailing one (a truncated reply has no final answer in it)."""
    s = re.sub(r"<think>.*?</think>", "", s, flags=re.DOTALL | re.IGNORECASE)
    s = re.sub(r"<think>.*$", "", s, flags=re.DOTALL | re.IGNORECASE)
    return s


def _find_matching_brace(s: str, open_idx: int) -> int:
    """Given index of a ``{`` return the index of its matching ``}`` (-1 if none)."""
    depth = 0
    for i in range(open_idx, len(s)):
        c = s[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _last_boxed_content(s: str):
    """Return the inner text of the last ``\\boxed{...}`` (brace-aware), or None."""
    content = None
    for m in re.finditer(r"\\boxed\s*", s):
        i = s.find("{", m.end())
        if i == -1:
            continue
        j = _find_matching_brace(s, i)
        if j == -1:
            continue
        content = s[i + 1 : j]
    return content


def _strip_fractions(s: str) -> str:
    """Remove LaTeX ``\\frac{A}{B}`` / ``\\dfrac`` / ``\\tfrac`` expressions.

    A bare fraction echoes the operands rather than computing a result, so we
    must not let the numerator/denominator be mistaken for the answer.
    """
    out = []
    i = 0
    n = len(s)
    while i < n:
        m = re.match(r"\\[dt]?frac\s*", s[i:])
        if m:
            k = i + m.end()
            if k < n and s[k] == "{":
                j1 = _find_matching_brace(s, k)
                if j1 != -1 and j1 + 1 < n and s[j1 + 1] == "{":
                    j2 = _find_matching_brace(s, j1 + 1)
                    if j2 != -1:
                        out.append(" ")
                        i = j2 + 1
                        continue
        out.append(s[i])
        i += 1
    return "".join(out)


# Characters used as a multiplication sign in scientific notation.
_MULT = r"[×xX✕✖·•*]"
_SUP_CHARS = "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻"


def _normalize(s: str) -> str:
    """Normalise formatting so number tokens become parseable."""
    # LaTeX spacing / grouping helpers.
    s = s.replace("\\,", "").replace("\\!", "").replace("{,}", ",")
    # LaTeX multiplication commands -> a symbol the sci-notation pass recognises.
    s = re.sub(r"\\(?:times|cdot|ast)\b", "×", s)
    # Scientific notation, only in *unambiguous* forms that carry an explicit
    # exponent marker, so markdown like "**Answer:** 10400" is never mistaken
    # for "× 10^...". A real mantissa (digits) must precede the × sign.
    #   "3.41×10¹⁷"  (superscript exponent)
    s = re.sub(
        rf"(\d(?:[\d.]*\d)?)\s*{_MULT}\s*10\s*([{_SUP_CHARS}]+)",
        lambda m: m.group(1) + "e" + m.group(2).translate(_SUPERSCRIPT),
        s,
    )
    #   "3.41 × 10^17" / "5 * 10 ^ 8"  (caret exponent)
    s = re.sub(
        rf"(\d(?:[\d.]*\d)?)\s*{_MULT}\s*10\s*\^\s*([+-]?\d+)",
        r"\1e\2",
        s,
    )
    # Any remaining unicode superscripts -> ASCII (harmless once sci is handled).
    s = s.translate(_SUPERSCRIPT)
    # Strip markdown/code/currency decorations.
    s = re.sub(r"[*`$]", "", s)
    s = s.replace("\\(", " ").replace("\\)", " ").replace("\\[", " ").replace("\\]", " ")
    # Drop scientific uncertainty notation: "90250000.000102(4)" -> "...102".
    s = re.sub(r"(?<=\d)\((\d+)\)", "", s)
    # Remove thousands separators: a comma between a digit and a 3-digit group.
    s = re.sub(r"(?<=\d),(?=\d{3}(?:\D|$))", "", s)
    return s


def _to_decimal(token: str):
    if not re.search(r"\d", token):
        return None
    try:
        return Decimal(token)
    except InvalidOperation:
        return None


def _extract_number(s: str, prefer_first: bool):
    """Return a Decimal for the first/last number token in ``s`` (or None)."""
    s = _normalize(s)
    tokens = [t for t in _NUMBER_RE.findall(s) if re.search(r"\d", t)]
    if not tokens:
        return None
    candidates = tokens if prefer_first else list(reversed(tokens))
    for tok in candidates:
        val = _to_decimal(tok)
        if val is not None:
            return val
    return None


def extract_number(raw: str):
    """Extract the single intended numeric answer from a raw response.

    Returns a ``Decimal`` or ``None`` when no number can be found.
    """
    if not raw:
        return None
    text = _strip_think(raw)

    boxed = _last_boxed_content(text)
    if boxed is not None:
        # The box holds the final answer; take its first numeric token.
        val = _extract_number(boxed, prefer_first=True)
        if val is not None:
            return val

    # Fall back to the last number in the body, ignoring echoed fractions.
    body = _strip_fractions(text)
    return _extract_number(body, prefer_first=False)


def parse_response(raw: str, correct, variant: str):
    """
    Parse the raw model response, classify it, and compute error if any.
    Returns (parsed, classification, error).
    """
    num = extract_number(raw)
    if num is None:
        return None, "NaN", None
    try:
        if variant.startswith("int"):
            # accept float-formatted ints (e.g. "15.0", "15.") and sci notation
            parsed = int(num)
            error = parsed - correct
        else:
            parsed = num.quantize(Decimal("0.0000"))
            error = parsed - correct
        if parsed == correct:
            return parsed, "Correct", None
        # Deviate
        error_val = abs(error)
        if variant.startswith("int"):
            error_out = error_val
        else:
            error_out = error_val.quantize(Decimal("0.0000"))
        return parsed, "Deviate", str(error_out)
    except Exception:
        return None, "NaN", None
