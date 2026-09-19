import json
from collections import Counter, defaultdict
from pathlib import Path

from generate_benchmark import classify


DATA = Path(
    f"/scratch/{Path.home().name}/csci548/data/generated/"
    "pilot_benchmark_split.json"
)


def main():
    data = json.loads(DATA.read_text())

    all_examples = []
    family_splits = defaultdict(set)

    for split_name, examples in data.items():
        for example in examples:
            all_examples.append(example)
            family_splits[example["family_id"]].add(split_name)

    print("=" * 60)
    print("CSCI 548 Pilot Benchmark Validation")
    print("=" * 60)

    # ------------------------------------------------------
    # Unique IDs
    # ------------------------------------------------------

    case_ids = [x["case_id"] for x in all_examples]

    if len(case_ids) != len(set(case_ids)):
        raise RuntimeError("Duplicate case IDs detected.")

    print("Unique case IDs: PASS")

    # ------------------------------------------------------
    # Family leakage
    # ------------------------------------------------------

    leaked = {
        family: splits
        for family, splits in family_splits.items()
        if len(splits) > 1
    }

    if leaked:
        raise RuntimeError(
            f"Family leakage detected: {leaked}"
        )

    print("Family split isolation: PASS")

    # ------------------------------------------------------
    # Ground-truth verification
    # ------------------------------------------------------

    failures = []

    for example in all_examples:
        observed = classify(
            example["code"],
            example["expected_output"],
        )

        if observed != example["defect_type"]:
            failures.append(
                (
                    example["case_id"],
                    example["defect_type"],
                    observed,
                )
            )

    if failures:
        raise RuntimeError(
            f"Ground-truth failures: {failures}"
        )

    print("Automatic ground truth: PASS")

    # ------------------------------------------------------
    # Dataset distribution
    # ------------------------------------------------------

    print()
    print("Total examples:", len(all_examples))
    print(
        "Total families:",
        len(family_splits),
    )

    for split_name, examples in data.items():
        label_counts = Counter(
            x["defect_type"] for x in examples
        )

        family_counts = len(
            {x["family_id"] for x in examples}
        )

        print()
        print(split_name.upper())
        print("Families:", family_counts)
        print("Examples:", len(examples))
        print("Labels:", dict(label_counts))

    # ------------------------------------------------------
    # Per-family checks
    # ------------------------------------------------------

    family_records = defaultdict(list)

    for example in all_examples:
        family_records[
            example["family_id"]
        ].append(example)

    for family, examples in family_records.items():
        labels = Counter(
            x["defect_type"]
            for x in examples
        )

        expected = {
            "SYNTAX": 2,
            "RUNTIME": 2,
            "LOGIC": 2,
        }

        if dict(labels) != expected:
            raise RuntimeError(
                f"{family} has unexpected distribution: "
                f"{dict(labels)}"
            )

    print()
    print("Per-family class balance: PASS")

    print()
    print("=" * 60)
    print("BENCHMARK VALIDATION PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
