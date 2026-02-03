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
