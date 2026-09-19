import hashlib
import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path

import torch
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"

LABELS = [
    "SYNTAX",
    "RUNTIME",
    "LOGIC",
]

CONDITIONS = [
    "baseline",
    "manual",
]

# Do not include test here.
EVALUATED_SPLITS = [
    "optimization",
    "validation",
]

ROOT = Path(__file__).resolve().parents[1]

PROMPT_DIR = ROOT / "prompts"

DATA_FILE = Path(
    f"/scratch/{os.environ['USER']}/csci548/"
    "data/generated/pilot2_benchmark_split.json"
)

RESULT_DIR = Path(
    f"/scratch/{os.environ['USER']}/csci548/"
    "results/pilot2"
)

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def sha256_text(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def git_revision():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip()

    except Exception:
        return "UNKNOWN"


def load_prompt(condition):
    return (
        PROMPT_DIR
        / f"{condition}.txt"
    ).read_text().strip()


def parse_prediction(raw):
    cleaned = raw.strip().upper()

    if cleaned in LABELS:
        return cleaned

    # Conservative fallback.
    for label in LABELS:
        if cleaned.startswith(label):
            return label

    return "INVALID"


def build_messages(
    instruction,
    description,
    code,
):
    user_message = f"""
{instruction}

Task specification:
{description}

Python implementation:

{code}
""".strip()

    return [
        {
            "role": "system",
            "content": (
                "You are an expert Python programmer "
                "performing defect classification."
            ),
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]


def classify(
    model,
    tokenizer,
    instruction,
    description,
    code,
):
    messages = build_messages(
        instruction,
        description,
        code,
    )

    prompt_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(
        prompt_text,
        return_tensors="pt",
    ).to("cuda")

    torch.cuda.synchronize()

    start = time.perf_counter()

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=8,
            do_sample=False,
        )

    torch.cuda.synchronize()

    elapsed = time.perf_counter() - start

    new_tokens = outputs[
        0,
        inputs["input_ids"].shape[1]:
    ]

    raw_output = tokenizer.decode(
        new_tokens,
        skip_special_tokens=True,
    ).strip()

    return {
        "prediction": parse_prediction(
            raw_output
        ),
        "raw_output": raw_output,
        "inference_seconds": elapsed,
        "input_tokens": int(
            inputs["input_ids"].shape[1]
        ),
        "output_tokens": int(
            new_tokens.shape[0]
        ),
    }


def compute_metrics(records):
    y_true = [
        record["expected"]
        for record in records
    ]

    y_pred = [
        record["prediction"]
        for record in records
    ]

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    precision, recall, f1, support = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=LABELS,
            zero_division=0,
        )
    )

    per_class = {}

    for index, label in enumerate(LABELS):
        per_class[label] = {
            "precision": float(
                precision[index]
            ),
            "recall": float(
                recall[index]
            ),
            "f1": float(
                f1[index]
            ),
            "support": int(
                support[index]
            ),
        }

    macro_f1 = float(
        sum(f1) / len(f1)
    )

    matrix_labels = (
        LABELS + ["INVALID"]
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=matrix_labels,
    ).tolist()

    invalid_count = sum(
        prediction == "INVALID"
        for prediction in y_pred
    )

    total_seconds = sum(
        record["inference_seconds"]
        for record in records
    )

    return {
        "accuracy": float(accuracy),
        "macro_f1": macro_f1,
        "per_class": per_class,
        "confusion_matrix": {
            "labels": matrix_labels,
            "matrix": matrix,
        },
        "invalid_outputs": invalid_count,
        "total_inference_seconds": (
            total_seconds
        ),
        "mean_inference_seconds": (
            total_seconds
            / len(records)
        ),
        "total_input_tokens": sum(
            x["input_tokens"]
            for x in records
        ),
        "total_output_tokens": sum(
            x["output_tokens"]
            for x in records
        ),
    }


