import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"

CASES = [
    {
        "id": "syntax_001",
        "label": "SYNTAX",
        "code": """
def add(a, b)
    return a + b
""",
    },
    {
        "id": "runtime_001",
        "label": "RUNTIME",
        "code": """
def divide(a, b):
    return a / b

print(divide(10, 0))
""",
    },
    {
        "id": "logic_001",
        "label": "LOGIC",
        "code": """
def multiply(a, b):
    return a + b

print(multiply(4, 5))
""",
    },
]


def classify(model, tokenizer, code):
    messages = [
        {
            "role": "system",
            "content": "You are an expert Python programmer.",
        },
        {
            "role": "user",
            "content": f"""Classify the Python defect as exactly one of:

SYNTAX
RUNTIME
LOGIC

Definitions:

SYNTAX: The program cannot be parsed or compiled as valid Python.

RUNTIME: The program is syntactically valid but raises an exception during execution.

LOGIC: The program runs without an exception but produces incorrect behavior.

Return only the label.

Python code:

{code}
""",
        },
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
    ).to("cuda")

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=8,
            do_sample=False,
        )

    new_tokens = outputs[
        0,
        inputs["input_ids"].shape[1]:
    ]

    return tokenizer.decode(
        new_tokens,
        skip_special_tokens=True,
    ).strip()


print("Loading model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype=torch.bfloat16,
).to("cuda")

model.eval()

correct = 0

for case in CASES:
    start = time.time()

    prediction = classify(
        model,
        tokenizer,
        case["code"],
    )

    elapsed = time.time() - start

    match = prediction == case["label"]

    if match:
        correct += 1

    print(
        f'{case["id"]}: '
        f'expected={case["label"]} '
        f'predicted={prediction} '
        f'correct={match} '
        f'time={elapsed:.3f}s'
    )

print()
print(f"Accuracy: {correct}/{len(CASES)}")
