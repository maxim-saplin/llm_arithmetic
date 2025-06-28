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
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Model                                      ┃ Trials ┃ Correct % ┃    NaN % ┃  Dev % ┃ Comp. Tok. ┃       Cost ┃ Avg Error (Dev) ┃ Avg Error (Dev&Corr) ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ o3-2025-04-16-low                          │    480 │    98.96% │  0.0000% │  1.04% │  660546.00 │ $26.578380 │         19.914% │               0.207% │
│ o4-mini-2025-04-16-high                    │    480 │    98.75% │  0.0000% │  1.25% │ 2080507.00 │  $9.171449 │         16.553% │               0.207% │
│ o4-mini-2025-04-16-medium                  │    480 │    97.08% │  0.0000% │  2.92% │ 1110603.00 │  $4.903872 │          0.002% │               0.000% │
│ o4-mini-2025-04-16-medium-4k               │    480 │    93.54% │  0.0000% │  6.46% │ 1083780.00 │  $6.741561 │          0.001% │               0.000% │
│ o4-mini-2025-04-16-low                     │    480 │    88.96% │  0.0000% │ 11.04% │  575871.00 │  $2.551050 │          0.959% │               0.106% │
│ deepseek-r1                                │    480 │    84.17% │  0.2083% │ 15.62% │ 1462524.00 │  $3.210413 │       2669.789% │             418.025% │
│ claude-sonnet-4-20250514-thinking16000     │    480 │    76.04% │  0.0000% │ 23.96% │ 1332908.00 │ $20.085939 │       1740.396% │             416.970% │
│ o3-mini-2025-01-31-medium                  │    480 │    75.21% │  0.0000% │ 24.79% │  945716.00 │  $4.178371 │          2.287% │               0.567% │
│ grok-3-mini-beta-high                      │    480 │    71.88% │  1.2500% │ 26.88% │    2702.00 │  $0.006156 │        827.580% │             225.228% │
│ deepseek-r1-4k                             │    480 │    70.00% │  0.0000% │ 30.00% │  620371.00 │  $2.328380 │        712.913% │             213.874% │
│ qwen3-32b@cerebras-thinking                │    480 │    69.58% │  5.6250% │ 24.79% │ 2767460.00 │  $2.222864 │  840317057.169% │       220745540.404% │
│ qwen3-14b@q8_0-ctx4k-thinking              │    480 │    66.25% │  0.2083% │ 33.54% │ 2338564.00 │  $0.000000 │       9492.622% │            3190.631% │
│ o1-mini-2024-09-12                         │    480 │    66.04% │  0.0000% │ 33.96% │  572960.00 │  $7.617905 │       6825.446% │            2317.808% │
│ claude-opus-4-20250514-thinking16000       │    480 │    65.83% │  0.0000% │ 34.17% │  396158.00 │ $30.173415 │       1831.015% │             625.597% │
│ qwen3-14b@iq4_xs-ctx32k-thinking           │    480 │    65.83% │  0.8333% │ 33.33% │ 2552276.00 │  $0.000000 │       8152.815% │            2740.442% │
│ qwen3-32b@iq4_xs-ctx16k-thinking           │    480 │    65.62% │  3.7500% │ 30.63% │ 3499454.00 │  $0.000000 │       5227.605% │            1663.329% │
│ o3-mini-2025-01-31-low                     │    480 │    65.21% │  0.0000% │ 34.79% │  284738.00 │  $1.270064 │          5.435% │               1.891% │
│ qwen3-14b@iq4_xs-ctx4k-thinking            │    480 │    65.00% │  0.4167% │ 34.58% │ 2245910.00 │  $0.000000 │   72213401.589% │        25078294.276% │
│ qwen3-14b@q4_k_m-ctx4k-thinking            │    480 │    64.79% │  0.0000% │ 35.21% │ 2334475.00 │  $0.000000 │       3769.350% │            1327.125% │
│ claude-sonnet-3.7-20250219-thinking4096    │    480 │    57.08% │ 18.9583% │ 23.96% │ 1214269.00 │ $18.306354 │        889.557% │             262.980% │
│ gemini-2.5-pro-preview-03-25               │    480 │    55.83% │  0.0000% │ 44.17% │    5517.00 │  $0.078019 │         20.602% │               9.099% │
│ qwen3-14b@iq4_xs-ctx32k-thinking-4k        │    480 │    55.21% │  0.2083% │ 44.58% │  710967.00 │  $0.000000 │        988.474% │             441.615% │
│ gemini-2.5-pro                             │    480 │    54.37% │  0.0000% │ 45.62% │    5380.00 │  $0.076647 │          5.845% │               2.667% │
│ claude-sonnet-3.7-20250219-4k              │    480 │    52.50% │  0.0000% │ 47.50% │    4213.00 │  $5.870871 │       2217.925% │            1053.514% │
│ xai/grok-3-mini-beta                       │    480 │    51.46% │  0.0000% │ 48.54% │    2511.00 │  $0.006060 │        913.579% │             443.466% │
│ gemini-2.5-flash                           │    480 │    51.04% │  0.0000% │ 48.96% │    5663.00 │  $0.006140 │        485.566% │             237.725% │
│ claude-sonnet-3.7-20250219                 │    480 │    51.04% │  0.0000% │ 48.96% │    4147.00 │  $0.114204 │       1302.437% │             637.652% │
│ claude-opus-4-20250514                     │    480 │    50.42% │  0.0000% │ 49.58% │    4169.00 │  $0.572685 │       5037.315% │            2497.669% │
│ gemini-2.5-flash-preview-04-17-thinking    │    480 │    50.42% │  0.2083% │ 49.38% │  521284.00 │  $0.315585 │         27.894% │              13.801% │
│ claude-sonnet-4-20250514                   │    480 │    50.00% │  0.0000% │ 50.00% │    4125.00 │  $0.113868 │         20.410% │              10.205% │
│ gemini-2.5-flash-preview-04-17-thinking    │    480 │    49.79% │  0.2083% │ 50.00% │  310022.00 │  $1.087891 │        481.693% │             241.349% │
│ claude-3.5-haiku                           │    480 │    49.58% │  0.0000% │ 50.42% │    3987.00 │  $0.029816 │       3351.666% │            1689.798% │
│ gpt-4.5-preview-2025-02-27                 │    480 │    49.58% │  0.0000% │ 50.42% │    2647.00 │  $1.607175 │         24.709% │              12.457% │
│ gpt-4.1-2025-04-14-4k                      │    480 │    48.54% │  0.0000% │ 51.46% │    2688.00 │  $5.163010 │         25.919% │              13.337% │
│ gemini-2.5-flash-preview-04-17-no-thinking │    480 │    48.54% │  0.0000% │ 51.46% │    5238.00 │  $0.005956 │         30.566% │              15.729% │
│ gpt-4.1-2025-04-14                         │    480 │    48.12% │  0.0000% │ 51.88% │    2729.00 │  $0.068629 │       7284.099% │            3778.626% │
│ qwen3-32b@cerebras                         │    480 │    46.46% │  0.0000% │ 53.54% │    7457.00 │  $0.016398 │         63.979% │              34.255% │
│ mistral-medium-2505                        │    480 │    46.25% │  2.5000% │ 51.25% │    7591.00 │  $0.023119 │  514401943.813% │       270390765.337% │
│ qwen3-32b@iq4_xs-ctx16k                    │    480 │    46.04% │  1.0417% │ 52.92% │    7132.00 │  $0.000000 │         63.271% │              33.833% │
│ qwen3-14b@iq4_xs-ctx32k                    │    480 │    45.21% │  1.6667% │ 53.12% │    7533.00 │  $0.000000 │  392239118.901% │       211908846.016% │
│ gpt-4-0613                                 │    480 │    41.04% │  0.0000% │ 58.96% │    2450.00 │  $0.631020 │     362466.402% │          213704.150% │
│ gpt-4.1-nano-2025-04-14                    │    480 │    38.54% │  0.4167% │ 61.04% │    2841.00 │  $0.002749 │     686001.894% │          420499.069% │
│ gpt-35-turbo-0125                          │    480 │    35.62% │  0.6250% │ 63.75% │    2438.00 │  $0.011725 │         43.177% │              27.698% │
│ gpt-35-turbo-1106                          │    480 │    33.96% │  0.2083% │ 65.83% │    2560.00 │  $0.011907 │        409.261% │             269.993% │
│ gpt-4o-mini-2024-07-18                     │    480 │    32.29% │  0.0000% │ 67.71% │    2862.00 │  $0.004137 │         64.570% │              43.719% │
│ claude-2.1                                 │    480 │    13.33% │  0.0000% │ 86.67% │    2661.00 │  $0.000000 │        174.584% │             151.306% │
│ deepseek-r1-distill-qwen-14b@iq4_xs        │    480 │    10.21% │ 70.2083% │ 19.58% │ 1113604.00 │  $0.000000 │        163.793% │             107.668% │
│ magistral-small-2506                       │    480 │     3.33% │ 96.2500% │  0.42% │ 7038890.00 │ $10.568254 │          0.783% │               0.087% │
│ magistral-small-2506@q6_k                  │    480 │     0.42% │ 99.5833% │  0.00% │ 7334062.00 │  $0.000000 │          0.000% │               0.000% │
└────────────────────────────────────────────┴────────┴───────────┴──────────┴────────┴────────────┴────────────┴─────────────────┴──────────────────────┘
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
