import ast
import subprocess
import sys
import tempfile

from benchmark import CASES


def classify_case(case):
    # Stage 1: Syntax
    try:
        ast.parse(case.code)
    except SyntaxError:
        return "SYNTAX"

    # Stage 2: Runtime
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False
    ) as f:
        f.write(case.code)
        path = f.name

    try:
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return "RUNTIME"

    if result.returncode != 0:
        return "RUNTIME"

    # Stage 3: Logic
    if case.expected_output is not None:
        actual = result.stdout.strip()

        if actual != case.expected_output:
            return "LOGIC"

    return "CORRECT"


def main():
    passed = 0

    for case in CASES:
        observed = classify_case(case)

        ok = observed == case.defect_type

        if ok:
            passed += 1

        print(
            f"{case.case_id}: "
            f"expected={case.defect_type} "
            f"verified={observed} "
            f"pass={ok}"
        )

    print()
    print(f"Verified: {passed}/{len(CASES)}")


if __name__ == "__main__":
    main()
