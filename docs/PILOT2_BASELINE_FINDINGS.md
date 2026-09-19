# Pilot 2 Baseline Findings

## Benchmark

Pilot 2 contains:

- 10 program families
- 60 automatically verified defect examples
- 20 SYNTAX
- 20 RUNTIME
- 20 LOGIC
- 48 distinct mutation IDs

Family-isolated split:

- Optimization: 6 families / 36 examples
- Validation: 2 families / 12 examples
- Test: 2 families / 12 examples

The test split remained sealed.

## Baseline Prompt

Optimization:

- Accuracy: 0.6111
- Macro-F1: 0.5532
- SYNTAX F1: 0.6486
- RUNTIME F1: 0.1538
- LOGIC F1: 0.8571
- Invalid outputs: 1

Validation:

- Accuracy: 0.7500
- Macro-F1: 0.7746
- SYNTAX F1: 0.8000
- RUNTIME F1: 0.6667
- LOGIC F1: 0.8571
- Invalid outputs: 1

## Manual Prompt

Optimization:

- Accuracy: 0.8889
- Macro-F1: 0.8861
- SYNTAX F1: 0.8800
- RUNTIME F1: 0.8182
- LOGIC F1: 0.9600
- Invalid outputs: 0

Validation:

- Accuracy: 0.8333
- Macro-F1: 0.8320
- SYNTAX F1: 0.7500
- RUNTIME F1: 0.8571
- LOGIC F1: 0.8889
- Invalid outputs: 0

## Interpretation

Prompt wording materially changes Qwen2.5-Coder-7B-Instruct's
classification behavior on the more realistic Pilot 2 benchmark.

The largest baseline weakness is confusion between runtime defects and
syntax defects. The manually engineered prompt substantially improves
runtime classification while maintaining strong logic classification.

Pilot 2 therefore provides a useful environment for testing automatic
prompt optimization.

The validation sample remains small, so Pilot 2 should be treated as an
optimization-method pilot rather than the final benchmark for statistical
claims.
