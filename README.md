# llm_arithmetic

A Python harness to evaluate Large Language Models (LLMs) on basic arithmetic operations (addition, subtraction, multiplication, division) across varying numeric depths (number of difits in numbers) and data types (integer, fixed-point denotaed as float). 

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

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Model                      ┃ Date             ┃ Trials ┃ Accuracy ┃ NaN % ┃  Dev % ┃      Cost ┃                Avg Error ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ gpt-4.1-nano-2025-04-14    │ 2025-05-11_16-04 │    720 │   46.94% │ 0.56% │ 52.50% │ $0.003862 │  64817201461194223990.77 │
│ gpt-4o-mini-2024-07-18     │ 2025-05-11_16-17 │    720 │   41.67% │ 0.14% │ 58.19% │ $0.005842 │     31324590308701428.93 │
│ gpt-4.1-2025-04-14         │ 2025-05-11_16-17 │    720 │   54.72% │ 0.00% │ 45.28% │ $0.097138 │ 109050039997375543453.57 │
│ claude-3-7-sonnet-20250219 │ 2025-05-11_19-06 │    720 │   58.19% │ 0.00% │ 41.81% │ $0.000000 │       980825444089298.35 │
│ o4-mini-2025-04-16-medium  │ 2025-05-11_16-17 │    720 │   98.06% │ 0.00% │  1.94% │ $5.281132 │               1703248.79 │
└────────────────────────────┴──────────────────┴────────┴──────────┴───────┴────────┴───────────┴──────────────────────────┘
╭─────────────────────────────────────────────────── Overall (gpt-4.1-nano-2025-04-14 @ 2025-05-11_16-04) ───────────────────────────────────────────────────╮
│ Total Trials: 720                                                                                                                                          │
│ Accuracy: 46.94%                                                                                                                                           │
│ Nan Rate: 0.56%                                                                                                                                            │
│ Deviate Rate: 52.50%                                                                                                                                       │
│ Total Prompt Tokens: 23387                                                                                                                                 │
│ Total Completion Tokens: 3808                                                                                                                              │
│ Total Cost: $0.003862                                                                                                                                      │
│ Avg Error: 64817201461194223990.77                                                                                                                         │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
                      Per-Variant Summary (gpt-4.1-nano-2025-04-14)                      
┏━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Variant   ┃ Trials ┃ Accuracy ┃ NaN % ┃  Dev % ┃                Avg Error ┃      Cost ┃
┡━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ int_add   │     90 │   83.33% │ 0.00% │ 16.67% │               4961559.33 │ $0.000396 │
│ int_sub   │     90 │   84.44% │ 0.00% │ 15.56% │            3245540414.29 │ $0.000402 │
│ int_mul   │     90 │   15.56% │ 0.00% │ 84.44% │ 317105073338485779164.96 │ $0.000465 │
│ int_div   │     90 │   22.22% │ 2.22% │ 75.56% │         3101371847568.34 │ $0.000436 │
│ float_add │     90 │   81.11% │ 1.11% │ 17.78% │              54394325.94 │ $0.000505 │
│ float_sub │     90 │   86.67% │ 0.00% │ 13.33% │             202900457.50 │ $0.000511 │
│ float_mul │     90 │    1.11% │ 0.00% │ 98.89% │   4504394084998604609.43 │ $0.000594 │
│ float_div │     90 │    1.11% │ 1.11% │ 97.78% │       287432949078445.35 │ $0.000554 │
└───────────┴────────┴──────────┴───────┴────────┴──────────────────────────┴───────────┘
╭─────────────────────────────────────────────────── Overall (gpt-4o-mini-2024-07-18 @ 2025-05-11_16-17) ────────────────────────────────────────────────────╮
│ Total Trials: 720                                                                                                                                          │
│ Accuracy: 41.67%                                                                                                                                           │
│ Nan Rate: 0.14%                                                                                                                                            │
│ Deviate Rate: 58.19%                                                                                                                                       │
│ Total Prompt Tokens: 23389                                                                                                                                 │
│ Total Completion Tokens: 3889                                                                                                                              │
│ Total Cost: $0.005842                                                                                                                                      │
│ Avg Error: 31324590308701428.93                                                                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
                     Per-Variant Summary (gpt-4o-mini-2024-07-18)                      
┏━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Variant   ┃ Trials ┃ Accuracy ┃ NaN % ┃   Dev % ┃             Avg Error ┃      Cost ┃
┡━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ int_add   │     90 │   68.89% │ 0.00% │  31.11% │            7934467.86 │ $0.000591 │
│ int_sub   │     90 │   81.11% │ 0.00% │  18.89% │           97670007.82 │ $0.000604 │
│ int_mul   │     90 │   13.33% │ 0.00% │  86.67% │   8231400172439852.56 │ $0.000695 │
│ int_div   │     90 │   15.56% │ 1.11% │  83.33% │          579547205.75 │ $0.000679 │
│ float_add │     90 │   67.78% │ 0.00% │  32.22% │           12108137.97 │ $0.000749 │
│ float_sub │     90 │   85.56% │ 0.00% │  14.44% │          105207413.77 │ $0.000763 │
│ float_mul │     90 │    0.00% │ 0.00% │ 100.00% │ 138699446154805931.48 │ $0.000908 │
│ float_div │     90 │    1.11% │ 0.00% │  98.89% │        44099950880.26 │ $0.000852 │
└───────────┴────────┴──────────┴───────┴─────────┴───────────────────────┴───────────┘
╭───────────────────────────────────────────────────── Overall (gpt-4.1-2025-04-14 @ 2025-05-11_16-17) ──────────────────────────────────────────────────────╮
│ Total Trials: 720                                                                                                                                          │
│ Accuracy: 54.72%                                                                                                                                           │
│ Nan Rate: 0.00%                                                                                                                                            │
│ Deviate Rate: 45.28%                                                                                                                                       │
│ Total Prompt Tokens: 23391                                                                                                                                 │
│ Total Completion Tokens: 3663                                                                                                                              │
│ Total Cost: $0.097138                                                                                                                                      │
│ Avg Error: 109050039997375543453.57                                                                                                                        │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
                         Per-Variant Summary (gpt-4.1-2025-04-14)                         
