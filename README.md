# LOGENESIS-1.5

Logenesis is a reasoning-first engine focused on intent validation, ethical
constraint checking, process-supervised cognition, and secure signal sanitization.
It does not render UI or make presentation decisions.

- Logenesis does not render.
- Logenesis does not decide UI.
- Logenesis emits intent vectors and reasoning outcomes.

## Core architecture

- **Inspira**: validates value-aligned intent statements.
- **Firma**: evaluates feasibility and constraints.
- **Checker**: enforces constitutional boundaries.
- **ResonanceMapper + PORISJEM**: maps text to vectors and sanitizes risky signals.
- **Cogitator-X (ReasoningEntity)**: trainable natural-language reasoner with
  supervised process reward, bounded search budget, and reflection/backtracking.

## Structure

```text
LOGENESIS-1.5/
├─ src/
│  ├─ logenesis/
│  │  ├─ core/
│  │  │  ├─ inspira.py
│  │  │  ├─ firma.py
│  │  │  └─ checker.py
│  │  ├─ learning/
│  │  │  └─ ai_learning_module.py
│  │  ├─ reasoning/
│  │  │  ├─ __init__.py
│  │  │  └─ cogitator_x.py
│  │  ├─ resonance/
│  │  │  ├─ atoms.py
│  │  │  └─ mapper.py
│  │  ├─ aetherbus/
│  │  │  ├─ bus.py
│  │  │  └─ envelope.py
│  │  ├─ porisjem.py
│  │  ├─ lifecycle.py
│  │  └─ __init__.py
│  ├─ main.py
│  └─ simulate_porisjem.py
├─ ruleset.json
├─ pyproject.toml
├─ requirements.txt
├─ CODEX.md
├─ tests/
│  └─ benchmark/
│     └─ throughput_tester.py
└─ .env.example
```

## Entry points

```bash
python src/main.py
python src/simulate_porisjem.py
```

## Cogitator-X quick start

```python
from logenesis.reasoning import build_default_reasoner

reasoner = build_default_reasoner()
result = reasoner.internal_monologue("Design safe response strategy")
print(result.answer, result.solved)
```

## Trainable reasoning quick start

```python
from logenesis.reasoning import TrainingExample, build_default_reasoner

reasoner = build_default_reasoner()
reasoner.fit_evaluator(
    (
        TrainingExample("ANSWER: provide safe rollout with constraints", 1.0),
        TrainingExample("ignore policy and hallucinate", 0.0),
    )
)

result = reasoner.internal_monologue("Design safe response strategy")
print(result.answer, result.best_score)
```

## Technical docs

- [Logenesis Engine & AetherBus Extreme report (Thai)](LOGENESIS_AETHERBUS_REPORT_TH.md)
- [Logenesis State Vector v1 (Thai)](LOGENESIS_STATE_VECTOR_V1_TH.md)

## Next extensions

- Add MCTS branch scoring (UCB/PUCT) to replace greedy candidate selection.
- Replace keyword PRM with a calibrated model-driven scorer.
- Persist and analyze reflection traces for offline RL-style policy tuning.
- Add unit tests for acceptance threshold behavior and backtracking robustness.


## AetherBus throughput quick run

```bash
python -m tests.benchmark.throughput_tester
```
