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
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Model                                      ┃ Trials ┃ Correct % ┃    NaN % ┃  Dev % ┃ Comp. Tok. ┃     Cost ┃ Avg Error (Dev) ┃ Avg Error (Dev&Corr) ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ o3-2025-04-16-medium                       │    480 │    99.79% │  0.0000% │  0.21% │  1,102,422 │ $44.2534 │       899.5261% │              1.8740% │
│ o3-2025-04-16-low                          │    480 │    98.96% │  0.0000% │  1.04% │    660,546 │ $26.5784 │        19.9138% │              0.2074% │
│ o4-mini-2025-04-16-high                    │    480 │    98.75% │  0.0000% │  1.25% │  2,080,507 │  $9.1714 │        16.5531% │              0.2069% │
│ o4-mini-2025-04-16-medium                  │    480 │    97.08% │  0.0000% │  2.92% │  1,110,603 │  $4.9039 │         0.0025% │              0.0001% │
│ o4-mini-2025-04-16-medium-4k               │    480 │    93.54% │  0.0000% │  6.46% │  1,083,780 │  $6.7416 │         0.0010% │              0.0001% │
│ o4-mini-2025-04-16-low                     │    480 │    88.96% │  0.0000% │ 11.04% │    575,871 │  $2.5510 │         0.9589% │              0.1059% │
│ o1-2024-12-17                              │    480 │    84.79% │  0.0000% │ 15.21% │  2,252,918 │  $0.0000 │        10.9997% │              1.6729% │
│ deepseek-r1                                │    480 │    84.17% │  0.2083% │ 15.62% │  1,462,524 │  $3.2104 │      2669.7892% │            418.0254% │
│ claude-sonnet-4-20250514-thinking16000     │    480 │    76.04% │  0.0000% │ 23.96% │  1,332,908 │ $20.0859 │      1740.3955% │            416.9698% │
│ o3-mini-2025-01-31-medium                  │    480 │    75.21% │  0.0000% │ 24.79% │    945,716 │  $4.1784 │         2.2868% │              0.5669% │
│ grok-3-mini-beta-high                      │    480 │    71.88% │  1.2500% │ 26.88% │      2,702 │  $0.0062 │       827.5804% │            225.2276% │
│ deepseek-r1-4k                             │    480 │    70.00% │  0.0000% │ 30.00% │    620,371 │  $2.3284 │       712.9126% │            213.8738% │
│ qwen3-32b@cerebras-thinking                │    480 │    69.58% │  5.6250% │ 24.79% │  2,767,460 │  $2.2229 │ 840317057.1686% │      220745540.4041% │
│ qwen3-14b@q8_0-ctx4k-thinking              │    480 │    66.25% │  0.2083% │ 33.54% │  2,338,564 │  $0.0000 │      9492.6219% │           3190.6308% │
│ o1-mini-2024-09-12                         │    480 │    66.04% │  0.0000% │ 33.96% │    572,960 │  $7.6179 │      6825.4456% │           2317.8076% │
│ claude-opus-4-20250514-thinking16000       │    480 │    65.83% │  0.0000% │ 34.17% │    396,158 │ $30.1734 │      1831.0146% │            625.5967% │
│ qwen3-14b@iq4_xs-ctx32k-thinking           │    480 │    65.83% │  0.8333% │ 33.33% │  2,552,276 │  $0.0000 │      8152.8152% │           2740.4421% │
│ qwen3-32b@iq4_xs-ctx16k-thinking           │    480 │    65.62% │  3.7500% │ 30.63% │  3,499,454 │  $0.0000 │      5227.6050% │           1663.3289% │
│ o3-mini-2025-01-31-low                     │    480 │    65.21% │  0.0000% │ 34.79% │    284,738 │  $1.2701 │         5.4352% │              1.8910% │
│ qwen3-14b@iq4_xs-ctx4k-thinking            │    480 │    65.00% │  0.4167% │ 34.58% │  2,245,910 │  $0.0000 │  72213401.5894% │       25078294.2758% │
│ qwen3-14b@q4_k_m-ctx4k-thinking            │    480 │    64.79% │  0.0000% │ 35.21% │  2,334,475 │  $0.0000 │      3769.3499% │           1327.1253% │
│ claude-sonnet-3.7-20250219-thinking4096    │    480 │    57.08% │ 18.9583% │ 23.96% │  1,214,269 │ $18.3064 │       889.5570% │            262.9796% │
│ gemini-2.5-pro-preview-03-25               │    480 │    55.83% │  0.0000% │ 44.17% │      5,517 │  $0.0780 │        20.6015% │              9.0990% │
│ qwen3-14b@iq4_xs-ctx32k-thinking-4k        │    480 │    55.21% │  0.2083% │ 44.58% │    710,967 │  $0.0000 │       988.4740% │            441.6147% │
│ gemini-2.5-pro                             │    480 │    54.37% │  0.0000% │ 45.62% │      5,380 │  $0.0766 │         5.8447% │              2.6666% │
│ claude-sonnet-3.7-20250219-4k              │    480 │    52.50% │  0.0000% │ 47.50% │      4,213 │  $5.8709 │      2217.9249% │           1053.5143% │
│ xai/grok-3-mini-beta                       │    480 │    51.46% │  0.0000% │ 48.54% │      2,511 │  $0.0061 │       913.5788% │            443.4664% │
│ gemini-2.5-flash                           │    480 │    51.04% │  0.0000% │ 48.96% │      5,663 │  $0.0061 │       485.5657% │            237.7249% │
│ claude-sonnet-3.7-20250219                 │    480 │    51.04% │  0.0000% │ 48.96% │      4,147 │  $0.1142 │      1302.4374% │            637.6517% │
│ claude-opus-4-20250514                     │    480 │    50.42% │  0.0000% │ 49.58% │      4,169 │  $0.5727 │      5037.3148% │           2497.6686% │
│ gemini-2.5-flash-preview-04-17-thinking    │    480 │    50.42% │  0.2083% │ 49.38% │    521,284 │  $0.3156 │        27.8937% │             13.8013% │
│ claude-sonnet-4-20250514                   │    480 │    50.00% │  0.0000% │ 50.00% │      4,125 │  $0.1139 │        20.4099% │             10.2049% │
│ gemini-2.5-flash-preview-04-17-thinking    │    480 │    49.79% │  0.2083% │ 50.00% │    310,022 │  $1.0879 │       481.6932% │            241.3494% │
│ claude-3.5-haiku                           │    480 │    49.58% │  0.0000% │ 50.42% │      3,987 │  $0.0298 │      3351.6664% │           1689.7985% │
│ gpt-4.5-preview-2025-02-27                 │    480 │    49.58% │  0.0000% │ 50.42% │      2,647 │  $1.6072 │        24.7086% │             12.4573% │
│ gpt-4.1-2025-04-14-4k                      │    480 │    48.54% │  0.0000% │ 51.46% │      2,688 │  $5.1630 │        25.9187% │             13.3373% │
│ gemini-2.5-flash-preview-04-17-no-thinking │    480 │    48.54% │  0.0000% │ 51.46% │      5,238 │  $0.0060 │        30.5656% │             15.7286% │
│ gpt-4.1-2025-04-14                         │    480 │    48.12% │  0.0000% │ 51.88% │      2,729 │  $0.0686 │      7284.0986% │           3778.6261% │
│ qwen3-32b@cerebras                         │    480 │    46.46% │  0.0000% │ 53.54% │      7,457 │  $0.0164 │        63.9790% │             34.2554% │
│ mistral-medium-2505                        │    480 │    46.25% │  2.5000% │ 51.25% │      7,591 │  $0.0231 │ 514401943.8127% │      270390765.3374% │
│ qwen3-32b@iq4_xs-ctx16k                    │    480 │    46.04% │  1.0417% │ 52.92% │      7,132 │  $0.0000 │        63.2709% │             33.8333% │
│ qwen3-14b@iq4_xs-ctx32k                    │    480 │    45.21% │  1.6667% │ 53.12% │      7,533 │  $0.0000 │ 392239118.9010% │      211908846.0164% │
│ gpt-4-0613                                 │    480 │    41.04% │  0.0000% │ 58.96% │      2,450 │  $0.6310 │    362466.4024% │         213704.1498% │
│ gpt-4.1-nano-2025-04-14                    │    480 │    38.54% │  0.4167% │ 61.04% │      2,841 │  $0.0027 │    686001.8943% │         420499.0691% │
│ gpt-35-turbo-0125                          │    480 │    35.62% │  0.6250% │ 63.75% │      2,438 │  $0.0117 │        43.1767% │             27.6983% │
│ gpt-35-turbo-1106                          │    480 │    33.96% │  0.2083% │ 65.83% │      2,560 │  $0.0119 │       409.2614% │            269.9929% │
│ gpt-4o-mini-2024-07-18                     │    480 │    32.29% │  0.0000% │ 67.71% │      2,862 │  $0.0041 │        64.5698% │             43.7192% │
│ claude-2.1                                 │    480 │    13.33% │  0.0000% │ 86.67% │      2,661 │  $0.0000 │       174.5843% │            151.3064% │
│ deepseek-r1-distill-qwen-14b@iq4_xs        │    480 │    10.21% │ 70.2083% │ 19.58% │  1,113,604 │  $0.0000 │       163.7932% │            107.6682% │
│ magistral-small-2506                       │    480 │     3.33% │ 96.2500% │  0.42% │  7,038,890 │ $10.5683 │         0.7827% │              0.0870% │
│ magistral-small-2506@q6_k                  │    480 │     0.42% │ 99.5833% │  0.00% │  7,334,062 │  $0.0000 │         0.0000% │              0.0000% │
└────────────────────────────────────────────┴────────┴───────────┴──────────┴────────┴────────────┴──────────┴─────────────────┴──────────────────────┘
```

**Notes:**
- `Correct %` are responses that got succesfully parsed as numbers (pasrsing is not strict and makes a best attempt to extract the last number in response) and were accurate to every digit
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
