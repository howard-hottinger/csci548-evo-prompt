# Pilot 1 Findings

## Purpose

Pilot 1 validated the CSCI 548 evolutionary prompt optimization
experimental pipeline on Medora using Qwen2.5-Coder-7B-Instruct.

The benchmark contained:

- 20 source-program families
- 120 defect examples
- 40 SYNTAX
- 40 RUNTIME
- 40 LOGIC

Families were separated into optimization, validation, and sealed test
sets.

## Baseline and Manual Prompt Results

Optimization:

- Baseline accuracy: 0.6667
- Baseline macro-F1: 0.6698
- Manual accuracy: 0.7167
- Manual macro-F1: 0.7075

Validation:

- Baseline accuracy: 0.7333
- Baseline macro-F1: 0.7348
- Manual accuracy: 0.7667
- Manual macro-F1: 0.7571

The test set was not evaluated.

## Mutation-Level Findings

Injected runtime error:

- 100% accuracy under all evaluated conditions.

Undefined variable:

- 0% accuracy under all evaluated conditions.
- Qwen systematically treated these runtime NameError defects as SYNTAX.

Return None:

- Baseline optimization: 20%
- Baseline validation: 40%
- Manual optimization: 100%
- Manual validation: 100%

Remove closing parenthesis:

- Baseline optimization: 90%
- Baseline validation: 100%
- Manual optimization: 30%
- Manual validation: 60%

Return zero:

- 90–100% accuracy.

## Interpretation

Pilot 1 demonstrates that prompt wording materially changes defect
classification behavior while model weights and decoding remain fixed.

However, performance is strongly associated with individual synthetic
mutation operators. This creates a risk that prompt optimization could
overfit to generator artifacts rather than learn generally useful defect
classification instructions.

Pilot 1 is therefore retained as pipeline-validation evidence but will
not be used as the primary final research benchmark.

## Pilot 2 Direction

Pilot 2 will use:

- multiple behavioral tests per program family;
- more realistic software defects;
- diverse mutation mechanisms;
- automatic classification based on compilation, execution, and test
  outcomes;
- family-isolated data splitting;
- analysis of transfer across mutation operators;
- a sealed final test set.
