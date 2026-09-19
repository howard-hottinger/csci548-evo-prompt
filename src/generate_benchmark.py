import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

SEED = 42
random.seed(SEED)

ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = Path(
    f"/scratch/{Path.home().name}/csci548/data/generated"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


PROGRAMS = [
    {
        "family_id": "addition",
        "description": "Add two integers",
        "correct_code": """
def solve(a, b):
    return a + b

print(solve(4, 7))
""",
        "expected_output": "11",
    },
    {
        "family_id": "subtraction",
        "description": "Subtract two integers",
        "correct_code": """
def solve(a, b):
    return a - b

print(solve(10, 3))
""",
        "expected_output": "7",
    },
    {
        "family_id": "multiplication",
        "description": "Multiply two integers",
        "correct_code": """
def solve(a, b):
    return a * b

print(solve(6, 5))
""",
        "expected_output": "30",
    },
    {
        "family_id": "division",
        "description": "Divide two numbers",
        "correct_code": """
def solve(a, b):
    return a / b

print(solve(20, 4))
""",
        "expected_output": "5.0",
    },
    {
        "family_id": "maximum",
        "description": "Return the larger of two numbers",
        "correct_code": """
def solve(a, b):
    return max(a, b)

print(solve(8, 3))
""",
        "expected_output": "8",
    },
    {
        "family_id": "minimum",
        "description": "Return the smaller of two numbers",
        "correct_code": """
def solve(a, b):
    return min(a, b)

print(solve(8, 3))
""",
        "expected_output": "3",
    },
    {
        "family_id": "even_check",
        "description": "Determine whether a number is even",
        "correct_code": """
def solve(n):
    return n % 2 == 0

print(solve(8))
""",
        "expected_output": "True",
    },
    {
        "family_id": "string_length",
        "description": "Return the length of a string",
        "correct_code": """
def solve(text):
    return len(text)

print(solve("python"))
""",
        "expected_output": "6",
    },
    {
        "family_id": "reverse_string",
        "description": "Reverse a string",
        "correct_code": """
def solve(text):
    return text[::-1]

print(solve("python"))
""",
        "expected_output": "nohtyp",
    },
    {
        "family_id": "uppercase",
        "description": "Convert text to uppercase",
        "correct_code": """
def solve(text):
    return text.upper()

print(solve("python"))
""",
        "expected_output": "PYTHON",
    },
    {
        "family_id": "list_sum",
        "description": "Sum a list of integers",
        "correct_code": """
def solve(values):
    return sum(values)

print(solve([1, 2, 3, 4]))
""",
        "expected_output": "10",
    },
    {
        "family_id": "list_max",
        "description": "Return the largest list element",
        "correct_code": """
def solve(values):
    return max(values)

print(solve([3, 9, 2, 5]))
""",
        "expected_output": "9",
    },
    {
        "family_id": "first_element",
        "description": "Return the first list element",
        "correct_code": """
def solve(values):
    return values[0]

print(solve([7, 8, 9]))
""",
        "expected_output": "7",
    },
    {
        "family_id": "factorial",
        "description": "Compute factorial",
        "correct_code": """
def solve(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

print(solve(5))
""",
        "expected_output": "120",
    },
    {
        "family_id": "count_vowels",
        "description": "Count vowels in a string",
        "correct_code": """
def solve(text):
    return sum(1 for c in text.lower() if c in "aeiou")

print(solve("education"))
""",
        "expected_output": "5",
    },
    {
        "family_id": "palindrome",
        "description": "Determine whether a string is a palindrome",
        "correct_code": """
def solve(text):
    return text == text[::-1]

print(solve("level"))
""",
        "expected_output": "True",
    },
    {
        "family_id": "square",
        "description": "Square a number",
        "correct_code": """
def solve(n):
    return n * n

print(solve(9))
""",
        "expected_output": "81",
    },
    {
        "family_id": "absolute_value",
        "description": "Return absolute value",
        "correct_code": """
def solve(n):
    return abs(n)

print(solve(-12))
""",
        "expected_output": "12",
    },
    {
        "family_id": "contains_value",
        "description": "Determine whether a list contains a value",
        "correct_code": """
def solve(values, target):
    return target in values

print(solve([1, 4, 7, 9], 7))
""",
        "expected_output": "True",
    },
    {
        "family_id": "average",
        "description": "Compute the arithmetic mean",
        "correct_code": """
def solve(values):
    return sum(values) / len(values)

print(solve([2, 4, 6, 8]))
""",
        "expected_output": "5.0",
    },
]


def run_code(code):
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
    ) as f:
        f.write(code)
        path = f.name

    try:
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception as exc:
        return {
            "returncode": 1,
            "stdout": "",
            "stderr": str(exc),
        }

    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def classify(code, expected_output):
    try:
        compile(code, "<benchmark>", "exec")
    except SyntaxError:
        return "SYNTAX"

    result = run_code(code)

    if result["returncode"] != 0:
        return "RUNTIME"

    if result["stdout"] != expected_output:
        return "LOGIC"

    return "CORRECT"


