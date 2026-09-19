import json
import random
from collections import Counter
from pathlib import Path


SEED = 548
random.seed(SEED)

DATA_DIR = Path(
    f"/scratch/{Path.home().name}/csci548/data/generated"
)

INPUT = DATA_DIR / "pilot_benchmark.json"
OUTPUT = DATA_DIR / "pilot_benchmark_split.json"


def main():
    examples = json.loads(INPUT.read_text())

    families = sorted(
        {x["family_id"] for x in examples}
    )

    random.shuffle(families)

    n = len(families)

    optimization_cut = int(n * 0.50)
    validation_cut = optimization_cut + int(n * 0.25)

    optimization_families = set(
        families[:optimization_cut]
    )

    validation_families = set(
        families[optimization_cut:validation_cut]
    )

    test_families = set(
        families[validation_cut:]
    )

    split_examples = {
        "optimization": [],
        "validation": [],
        "test": [],
    }

    for example in examples:
        family = example["family_id"]

        if family in optimization_families:
            split = "optimization"
        elif family in validation_families:
            split = "validation"
        elif family in test_families:
            split = "test"
        else:
            raise RuntimeError(
                f"Family not assigned: {family}"
            )

        record = dict(example)
        record["split"] = split

        split_examples[split].append(record)

    OUTPUT.write_text(
        json.dumps(split_examples, indent=2)
    )

    print("Seed:", SEED)

    for split, records in split_examples.items():
        family_count = len(
            {x["family_id"] for x in records}
        )

        labels = Counter(
            x["defect_type"] for x in records
        )

        print()
        print(split.upper())
        print("Families:", family_count)
        print("Examples:", len(records))
        print("Labels:", dict(labels))

    print()
    print("Saved to:")
    print(OUTPUT)


if __name__ == "__main__":
    main()
