# RFC-LGN-1.5-001 — Logenesis 1.5 Conversational Reasoning Architecture

## 1. Purpose

This RFC defines a constrained, production-oriented conversational reasoning architecture that separates hidden reasoning from public outputs while preserving long-horizon dialogue continuity via structured state.

## 2. Canonical Architecture

`User Input -> Constitution Layer -> Context Governor -> Dialogue State Ledger -> Reasoning Router -> (Fast Dialogue Path | Deliberative Path{LLM Core + Verifier + optional Multi-Path}) -> Response Planner -> MIRAS Memory Stack`

## 3. Design Principles

1. Logenesis 1.5 is a conversational reasoning system, not merely larger-context prompting.
2. Internal reasoning traces are hidden and never emitted directly.
3. Multi-path search is selective, bounded, and optional.
4. Unverified branches cannot write long-term memory.
5. Long-term memory writes are gated by MIRAS Commit Gate.
6. Continuity is state-driven (intent/topic/ledger), not transcript append-only.
7. Constitution constrains execution, reasoning, and memory writes.
8. RSI runs post-episode and cannot mutate active constitutional policy mid-episode.
9. Avoid uncontrolled autonomous multi-agent behavior.

## 4. Data Model

Core schema entities:
- `IntentFrame`: normalized user intent, task type, risk markers.
- `TopicFrame`: active topic, stack history, return anchors.
- `DialogueState`: turn-scoped working state.
- `DialogueLedger`: confirmed facts, unresolved items, commitments, contradictions.
- `ContextPacket`: compiled bounded context for inference.
- `ThoughtNode`: internal deliberation node (never user-facing).
- `VerificationResult`: per-verifier and aggregate safety/quality signals.
- `MemoryRecord`: episodic/semantic commit candidate + provenance.

## 5. Inference Loop (Per Turn)

1. Ingest user input and metadata.
2. Run constitution checks (content, execution, memory constraints).
3. Normalize intent and update topic frame.
4. Compile bounded context packet from state + retrieved memory (not raw replay).
5. Update ledger with observed claims and open items.
6. Route to fast or deliberative path via configurable thresholds.
7. If deliberative: use LLM core, run verifiers, optionally run bounded multi-path search.
8. Aggregate verification score and produce planner-ready internal result.
9. Response planner renders user-safe answer with no internal trace leakage.
10. MIRAS commit gate evaluates eligible memory writes.

## 6. Memory Policy (MIRAS)

- `working_memory`: transient per-episode state.
- `episodic_memory`: event records and outcomes.
- `semantic_memory`: stable facts and reusable abstractions.
- `diffmem`: records changes and contradictions for repair.
- Commit gate requirements:
  - verification score above threshold
  - stable/confirmed content only
  - constitution allows memory commit
  - policy tier approval for long-term writes

## 7. Verifier Rules

Verifier modules:
- Process verifier: checks policy/process compliance.
- Factual verifier: checks claims against known state/sources.
- Context verifier: checks topic consistency and drift.
- Commitment verifier: checks promises and obligation integrity.
- Scoring aggregator: weighted aggregate + abstain trigger.

Abstain-over-hallucinate is required when confidence fails thresholds.

## 8. Anti-Drift Invariants

- Topic continuity uses structured `TopicFrame` and anchors.
- Contradictions are ledgered and unresolved until repaired.
- Context packet must remain bounded by policy limits.
- Repair mode can be triggered when drift or contradiction risk exceeds threshold.

## 9. Training Roadmap (Documented Only)

Training-related roadmap is out of this codebase scope but includes:
- PRM-informed verifier calibration.
- selective MCTS policy tuning for branching budgets.
- memory commit classifiers for stability estimation.
- benchmark-driven threshold tuning.

## 10. Benchmarks

Target benchmark families:
- topic retention over long dialogues
- contradiction detection/repair rate
- abstention correctness under uncertainty
- memory precision/recall for committed items
- latency split for fast vs deliberative routing

## 11. Non-Goals

- Full autonomous multi-agent swarm control.
- Direct exposure of chain-of-thought.
- Always-on deep search for every prompt.
- Cluster-dependent training pipelines in this repository.

## 12. Implementation Status Notes (Behavior-Complete Reference)

Current implementation now wires full turn lifecycle, bounded optional multipath search modules, weighted verifier aggregation with uncertainty factors, richer schema models, and MIRAS turn-loop memory updates (working/episodic/semantic/DiffMem) with post-episode RSI gating.
