from dataclasses import dataclass
from typing import Any, List

# Define the 8 variants: int and float operations
VARIANTS = [
    "int_add", "int_sub", "int_mul", "int_div",
    "float_add", "float_sub", "float_mul", "float_div"
]

@dataclass
class Trial:
    model: str
    variant: str
    depth: int
    operands: List[Any]
    correct: Any
    raw_response: str
    parsed: Any
    classification: str
    error: Any
    prompt_tokens: int
    completion_tokens: int
    cost: float
    timestamp: str
    attempts: int
    failed_to_get_reply: bool
    extra_context: int = 0