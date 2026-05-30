# llm_arithmetic

An evaluatiation harness for Large Language Models (LLMs) testing performance in basic arithmetic operations (addition, subtraction, multiplication, division) across varying number lengths (aka depth) and data types (integer, fixed-point denotaed as float). 

E.g. integer at depth 2:
```
Compute the following and reply with just the numeric result (no explanation):
   23 + 48
```

E.g. float at depth 5:
```
Compute the following and reply with just the numeric result (no explanation):
   82248.19 * 96362.66
```

## Results (Depth >= 5)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Model                                      ┃ Trials ┃ Correct % ┃    NaN % ┃  Dev % ┃ Comp. Tok. ┃     Cost ┃   Avg Error (Dev) ┃ Avg Error (Dev&Corr) ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ o3-2025-04-16-medium                       │    480 │    99.79% │  0.0000% │  0.21% │  1,102,422 │ $44.2534 │         899.5261% │              1.8740% │
│ o3-2025-04-16-low                          │    480 │    98.96% │  0.0000% │  1.04% │    660,546 │ $26.5784 │          19.9138% │              0.2074% │
│ o4-mini-2025-04-16-high                    │    480 │    98.75% │  0.0000% │  1.25% │  2,080,507 │  $9.1714 │          16.5531% │              0.2069% │
│ o4-mini-2025-04-16-medium                  │    480 │    97.08% │  0.0000% │  2.92% │  1,110,603 │  $4.9039 │           0.0025% │              0.0001% │
│ o4-mini-2025-04-16-medium-4k               │    480 │    93.54% │  0.0000% │  6.46% │  1,083,780 │  $6.7416 │           0.0010% │              0.0001% │
│ o4-mini-2025-04-16-low                     │    480 │    88.96% │  0.0000% │ 11.04% │    575,871 │  $2.5510 │           0.9589% │              0.1059% │
│ o1-2024-12-17                              │    480 │    84.79% │  0.0000% │ 15.21% │  2,252,918 │  $0.0000 │           1.4108% │              0.2146% │
│ deepseek-r1                                │    480 │    84.58% │  0.0000% │ 15.42% │  1,462,524 │  $3.2104 │        2703.1648% │            416.7379% │
│ magistral-small-2506                       │    480 │    79.17% │  0.0000% │ 20.83% │  7,038,890 │ $10.5683 │ 10204147409.7149% │     2125864043.6906% │
│ openreasoning-nemotron-14b@q6_k            │    480 │    77.50% │  0.2083% │ 22.29% │  7,700,131 │  $0.0000 │         218.2303% │             48.7487% │
│ claude-sonnet-4-20250514-thinking16000     │    480 │    76.04% │  0.0000% │ 23.96% │  1,332,908 │ $20.0859 │        1737.7871% │            416.3448% │
│ o3-mini-2025-01-31-medium                  │    480 │    75.21% │  0.0000% │ 24.79% │    945,716 │  $4.1784 │           1.4465% │              0.3586% │
│ grok-3-mini-beta-high                      │    480 │    73.12% │  0.0000% │ 26.88% │      2,702 │  $0.0062 │         827.5804% │            222.4122% │
│ qwen3-32b@cerebras-thinking                │    480 │    72.50% │  2.7083% │ 24.79% │  2,767,460 │  $2.2229 │   840317055.4887% │      214127900.6491% │
│ deepseek-r1-4k                             │    480 │    71.04% │  0.0000% │ 28.96% │    620,371 │  $2.3284 │         734.2407% │            212.6239% │
│ qwen3-32b@iq4_xs-ctx16k-thinking           │    480 │    67.08% │  0.0000% │ 32.92% │  3,499,454 │  $0.0000 │        5497.1987% │           1809.4946% │
│ o1-mini-2024-09-12                         │    480 │    66.67% │  0.0000% │ 33.33% │    572,960 │  $7.6179 │        6950.9400% │           2316.9800% │
│ qwen3-14b@q8_0-ctx4k-thinking              │    480 │    66.46% │  0.0000% │ 33.54% │  2,338,564 │  $0.0000 │        9487.6573% │           3182.3184% │
│ qwen3-14b@iq4_xs-ctx32k-thinking           │    480 │    66.04% │  0.0000% │ 33.96% │  2,552,276 │  $0.0000 │        7999.0824% │           2716.3551% │
│ claude-opus-4-20250514-thinking16000       │    480 │    65.83% │  0.0000% │ 34.17% │    396,158 │ $30.1734 │        1831.0146% │            625.5967% │
│ qwen3-14b@iq4_xs-ctx4k-thinking            │    480 │    65.21% │  0.0000% │ 34.79% │  2,245,910 │  $0.0000 │    71780977.6286% │       24973798.4666% │
│ o3-mini-2025-01-31-low                     │    480 │    65.21% │  0.0000% │ 34.79% │    284,738 │  $1.2701 │           1.8431% │              0.6412% │
│ qwen3-14b@q4_k_m-ctx4k-thinking            │    480 │    64.79% │  0.0000% │ 35.21% │  2,334,475 │  $0.0000 │        3774.0861% │           1328.7928% │
│ magistral-small-2506@q6_k                  │    480 │    63.75% │  0.0000% │ 36.25% │  7,334,062 │  $0.0000 │     6325478.9973% │        2292986.1365% │
│ claude-sonnet-3.7-20250219-thinking4096    │    480 │    57.08% │ 18.9583% │ 23.96% │  1,214,269 │ $18.3064 │         888.6875% │            262.7225% │
│ gemini-2.5-pro-preview-03-25               │    480 │    55.83% │  0.0000% │ 44.17% │      5,517 │  $0.0780 │          20.6015% │              9.0990% │
│ qwen3-14b@iq4_xs-ctx32k-thinking-4k        │    480 │    55.21% │  0.0000% │ 44.79% │    710,967 │  $0.0000 │        1029.8199% │            461.2735% │
│ gemini-2.5-pro                             │    480 │    54.37% │  0.0000% │ 45.62% │      5,380 │  $0.0766 │           5.8447% │              2.6666% │
│ claude-sonnet-3.7-20250219-4k              │    480 │    52.50% │  0.0000% │ 47.50% │      4,213 │  $5.8709 │        2211.3448% │           1050.3888% │
│ xai/grok-3-mini-beta                       │    480 │    51.46% │  0.0000% │ 48.54% │      2,511 │  $0.0061 │         913.5788% │            443.4664% │
│ gemini-2.5-flash                           │    480 │    51.04% │  0.0000% │ 48.96% │      5,663 │  $0.0061 │         485.5657% │            237.7249% │
│ claude-sonnet-3.7-20250219                 │    480 │    51.04% │  0.0000% │ 48.96% │      4,147 │  $0.1142 │        1302.4374% │            637.6517% │
│ claude-opus-4-20250514                     │    480 │    50.42% │  0.0000% │ 49.58% │      4,169 │  $0.5727 │        5036.8948% │           2497.4603% │
│ gemini-2.5-flash-preview-04-17-thinking    │    480 │    50.42% │  0.0000% │ 49.58% │    521,284 │  $0.3156 │          28.1963% │             13.9807% │
│ claude-sonnet-4-20250514                   │    480 │    50.00% │  0.0000% │ 50.00% │      4,125 │  $0.1139 │          15.8273% │              7.9137% │
│ gemini-2.5-flash-preview-04-17-thinking    │    480 │    49.79% │  0.2083% │ 50.00% │    310,022 │  $1.0879 │         481.6932% │            241.3494% │
│ claude-3.5-haiku                           │    480 │    49.58% │  0.0000% │ 50.42% │      3,987 │  $0.0298 │        3350.0137% │           1688.9653% │
│ gpt-4.5-preview-2025-02-27                 │    480 │    49.58% │  0.0000% │ 50.42% │      2,647 │  $1.6072 │          17.6847% │              8.9160% │
│ gpt-4.1-2025-04-14-4k                      │    480 │    49.17% │  0.0000% │ 50.83% │      2,688 │  $5.1630 │          24.5982% │             12.5041% │
│ gemini-2.5-flash-preview-04-17-no-thinking │    480 │    48.54% │  0.0000% │ 51.46% │      5,238 │  $0.0060 │          30.5656% │             15.7286% │
│ gpt-4.1-2025-04-14                         │    480 │    48.12% │  0.0000% │ 51.88% │      2,729 │  $0.0686 │        7283.2956% │           3778.2096% │
│ qwen3-32b@iq4_xs-ctx16k                    │    480 │    47.29% │  0.0000% │ 52.71% │      7,132 │  $0.0000 │          57.9904% │             30.5658% │
│ qwen3-32b@cerebras                         │    480 │    46.46% │  0.0000% │ 53.54% │      7,457 │  $0.0164 │         443.5643% │            237.4917% │
│ deepseek-r1-distill-qwen-14b@iq4_xs        │    480 │    46.46% │  0.0000% │ 53.54% │  1,113,604 │  $0.0000 │      395994.0440% │         212021.8111% │
│ mistral-medium-2505                        │    480 │    46.46% │  0.0000% │ 53.54% │      7,591 │  $0.0231 │  1348332206.2925% │      721919535.4524% │
│ qwen3-14b@iq4_xs-ctx32k                    │    480 │    45.83% │  0.0000% │ 54.17% │      7,533 │  $0.0000 │   384696055.8359% │      208377030.2445% │
│ gpt-4-0613                                 │    480 │    41.04% │  0.0000% │ 58.96% │      2,450 │  $0.6310 │      363520.1249% │         214325.4070% │
│ gpt-4.1-nano-2025-04-14                    │    480 │    38.96% │  0.0000% │ 61.04% │      2,841 │  $0.0027 │      685997.4621% │         418744.2841% │
│ gpt-35-turbo-0125                          │    480 │    36.88% │  0.0000% │ 63.12% │      2,438 │  $0.0117 │          67.3884% │             42.5390% │
│ gpt-35-turbo-1106                          │    480 │    34.38% │  0.0000% │ 65.62% │      2,560 │  $0.0119 │         407.6765% │            267.5377% │
│ gpt-4o-mini-2024-07-18                     │    480 │    32.29% │  0.0000% │ 67.71% │      2,862 │  $0.0041 │          63.9555% │             43.3032% │
│ claude-2.1                                 │    480 │    16.67% │  0.0000% │ 83.33% │      2,661 │  $0.0000 │        5506.2324% │           4588.5270% │
│ o4-mini-2025-04-16-medium-1k               │    102 │   100.00% │  0.0000% │  0.00% │     37,700 │  $0.2560 │           0.0000% │              0.0000% │
│ o4-mini-2025-04-16-medium-2k               │     60 │   100.00% │  0.0000% │  0.00% │     27,946 │  $0.2440 │           0.0000% │              0.0000% │
│ phi-4-reasoning-plus@q8_0                  │     51 │    96.08% │  0.0000% │  3.92% │    416,681 │  $0.0000 │           4.2126% │              0.1652% │
│ magistral-medium-2506                      │    230 │    95.22% │  2.1739% │  2.61% │  2,072,825 │  $4.1491 │          16.6715% │              0.4446% │
│ phi-4-reasoning-plus@q4_k_s                │    148 │    87.84% │  0.0000% │ 12.16% │  1,369,685 │  $0.0000 │          48.2243% │              5.8651% │
│ deepseek-r1-0528                           │    176 │    86.36% │  0.0000% │ 13.64% │  1,150,323 │  $2.5219 │         104.9243% │             14.3079% │
└────────────────────────────────────────────┴────────┴───────────┴──────────┴────────┴────────────┴──────────┴───────────────────┴──────────────────────┘
```

**Notes:**
- Results were re-parsed with the improved parser (see [REPORT_parsing_fix.md](REPORT_parsing_fix.md)): the previous parser only accepted a number at the very end of a reply and discarded ~3,000 legitimate answers (mostly `\boxed{...}`, thousands separators and scientific notation) as `NaN`. Reasoning models are the big movers — e.g. `magistral-small-2506` went from 3.33% to 79.17% and `openreasoning-nemotron-14b@q6_k` from 1.46% to 77.50% Correct.
- `Correct %` are responses that got succesfully parsed as numbers (pasrsing is not strict and makes a best attempt to extract the answer — `\boxed{}` first, otherwise the last number in the reply) and were accurate to every digit
- `NaN %` (Not-a-Number) - number was not parsed from LLM reply
- `Dev %` - parsed number is not accurate and there's a non-zero deviation from the true value
- `Avg Error (Dev)` is the deciating numbers (not accurate to the point), i.e. it is an avg error for all responses that got into `Dev %` category
- `Avg Error (Dev&Corr)` is the average error for all responses that parsed as numbers (`Correct %` and `Dev %` cateories), i.e. it is an overall error estimate including both accurate responses and responses that deviated
- Resulta exclude depths <5 since shorter numbers are generally easy for LLMs and many get close to 100% accuracy
- `grok-3-mini-beta-high` reasoning tokens wre not registered, price is incorrect
- Some models have incomplete trials (at the bottom)
- Some models have been tested locally quantized as signified by @ symbol (e.g. qwen3-14b@iq4_xs is 4 bit quant)
- Models that have reasoning/thinking mode and when tested in this mode have `-thinking` in the name
- Qwen3 14B when tested in thinking mode used to produce A LOT OF tokens, hense I had to retest with increased context size (e.g. `ctx32k` means 32k context windows in LM Studio settings)
- Some models have been tested with extra context, i.e. before the computation prompt there is a small talk dialog included above - denotes as `-1k`, `-2k` and `-4k` at the end of the model name. Testing how perormance can dropm with more text in the context which is closer to real life scenarious.
  

## Features

- Supports integer and fixed-point "float" arithmetic
- Parametrized digit depths (2 to 10)
- Generates random test operands with controlled valid inputs (e.g., integer division always yields integer results)
- Prompts LLMs via `litellm`
- Parses numeric responses with a tolerant extractor: takes the `\boxed{...}` answer if present, otherwise the last number in the reply, while stripping markdown, thousands separators, scientific notation, `<think>` blocks, etc. (see [REPORT_parsing_fix.md](REPORT_parsing_fix.md))
- Classifies results as `Correct` (exact match), `Deviate`, or `NaN` (not a number in model response)
- Records token usage and costs
- Outputs per-trial JSONL

## Testing Rules and Constraints

- **Integer operands**:
  - Depth *d*: values from $10^{d-1}$ to $10^d - 1$
  - `int_div` pairs are constructed so division yields an exact integer result

- **Floating-point operands**:
  - Inputs have two decimal places (fixed-point scale 0.01)
  - Depth *d*: base magnitudes from $10^{d-1}$ to $10^d - 1$ before scaling
  - Addition/Subtraction: exact two decimal places
  - Multiplication/Division: results quantized to four decimal places

- **Prompting & parsing**:
  - Models receive: "Compute the following and reply with just the numeric result (no explanation)"
  - The answer is extracted leniently (`\boxed{...}` first, else the last number, after normalising markdown / separators / scientific notation), but the value comparison is exact. Classified as:
    - `Correct`: exact match to the computed result
    - `Deviate`: numeric but off – logged with absolute error
    - `NaN`: non-numeric or parsing failure (no number anywhere in the reply)

- **Trials & depths**:
  - Default 10 trials per variant/depth combination
  - Default depths: 2 through 10 digits

- **Outputs**:
  - Per-trial JSONL written to the configured results directory
  - A summary record appended to `aggregate.jsonl` at project root

## Considerations
- Models often ignore the "just the numeric result" instruction and wrap the answer in markup (`\boxed{}`, markdown, code fences, prose). The parser now sees through this — it extracts the intended number rather than discarding the reply as `NaN` (see [REPORT_parsing_fix.md](REPORT_parsing_fix.md)). The *value* match is still strict (`Correct` = exact to every digit); a separate metric for raw format adherence could still be tracked.
- After the parsing fix, `NaN` reflects genuine non-answers — empty replies or reasoning truncated before a final answer — not discarded-but-correct numbers. (Pre-fix, most `NaN` for models like `grok-3-mini-beta-high` and the `\boxed{}`-heavy reasoning models were actually correct answers being thrown away.)
- Floats are actually decimals - i.e. fixed point math using numbers with 2 decimals after the decimal separator
- Float's also are longer at same depths - i.e. int at 4 is exactly 4 digits (e.g. 1234), float at 4 deptyh is 6 digits (1234.56) - that's a bug that made it into a feature

## Installation

1. Clone the repository

```bash
 git clone <repo_url>
 cd llm_arithmetic
