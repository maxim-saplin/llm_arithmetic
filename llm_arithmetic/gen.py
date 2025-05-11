import random
from decimal import Decimal, getcontext

# Set sufficient precision for Decimal operations
getcontext().prec = 28


def gen_int_pair(variant: str, depth: int):
    """
    Generate a pair of integers for the given variant and digit depth.
    For int_div, guarantees an integer quotient.
    """
    low = 10 ** (depth - 1)
    high = 10 ** depth - 1
    if variant == "int_div":
        divisor = random.randint(low, high)
        quotient = random.randint(low, high)
        dividend = divisor * quotient
        return dividend, divisor
    lhs = random.randint(low, high)
    rhs = random.randint(low, high)
    return lhs, rhs


def gen_float_pair(variant: str, depth: int):
    """
    Generate a pair of fixed-point floats (Decimal) for the given variant and digit depth.
    Two decimal places.
    """
    low = 10 ** (depth - 1)
    high = 10 ** depth - 1
    scale = Decimal("0.01")
    int_low = low * 100
    int_high = high * 100
    if variant == "float_div":
        divisor_int = random.randint(int_low, int_high)
        quotient_int = random.randint(int_low, int_high)
        dividend_int = divisor_int * quotient_int
        dividend = Decimal(dividend_int) * scale
        divisor = Decimal(divisor_int) * scale
        return dividend, divisor
    lhs_int = random.randint(int_low, int_high)
    rhs_int = random.randint(int_low, int_high)
    lhs = Decimal(lhs_int) * scale
    rhs = Decimal(rhs_int) * scale
    return lhs, rhs


def compute_correct(variant: str, lhs, rhs):
    """
    Compute the correct result for the given operands and variant.
    """
    if variant.startswith("int"):
        if variant.endswith("add"):
            return lhs + rhs
        if variant.endswith("sub"):
            return lhs - rhs
        if variant.endswith("mul"):
            return lhs * rhs
        if variant.endswith("div"):
            return lhs // rhs
    else:
        # float variants using Decimal
        if variant.endswith("add"):
            return lhs + rhs
        if variant.endswith("sub"):
            return lhs - rhs
        if variant.endswith("mul"):
            return lhs * rhs
        if variant.endswith("div"):
            result = lhs / rhs
            # quantize to two decimal places
            return result.quantize(Decimal("0.00"))
    raise ValueError(f"Unknown variant: {variant}") 