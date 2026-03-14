# Logenesis 1.5 Unified Reasoning Architecture

## Positioning

Logenesis 1.5 is a **constitutional, stateful, multi-path reasoning controller** with process-aware verification, risk-sensitive pruning, and memory-coupled learning.

It is not:
- UI renderer
- autonomous swarm runtime
- free-running execution orchestrator

## Planes

1. **Constitutional Plane**: Inspira, Firma, Checker.
2. **Cognitive Control Plane**: state snapshots, gate physics, search tree, verification, pruning, termination.
3. **Execution Plane**: LLM/tool executor integration surfaces and manifest synthesis.
4. **Learning & Memory Plane**: MIRAS policy + Gems + DiffMem + compaction + lineage + calibration.

## Hard Invariants

- Single root intent per episode.
- Single writer for long-term memory: Commit Gate + MIRAS.
- Append-only tree operations: append child, prune flag, terminal mark.
- No uncontrolled tool autonomy in branches.
- RSI rule updates are post-episode.
- Constitutional gating at admission, branch, and commit levels.
- Public answer contract excludes internal reasoning tree.

## Core Entities

- `IntentFrame`
- `CognitiveStateSnapshot`
- `ThoughtNode`
- `VerificationResult`
- `RiskProfile`
- `SearchEpisode`
- `PublicReasoningResult`

## Canonical Loop

```text
select_node → expand_node → verify_children → apply_risk_pruning
→ update_frontier → backpropagate → check_termination
```

Search runs strictly inside one bounded episode, never as agent competition.

## Selection / Verification / Pruning

- Selection uses UCB-like score with novelty bonus and risk/cost penalties.
- Verifier computes PRM-style weighted score over process, truthfulness, coherence, and constitutional compatibility.
- Critical failures trigger hard prune.
- Soft failures downweight branch value and increase risk.

## Termination

Stable termination requires confidence, risk, coherence, and gate compatibility thresholds.
Additional exits: budget exhaustion and stagnation.

## Public vs Internal Contract

Public output exposes only:
- stable summary
- confidence
- uncertainty factors
- final status
- risk

Internal tree and node contents remain for debug/test surfaces only.

## MIRAS Memory Policy

MIRAS governs retention and contamination control. Allowed commit classes:
- stable_solution
- reusable_strategy
- failure_lesson
- policy_update_hint
- calibration_signal
- episode_summary

Commit artifacts are written through DiffMem, mirrored as Gems, and compacted by salience/age policy.
