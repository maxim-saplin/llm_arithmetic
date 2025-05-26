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

## Features

- Supports integer and fixed-point "float" arithmetic
- Parametrized digit depths (2 to 10)
- Generates random test operands with controlled valid inputs (e.g., integer division always yields integer results)
- Prompts LLMs via `litellm`
- Parses numeric responses with regex
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
  - Responses are parsed via regex and classified as:
    - `Correct`: exact match to the computed result
    - `Deviate`: numeric but off – logged with absolute error
    - `NaN`: non-numeric or parsing failure

- **Trials & depths**:
  - Default 10 trials per variant/depth combination
  - Default depths: 2 through 10 digits

- **Outputs**:
  - Per-trial JSONL written to the configured results directory
  - A summary record appended to `aggregate.jsonl` at project root

## Results

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Model                                      ┃ Trials ┃ Correct % ┃  NaN % ┃  Dev % ┃ Comp. Tok. ┃     Cost ┃                Avg Error ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ o4-mini-2025-04-16-medium                  │    480 │    97.08% │  0.00% │  2.92% │  1 110 603 │  $4.9039 │               1703248.79 │
│ o4-mini-2025-04-16-medium-4k               │    480 │    93.54% │  0.00% │  6.46% │  1 083 780 │  $6.7416 │          299018226294.22 │
│ o4-mini-2025-04-16-low                     │    480 │    88.96% │  0.00% │ 11.04% │    575 871 │  $2.5510 │            6298383348.51 │
│ deepseek-r1                                │    480 │    84.17% │  0.21% │ 15.62% │  1 462 524 │  $3.2104 │ 154039382084726161408.00 │
│ o3-mini-2025-01-31-medium                  │    480 │    75.21% │  0.00% │ 24.79% │    945 716 │  $4.1784 │    305476632529746112.00 │
│ grok-3-mini-beta-high                      │    480 │    71.88% │  1.25% │ 26.88% │      2 702 │  $0.0062 │   3211229392017596416.00 │
│ deepseek-r1-4k                             │    480 │    70.00% │  0.00% │ 30.00% │    620 371 │  $0.0000 │ 152466712966320324608.00 │
│ qwen3-32b@cerebras-thinking                │    480 │    69.58% │  5.62% │ 24.79% │  2 767 460 │  $0.0000 │ 370037212665444433920.00 │
│ qwen3-14b@q8_0-ctx4k-thinking              │    480 │    66.25% │  0.21% │ 33.54% │  2 338 564 │  $0.0000 │  77885090214417252352.00 │
│ o1-mini-2024-09-12                         │    480 │    66.04% │  0.00% │ 33.96% │    572 960 │  $7.6179 │    659421940438044032.00 │
│ qwen3-14b@iq4_xs-ctx32k-thinking           │    480 │    65.83% │  0.83% │ 33.33% │  2 552 276 │  $0.0000 │   1592549121776785408.00 │
│ qwen3-32b@iq4_xs-ctx16k-thinking           │    480 │    65.62% │  3.75% │ 30.63% │  3 499 454 │  $0.0000 │ 758724839657859055616.00 │
│ o3-mini-2025-01-31-low                     │    480 │    65.21% │  0.00% │ 34.79% │    284 738 │  $1.2701 │    301685096061138176.00 │
│ qwen3-14b@iq4_xs-ctx4k-thinking            │    480 │    65.00% │  0.42% │ 34.58% │  2 245 910 │  $0.0000 │  11234465100846067712.00 │
│ qwen3-14b@q4_k_m-ctx4k-thinking            │    480 │    64.79% │  0.00% │ 35.21% │  2 334 475 │  $0.0000 │  47105668635560574976.00 │
│ claude-3-7-sonnet-20250219-thinking4096    │    480 │    57.08% │ 18.96% │ 23.96% │  1 214 269 │ $18.3064 │    773109131839652992.00 │
│ gemini-2.5-pro-preview-03-25               │    480 │    55.83% │  0.00% │ 44.17% │      5 517 │  $0.0780 │    489039253224715008.00 │
│ qwen3-14b@iq4_xs-ctx32k-thinking-4k        │    480 │    55.21% │  0.21% │ 44.58% │    710 967 │  $0.0000 │   1651308628662385152.00 │
│ claude-3-7-sonnet-20250219-4k              │    480 │    52.50% │  0.00% │ 47.50% │      4 213 │  $0.0000 │    165137356366985824.00 │
│ xai/grok-3-mini-beta                       │    480 │    51.46% │  0.00% │ 48.54% │      2 511 │  $0.0061 │ 269577858689371013120.00 │
│ claude-3-7-sonnet-20250219                 │    480 │    51.04% │  0.00% │ 48.96% │      4 147 │  $0.1142 │      1256291313492864.50 │
│ gemini-2.5-flash-preview-04-17-thinking    │    480 │    50.42% │  0.21% │ 49.38% │    521 284 │  $0.3156 │   1670226792174047744.00 │
│ gemini-2.5-flash-preview-04-17-thinking    │    480 │    49.79% │  0.21% │ 50.00% │    310 022 │  $1.0879 │   1673196184364916480.00 │
│ claude-v3-5-haiku                          │    480 │    49.58% │  0.00% │ 50.42% │      3 987 │  $0.0298 │ 309550101099442143232.00 │
│ gpt-4.5-preview-2025-02-27                 │    480 │    49.58% │  0.00% │ 50.42% │      2 647 │  $1.6072 │   1076427701424673536.00 │
│ gpt-4.1-2025-04-14-4k                      │    480 │    48.54% │  0.00% │ 51.46% │      2 688 │  $5.1630 │       649981598894473.88 │
│ gemini-2.5-flash-preview-04-17-no-thinking │    480 │    48.54% │  0.00% │ 51.46% │      5 238 │  $0.0060 │    274503737851614912.00 │
│ gpt-4.1-2025-04-14                         │    480 │    48.12% │  0.00% │ 51.88% │      2 729 │  $0.0686 │ 142772341522668371968.00 │
│ qwen3-32b@cerebras                         │    480 │    46.46% │  0.00% │ 53.54% │      7 457 │  $0.0000 │   1952977302069369344.00 │
│ qwen3-32b@iq4_xs-ctx16k                    │    480 │    46.04% │  1.04% │ 52.92% │      7 132 │  $0.0000 │   1396884426959831296.00 │
│ qwen3-14b@iq4_xs-ctx32k                    │    480 │    45.21% │  1.67% │ 53.12% │      7 533 │  $0.0000 │   2080539977910410240.00 │
│ gpt-4.1-nano-2025-04-14                    │    480 │    38.54% │  0.42% │ 61.04% │      2 841 │  $0.0027 │  83620826458468040704.00 │
│ gpt-4o-mini-2024-07-18                     │    480 │    32.29% │  0.00% │ 67.71% │      2 862 │  $0.0041 │     40384625659291624.00 │
│ deepseek-r1-distill-qwen-14b@iq4_xs        │    480 │    10.21% │ 70.21% │ 19.58% │  1 113 604 │  $0.0000 │   1957756474590030848.00 │
│ o4-mini-2025-04-16-medium-1k               │    102 │   100.00% │  0.00% │  0.00% │     37 700 │  $0.2560 │                     0.00 │
│ o4-mini-2025-04-16-medium-2k               │     60 │   100.00% │  0.00% │  0.00% │     27 946 │  $0.2440 │                     0.00 │
│ phi-4-reasoning-plus@q8_0                  │     51 │    96.08% │  0.00% │  3.92% │    416 681 │  $0.0000 │                  4800.00 │
│ phi-4-reasoning-plus@q4_k_s                │    148 │    87.84% │  0.00% │ 12.16% │  1 369 685 │  $0.0000 │             147669260.00 │
└────────────────────────────────────────────┴────────┴───────────┴────────┴────────┴────────────┴──────────┴──────────────────────────┘
```

**Notes:**

- `grok-3-mini-beta-high` reasoning tokens wre not registered, price is incorrect
- Some models have incomplete trials (at the bottom)
- Some models have been tested locally quantized as signified by @ symbol (e.g. qwen3-14b@iq4_xs is 4 bit quant)
- Models that have reasoning/thinking mode and when tested in this mode have `-thinking` in the name
- Qwen3 14B when tested in thinking mode used to produce A LOT OF tokens, hense I had to retest with increased context size (e.g. `ctx32k` means 32k context windows in LM Studio settings)
- Some models have been tested with extra context, i.e. before the computation prompt there is a small talk dialog included above - denotes as `-1k`, `-2k` and `-4k` at the end of the model name. Testing how perormance can dropm with more text in the context which is closer to real life scenarious.
  
## Considerations
- It's reasonable to do a non-strict verification, currently there's strict match of response, yet sometimes models do not follow the rules and can wrap correct replies in some markup (e.g. most of NaN results for `grok-3-mini-beta-high` are actully correct) - a separate metric for format adherence can be tracked
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

Run the evaluation suite with:

```bash
 python run.py --model <model> --trials 10 --depths 2 3 4 5 6 7 8 9 10 --output_dir results
```

To resume an interrupted run, point `--resume_file` at the existing trials JSONL:

```bash
 python run.py --model <model> --trials 10 --depths 2 3 4 5 6 7 8 9 10 --output_dir results \
     --resume_file results/<model>_<date>.jsonl
```

By default the harness will retry failed LLM calls 3 times; override with `--retries <N>`:

```bash
 python run.py --model <model> --trials 10 --depths 2 3 --output_dir results \
     --resume_file results/<model>_<date>.jsonl --retries 5
```
