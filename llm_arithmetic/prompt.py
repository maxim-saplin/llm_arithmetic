# Mapping of operation names to symbols
OP_SYMBOLS = {
    "add": "+",
    "sub": "-",
    "mul": "×",
    "div": "÷"
}

def make_prompt(lhs, op_symbol, rhs):
    """
    Generate the prompt string for the LLM.
    """
    return (
        "Compute the following and reply with just the numeric result (no explanation):\n"
        f"   {lhs} {op_symbol} {rhs}"
    ) 