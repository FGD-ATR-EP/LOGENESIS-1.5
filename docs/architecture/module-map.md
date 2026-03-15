# Module Map (RFC Alignment)

## Constitution Layer
- `src/logenesis/constitution/constitution_engine.py`: orchestrates constitutional decisions.
- `ruleset_loader.py`: loads and validates YAML rulesets.
- `checker.py`: atomic checks for reasoning, execution, and commit permission.

## Context Governor
- `intent_normalizer.py`: richer intent fields (constraints, success criteria, urgency, safety class).
- `topic_frame_manager.py`: topic stack, switch, contradiction-aware return behavior.
- `context_compiler.py`: bounded `ContextPacket` with anchor summaries and retrieval snippets.
- `retrieval_gate.py`: topic/time/confidence/session-aware retrieval filters.
- `drift_detector.py`: structured drift and contradiction cues integrated into turn flow.

## Dialogue State Ledger
- `ledger/dialogue_ledger.py`: confirmed facts, unverified claims, commitments, unresolved items, contradictions, repair hints.

## Reasoning Router
- `router/reasoning_router.py`: configurable fast vs deliberative selection.

## Fast/Deliberative Paths
- `runtime/orchestrator.py`: full per-turn lifecycle + memory wiring.
- `llm_core/providers.py`: provider-agnostic LLM interface + mock/openai-compatible placeholder.
- `verifier/*.py`: modular verification components and weighted aggregation.
- `reasoning/search_controller.py` + `selection.py` + `expansion.py` + `pruning.py` + `backpropagation.py` + `termination.py`.

## Response Planner
- `response/response_planner.py`: verified-state response rendering, uncertainty packaging, anti-trace leakage.

## MIRAS Memory Stack
- `memory/working_memory.py`, `episodic_memory.py`, `semantic_memory.py`, `diffmem.py`.
- `memory/commit_gate.py`: only authority for long-term writes.
- `memory/rsi.py`: post-episode reflective summaries, no active-policy mutation.

## API + Contracts
- `api/contracts.py`: request/response types including confidence/uncertainty fields.
- `api/server.py`: `POST /v1/conversation/turn` endpoint.

## Schemas
- `schemas/models.py`: expanded pydantic models for RFC-level fields.
