# LOGENESIS-1.5

Logenesis is a reasoning-first engine focused on intent validation, ethical
constraint checking, and process-supervised cognition. It does not render UI
or make presentation decisions.

- Logenesis does not render.
- Logenesis does not decide UI.
- Logenesis emits intent vectors only.

## Structure

```
LOGENESIS-1.5/
├─ src/
│  ├─ logenesis/
│  │  ├─ core/
│  │  │  ├─ inspira.py
│  │  │  ├─ firma.py
│  │  │  ├─ checker.py
│  │  ├─ learning/
│  │  │  └─ ai_learning_module.py
│  │  ├─ lifecycle.py
│  │  ├─ reasoning/
│  │  │  ├─ __init__.py
│  │  │  └─ cogitator_x.py
│  │  └─ __init__.py
│  └─ main.py
├─ ruleset.json
├─ pyproject.toml
├─ requirements.txt
├─ CODEX.md
└─ .env.example
```

## Entry Point

```bash
python src/main.py
```

## Documentation

- [Logenesis Engine & AetherBusExtreme report (Thai)](LOGENESIS_AETHERBUS_REPORT_TH.md)
- [Logenesis State Vector v1 (Thai)](LOGENESIS_STATE_VECTOR_V1_TH.md)


## Cogitator-X Reasoning

`src/logenesis/reasoning/cogitator_x.py` adds a bounded internal monologue loop:

- `ReasoningConfig.max_thinking_tokens` now actively limits accumulated reasoning trace size.
- `internal_monologue` tracks rejected candidates and passes iteration/history into `generate_next_thoughts`.
- Default `generate_next_thoughts` yields iterative, diverse draft + answer candidates so search/reflection is testable across multiple steps.
- Subclasses can override `generate_next_thoughts(...)` to inject domain-specific planning heuristics.

### Extension ideas

- Replace heuristic scoring in `evaluate_life` with a learned evaluator model.
- Use `experience_empathy` output to dynamically lower/raise `acceptance_threshold`.
- Persist rejection history across sessions to avoid repeating low-value reasoning paths.
