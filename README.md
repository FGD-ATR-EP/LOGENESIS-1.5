# LOGENESIS-1.5

Logenesis is a control-first reasoning governor focused on intent admission, constitutional gating, bounded multi-path search, process-aware verification, and contamination-aware memory policy.
It does not render UI or make presentation decisions.

- Logenesis does not render.
- Logenesis does not decide UI.
- Logenesis emits intent vectors and reasoning outcomes.

## Core architecture

- **Inspira**: validates value-aligned intent statements.
- **Firma**: evaluates feasibility and constraints.
- **Checker**: enforces constitutional boundaries.
- **ResonanceMapper + PORISJEM**: maps text to vectors and sanitizes risky signals.
- **Cogitator-X (ReasoningEntity)**: bounded search-episode manager with typed thought nodes, UCB-like selection, PRM-style verification, risk pruning, backpropagation, and stable termination policy.
- **CommitGate + MIRAS**: single-writer long-term memory policy for stable solution commits, failure lessons, and calibrated episode summaries.

## System Architecture Diagram (Database-Oriented)

```mermaid
erDiagram
    STATE_SNAPSHOT ||--|| STATE_IDENTITY : contains
    STATE_SNAPSHOT ||--|| STATE_TEMPORAL : contains
    STATE_SNAPSHOT ||--|| STATE_INTENT : contains
    STATE_SNAPSHOT ||--|| STATE_ENERGY : contains
    STATE_SNAPSHOT ||--|| STATE_COHERENCE : contains
    STATE_SNAPSHOT ||--|| STATE_ENTROPY : contains
    STATE_SNAPSHOT ||--|| STATE_DYNAMICS : contains
    STATE_SNAPSHOT ||--|| STATE_GATE : contains
    STATE_SNAPSHOT ||--|| STATE_METADATA : contains
    STATE_SNAPSHOT ||--o{ REFLECTION_TRACE : logs
    STATE_SNAPSHOT ||--o{ GATE_DECISION_LOG : audits
    STATE_SNAPSHOT ||--o{ MEMORY_SNAPSHOT : persists

    STATE_SNAPSHOT {
      uuid state_id PK
      string source
      float timestamp
      string schema_version
    }
    STATE_IDENTITY {
      uuid state_id PK,FK
      string origin
      string owner
    }
    STATE_TEMPORAL {
      uuid state_id PK,FK
      float delta_t
      float continuity_score
    }
    STATE_INTENT {
      uuid state_id PK,FK
      json intent_vector_5d
      float strength
      float clarity
      int multiplicity
    }
    STATE_GATE {
      uuid state_id PK,FK
      boolean allowed
      string action
      string reason
    }
    REFLECTION_TRACE {
      bigint id PK
      uuid state_id FK
      int step_no
      float candidate_score
      string note
    }
    GATE_DECISION_LOG {
      bigint id PK
      uuid state_id FK
      string policy
      string decision
      string explanation
    }
    MEMORY_SNAPSHOT {
      bigint id PK
      uuid state_id FK
      string memory_type
      string pointer
      float salience
    }
```

> This diagram maps the State Vector layers into a normalized storage model so
> each cognitive snapshot can be audited, replayed, and linked to memory + gate
> decisions.


## Canonical reasoning-control stack

```text
[Input] -> Intent Normalizer -> Inspira/Firma Admission Gate
-> Logenesis Search Episode Manager -> Multi-Path Reasoning Controller
-> Best Stable Reasoned State -> Manifest/Answer Synthesis
-> Commit Gate -> MIRAS Memory Policy
```

Public contracts expose only `final_state`, `best_node`, `confidence`, `risk`, `uncertainty_factors`, `termination_reason`, and `answer_summary`. Internal reasoning trees are kept private for debug/testing.


## Canonical bounded episode loop

`ReasoningEntity.run_public_episode()` executes:

```text
select_node -> expand_node -> verify_children -> apply_risk_pruning
-> update_frontier -> backpropagate -> check_termination
```

Branch generation is typed (`decompose`, `alternative_hypothesis`, `constraint_repair`, `evidence_check`, `simulation`, `synthesis`) and bounded by depth, viability, and constitutional verification.

## Structure

```text
LOGENESIS-1.5/
├─ src/
│  ├─ logenesis/
│  │  ├─ agents/
│  │  │  ├─ pangenes_agent.py
│  │  │  └─ validator_agent.py
│  │  ├─ core/
│  │  │  ├─ inspira.py
│  │  │  ├─ firma.py
│  │  │  └─ checker.py
│  │  ├─ learning/
│  │  │  └─ ai_learning_module.py
│  │  ├─ memory/
│  │  │  ├─ diffmem.py
│  │  │  └─ gems_of_wisdom.py
│  │  ├─ reasoning/
│  │  │  ├─ __init__.py
│  │  │  └─ cogitator_x.py
│  │  ├─ resonance/
│  │  │  ├─ atoms.py
│  │  │  └─ mapper.py
│  │  ├─ platform/
│  │  │  ├─ storage.py
│  │  │  ├─ lineage.py
│  │  │  ├─ calibration.py
│  │  │  ├─ policy_sandbox.py
│  │  │  ├─ memory_compaction.py
│  │  │  └─ analytics.py
│  │  ├─ aetherbus.py
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

`src/logenesis/platform/` contains platform implementation modules for state
lineage, uncertainty calibration, policy simulation, adaptive memory
compaction, and cross-run analytics.

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

## AETHERIUM-GENESIS quick start

```python
from pathlib import Path

from logenesis.agents import PangenesAgent
from logenesis.memory import GemsOfWisdomStorage, GitBasedDiffMemory

storage = GemsOfWisdomStorage()
agent = PangenesAgent(memory_storage=storage)
intent = agent.create_intent("Draft responsible research brief")
feedback = agent.execute_and_audit(intent)

repo = GitBasedDiffMemory(Path("./memory_repo"))
repo.write_snapshot("gems/latest.txt", "\n".join(storage.retrieve_active_context()), "persist gems")
print(feedback)
```

## Technical docs

- [Unified Reasoning Architecture](docs/LOGENESIS_UNIFIED_REASONING_ARCHITECTURE.md)
- [Logenesis Engine & AetherBus Extreme report (Thai)](LOGENESIS_AETHERBUS_REPORT_TH.md)
- [Logenesis State Vector v1 (Thai)](LOGENESIS_STATE_VECTOR_V1_TH.md)
- [Logenesis 1.5-C Context-Governed Conversational Model (Thai)](docs/LOGENESIS_1_5C_CONTEXT_GOVERNED_MODEL_TH.md)
- [RFC-LGN-1.5-001: Conversational Reasoning Architecture Specification](docs/RFC-LGN-1.5-001.md)

## Platform updates implemented

The repository now includes production-ready foundations for:

- **State lineage graphing** for causality path tracing.
- **Uncertainty calibration tables** for confidence-drift checks.
- **Policy simulation sandbox** for gate-rule A/B rehearsal.
- **Adaptive memory compaction** using salience and recency.
- **Cross-run analytics summaries** for intent/coherence trend monitoring.

See `src/logenesis/platform/` for implementation modules and
`tests/test_platform_extensions.py` for validation coverage.


## AetherBus throughput quick run

```bash
python -m tests.benchmark.throughput_tester
```
