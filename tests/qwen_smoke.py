import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"


print("=" * 60)
print("CSCI 548 — Qwen Medora Smoke Test")
print("=" * 60)

print("PyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if not torch.cuda.is_available():
    raise RuntimeError("CUDA is not available.")

print("GPU:", torch.cuda.get_device_name(0))

print("\nLoading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

print("Loading model...")
start = time.time()

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype=torch.bfloat16,
)

model = model.to("cuda")
model.eval()

load_time = time.time() - start

print(f"Model loaded in {load_time:.2f} seconds")
print(
    "Allocated GPU memory:",
    f"{torch.cuda.memory_allocated() / 1024**3:.2f} GiB"
)

messages = [
    {
        "role": "system",
        "content": "You are an expert Python programmer.",
    },
    {
        "role": "user",
        "content": """Classify the Python defect as exactly one of:

SYNTAX
RUNTIME
LOGIC

Return only the label.

def divide(a, b):
    return a / b

print(divide(10, 0))
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

start = time.time()

with torch.inference_mode():
    outputs = model.generate(
        **inputs,
        max_new_tokens=8,
        do_sample=False,
    )

inference_time = time.time() - start

new_tokens = outputs[
    0,
    inputs["input_ids"].shape[1]:
]

answer = tokenizer.decode(
    new_tokens,
    skip_special_tokens=True,
).strip()

print("\nExpected: RUNTIME")
print("Model answer:", answer)
print(f"Inference time: {inference_time:.3f} seconds")
print(
    "Peak GPU memory:",
    f"{torch.cuda.max_memory_allocated() / 1024**3:.2f} GiB"
)
