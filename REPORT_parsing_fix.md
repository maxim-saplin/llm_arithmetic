# Result-Parsing Fix — Failure Modes, Fix, and Before/After Comparison

## TL;DR

The original response parser only accepted a number that sat at the **very end**
of the model's reply. Any answer wrapped in `\boxed{}`, written with thousands
separators, in scientific notation, in markdown, or followed by a stray word was
silently discarded as `NaN` ("model gave no number"). This penalized the most
capable reasoning models, which almost always present their answer as
`\boxed{…}` followed by commentary.

After the fix, re-parsing the **38,628 stored raw responses** (no models were
re-queried — every record keeps its original `raw_response`):

| Class    | Before            | After             | Δ          |
|----------|-------------------|-------------------|------------|
| Correct  | 24,414  (63.20 %) | 26,898  (69.63 %) | **+2,484** |
| Deviate  | 11,050  (28.61 %) | 11,613  (30.06 %) | +563       |
| **NaN**  | 3,164   (8.19 %)  | **117   (0.30 %)**| **−3,047** |

- **3,055 legitimate answers recovered** from `NaN` (2,370 exactly Correct,
  685 Deviate). That is **96.3 % of all previously-`NaN` records**.
- **0 true regressions** — not one response the old parser scored as `Correct`
  changed class.
- The 117 `NaN` that remain are genuinely unparseable: **98 empty replies,
  16 truncated/unclosed `<think>` blocks, 3 digit-free garbage strings, and
  exactly 0 responses that still contain a recoverable number.**

Reproduce with `python scripts/recalc_results.py` (analysis only) or
`python scripts/recalc_results.py --write` (also rewrites `results/*.jsonl`
in place, creating `.bak` backups so `scripts/report.py` reflects the fix).

---

## 1. Failure modes — why legitimate answers were discarded

The old logic was a single end-anchored regex:

```python
NUMBER_REGEX = re.compile(r"(-?\d+(?:\.\d*)?)\s*$")   # number must be at end
```

Scanning all 3,164 `NaN` records (3,066 of them non-empty) classified the
discarded answers as follows:

| # discarded | Failure mode | Example raw response |
|------------:|--------------|----------------------|
| **2,977** | **`\boxed{}` LaTeX answer** — the de-facto final-answer marker for reasoning models; ends in `}`, so the end-anchor never matched. | `\boxed{179}` · `$$\n\boxed{428770819727}\n$$` · `**Final Answer:** the sum is \(\boxed{146}\).` |
| 21 | **Thousands separators** — commas break `\d+`, so only the last 3 digits (or nothing) matched. | `11,026,217,783` · `**1,019,777**` |
| 19 | **Scientific notation** — `×10ⁿ`, `\times 10^n`, superscripts. | `3.412041225×10¹⁷` |
| 7 | **Markdown emphasis** around the number. | `**3401.738693**` |
| 3 | **Trailing ellipsis** (rounded value). | `929791.047...` |
| 33 | **Trailing word / token after the number** — explanation, stray token, or a code fence. | `1716.973 net profit` · `5674390730.626starttime` · `[1796.89]` |
| 3 | **Genuinely unparseable** (no digits). | non-Latin garbage |
| 2 | **Bare fraction** (operands echoed, nothing computed). | `\frac{25262843262596985745}{3990169273}` |
| 98 | **Empty reply** (API error / no content). | `""` |

The dominant mode — by two orders of magnitude — was `\boxed{}`. It hit
reasoning models hardest: e.g. `magistral-small-2506` lost **688/720** trials to
`NaN`, `deepseek-r1-distill-qwen-14b` lost **510/720**.

---

## 2. The fix

`llm_arithmetic/parse.py` now extracts the *intended* answer with a small,
layered, priority-ordered strategy (`extract_number`):

1. **`\boxed{…}` (highest priority).** The content of the **last** box wins —
   this is the explicit "final answer" convention used by reasoning models.
   Brace-aware matching handles LaTeX grouping such as `\boxed{540{,}760{,}136}`,
   and scientific notation inside the box (`\boxed{1.18 \times 10^8}`).
2. **Last number in the body, otherwise.** This matches the project's stated
   "extract the last number in response" philosophy, but with a far more capable
   recognizer.

Normalization applied before number matching:

- `<think>…</think>` blocks are removed — **including an unclosed trailing one**,
  because a reply truncated mid-reasoning contains no final answer (it must not
  be mined for a stray number).
- LaTeX fractions `\frac{A}{B}` are **stripped**, so an echoed operand
  (numerator/denominator) is never mistaken for a computed answer.
- Thousands separators (`,` between a digit and a 3-digit group) are removed.
- Scientific notation is converted to `e`-notation, but **only in unambiguous
  forms** that carry an explicit exponent marker — a superscript (`×10¹⁷`) or a
  caret (`× 10^17`) — and only when a real mantissa precedes the `×`. This was
  important: an earlier version mis-read markdown like `**Answer:** 10400` as
  `× 10^400` and dropped the leading "10". The recalculation caught this; the
  rule was tightened and the regression eliminated (see §4).
