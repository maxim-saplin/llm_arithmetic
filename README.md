# llm_arithmetic

A Python harness to evaluate large language models (LLMs) on basic arithmetic operations (addition, subtraction, multiplication, division) across varying numeric depths and data types.

## Features

- Supports integer and fixed-point float arithmetic
- Parametrized digit depths (2 to 10)
- Generates random test operands with controlled valid inputs (e.g., integer division always yields integer results)
- Prompts LLMs via `litellm.completion`
- Parses numeric responses with regex
- Classifies results as `Correct`, `Deviate`, or `NaN`
- Records token usage and timing
- Outputs per-trial JSONL and updates an aggregate JSONL summary

## Installation

1. Clone the repository

```
git clone <repo_url>
cd llm_arithmetic
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Set your API key environment variable

```
export OPENAI_API_KEY="your-api-key"
```

Alternatively, create a `.env` file at the project root with the following content:

```
OPENAI_API_KEY=your-api-key
MODEL=openai/gpt-4o
```

The script will automatically load environment variables from this file.

## Usage

Run the evaluation suite with:

```