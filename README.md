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
- **Cogitator-X (ReasoningEntity)**: System-2 style reasoning with process reward,
  bounded search budget, and reflection/backtracking.

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
│  │  │  ├─ cogitator_x.py
│  │  │  └─ __init__.py
│  │  ├─ resonance/
│  │  │  └─ mapper.py
│  │  ├─ porisjem.py
│  │  ├─ lifecycle.py
│  │  └─ __init__.py
│  ├─ main.py
│  └─ simulate_porisjem.py
├─ ruleset.json
├─ pyproject.toml
├─ requirements.txt
├─ CODEX.md
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

## Technical docs

- [Logenesis Engine & AetherBusExtreme report (Thai)](LOGENESIS_AETHERBUS_REPORT_TH.md)
- [Logenesis State Vector v1 (Thai)](LOGENESIS_STATE_VECTOR_V1_TH.md)

## Next extensions

- Add MCTS branch scoring (UCB/PUCT) to replace greedy candidate selection.
- Replace keyword PRM with a calibrated model-driven scorer.
- Persist and analyze reflection traces for offline RL-style policy tuning.
- Add unit tests for acceptance threshold behavior and backtracking robustness.
