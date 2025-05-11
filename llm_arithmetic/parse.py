import re
from decimal import Decimal

# Regex to extract the last number in the response
NUMBER_REGEX = re.compile(r"(-?\d+(?:\.\d+)?)\s*$")


def parse_response(raw: str, correct, variant: str):
    """
    Parse the raw model response, classify it, and compute error if any.
    Returns (parsed, classification, error).
    """
    match = NUMBER_REGEX.search(raw)
    if not match:
        return None, "NaN", None
    num_str = match.group(1)
    try:
        if variant.startswith("int"):
            parsed = int(num_str)
            error = parsed - correct
        else:
            parsed = Decimal(num_str)
            parsed = parsed.quantize(Decimal("0.00"))
            error = parsed - correct
        if parsed == correct:
            return parsed, "Correct", None
        # Deviate
        error_val = abs(error)
        if variant.startswith("int"):
            error_out = error_val
        else:
            error_out = error_val.quantize(Decimal("0.00"))
        return parsed, "Deviate", str(error_out)
    except Exception:
        return None, "NaN", None 