def evaluate_condition_split(
    model,
    tokenizer,
    condition,
    split_name,
    examples,
):
    instruction = load_prompt(
        condition
    )

    records = []

    print()
    print("=" * 72)
    print(
        f"Condition: {condition} | "
        f"Split: {split_name}"
    )
    print("=" * 72)

    for index, example in enumerate(
        examples,
        start=1,
    ):
        result = classify(
            model=model,
            tokenizer=tokenizer,
            instruction=instruction,
            description=example[
                "description"
            ],
            code=example["code"],
        )

        correct = (
            result["prediction"]
            == example["defect_type"]
        )

        record = {
            "case_id": example["case_id"],
            "family_id": (
                example["family_id"]
            ),
            "mutation_id": (
                example["mutation_id"]
            ),
            "expected": (
                example["defect_type"]
            ),
            "prediction": (
                result["prediction"]
            ),
            "raw_output": (
                result["raw_output"]
            ),
            "correct": correct,
            "inference_seconds": (
                result[
                    "inference_seconds"
                ]
            ),
            "input_tokens": (
                result["input_tokens"]
            ),
            "output_tokens": (
                result["output_tokens"]
            ),
        }

        records.append(record)

        print(
            f"[{index:02d}/{len(examples):02d}] "
            f"{example['case_id']} "
            f"expected={example['defect_type']} "
            f"predicted={result['prediction']} "
            f"correct={correct}"
        )

    metrics = compute_metrics(
        records
    )

    print()
    print(
        f"Accuracy: "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        f"Macro-F1: "
        f"{metrics['macro_f1']:.4f}"
    )

    print(
        "Invalid outputs:",
        metrics["invalid_outputs"],
    )

    print("Per-class F1:")

    for label in LABELS:
        print(
            f"  {label}: "
            f"{metrics['per_class'][label]['f1']:.4f}"
        )

    return {
        "condition": condition,
        "split": split_name,
        "prompt_text": instruction,
        "prompt_sha256": (
            sha256_text(instruction)
        ),
        "metrics": metrics,
        "examples": records,
    }


def main():
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA unavailable. "
            "Run through Slurm on a GPU node."
        )

    dataset = json.loads(
        DATA_FILE.read_text()
    )

    print("=" * 72)
    print("CSCI 548 Pilot 2 Evaluation")
    print("=" * 72)

    print("Model:", MODEL_ID)
    print(
        "GPU:",
        torch.cuda.get_device_name(0),
    )
    print(
        "Git revision:",
        git_revision(),
    )
    print(
        "Slurm job:",
        os.environ.get(
            "SLURM_JOB_ID",
            "interactive",
        ),
    )
    print(
        "Dataset SHA256:",
        sha256_file(DATA_FILE),
    )

    print()
    print("Dataset:")

    for split in EVALUATED_SPLITS:
        examples = dataset[split]

        families = {
            x["family_id"]
            for x in examples
        }

        labels = Counter(
            x["defect_type"]
            for x in examples
        )

        print(
            f"  {split}: "
            f"{len(examples)} examples, "
            f"{len(families)} families, "
            f"{dict(labels)}"
        )

    print()
    print(
        "TEST SET: SEALED — "
        "not evaluated"
    )

    print()
    print("Loading tokenizer...")

    tokenizer = (
        AutoTokenizer.from_pretrained(
            MODEL_ID
        )
    )

    print("Loading model...")

    model = (
        AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            dtype=torch.bfloat16,
        )
        .to("cuda")
    )

    model.eval()

    output = {
        "experiment": (
            "csci548_pilot2_"
            "baseline_manual"
        ),
        "model": MODEL_ID,
        "git_revision": git_revision(),
        "slurm_job_id": (
            os.environ.get(
                "SLURM_JOB_ID"
            )
        ),
        "dataset_file": str(
            DATA_FILE
        ),
        "dataset_sha256": (
            sha256_file(DATA_FILE)
        ),
        "evaluated_splits": (
            EVALUATED_SPLITS
        ),
        "test_set_evaluated": False,
        "conditions": [],
    }

    for condition in CONDITIONS:
        for split_name in EVALUATED_SPLITS:

            result = (
                evaluate_condition_split(
                    model=model,
                    tokenizer=tokenizer,
                    condition=condition,
                    split_name=split_name,
                    examples=dataset[
                        split_name
                    ],
                )
            )

            output[
                "conditions"
            ].append(result)

    timestamp = time.strftime(
        "%Y%m%d-%H%M%S"
    )

    job_id = os.environ.get(
        "SLURM_JOB_ID",
        "interactive",
    )

    output_file = RESULT_DIR / (
        f"pilot2-baseline-manual-"
        f"{job_id}-{timestamp}.json"
    )

    output_file.write_text(
        json.dumps(
            output,
            indent=2,
        )
    )

    print()
    print("=" * 72)
    print("PILOT 2 EVALUATION COMPLETE")
    print("=" * 72)

    print(
        "Results:",
        output_file,
    )

    print()
    print(
        "TEST SET REMAINS SEALED."
    )


if __name__ == "__main__":
    main()
