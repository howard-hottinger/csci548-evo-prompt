import json
import os
import random
from collections import Counter
from pathlib import Path


SEED = 5482

DATA_DIR = Path(
    f"/scratch/{os.environ['USER']}/csci548/data/generated"
)

INPUT = DATA_DIR / "pilot2_benchmark.json"
OUTPUT = DATA_DIR / "pilot2_benchmark_split.json"


def main():
    random.seed(SEED)

    examples = json.loads(
        INPUT.read_text()
    )

    families = sorted(
        {
            example["family_id"]
            for example in examples
        }
    )

    random.shuffle(families)

    # 60 / 20 / 20 family split
    optimization_families = set(
        families[:6]
    )

    validation_families = set(
        families[6:8]
    )

    test_families = set(
        families[8:]
    )

    split_data = {
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
                f"Unassigned family: {family}"
            )

        record = dict(example)
        record["split"] = split

        split_data[split].append(
            record
        )

    OUTPUT.write_text(
        json.dumps(
            split_data,
            indent=2,
        )
    )

    print("Seed:", SEED)

    for split, records in split_data.items():
        family_names = sorted(
            {
                x["family_id"]
                for x in records
            }
        )

        labels = Counter(
            x["defect_type"]
            for x in records
        )

        print()
        print(split.upper())
        print("Families:", len(family_names))
        print("Family IDs:", family_names)
        print("Examples:", len(records))
        print("Labels:", dict(labels))

    print()
    print("Saved to:")
    print(OUTPUT)


if __name__ == "__main__":
    main()
