from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List

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

@dataclass
class Aggregate:
    model: str
    date: str
    trials_per_cell: int
    cells: Dict[str, Dict[str, Any]]
    overall: Dict[str, Any]
    per_category: Dict[str, Dict[str, Any]] 