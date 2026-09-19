FAMILIES = [
    {
        "family_id": "multiply",
        "description": "Return the product of two numbers.",
        "source": """
def solve(a, b):
    return a * b
""",
        "tests": [
            {"args": [2, 3], "expected": 6},
            {"args": [-4, 5], "expected": -20},
            {"args": [0, 9], "expected": 0},
        ],
        "mutations": [
            {
                "id": "missing_def_colon",
                "target": "SYNTAX",
                "old": "def solve(a, b):",
                "new": "def solve(a, b)",
            },
            {
                "id": "unclosed_expression",
                "target": "SYNTAX",
                "old": "return a * b",
                "new": "return (a * b",
            },
            {
                "id": "variable_typo",
                "target": "RUNTIME",
                "old": "return a * b",
                "new": "return aa * b",
            },
            {
                "id": "invalid_index",
                "target": "RUNTIME",
                "old": "return a * b",
                "new": "return a[0] * b",
            },
            {
                "id": "wrong_arithmetic_operator",
                "target": "LOGIC",
                "old": "return a * b",
                "new": "return a + b",
            },
            {
                "id": "off_by_one_operand",
                "target": "LOGIC",
                "old": "return a * b",
                "new": "return a * (b + 1)",
            },
        ],
    },

    {
        "family_id": "factorial",
        "description": "Return the factorial of a non-negative integer.",
        "source": """
def solve(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
""",
        "tests": [
            {"args": [0], "expected": 1},
            {"args": [1], "expected": 1},
            {"args": [5], "expected": 120},
            {"args": [6], "expected": 720},
        ],
        "mutations": [
            {
                "id": "missing_def_colon",
                "target": "SYNTAX",
                "old": "def solve(n):",
                "new": "def solve(n)",
            },
            {
                "id": "missing_loop_colon",
                "target": "SYNTAX",
                "old": "for i in range(1, n + 1):",
                "new": "for i in range(1, n + 1)",
            },
            {
                "id": "loop_variable_typo",
                "target": "RUNTIME",
                "old": "result *= i",
                "new": "result *= ii",
            },
            {
                "id": "index_scalar",
                "target": "RUNTIME",
                "old": "result *= i",
                "new": "result *= i[0]",
            },
            {
                "id": "off_by_one_loop",
                "target": "LOGIC",
                "old": "range(1, n + 1)",
                "new": "range(1, n)",
            },
            {
                "id": "wrong_accumulator_initialization",
                "target": "LOGIC",
                "old": "result = 1",
                "new": "result = 0",
            },
        ],
    },

    {
        "family_id": "palindrome",
        "description": "Return True when the supplied string is a palindrome and False otherwise.",
        "source": """
def solve(text):
    return text == text[::-1]
""",
        "tests": [
            {"args": ["level"], "expected": True},
            {"args": ["python"], "expected": False},
            {"args": ["a"], "expected": True},
            {"args": ["abba"], "expected": True},
        ],
        "mutations": [
            {
                "id": "missing_def_colon",
                "target": "SYNTAX",
                "old": "def solve(text):",
                "new": "def solve(text)",
            },
            {
                "id": "malformed_slice",
                "target": "SYNTAX",
                "old": "return text == text[::-1]",
                "new": "return text == text[::-1",
            },
            {
                "id": "missing_method",
                "target": "RUNTIME",
                "old": "return text == text[::-1]",
                "new": "return text.missing_method() == text[::-1]",
            },
            {
                "id": "out_of_range_index",
                "target": "RUNTIME",
                "old": "return text == text[::-1]",
                "new": "return text[999] == text[::-1]",
            },
            {
                "id": "inverted_comparison",
                "target": "LOGIC",
                "old": "return text == text[::-1]",
                "new": "return text != text[::-1]",
            },
            {
                "id": "incorrect_slice",
                "target": "LOGIC",
                "old": "return text == text[::-1]",
                "new": "return text == text[1::-1]",
            },
        ],
    },

    {
        "family_id": "count_vowels",
        "description": "Return the number of vowels in the supplied string.",
        "source": """
def solve(text):
    return sum(1 for c in text.lower() if c in "aeiou")
""",
        "tests": [
            {"args": ["education"], "expected": 5},
            {"args": ["rhythm"], "expected": 0},
            {"args": ["APPLE"], "expected": 2},
            {"args": [""], "expected": 0},
        ],
        "mutations": [
            {
                "id": "missing_def_colon",
                "target": "SYNTAX",
                "old": "def solve(text):",
                "new": "def solve(text)",
            },
            {
                "id": "unclosed_call",
                "target": "SYNTAX",
                "old": 'return sum(1 for c in text.lower() if c in "aeiou")',
                "new": 'return sum(1 for c in text.lower() if c in "aeiou"',
            },
            {
                "id": "method_typo",
                "target": "RUNTIME",
                "old": "text.lower()",
                "new": "text.lowerr()",
            },
            {
                "id": "undefined_collection",
                "target": "RUNTIME",
                "old": 'c in "aeiou"',
                "new": "c in vowels",
            },
            {
                "id": "missing_vowel",
                "target": "LOGIC",
                "old": '"aeiou"',
                "new": '"aeio"',
            },
            {
                "id": "inverted_membership",
                "target": "LOGIC",
                "old": 'c in "aeiou"',
                "new": 'c not in "aeiou"',
            },
        ],
    },

    {
        "family_id": "find_max",
        "description": "Return the largest value in a non-empty list.",
        "source": """
def solve(values):
    return max(values)
""",
        "tests": [
            {"args": [[3, 9, 2, 5]], "expected": 9},
            {"args": [[-8, -2, -10]], "expected": -2},
            {"args": [[4, 4, 1]], "expected": 4},
        ],
        "mutations": [
            {
                "id": "missing_def_colon",
                "target": "SYNTAX",
                "old": "def solve(values):",
                "new": "def solve(values)",
            },
            {
                "id": "unclosed_call",
                "target": "SYNTAX",
                "old": "return max(values)",
                "new": "return max(values",
            },
            {
                "id": "function_typo",
                "target": "RUNTIME",
                "old": "return max(values)",
                "new": "return maxx(values)",
            },
            {
                "id": "out_of_range_index",
                "target": "RUNTIME",
                "old": "return max(values)",
                "new": "return values[99]",
            },
            {
                "id": "max_min_swap",
                "target": "LOGIC",
                "old": "return max(values)",
                "new": "return min(values)",
            },
            {
                "id": "wrong_sorted_position",
                "target": "LOGIC",
                "old": "return max(values)",
                "new": "return sorted(values)[-2]",
            },
        ],
    },

    {
        "family_id": "average",
        "description": "Return the arithmetic mean of a non-empty list of numbers.",
        "source": """
def solve(values):
    return sum(values) / len(values)
""",
        "tests": [
            {"args": [[2, 4, 6, 8]], "expected": 5.0},
            {"args": [[1, 2]], "expected": 1.5},
            {"args": [[-2, 2]], "expected": 0.0},
        ],
        "mutations": [
            {
                "id": "missing_def_colon",
                "target": "SYNTAX",
                "old": "def solve(values):",
                "new": "def solve(values)",
            },
            {
                "id": "unclosed_len_call",
                "target": "SYNTAX",
                "old": "len(values)",
                "new": "len(values",
            },
            {
                "id": "zero_denominator",
                "target": "RUNTIME",
                "old": "len(values)",
                "new": "len([])",
            },
            {
                "id": "undefined_iterable",
                "target": "RUNTIME",
                "old": "sum(values)",
                "new": "sum(missing_values)",
            },
            {
                "id": "floor_division",
                "target": "LOGIC",
                "old": " / ",
                "new": " // ",
            },
            {
                "id": "wrong_denominator",
                "target": "LOGIC",
                "old": "len(values)",
                "new": "(len(values) + 1)",
            },
        ],
    },

    {
        "family_id": "first_element",
        "description": "Return the first element of a non-empty list.",
        "source": """
def solve(values):
    return values[0]
""",
        "tests": [
            {"args": [[7, 8, 9]], "expected": 7},
            {"args": [["a", "b", "c"]], "expected": "a"},
            {"args": [[42, 10]], "expected": 42},
        ],
        "mutations": [
            {
                "id": "missing_def_colon",
                "target": "SYNTAX",
                "old": "def solve(values):",
                "new": "def solve(values)",
            },
            {
                "id": "unclosed_subscript",
                "target": "SYNTAX",
                "old": "return values[0]",
                "new": "return values[0",
            },
            {
                "id": "off_by_one_index_runtime",
                "target": "RUNTIME",
                "old": "return values[0]",
                "new": "return values[len(values)]",
            },
            {
                "id": "undefined_variable",
                "target": "RUNTIME",
                "old": "return values[0]",
                "new": "return missing_values[0]",
            },
            {
                "id": "last_instead_of_first",
                "target": "LOGIC",
                "old": "return values[0]",
                "new": "return values[-1]",
            },
            {
                "id": "second_instead_of_first",
                "target": "LOGIC",
                "old": "return values[0]",
                "new": "return values[1]",
            },
        ],
    },

    {
        "family_id": "clamp",
        "description": "Clamp a value so it is no lower than low and no higher than high.",
        "source": """
def solve(value, low, high):
    if value < low:
        return low
    if value > high:
        return high
    return value
""",
        "tests": [
            {"args": [-5, 0, 10], "expected": 0},
            {"args": [15, 0, 10], "expected": 10},
            {"args": [5, 0, 10], "expected": 5},
            {"args": [0, 0, 10], "expected": 0},
        ],
        "mutations": [
            {
                "id": "missing_def_colon",
                "target": "SYNTAX",
                "old": "def solve(value, low, high):",
                "new": "def solve(value, low, high)",
            },
            {
                "id": "missing_if_colon",
                "target": "SYNTAX",
                "old": "if value < low:",
                "new": "if value < low",
            },
            {
                "id": "undefined_boundary",
                "target": "RUNTIME",
                "old": "if value < low:",
                "new": "if value < missing_low:",
            },
            {
                "id": "index_numeric_boundary",
                "target": "RUNTIME",
                "old": "return low",
                "new": "return low[0]",
            },
            {
                "id": "wrong_lower_comparison",
                "target": "LOGIC",
                "old": "if value < low:",
                "new": "if value > low:",
            },
            {
                "id": "wrong_upper_return",
                "target": "LOGIC",
                "old": "return high",
                "new": "return low",
            },
        ],
    },

    {
        "family_id": "sum_even",
        "description": "Return the sum of all even integers in a list.",
        "source": """
def solve(values):
    return sum(x for x in values if x % 2 == 0)
""",
        "tests": [
            {"args": [[1, 2, 3, 4]], "expected": 6},
            {"args": [[2, 4, 6]], "expected": 12},
            {"args": [[1, 3, 5]], "expected": 0},
            {"args": [[-2, -3, 4]], "expected": 2},
        ],
        "mutations": [
            {
                "id": "missing_def_colon",
                "target": "SYNTAX",
                "old": "def solve(values):",
                "new": "def solve(values)",
            },
            {
                "id": "unclosed_generator",
                "target": "SYNTAX",
                "old": "return sum(x for x in values if x % 2 == 0)",
                "new": "return sum(x for x in values if x % 2 == 0",
            },
            {
                "id": "iterable_typo",
                "target": "RUNTIME",
                "old": "x in values",
                "new": "x in value",
            },
            {
                "id": "index_scalar",
                "target": "RUNTIME",
                "old": "x % 2",
                "new": "x[0] % 2",
            },
            {
                "id": "odd_instead_of_even",
                "target": "LOGIC",
                "old": "x % 2 == 0",
                "new": "x % 2 == 1",
            },
            {
                "id": "altered_accumulated_value",
                "target": "LOGIC",
                "old": "sum(x for x",
                "new": "sum(x + 1 for x",
            },
        ],
    },

    {
        "family_id": "gcd",
        "description": "Return the greatest common divisor of two integers.",
        "source": """
def solve(a, b):
    while b:
        a, b = b, a % b
    return abs(a)
""",
        "tests": [
            {"args": [48, 18], "expected": 6},
            {"args": [54, 24], "expected": 6},
            {"args": [17, 13], "expected": 1},
            {"args": [20, 0], "expected": 20},
        ],
        "mutations": [
            {
                "id": "missing_def_colon",
                "target": "SYNTAX",
                "old": "def solve(a, b):",
                "new": "def solve(a, b)",
            },
            {
                "id": "missing_while_colon",
                "target": "SYNTAX",
                "old": "while b:",
                "new": "while b",
            },
            {
                "id": "modulus_variable_typo",
                "target": "RUNTIME",
                "old": "a % b",
                "new": "a % missing_b",
            },
            {
                "id": "invalid_numeric_method",
                "target": "RUNTIME",
                "old": "return abs(a)",
                "new": "return a.abs()",
            },
            {
                "id": "wrong_return_variable",
                "target": "LOGIC",
                "old": "return abs(a)",
                "new": "return abs(b)",
            },
            {
                "id": "off_by_one_result",
                "target": "LOGIC",
                "old": "return abs(a)",
                "new": "return abs(a) + 1",
            },
        ],
    },
]
