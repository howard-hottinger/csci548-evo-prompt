import json
import os
from collections import Counter
from pathlib import Path

from benchmark_v2_catalog import FAMILIES
from benchmark_v2_core import classify_source


OUTPUT_DIR = Path(
    f"/scratch/{os.environ['USER']}/csci548/"
    "data/generated"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_FILE = (
    OUTPUT_DIR / "pilot2_benchmark.json"
)


def apply_mutation(source, mutation):
    old = mutation["old"]
    new = mutation["new"]

    count = source.count(old)

    if count != 1:
        raise RuntimeError(
            f"Mutation {mutation['id']} expected "
            f"exactly one occurrence of {old!r}, "
            f"found {count}."
        )

    return source.replace(
        old,
        new,
        1,
    )


def main():
    examples = []

    print("=" * 72)
    print("CSCI 548 Pilot 2 Benchmark Generator")
    print("=" * 72)

    for family in FAMILIES:
        family_id = family["family_id"]

        source = (
            family["source"].strip()
            + "\n"
        )

        tests = family["tests"]

        observed_correct = classify_source(
            source,
            tests,
        )

        if observed_correct != "CORRECT":
            raise RuntimeError(
                f"Reference implementation "
                f"{family_id} classified as "
                f"{observed_correct}"
            )

        print()
        print(f"Family: {family_id}")
        print("  Reference: CORRECT")

        for mutation in family["mutations"]:
            mutated_source = apply_mutation(
                source,
                mutation,
            )

            observed = classify_source(
                mutated_source,
                tests,
            )

            expected = mutation["target"]

            passed = observed == expected

            print(
                f"  {mutation['id']:<30} "
                f"expected={expected:<7} "
                f"observed={observed:<7} "
                f"pass={passed}"
            )

            if not passed:
                raise RuntimeError(
                    f"Mutation validation failed: "
                    f"{family_id}/"
                    f"{mutation['id']} "
                    f"expected={expected} "
                    f"observed={observed}"
                )

            case_id = (
                f"{family_id}_"
                f"{expected.lower()}_"
                f"{mutation['id']}"
            )

            examples.append(
                {
                    "case_id": case_id,
                    "family_id": family_id,
                    "description": (
                        family["description"]
                    ),
                    "defect_type": expected,
                    "mutation_id": (
                        mutation["id"]
                    ),
                    "tests": tests,
                    "code": mutated_source,
                }
            )

    case_ids = [
        example["case_id"]
        for example in examples
    ]

    if len(case_ids) != len(set(case_ids)):
        raise RuntimeError(
            "Duplicate case IDs detected."
        )

    label_counts = Counter(
        example["defect_type"]
        for example in examples
    )

    family_count = len(
        {
            example["family_id"]
            for example in examples
        }
    )

    mutation_count = len(
        {
            example["mutation_id"]
            for example in examples
        }
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            examples,
            indent=2,
        )
    )

    print()
    print("=" * 72)
    print("PILOT 2 GENERATION PASSED")
    print("=" * 72)

    print("Families:", family_count)
    print("Examples:", len(examples))
    print(
        "Distinct mutation IDs:",
        mutation_count,
    )

    print(
        "SYNTAX:",
        label_counts["SYNTAX"],
    )

    print(
        "RUNTIME:",
        label_counts["RUNTIME"],
    )

    print(
        "LOGIC:",
        label_counts["LOGIC"],
    )

    print()
    print("Saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
