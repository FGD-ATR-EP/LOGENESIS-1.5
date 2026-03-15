# ADR-0002: Lifecycle Behavior Completion

Status: Accepted

## Context
The repository had RFC-aligned structure but incomplete runtime behavior (missing retrieval gating, multipath wiring, verifier mode richness, and MIRAS loop execution).

## Decision
Implement full turn lifecycle in `TurnOrchestrator` with:
- constitution gating,
- context governor integration,
- routing + optional bounded deliberative search,
- weighted verifier aggregation,
- safe response planning,
- MIRAS working/episodic/semantic + DiffMem updates,
- post-episode-only RSI behavior.

## Consequences
- Better architectural parity with RFC-LGN-1.5-001.
- Stronger guarantees for abstain-over-hallucinate and memory commit safety.
- Increased test surface for lifecycle and memory policy invariants.
