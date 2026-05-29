"""Extensive tests for the response parser (llm_arithmetic.parse).

Organised by the failure modes observed in the real result corpus:
  - backward compatibility (legacy-accepted strings unchanged)
  - \\boxed{} extraction (the dominant failure mode: ~2977 dropped answers)
  - thousands separators, scientific notation, markdown, ellipsis, brackets
  - trailing commentary / junk tokens
  - fractions (must NOT mistake an echoed operand for the answer)
  - genuine non-answers (must stay NaN)
  - classification & error correctness (Correct / Deviate / NaN)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from decimal import Decimal
import pytest

from llm_arithmetic.parse import (
    parse_response,
    extract_number,
    LEGACY_NUMBER_REGEX,
)


def D(x):
    return Decimal(str(x))


# --------------------------------------------------------------------------
# extract_number: raw -> Decimal (independent of classification)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("raw, expected", [
    # plain numbers
    ("300", D("300")),
    ("-5", D("-5")),
    ("106.59", D("106.59")),
    ("15.0", D("15.0")),
    ("300.", D("300")),
    (".5", D("0.5")),
    ("+42", D("42")),

    # \boxed{}
    (r"\boxed{179}", D("179")),
    ("$$\n\\boxed{428770819727}\n$$", D("428770819727")),
    (r"The final answer is $\boxed{179}$. (extra text)", D("179")),
    (r"**Final Answer:** The sum is \(\boxed{146}\).", D("146")),
    (r"\boxed{-548168} \]  However, strictly...", D("-548168")),
    (r"\boxed{19119214.00}", D("19119214.00")),
    # last boxed wins
    (r"\boxed{1}\n... reconsidering ...\n\boxed{140}", D("140")),
    # boxed beats later free-text number (boxed is the final-answer marker)
    (r"\boxed{138}\n\nActually wait, 999", D("138")),
    # nested latex grouping braces inside the box
    (r"\boxed{540{,}760{,}136}", D("540760136")),
    # scientific notation inside the box
    (r"\boxed{1.1795759779 \times 10^8}", D("117957597.79")),

    # thousands separators
    ("11,026,217,783", D("11026217783")),
    ("The result is:\n\n**11,026,217,783**", D("11026217783")),
    ("4865776 - 3845999 = **1,019,777**", D("1019777")),
    ("316,291,", D("316291")),
    ("approximately 8,897,533,458.52", D("8897533458.52")),

    # scientific notation in free text
    ("1.23e5", D("123000")),
    ("3.412041225×10¹⁷", D("3.412041225E17")),
    ("3.412041225 * 10^17", D("3.412041225E17")),

    # markdown / ellipsis
    ("3401.738693...  \n**3401.738693**", D("3401.738693")),
    ("929791.047...", D("929791.047")),
    ("50623250184177448869 ÷ 9994036039 = **5065**.", D("5065")),

    # brackets / json / currency
    ("[1796.89]", D("1796.89")),
    ('```json\n{\n  "result": "39301321418602425300"\n}\n```', D("39301321418602425300")),
    ("$1,250.00", D("1250.00")),

    # uncertainty notation stripped
    ("90250000.000102(4)", D("90250000.000102")),

    # trailing junk tokens after a valid number
    ("5674390730.626starttime", D("5674390730.626")),
    ("38228968341822136159. registratiResultsController", D("38228968341822136159")),
    ("1716.973 net profit", D("1716.973")),

    # trailing words (old parser anchored to end-of-string -> would fail)
    ("300 is the sum", D("300")),
    ("The answer: 300.\n\nGreat!", D("300")),

    # think blocks
    ("<think>\n12345 scratch work\n</think>\n300", D("300")),

    # markdown bold adjacent to an answer starting with "10" must NOT be read
    # as scientific notation ("** 10400" is not "× 10^400").
    ("The sum is 10,400.30.\n\n**Answer:** 10400.30", D("10400.30")),
    ("The result is 29 multiplied by 36 is 1044.\n\n**Answer:** 1044", D("1044")),
    ("**104307487.25**", D("104307487.25")),
    # genuine multiplication-as-text without an exponent marker is not sci
    ("5 * 10400", D("10400")),
])
def test_extract_number(raw, expected):
    assert extract_number(raw) == expected


@pytest.mark.parametrize("raw", [
    "",
    None,
    "no number here",
    "чении أص misleading tým LabourDU",
    "\\sigma liberated-G male slic Cors ultimately lower",
    # truncated reasoning with no closing tag and no final answer
    "<think>\nLet me compute 5 + 5 which is 10, then 10 + 2 ...",
    # bare echoed fraction: operands restated, nothing computed
    "To solve:\n\n$$\n\\frac{25262843262596985745}{3990169273}\n$$",
])
def test_extract_number_none(raw):
    assert extract_number(raw) is None


def test_fraction_with_explicit_result_is_used():
    # The fraction is stripped; the stated approximate result is what we keep.
    raw = "$$\n\\frac{22455794635897170802.58}{295202407.34} \\approx 76069000000\n$$"
    assert extract_number(raw) == D("76069000000")


# --------------------------------------------------------------------------
# Backward compatibility: anything the legacy regex accepted must parse to the
# same numeric value under the new logic.
# --------------------------------------------------------------------------

LEGACY_OK = [
    "300", "-5", "0", "106.59", "-72.51", "15.0", "300.", "42\n",
    "The answer is 300", "result:\n-1234.5", "2102.5620",
]

@pytest.mark.parametrize("raw", LEGACY_OK)
def test_backward_compatible_with_legacy_regex(raw):
    m = LEGACY_NUMBER_REGEX.search(raw)
    assert m is not None, "test input should be legacy-acceptable"
    legacy_val = Decimal(m.group(1))
    assert extract_number(raw) == legacy_val


# --------------------------------------------------------------------------
# parse_response: classification & error
# --------------------------------------------------------------------------

def test_classify_int_correct():
    parsed, cls, err = parse_response(r"\boxed{428770819727}", 428770819727, "int_mul")
    assert (cls, parsed, err) == ("Correct", 428770819727, None)


def test_classify_int_float_formatted():
    parsed, cls, err = parse_response("15.0", 15, "int_div")
    assert cls == "Correct" and parsed == 15


def test_classify_int_deviate():
    parsed, cls, err = parse_response("301", 300, "int_add")
    assert cls == "Deviate" and parsed == 301 and err == "1"


def test_classify_int_scientific():
    parsed, cls, err = parse_response("3.412041225×10¹⁷", 341204122500000000, "int_mul")
    assert cls == "Correct" and parsed == 341204122500000000


def test_classify_float_correct():
    parsed, cls, err = parse_response("106.59", D("106.59"), "float_add")
    assert cls == "Correct" and parsed == D("106.5900")


def test_classify_float_correct_via_boxed_sci():
    parsed, cls, err = parse_response(r"\boxed{1.1795759779 \times 10^8}", D("117957597.79"), "float_mul")
    assert cls == "Correct" and parsed == D("117957597.7900")


def test_classify_float_deviate_rounded_boxed():
    # model boxed a 2-dp rounded answer; true value differs in the 4th dp
    parsed, cls, err = parse_response(r"\boxed{19119214.00}", D("19119214.0018"), "float_mul")
    assert cls == "Deviate" and parsed == D("19119214.0000") and err == "0.0018"


def test_classify_float_deviate_error_string():
    parsed, cls, err = parse_response("106.58", D("106.59"), "float_add")
    assert cls == "Deviate" and err == "0.0100"


def test_classify_nan_empty():
    assert parse_response("", 5, "int_add") == (None, "NaN", None)


def test_classify_nan_garbage():
    assert parse_response("no digits at all", 5, "int_add") == (None, "NaN", None)


def test_classify_nan_bare_fraction_does_not_grab_operand():
    # Must not classify as Deviate by grabbing the denominator 3990169273.
    raw = "$$\n\\frac{25262843262596985745}{3990169273}\n$$"
    assert parse_response(raw, 6330000000, "int_div") == (None, "NaN", None)


def test_think_block_answer_not_scratch():
    # answer is 300, not the 12345 in scratch work
    parsed, cls, err = parse_response("<think>\n12345 scratch\n</think>\n300", 300, "int_add")
    assert cls == "Correct" and parsed == 300


def test_truncated_think_is_nan():
    # unclosed reasoning with no final answer -> must not extract 10
    assert parse_response("<think>\n5 + 5 = 10 then keep going", 10, "int_add") == (None, "NaN", None)


def test_comma_thousands_correct():
    parsed, cls, err = parse_response("The result is **11,026,217,783**", 11026217783, "int_add")
    assert cls == "Correct" and parsed == 11026217783


def test_negative_via_boxed():
    parsed, cls, err = parse_response(r"\boxed{-5603186868} \]  However...", -5603186868, "int_sub")
    assert cls == "Correct" and parsed == -5603186868
