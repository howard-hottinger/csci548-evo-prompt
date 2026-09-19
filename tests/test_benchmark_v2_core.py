import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from benchmark_v2_core import classify_source


TESTS = [
    {
        "args": [2, 3],
        "expected": 6,
    },
    {
        "args": [4, 5],
        "expected": 20,
    },
    {
        "args": [-2, 3],
        "expected": -6,
    },
]


CORRECT = """
def solve(a, b):
    return a * b
"""


SYNTAX = """
def solve(a, b)
    return a * b
"""


RUNTIME = """
def solve(a, b):
    return aa * b
"""


LOGIC = """
def solve(a, b):
    return a + b
"""


CASES = {
    "CORRECT": CORRECT,
    "SYNTAX": SYNTAX,
    "RUNTIME": RUNTIME,
    "LOGIC": LOGIC,
}


def main():
    passed = 0

    for expected, source in CASES.items():
        observed = classify_source(
            source,
            TESTS,
        )

        ok = observed == expected

        print(
            f"expected={expected:7} "
            f"observed={observed:7} "
            f"pass={ok}"
        )

        if ok:
            passed += 1

    print()
    print(
        f"Pilot 2 core tests: "
        f"{passed}/{len(CASES)}"
    )

    if passed != len(CASES):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
