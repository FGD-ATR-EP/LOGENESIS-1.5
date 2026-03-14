# Module Map (RFC Alignment)

## Constitution Layer
- `src/logenesis/constitution/constitution_engine.py`: orchestrates constitutional decisions.
- `ruleset_loader.py`: loads and validates YAML rulesets.
- `checker.py`: atomic checks for reasoning, execution, and commit permission.

## Context Governor
- `intent_normalizer.py`: converts raw input into `IntentFrame`.
- `topic_frame_manager.py`: topic stack, switch, and return.
- `context_compiler.py`: compiles `ContextPacket` from state+memory.
- `retrieval_gate.py`: policy gate before retrieval.
- `drift_detector.py`: structured drift and contradiction cues.

## Dialogue State Ledger
- `ledger/dialogue_ledger.py`: tracks confirmed facts, claims, commitments, unresolved items, contradictions.

## Reasoning Router
- `router/reasoning_router.py`: configurable fast vs deliberative selection.

## Fast/Deliberative Paths
- `runtime/orchestrator.py`: per-turn lifecycle.
- `llm_core/providers.py`: provider-agnostic LLM interface + mock/openai-compatible placeholder.
- `verifier/*.py`: modular verification components.
- `reasoning/multipath.py`: bounded optional multi-path logic.

## Response Planner
- `response/response_planner.py`: transforms verified internal state to safe natural-language output.

## MIRAS Memory Stack
- `memory/working_memory.py`, `episodic_memory.py`, `semantic_memory.py`, `diffmem.py`.
- `memory/commit_gate.py`: only authority for long-term writes.
- `memory/rsi.py`: post-episode reflective summaries, no active-policy mutation.

## API + Contracts
- `api/contracts.py`: request/response types.
- `api/server.py`: minimal conversation endpoint.

## Schemas
- `schemas/models.py`: strong typed pydantic models for all RFC entities.