- Markdown/code/currency decorations (`*`, `` ` ``, `$`, `\(`, `\[`) are dropped.
- Scientific uncertainty notation (`90250000.000102(4)`) is trimmed.
- Unicode superscripts (`¹⁷`) map to ASCII.

The classification and error logic (Correct / Deviate / NaN, int-vs-float
quantization to 4 dp) is **unchanged** — only number *extraction* improved.
The original end-anchored regex is retained as `LEGACY_NUMBER_REGEX` and used by
the test suite to assert backward compatibility.

---

## 3. Validation methodology

Because every trial record persists its `raw_response`, the fix is validated by
**re-parsing the historical corpus** rather than re-running any model
(`scripts/recalc_results.py`). For each of the 38,628 records it reconstructs
the stored `correct` value (int or 4-dp Decimal), re-runs `parse_response`, and
diffs the new classification against the one stored at collection time.

Two properties are required of a valid fix:
- **Recall:** previously-`NaN` answers that are in fact numeric become parsed.
- **Precision / non-regression:** nothing the old parser already scored as
  `Correct` is broken.

Both hold (§4).

---

## 4. Before / after comparison

### Overall transition matrix (old class → new class)

```
old → new                  count
--------------------------------
Correct → Correct          24414   (unchanged)
Deviate → Deviate          10928   (unchanged)
NaN     → Correct           2370   ← recovered, exact
NaN     → Deviate            685   ← recovered, deviating
Deviate → Correct            114   ← de-grouped thousands fixed a wrong parse
NaN     → NaN                109   (genuine non-answers)
Deviate → NaN                  8   ← truncated-reasoning relabel (see below)
--------------------------------
TOTAL                      38628
```

- **NaN → Correct/Deviate (3,055):** the recovered answers. Examples:
  - `\boxed{103186991625}` → Correct (`qwen3-32b@cerebras-thinking`)
  - `…is:\n\n**1789979983.077**` → Correct (`deepseek-r1`)
  - `38228968341822136159. registratiResultsController` → Deviate (`gpt-35-turbo-0125`)
- **Deviate → Correct (114):** responses like `565,250` and `10,797,720` whose
  thousands separators made the old parser read only `250` / `720`. Fixing the
  grouping turns a spurious Deviate into the correct value (mostly the Claude
  models, which favor comma-grouped output).
- **Deviate → NaN (8) are *not* regressions.** All eight are
  `qwen3-32b@cerebras-thinking` replies with a **32k–42k-char unclosed `<think>`
  block** — truncated reasoning that never produced a final answer. The old
  parser grabbed an arbitrary number from the middle of the reasoning (old
  parsed values were `0, 1, 3, 73708, 78, …` — all wrong, hence Deviate). `NaN`
  ("no answer produced") is the *more* correct label.
- **Correct → Deviate / Correct → NaN: 0.** No legitimate prior result was
  harmed.

### Per-model highlights (largest NaN reductions, all depths)

| Model | Trials | NaN before → after | Correct before → after |
|-------|-------:|--------------------|------------------------|
| magistral-small-2506@q6_k          | 720 | 712 → **0**  | 8 → 541 |
| openreasoning-nemotron-14b@q6_k    | 720 | 705 → **1**  | 14 → 608 |
| magistral-small-2506               | 720 | 688 → **0**  | 30 → 619 |
| deepseek-r1-distill-qwen-14b@iq4_xs| 720 | 510 → **0**  | 100 → 410 |
| magistral-medium-2506              | 350 | 326 → **5**  | 23 → 339 |
| qwen3-32b@iq4_xs-ctx16k-thinking   | 720 | 18 → **0**   | 551 → 558 |
| qwen3-32b@cerebras-thinking        | 720 | 30 → **13**  | 569 → 587 |
| grok-3-mini-beta-high              | 720 | 17 → **0**   | 571 → 588 |
| mistral-medium-2505                | 720 | 15 → **0**   | 377 → 380 |

The headline impact: several reasoning models that the README scored at near-0 %
accuracy were not bad at arithmetic — their answers were being thrown away.
`magistral-small-2506` goes from 8 to **541** correct trials once its
`\boxed{}` answers are read.

### Remaining `NaN` after the fix — proof of completeness

| # | Reason | Recoverable? |
|--:|--------|--------------|
| 98 | Empty reply (no content returned)        | No — nothing to parse |
| 16 | Truncated, unclosed `<think>` (no answer) | No — model never answered |
| 3  | Digit-free garbage text                   | No — contains no number |
| **0** | **Responses still containing a number** | — |

There are **zero** responses left that contain a recoverable digit. Every
parseable answer in the corpus is now parsed; the residual `NaN` rate (0.30 %)
consists entirely of replies that legitimately contain no answer.

---

## 5. Tests

`tests/test_parse.py` — 76 cases covering:

- **Backward compatibility:** every string the legacy regex accepted parses to
  the identical value (asserted against `LEGACY_NUMBER_REGEX`).
- **Each failure mode:** `\boxed{}` (incl. nested braces, sci notation, "last
  box wins", box-beats-later-text), thousands separators, scientific/superscript
  notation, markdown, ellipsis, brackets, JSON, currency, uncertainty notation,
  trailing junk, trailing words.
- **Non-regression guards:** the markdown-`**`-before-`10` false positive;
  plain text multiplication without an exponent marker is not read as sci.
- **Correct vs. Deviate vs. NaN classification** including int/float
  quantization, error strings, truncated-think → NaN, and the fraction guard
  (a bare `\frac{A}{B}` must not be mistaken for the denominator).

```
$ python -m pytest tests/test_parse.py -q
76 passed

$ python -m pytest tests/ -q
79 passed     # incl. the pre-existing runner tests, still green
```

---

## 6. Reproducing / applying

```bash
# Validate (non-destructive): prints the matrix above, writes recalc_summary.json
python scripts/recalc_results.py

# Apply: rewrite results/*.jsonl with recalculated classifications
# (creates <file>.bak backups; afterwards scripts/report.py reflects the fix)
python scripts/recalc_results.py --write
```

Files changed:
- `llm_arithmetic/parse.py` — new layered parser (logic for Correct/Deviate/NaN
  unchanged).
- `tests/test_parse.py` — new, 76 cases.
- `scripts/recalc_results.py` — new recalculation / comparison tool.
