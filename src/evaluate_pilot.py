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
LABELS = ["SYNTAX", "RUNTIME", "LOGIC"]
EVALUATED_SPLITS = ["optimization", "validation"]
CONDITIONS = ["baseline", "manual"]

ROOT = Path(__file__).resolve().parents[1]

PROMPT_DIR = ROOT / "prompts"

DATA_FILE = Path(
    f"/scratch/{os.environ['USER']}/csci548/"
    "data/generated/pilot_benchmark_split.json"
)

RESULT_DIR = Path(
    f"/scratch/{os.environ['USER']}/csci548/"
    "results/pilot"
)

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


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


def load_prompt(name):
    path = PROMPT_DIR / f"{name}.txt"

    return path.read_text().strip()


def parse_prediction(raw):
    value = raw.strip().upper()

    if value in LABELS:
        return value

    # Allow a little defensive parsing while still
    # recording the raw output.
    for label in LABELS:
        if value == label:
            return label

    return "INVALID"


def build_messages(
    instruction,
    description,
    code,
):
    user_content = f"""
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
            "content": user_content,
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

    raw = tokenizer.decode(
        new_tokens,
        skip_special_tokens=True,
    ).strip()

    prediction = parse_prediction(raw)

    input_tokens = int(
        inputs["input_ids"].shape[1]
    )

    output_tokens = int(
        new_tokens.shape[0]
    )

    return {
        "prediction": prediction,
        "raw_output": raw,
        "inference_seconds": elapsed,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


def compute_metrics(records):
    y_true = [
        x["expected"]
        for x in records
    ]

    y_pred = [
        x["prediction"]
        for x in records
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

    for i, label in enumerate(LABELS):
        per_class[label] = {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        }

    macro_f1 = float(
        sum(f1) / len(f1)
    )

    cm_labels = LABELS + ["INVALID"]

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=cm_labels,
    ).tolist()

    invalid_count = sum(
        1
        for x in y_pred
        if x == "INVALID"
    )

    total_seconds = sum(
        x["inference_seconds"]
        for x in records
    )

    total_input_tokens = sum(
        x["input_tokens"]
        for x in records
    )

    total_output_tokens = sum(
        x["output_tokens"]
        for x in records
    )

    return {
        "accuracy": float(accuracy),
        "macro_f1": macro_f1,
        "per_class": per_class,
        "confusion_matrix": {
            "labels": cm_labels,
            "matrix": matrix,
        },
        "invalid_outputs": invalid_count,
        "total_inference_seconds": total_seconds,
        "mean_inference_seconds": (
            total_seconds / len(records)
        ),
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
    }


def evaluate_condition_split(
    model,
    tokenizer,
    condition,
    split_name,
    examples,
):
    instruction = load_prompt(condition)

    records = []

    print()
    print("=" * 70)
    print(
        f"Condition: {condition} | "
        f"Split: {split_name}"
    )
    print("=" * 70)

    for index, example in enumerate(
        examples,
        start=1,
    ):
        result = classify(
            model,
            tokenizer,
            instruction,
            example["description"],
            example["code"],
        )

        correct = (
            result["prediction"]
            == example["defect_type"]
        )

        record = {
            "case_id": example["case_id"],
            "family_id": example["family_id"],
            "mutation": example["mutation"],
            "expected": example["defect_type"],
            "prediction": result["prediction"],
            "raw_output": result["raw_output"],
            "correct": correct,
            "inference_seconds": (
                result["inference_seconds"]
            ),
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
        }

        records.append(record)

        print(
            f"[{index:03d}/{len(examples):03d}] "
            f"{example['case_id']} "
            f"expected={example['defect_type']} "
            f"predicted={result['prediction']} "
            f"correct={correct}"
        )

    metrics = compute_metrics(records)

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
        f"Invalid outputs: "
        f"{metrics['invalid_outputs']}"
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
        "prompt_sha256": sha256_text(
            instruction
        ),
        "metrics": metrics,
        "examples": records,
    }


def main():
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA unavailable. "
            "This must run on a GPU node."
        )

    print("=" * 70)
    print("CSCI 548 Pilot Evaluation")
    print("=" * 70)

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

    dataset = json.loads(
        DATA_FILE.read_text()
    )

    # Deliberately do not access the test set.
    for split in EVALUATED_SPLITS:
        if split not in dataset:
            raise RuntimeError(
                f"Missing split: {split}"
            )

    print()
    print("Dataset:")

    for split in EVALUATED_SPLITS:
        records = dataset[split]

        labels = Counter(
            x["defect_type"]
            for x in records
        )

        families = {
            x["family_id"]
            for x in records
        }

        print(
            f"  {split}: "
            f"{len(records)} examples, "
            f"{len(families)} families, "
            f"{dict(labels)}"
        )

    print()
    print(
        "TEST SET: SEALED — "
        "not evaluated in this run"
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

    results = {
        "experiment": (
            "csci548_pilot_baseline_manual"
        ),
        "model": MODEL_ID,
        "git_revision": git_revision(),
        "slurm_job_id": os.environ.get(
            "SLURM_JOB_ID"
        ),
        "dataset_file": str(DATA_FILE),
        "dataset_sha256": sha256_file(
            DATA_FILE
        ),
        "evaluated_splits": (
            EVALUATED_SPLITS
        ),
        "test_set_evaluated": False,
        "conditions": [],
    }

    for condition in CONDITIONS:
        for split in EVALUATED_SPLITS:
            result = (
                evaluate_condition_split(
                    model,
                    tokenizer,
                    condition,
                    split,
                    dataset[split],
                )
            )

            results["conditions"].append(
                result
            )

    timestamp = time.strftime(
        "%Y%m%d-%H%M%S"
    )

    job_id = os.environ.get(
        "SLURM_JOB_ID",
        "interactive",
    )

    output_file = RESULT_DIR / (
        f"pilot-baseline-manual-"
        f"{job_id}-{timestamp}.json"
    )

    output_file.write_text(
        json.dumps(
            results,
            indent=2,
        )
    )

    print()
    print("=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)

    print(
        "Results saved to:",
        output_file,
    )

    print()
    print(
        "TEST SET REMAINS UNTOUCHED."
    )


if __name__ == "__main__":
    main()
