# llm_arithmetic

<img width="1163" alt="image" src="https://github.com/user-attachments/assets/5128644e-b881-4e4b-821d-4159ca13e10b" />

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
- Outputs per-trial JSONL and updates an aggregate JSONL summary

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
- `grok-3-mini-beta-high` reasoning tokens wre not reghistered, price is incorrect
- It's reasonable to do a non-strict verification, currently there's strict match of response, yet sometimes models do not follow the rules and can wrap correct replies in some markup (e.g. most of NaN results for `grok-3-mini-beta-high` are actully correct) - a separate metric for format adherence can be tracked
- `gemini-2.5-flash-preview-04-17-??thinking` - seems Google AI Studio disregarded the provided htinking params

```
                                                                Models Overview                                                                 
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Model                                      ┃ Date             ┃ Trials ┃ Correct % ┃  NaN % ┃  Dev % ┃       Cost ┃                Avg Error ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ claude-3-7-sonnet-20250219                 │ 2025-05-11_19-06 │    480 │    51.04% │  0.00% │ 48.96% │  $0.114204 │      1256291313492864.50 │
│ claude-3-7-sonnet-20250219-thinking4096    │ 2025-05-11_19-20 │    480 │    57.08% │ 18.96% │ 23.96% │ $18.306354 │    773109131839652992.00 │
│ claude-v3-5-haiku                          │ 2025-05-12_13-40 │    480 │    49.58% │  0.00% │ 50.42% │  $0.029816 │ 309550101099442143232.00 │
│ deepseek-r1                                │ 2025-05-12_13-35 │    480 │    84.17% │  0.21% │ 15.62% │  $3.210413 │ 154039382084726128640.00 │
│ gemini-2.5-flash-preview-04-17-no-thinking │ 2025-05-14_18-38 │    480 │    48.54% │  0.00% │ 51.46% │  $0.005956 │    274503737851614944.00 │
│ gemini-2.5-flash-preview-04-17-thinking    │ 2025-05-12_12-28 │    480 │    49.79% │  0.21% │ 50.00% │  $1.087891 │   1673196184364916480.00 │
│ gemini-2.5-pro-preview-03-25               │ 2025-05-12_13-31 │    480 │    55.83% │  0.00% │ 44.17% │  $0.078019 │    489039253224715008.00 │
│ gpt-4.1-2025-04-14                         │ 2025-05-11_16-17 │    480 │    48.12% │  0.00% │ 51.88% │  $0.068629 │ 142772341522668371968.00 │
│ gpt-4.1-nano-2025-04-14                    │ 2025-05-11_16-04 │    480 │    38.54% │  0.42% │ 61.04% │  $0.002750 │  83620826458468040704.00 │
│ gpt-4.5-preview-2025-02-27                 │ 2025-05-14_08-57 │    480 │    49.58% │  0.00% │ 50.42% │  $1.607175 │   1076427701424673536.00 │
│ gpt-4o-mini-2024-07-18                     │ 2025-05-11_16-17 │    480 │    32.29% │  0.00% │ 67.71% │  $0.004137 │     40384625659291632.00 │
│ grok-3-mini-beta                           │ 2025-05-11_19-53 │    480 │    51.46% │  0.00% │ 48.54% │  $0.006060 │ 269577858689370947584.00 │
│ grok-3-mini-beta-high                      │ 2025-05-12_06-52 │    480 │    71.88% │  1.25% │ 26.88% │  $0.006156 │   3211229392017596416.00 │
│ o1-mini-2024-09-12                         │ 2025-05-14_08-57 │    480 │    66.04% │  0.00% │ 33.96% │  $7.617905 │    659421940438043904.00 │
│ o3-mini-2025-01-31-low                     │ 2025-05-14_08-55 │    480 │    65.21% │  0.00% │ 34.79% │  $1.270064 │    301685096061138304.00 │
│ o3-mini-2025-01-31-medium                  │ 2025-05-14_08-56 │    480 │    75.21% │  0.00% │ 24.79% │  $4.178371 │    305476632529746112.00 │
│ o4-mini-2025-04-16-low                     │ 2025-05-14_08-54 │    480 │    88.96% │  0.00% │ 11.04% │  $2.551050 │            6298383348.51 │
│ o4-mini-2025-04-16-medium                  │ 2025-05-11_16-17 │    480 │    97.08% │  0.00% │  2.92% │  $4.903872 │               1703248.79 │
└────────────────────────────────────────────┴──────────────────┴────────┴───────────┴────────┴────────┴────────────┴──────────────────────────┘
```

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
