import json
from collections import defaultdict
from pathlib import Path

RESULT_DIR = Path(
    f"/scratch/{Path.home().name}/csci548/results/pilot"
)

files = sorted(
    RESULT_DIR.glob("pilot-baseline-manual-*.json"),
    key=lambda p: p.stat().st_mtime,
)

if not files:
    raise RuntimeError("No pilot result files found.")

result_file = files[-1]
data = json.loads(result_file.read_text())

print("Analyzing:")
print(result_file)
print()

groups = defaultdict(
    lambda: {
        "total": 0,
        "correct": 0,
    }
)

for condition in data["conditions"]:
    prompt = condition["condition"]
    split = condition["split"]

    for example in condition["examples"]:
        key = (
            prompt,
            split,
            example["mutation"],
        )

        groups[key]["total"] += 1

        if example["correct"]:
            groups[key]["correct"] += 1

print("=" * 78)
print("Accuracy by mutation operator")
print("=" * 78)

for key in sorted(groups):
    prompt, split, mutation = key
    stats = groups[key]

    accuracy = (
        stats["correct"] / stats["total"]
    )

    print(
        f"{prompt:10} "
        f"{split:13} "
        f"{mutation:28} "
        f"{stats['correct']:2}/{stats['total']:2} "
        f"{accuracy:.3f}"
    )
