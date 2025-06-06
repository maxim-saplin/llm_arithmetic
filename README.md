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

## Results (Depth >= 5)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Model                                      ┃ Trials ┃ Correct % ┃  NaN % ┃  Dev % ┃ Comp. Tok. ┃       Cost ┃      Avg Error ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ o4-mini-2025-04-16-medium                  │    480 │    97.08% │  0.00% │  2.92% │ 1110603.00 │  $4.903872 │         0.002% │
│ o4-mini-2025-04-16-medium-4k               │    480 │    93.54% │  0.00% │  6.46% │ 1083780.00 │  $6.741561 │         0.001% │
│ o4-mini-2025-04-16-low                     │    480 │    88.96% │  0.00% │ 11.04% │  575871.00 │  $2.551050 │         0.959% │
│ deepseek-r1                                │    480 │    84.17% │  0.21% │ 15.62% │ 1462524.00 │  $3.210413 │      2669.789% │
│ claude-sonnet-4-20250514-thinking16000     │    480 │    76.04% │  0.00% │ 23.96% │ 1332908.00 │ $20.085939 │      1740.396% │
│ o3-mini-2025-01-31-medium                  │    480 │    75.21% │  0.00% │ 24.79% │  945716.00 │  $4.178371 │         2.287% │
│ grok-3-mini-beta-high                      │    480 │    71.88% │  1.25% │ 26.88% │    2702.00 │  $0.006156 │       827.580% │
│ deepseek-r1-4k                             │    480 │    70.00% │  0.00% │ 30.00% │  620371.00 │  $0.000000 │       712.913% │
│ qwen3-32b@cerebras-thinking                │    480 │    69.58% │  5.62% │ 24.79% │ 2767460.00 │  $0.000000 │ 840317057.169% │
│ qwen3-14b@q8_0-ctx4k-thinking              │    480 │    66.25% │  0.21% │ 33.54% │ 2338564.00 │  $0.000000 │      9492.622% │
│ o1-mini-2024-09-12                         │    480 │    66.04% │  0.00% │ 33.96% │  572960.00 │  $7.617905 │      6825.446% │
│ claude-opus-4-20250514-thinking16000       │    480 │    65.83% │  0.00% │ 34.17% │  396158.00 │  $0.000000 │      1831.015% │
│ qwen3-14b@iq4_xs-ctx32k-thinking           │    480 │    65.83% │  0.83% │ 33.33% │ 2552276.00 │  $0.000000 │      8152.815% │
│ qwen3-32b@iq4_xs-ctx16k-thinking           │    480 │    65.62% │  3.75% │ 30.63% │ 3499454.00 │  $0.000000 │      5227.605% │
│ o3-mini-2025-01-31-low                     │    480 │    65.21% │  0.00% │ 34.79% │  284738.00 │  $1.270064 │         5.435% │
│ qwen3-14b@iq4_xs-ctx4k-thinking            │    480 │    65.00% │  0.42% │ 34.58% │ 2245910.00 │  $0.000000 │  72213401.589% │
│ qwen3-14b@q4_k_m-ctx4k-thinking            │    480 │    64.79% │  0.00% │ 35.21% │ 2334475.00 │  $0.000000 │      3769.350% │
│ claude-sonnet-3.7-20250219-thinking4096    │    480 │    57.08% │ 18.96% │ 23.96% │ 1214269.00 │ $18.306354 │       889.557% │
│ gemini-2.5-pro-preview-03-25               │    480 │    55.83% │  0.00% │ 44.17% │    5517.00 │  $0.078019 │        20.602% │
│ qwen3-14b@iq4_xs-ctx32k-thinking-4k        │    480 │    55.21% │  0.21% │ 44.58% │  710967.00 │  $0.000000 │       988.474% │
│ claude-sonnet-3.7-20250219-4k              │    480 │    52.50% │  0.00% │ 47.50% │    4213.00 │  $0.000000 │      2217.925% │
│ xai/grok-3-mini-beta                       │    480 │    51.46% │  0.00% │ 48.54% │    2511.00 │  $0.006060 │       913.579% │
│ claude-sonnet-3.7-20250219                 │    480 │    51.04% │  0.00% │ 48.96% │    4147.00 │  $0.114204 │      1302.437% │
│ claude-opus-4-20250514                     │    480 │    50.42% │  0.00% │ 49.58% │    4169.00 │  $0.572685 │      5037.315% │
│ gemini-2.5-flash-preview-04-17-thinking    │    480 │    50.42% │  0.21% │ 49.38% │  521284.00 │  $0.315585 │        27.894% │
│ claude-sonnet-4-20250514                   │    480 │    50.00% │  0.00% │ 50.00% │    4125.00 │  $0.113868 │        20.410% │
│ gemini-2.5-flash-preview-04-17-thinking    │    480 │    49.79% │  0.21% │ 50.00% │  310022.00 │  $1.087891 │       481.693% │
│ claude-3.5-haiku                           │    480 │    49.58% │  0.00% │ 50.42% │    3987.00 │  $0.029816 │      3351.666% │
│ gpt-4.5-preview-2025-02-27                 │    480 │    49.58% │  0.00% │ 50.42% │    2647.00 │  $1.607175 │        24.709% │
│ gpt-4.1-2025-04-14-4k                      │    480 │    48.54% │  0.00% │ 51.46% │    2688.00 │  $5.163010 │        25.919% │
│ gemini-2.5-flash-preview-04-17-no-thinking │    480 │    48.54% │  0.00% │ 51.46% │    5238.00 │  $0.005956 │        30.566% │
│ gpt-4.1-2025-04-14                         │    480 │    48.12% │  0.00% │ 51.88% │    2729.00 │  $0.068629 │      7284.099% │
│ qwen3-32b@cerebras                         │    480 │    46.46% │  0.00% │ 53.54% │    7457.00 │  $0.000000 │        63.979% │
│ qwen3-32b@iq4_xs-ctx16k                    │    480 │    46.04% │  1.04% │ 52.92% │    7132.00 │  $0.000000 │        63.271% │
│ qwen3-14b@iq4_xs-ctx32k                    │    480 │    45.21% │  1.67% │ 53.12% │    7533.00 │  $0.000000 │ 392239118.901% │
│ gpt-4-0613                                 │    480 │    41.04% │  0.00% │ 58.96% │    2450.00 │  $0.631020 │    362466.402% │
│ gpt-4.1-nano-2025-04-14                    │    480 │    38.54% │  0.42% │ 61.04% │    2841.00 │  $0.002749 │    686001.894% │
│ gpt-35-turbo-0125                          │    480 │    35.62% │  0.62% │ 63.75% │    2438.00 │  $0.011725 │        43.177% │
│ gpt-35-turbo-1106                          │    480 │    33.96% │  0.21% │ 65.83% │    2560.00 │  $0.011907 │       409.261% │
│ gpt-4o-mini-2024-07-18                     │    480 │    32.29% │  0.00% │ 67.71% │    2862.00 │  $0.004137 │        64.570% │
│ claude-2.1                                 │    480 │    13.33% │  0.00% │ 86.67% │    2661.00 │  $0.000000 │       174.584% │
│ deepseek-r1-distill-qwen-14b@iq4_xs        │    480 │    10.21% │ 70.21% │ 19.58% │ 1113604.00 │  $0.000000 │       163.793% │
└────────────────────────────────────────────┴────────┴───────────┴────────┴────────┴────────────┴────────────┴────────────────┘
```

**Notes:**

- Resulta exclude depths <5 since shorter numbers are generally easy for LLMs and many get close to 100% accuracy
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

Run the evaluation suite with `python run.py`. Get the trials saved under `results/` folder. Use scripts in `scripts/` folder to analyze and visualize the results.
