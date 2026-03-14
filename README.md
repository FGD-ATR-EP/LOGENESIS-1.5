# Logenesis 1.5

Logenesis 1.5 is a production-oriented reference implementation for RFC-LGN-1.5-001, a **conversational reasoning architecture** (not a generic chatbot).

## Core Pipeline

`User Input -> Constitution -> Context Governor -> Dialogue Ledger -> Reasoning Router -> (Fast|Deliberative) -> Response Planner -> MIRAS Memory Stack`

## Key Safety Guarantees

- Public responses are separated from hidden internal reasoning.
- Optional multi-path reasoning is bounded and internal-only.
- Unverified reasoning cannot commit to long-term memory.
- Long-term memory writes are only possible via MIRAS Commit Gate.
- Context continuity is derived from structured state, not full transcript replay.

## Repository Map

- `docs/` architecture, RFC rewrite, schema docs, flows, and decisions
- `src/logenesis/` implementation modules
- `tests/` unit/integration skeleton with deterministic fixtures
- `config/` example policies and thresholds
- `examples/` runnable usage flows

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

## Minimal API Run

```bash
uvicorn logenesis.api.server:app --reload
```

Then call `POST /v1/conversation/turn`.

## Architecture-first Notes

- External model providers are abstracted behind `LLMProvider`.
- Verification is modular (`process`, `factual`, `context`, `commitment`).
- Memory is split into working, episodic, semantic, DiffMem, and commit controls.
- RSI is post-episode only and does not mutate active constitutional policy mid-episode.

## Limitations

- This repository includes mock/stub providers and deterministic defaults.
- It does not include cluster-scale training pipelines.