```

2. Install dependencies

```bash
 pip install -r requirements.txt
```

3. Set your API key environment variable

```bash
 export OPENAI_API_KEY="your-api-key"
```

Alternatively, create a `.env` file at the project root with the following content:

```env
 OPENAI_API_KEY=your-api-key
 MODEL=openai/gpt-4o
```

## Usage

Run the evaluation suite with `python run.py` (or `uv run run.py`). Trials are saved under `results/`. Use scripts in `scripts/` to analyze and visualize results.

Configure the run via CLI flags or by editing `DEFAULTS` at the top of `run.py`. CLI overrides `.env` for `--model`. Example:

```bash
uv run run.py --model openai/gpt-4o --model-alias=gpt4o-baseline --trials=5 --depths=2-6
```

See `uv run run.py --help` for all options (`--reasoning-effort`, `--litellm-params`, `--resume-file`, etc.).

## Reports & Analysis

Each run writes one JSONL file per model under `results/`, with one record per trial
(operands, `correct`, `raw_response`, `classification`, `error`, tokens, cost). All
reporting reads those files, so you can re-render any view at any time without
re-querying the models. The scripts are configured via the globals at the top of each
file (e.g. `MIN_DEPTH`, `MODEL`, `RESULTS_DIR`) rather than CLI flags.

### Overview & per-model breakdown — `scripts/report.py`

```bash
python scripts/report.py
```

Prints the **Models Overview** table shown above (Correct / NaN / Dev %, tokens, cost,
average error), a **Verification** table (per-variant trial counts, flags incomplete
runs), and a **per-model card** for every run with a per-variant (`int_add`, `float_div`, …)
breakdown. Edit the globals at the top to focus:

- `MIN_DEPTH = 5` — only include trials at depth ≥ N (set `None` for all depths).
- `MODEL = "o3-2025-04-16-medium"` — show only the detailed card for one model.
- `SORT_BY` — `MODEL`, `CORRECT`, `NAN`, or `DEV`.

### Heatmaps

```bash
python scripts/heatmap.py            # per-model grid: variant × depth, colour-coded
python scripts/heatmap_accuracy.py   # cross-model: accuracy by depth, sorted
```

- `heatmap.py` renders, for each model, a variant × depth grid for `accuracy`,
  `deviate_rate` and `nan_rate` (`METRICS`, `MODEL_FILTER` at the top).
- `heatmap_accuracy.py` renders one row per model with accuracy per depth
  (`MIN_DEPTH`/`MAX_DEPTH`, default 6–10) to show where each model breaks down as
  numbers get longer.

### Re-parsing historical results — `scripts/recalc_results.py`

Re-runs the current parser over every stored `raw_response` and compares against the
classification saved at collection time — useful after any parser change.

```bash
python scripts/recalc_results.py            # analysis only: transition matrix,
                                            # before/after counts, recalc_summary.json
python scripts/recalc_results.py --write     # also rewrite results/*.jsonl in place
                                            # (.bak backups) so report.py reflects it
```

See [REPORT_parsing_fix.md](REPORT_parsing_fix.md) for the failure-mode breakdown and the
before/after comparison this produced.

### Recomputing cost — `scripts/recalcute_prices.py`

Recomputes per-trial `cost` for a results file from `data/models_metadata.csv` (set
`TRIAL_FILE`/`METADATA_FILE` at the top), e.g. after correcting a model's token prices.