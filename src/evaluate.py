import json
import os
import time
from pathlib import Path

import torch
from sklearn.metrics import accuracy_score, f1_score
from transformers import AutoModelForCausalLM, AutoTokenizer

from benchmark import CASES


MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"
LABELS = ["SYNTAX", "RUNTIME", "LOGIC"]

ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "prompts"

SCRATCH = Path(
    os.environ.get(
        "CSCI548_SCRATCH",
        f"/scratch/{os.environ['USER']}/csci548",
    )
)

RESULT_DIR = SCRATCH / "results" / "pilot"
RESULT_DIR.mkdir(parents=True, exist_ok=True)


def load_prompt(name):
    path = PROMPT_DIR / f"{name}.txt"
    return path.read_text().strip()


def parse_prediction(raw):
    value = raw.strip().upper()

    if value in LABELS:
        return value

    return "INVALID"


def classify(model, tokenizer, instruction, code):
    messages = [
        {
            "role": "system",
            "content": "You are an expert Python programmer.",
        },
        {
            "role": "user",
            "content": f"""{instruction}

Python code:

{code}
""",
        },
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(
        text,
        return_tensors="pt",
    ).to("cuda")

    start = time.perf_counter()

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=8,
            do_sample=False,
        )

    elapsed = time.perf_counter() - start

    new_tokens = outputs[
        0,
        inputs["input_ids"].shape[1]:
    ]

    raw = tokenizer.decode(
        new_tokens,
        skip_special_tokens=True,
    )

    return raw.strip(), elapsed


def evaluate_condition(model, tokenizer, condition):
    prompt = load_prompt(condition)

    y_true = []
    y_pred = []
    records = []

    print()
    print("=" * 60)
    print(f"Condition: {condition}")
    print("=" * 60)

    for case in CASES:
        raw, elapsed = classify(
            model,
            tokenizer,
            prompt,
            case.code,
        )

        prediction = parse_prediction(raw)

        y_true.append(case.defect_type)
        y_pred.append(prediction)

        correct = prediction == case.defect_type

        record = {
            "case_id": case.case_id,
            "family_id": case.family_id,
            "expected": case.defect_type,
            "prediction": prediction,
            "raw_output": raw,
            "correct": correct,
            "inference_seconds": elapsed,
        }

        records.append(record)

        print(
            f"{case.case_id}: "
            f"expected={case.defect_type} "
            f"predicted={prediction} "
            f"correct={correct} "
            f"time={elapsed:.3f}s"
        )

    accuracy = accuracy_score(y_true, y_pred)

    macro_f1 = f1_score(
        y_true,
        y_pred,
        labels=LABELS,
        average="macro",
        zero_division=0,
    )

    result = {
        "condition": condition,
        "model": MODEL_ID,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "examples": records,
    }

    print()
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Macro-F1: {macro_f1:.4f}")

    return result


def main():
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is unavailable. Run this on a Medora GPU node."
        )

    print("GPU:", torch.cuda.get_device_name(0))
    print("Loading:", MODEL_ID)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype=torch.bfloat16,
    ).to("cuda")

    model.eval()

    all_results = []

    for condition in ["baseline", "manual"]:
        result = evaluate_condition(
            model,
            tokenizer,
            condition,
        )
        all_results.append(result)

    output_file = RESULT_DIR / "baseline_manual.json"

    output_file.write_text(
        json.dumps(all_results, indent=2)
    )

    print()
    print("Results saved to:")
    print(output_file)


if __name__ == "__main__":
    main()