def syntax_mutations(code):
    mutations = []

    lines = code.splitlines()

    # Remove a colon from the function definition.
    mutated = []
    changed = False

    for line in lines:
        if not changed and line.lstrip().startswith("def ") and line.rstrip().endswith(":"):
            mutated.append(line.rstrip()[:-1])
            changed = True
        else:
            mutated.append(line)

    if changed:
        mutations.append(
            ("remove_function_colon", "\n".join(mutated))
        )

    # Remove a closing parenthesis from the print statement.
    mutated = []
    changed = False

    for line in lines:
        if not changed and "print(" in line and line.rstrip().endswith(")"):
            mutated.append(line.rstrip()[:-1])
            changed = True
        else:
            mutated.append(line)

    if changed:
        mutations.append(
            ("remove_closing_parenthesis", "\n".join(mutated))
        )

    return mutations


def runtime_mutations(code):
    mutations = []

    marker = "\nprint(solve"

    if marker in code:
        before, after = code.split(marker, 1)

        mutation = (
            before
            + '\nraise RuntimeError("injected defect")\n'
            + marker
            + after
        )

        mutations.append(
            ("injected_runtime_error", mutation)
        )

    # Undefined variable inside solve().
    lines = code.splitlines()
    mutated = []
    inserted = False

    for line in lines:
        mutated.append(line)

        if (
            not inserted
            and line.lstrip().startswith("def solve")
        ):
            indent = " " * 4
            mutated.append(
                indent + "return undefined_variable"
            )
            inserted = True

    if inserted:
        mutations.append(
            ("undefined_variable", "\n".join(mutated))
        )

    return mutations


def logic_mutations(code):
    mutations = []

    # Replace the solve() function body with a deterministic,
    # syntactically valid but incorrect return value.
    lines = code.splitlines()

    mutated = []
    in_solve = False
    replaced = False

    for line in lines:
        if line.startswith("def solve"):
            mutated.append(line)
            mutated.append("    return None")
            in_solve = True
            replaced = True
            continue

        if in_solve:
            if line.startswith("    ") or not line.strip():
                continue
            else:
                in_solve = False

        mutated.append(line)

    if replaced:
        mutations.append(
            ("return_none", "\n".join(mutated))
        )

    # Second deterministic wrong result.
    lines = code.splitlines()

    mutated = []
    in_solve = False
    replaced = False

    for line in lines:
        if line.startswith("def solve"):
            mutated.append(line)
            mutated.append("    return 0")
            in_solve = True
            replaced = True
            continue

        if in_solve:
            if line.startswith("    ") or not line.strip():
                continue
            else:
                in_solve = False

        mutated.append(line)

    if replaced:
        mutations.append(
            ("return_zero", "\n".join(mutated))
        )

    return mutations


def main():
    examples = []

    mutation_functions = {
        "SYNTAX": syntax_mutations,
        "RUNTIME": runtime_mutations,
        "LOGIC": logic_mutations,
    }

    for program in PROGRAMS:
        family = program["family_id"]
        correct_code = program["correct_code"].strip() + "\n"
        expected_output = program["expected_output"]

        correct_class = classify(
            correct_code,
            expected_output,
        )

        if correct_class != "CORRECT":
            raise RuntimeError(
                f"Reference program {family} is not correct: "
                f"{correct_class}"
            )

        for target_class, mutation_function in mutation_functions.items():
            candidates = mutation_function(correct_code)

            accepted = 0

            for mutation_name, mutated_code in candidates:
                observed = classify(
                    mutated_code,
                    expected_output,
                )

                if observed != target_class:
                    print(
                        f"REJECT {family} {mutation_name}: "
                        f"wanted={target_class} "
                        f"observed={observed}"
                    )
                    continue

                accepted += 1

                case_id = (
                    f"{family}_{target_class.lower()}_"
                    f"{accepted:02d}"
                )

                examples.append(
                    {
                        "case_id": case_id,
                        "family_id": family,
                        "description": program["description"],
                        "defect_type": target_class,
                        "mutation": mutation_name,
                        "expected_output": expected_output,
                        "code": mutated_code,
                    }
                )

            if accepted < 2:
                print(
                    f"WARNING: {family} produced only "
                    f"{accepted} accepted {target_class} cases"
                )

    output_file = OUTPUT_DIR / "pilot_benchmark.json"

    output_file.write_text(
        json.dumps(examples, indent=2)
    )

    counts = {}

    for example in examples:
        label = example["defect_type"]
        counts[label] = counts.get(label, 0) + 1

    print()
    print("=" * 60)
    print("Pilot benchmark generated")
    print("=" * 60)
    print("Examples:", len(examples))
    print("Families:", len(set(x["family_id"] for x in examples)))

    for label in ["SYNTAX", "RUNTIME", "LOGIC"]:
        print(f"{label}: {counts.get(label, 0)}")

    print()
    print("Saved to:")
    print(output_file)


if __name__ == "__main__":
    main()
