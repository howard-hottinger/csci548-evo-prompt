import json
import os
from collections import Counter, defaultdict
from pathlib import Path

from benchmark_v2_core import classify_source


DATA_FILE = Path(
    f"/scratch/{os.environ['USER']}/csci548/"
    "data/generated/pilot2_benchmark_split.json"
)


def main():
    data = json.loads(
        DATA_FILE.read_text()
    )

    all_examples = []

    family_splits = defaultdict(set)

    for split, examples in data.items():
        for example in examples:
            all_examples.append(example)

            family_splits[
                example["family_id"]
            ].add(split)

    print("=" * 70)
    print("CSCI 548 Pilot 2 Benchmark Validation")
    print("=" * 70)

    # Unique case IDs
    case_ids = [
        x["case_id"]
        for x in all_examples
    ]

    if len(case_ids) != len(set(case_ids)):
        raise RuntimeError(
            "Duplicate case IDs detected."
        )

    print("Unique case IDs: PASS")

    # Family leakage
    leaked = {
        family: splits
        for family, splits
        in family_splits.items()
        if len(splits) > 1
    }

    if leaked:
        raise RuntimeError(
            f"Family leakage detected: {leaked}"
        )

    print("Family split isolation: PASS")

    # Ground truth
    failures = []

    for example in all_examples:
        observed = classify_source(
            example["code"],
            example["tests"],
        )

        if observed != example["defect_type"]:
            failures.append(
                {
                    "case_id": example["case_id"],
                    "expected": example["defect_type"],
                    "observed": observed,
                }
            )

    if failures:
        raise RuntimeError(
            f"Ground-truth failures: {failures}"
        )

    print("Automatic ground truth: PASS")

    # Counts
    print()
    print("Total examples:", len(all_examples))
    print(
        "Total families:",
        len(family_splits),
    )

    for split, examples in data.items():
        labels = Counter(
            x["defect_type"]
            for x in examples
        )

        families = {
            x["family_id"]
            for x in examples
        }

        print()
        print(split.upper())
        print("Families:", len(families))
        print("Examples:", len(examples))
        print("Labels:", dict(labels))

    # Every family must contain 2 of each class
    family_records = defaultdict(list)

    for example in all_examples:
        family_records[
            example["family_id"]
        ].append(example)

    expected_counts = {
        "SYNTAX": 2,
        "RUNTIME": 2,
        "LOGIC": 2,
    }

    for family, examples in family_records.items():
        counts = Counter(
            x["defect_type"]
            for x in examples
        )

        if dict(counts) != expected_counts:
            raise RuntimeError(
                f"{family} has unexpected "
                f"class balance: {dict(counts)}"
            )

    print()
    print("Per-family class balance: PASS")

    mutation_ids = {
        x["mutation_id"]
        for x in all_examples
    }

    print(
        "Distinct mutation IDs:",
        len(mutation_ids),
    )

    print()
    print("=" * 70)
    print("PILOT 2 BENCHMARK VALIDATION PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
