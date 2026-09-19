import json
import subprocess
import sys
import tempfile


RESULT_MARKER = "__CSCI548_RESULTS__"


def compile_source(source):
    try:
        compile(
            source,
            "<benchmark>",
            "exec",
        )
        return True
    except SyntaxError:
        return False


def execute_tests(source, tests, timeout=5):
    tests_json = json.dumps(tests)

    harness = f"""
import json

{source}

tests = json.loads({tests_json!r})

results = []

for test in tests:
    try:
        args = test.get("args", [])
        kwargs = test.get("kwargs", {{}})

        value = solve(
            *args,
            **kwargs,
        )

        results.append(
            {{
                "ok": True,
                "value": value,
            }}
        )

    except Exception as exc:
        results.append(
            {{
                "ok": False,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            }}
        )

print(
    {RESULT_MARKER!r}
    + json.dumps(results)
)
"""

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
    ) as f:
        f.write(harness)
        path = f.name

    result = subprocess.run(
        [sys.executable, path],
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if result.returncode != 0:
        return {
            "harness_failed": True,
            "stderr": result.stderr,
            "results": [],
        }

    result_line = None

    for line in result.stdout.splitlines():
        if line.startswith(RESULT_MARKER):
            result_line = line[
                len(RESULT_MARKER):
            ]

    if result_line is None:
        return {
            "harness_failed": True,
            "stderr": (
                "Result marker missing from harness."
            ),
            "results": [],
        }

    return {
        "harness_failed": False,
        "stderr": result.stderr,
        "results": json.loads(
            result_line
        ),
    }


def classify_source(source, tests):
    """
    Classify a Python implementation using objective execution rules.

    SYNTAX:
        Source cannot compile.

    RUNTIME:
        Source compiles, but at least one test raises an exception.

    LOGIC:
        All tests execute, but at least one value differs from expected.

    CORRECT:
        Every test executes and every expected value matches.
    """

    if not compile_source(source):
        return "SYNTAX"

    execution = execute_tests(
        source,
        tests,
    )

    if execution["harness_failed"]:
        return "RUNTIME"

    results = execution["results"]

    if len(results) != len(tests):
        return "RUNTIME"

    for result in results:
        if not result["ok"]:
            return "RUNTIME"

    for test, result in zip(
        tests,
        results,
    ):
        if result["value"] != test["expected"]:
            return "LOGIC"

    return "CORRECT"