┏━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Variant   ┃ Trials ┃ Accuracy ┃ NaN % ┃   Dev % ┃                Avg Error ┃      Cost ┃
┡━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ int_add   │     90 │  100.00% │ 0.00% │   0.00% │                     0.00 │ $0.010255 │
│ int_sub   │     90 │   97.78% │ 0.00% │   2.22% │                 50050.00 │ $0.010447 │
│ int_mul   │     90 │   21.11% │ 0.00% │  78.89% │  13603952203332597929.17 │ $0.011567 │
│ int_div   │     90 │   26.67% │ 0.00% │  73.33% │              14795546.94 │ $0.010805 │
│ float_add │     90 │   95.56% │ 0.00% │   4.44% │                   525.25 │ $0.012747 │
│ float_sub │     90 │   94.44% │ 0.00% │   5.56% │                200040.40 │ $0.012971 │
│ float_mul │     90 │    2.22% │ 0.00% │  97.78% │ 393004913934939855678.19 │ $0.014611 │
│ float_div │     90 │    0.00% │ 0.00% │ 100.00% │           71468086719.00 │ $0.013735 │
└───────────┴────────┴──────────┴───────┴─────────┴──────────────────────────┴───────────┘
╭───────────────────────────────────────────────── Overall (claude-3-7-sonnet-20250219 @ 2025-05-11_19-06) ──────────────────────────────────────────────────╮
│ Total Trials: 720                                                                                                                                          │
│ Accuracy: 58.19%                                                                                                                                           │
│ Nan Rate: 0.00%                                                                                                                                            │
│ Deviate Rate: 41.81%                                                                                                                                       │
│ Total Prompt Tokens: 25190                                                                                                                                 │
│ Total Completion Tokens: 5783                                                                                                                              │
│ Total Cost: $0.000000                                                                                                                                      │
│ Avg Error: 980825444089298.35                                                                                                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
                  Per-Variant Summary (claude-3-7-sonnet-20250219)                  
┏━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Variant   ┃ Trials ┃ Accuracy ┃ NaN % ┃  Dev % ┃           Avg Error ┃      Cost ┃
┡━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ int_add   │     90 │  100.00% │ 0.00% │  0.00% │                0.00 │ $0.000000 │
│ int_sub   │     90 │  100.00% │ 0.00% │  0.00% │                0.00 │ $0.000000 │
│ int_mul   │     90 │   24.44% │ 0.00% │ 75.56% │  137855905180695.47 │ $0.000000 │
│ int_div   │     90 │   35.56% │ 0.00% │ 64.44% │     156376739750.31 │ $0.000000 │
│ float_add │     90 │   98.89% │ 0.00% │  1.11% │                0.01 │ $0.000000 │
│ float_sub │     90 │   98.89% │ 0.00% │  1.11% │           100000.00 │ $0.000000 │
│ float_mul │     90 │    6.67% │ 0.00% │ 93.33% │ 3402863765988536.45 │ $0.000000 │
│ float_div │     90 │    1.11% │ 0.00% │ 98.89% │      52032860100.37 │ $0.000000 │
└───────────┴────────┴──────────┴───────┴────────┴─────────────────────┴───────────┘
╭────────────────────────────────────────────────── Overall (o4-mini-2025-04-16-medium @ 2025-05-11_16-17) ──────────────────────────────────────────────────╮
│ Total Trials: 720                                                                                                                                          │
│ Accuracy: 98.06%                                                                                                                                           │
│ Nan Rate: 0.00%                                                                                                                                            │
│ Deviate Rate: 1.94%                                                                                                                                        │
│ Total Prompt Tokens: 22665                                                                                                                                 │
│ Total Completion Tokens: 1194591                                                                                                                           │
│ Total Cost: $5.281132                                                                                                                                      │
│ Avg Error: 1703248.79                                                                                                                                      │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
              Per-Variant Summary (o4-mini-2025-04-16-medium)              
┏━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Variant   ┃ Trials ┃ Accuracy ┃ NaN % ┃  Dev % ┃  Avg Error ┃      Cost ┃
┡━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ int_add   │     90 │  100.00% │ 0.00% │  0.00% │       0.00 │ $0.153595 │
│ int_sub   │     90 │  100.00% │ 0.00% │  0.00% │       0.00 │ $0.135951 │
│ int_mul   │     90 │  100.00% │ 0.00% │  0.00% │       0.00 │ $0.656951 │
│ int_div   │     90 │  100.00% │ 0.00% │  0.00% │       0.00 │ $0.892257 │
│ float_add │     90 │  100.00% │ 0.00% │  0.00% │       0.00 │ $0.093368 │
│ float_sub │     90 │  100.00% │ 0.00% │  0.00% │       0.00 │ $0.116002 │
│ float_mul │     90 │   98.89% │ 0.00% │  1.11% │ 1099989.00 │ $1.330437 │
│ float_div │     90 │   85.56% │ 0.00% │ 14.44% │ 1749653.39 │ $1.902571 │
└───────────┴────────┴──────────┴───────┴────────┴────────────┴───────────┘
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
