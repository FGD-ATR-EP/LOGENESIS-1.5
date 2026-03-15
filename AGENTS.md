# AGENTS.md — LOGENESIS-1.5

This file defines the working rules for Codex and other coding agents operating in this repository.

Repository: `lnspirafirmaGPK/LOGENESIS-1.5`

Primary goal:
Implement and maintain **Logenesis 1.5** as a **conversational reasoning architecture**, not as a generic chatbot or an autonomous multi-agent swarm.

The architecture of this repository is centered on these layers:

1. Constitution Layer
2. Context Governor
3. Dialogue State Ledger
4. LLM Core
5. Verifier
6. MIRAS Memory Stack

Codex must preserve this architecture and improve behavior without collapsing it into a simpler but incorrect design.

---

## 1. Architectural identity

Treat this project as a **conversational reasoning system** with constrained internal reasoning and controlled memory.

Core expectations:

- Hidden internal reasoning must never be exposed directly to end users.
- Public answers must be separated from internal reasoning traces.
- Multi-path reasoning is selective, bounded, and internal-only.
- Unverified branches must never commit to long-term memory.
- MIRAS Commit Gate is the only authority allowed to write long-term memory.
- Dialogue continuity must be state-driven, not based on raw transcript replay alone.
- Constitution rules must constrain reasoning, execution, and memory writes.
- RSI is post-episode only and must not mutate active constitutional policy during an active episode.
- Avoid agent chaos and uncontrolled autonomous swarm behavior.

Do not refactor this repository into:
- a plain prompt wrapper,
- a generic memory chatbot,
- an always-on agent framework,
- a transcript-dumping chat loop.

---

## 2. Repository map and intended responsibilities

Use the current structure as the base design:

- `src/logenesis/constitution/` — constitutional gating, ruleset loading, input/commit/execution checks
- `src/logenesis/context_governor/` — intent normalization, topic management, retrieval gating, drift detection, context compilation
- `src/logenesis/ledger/` — dialogue facts, claims, commitments, contradictions, unresolved items
- `src/logenesis/router/` — fast vs deliberative routing
- `src/logenesis/llm_core/` — provider abstraction and mock/provider-compatible model interfaces
- `src/logenesis/verifier/` — process/factual/context/commitment verification and aggregation
- `src/logenesis/reasoning/` — bounded internal reasoning and optional multi-path search
- `src/logenesis/memory/` — working, episodic, semantic, DiffMem, commit gate, RSI
- `src/logenesis/response/` — safe user-facing answer synthesis
- `src/logenesis/runtime/` — orchestrator and turn lifecycle
- `src/logenesis/api/` — request/response contracts and API endpoint
- `src/logenesis/schemas/` — strongly typed shared models
- `docs/` — RFC, module map, request lifecycle, decisions, flows, schemas
- `tests/` — unit, integration, and benchmark-oriented checks
- `config/` — routing, verifier, memory, and constitutional policy files
- `examples/` — runnable examples

Preserve these boundaries unless there is a strong architectural reason to change them.

---

## 3. Change policy

When changing code, prefer:
1. safety
2. auditability
3. RFC alignment
4. correctness
5. modularity
6. convenience

When a tradeoff is necessary:
- preserve architectural invariants over cosmetic simplicity,
- preserve explicit contracts over hidden coupling,
- preserve testability over cleverness.

Do not make large speculative rewrites when a smaller RFC-aligned fix is possible.

---

## 4. Required behavior when editing code

For code changes, Codex must:

1. inspect the relevant module boundaries first,
2. understand how the change affects the turn lifecycle,
3. preserve or improve:
   - constitution checks,
   - context discipline,
   - verifier discipline,
   - memory commit safety,
   - hidden reasoning separation,
4. update or add tests,
5. update docs when behavior changes materially.

If a change affects any of the following, treat it as a **behavioral architecture change**:
- `runtime/`
- `context_governor/`
- `verifier/`
- `memory/`
- `reasoning/`
- `router/`
- `schemas/`
- `constitution/`
- `response/`
- files in `config/`

Such changes require targeted tests and a summary of impact.

---

## 5. Testing and linting rules

### 5.1 Mandatory rule

Run relevant tests and lint/format checks on every **behavioral code change**.

Do **not** skip checks silently.

Before finishing, report:
- what changed,
- whether the change was:
  - `code change`
  - `comment-only change`
  - `docs-only change`
- what tests were run,
- what lint/format checks were run,
- what was intentionally not run and why.

### 5.2 When tests/lint must run

Run tests and lint/format checks when changes affect:
- executable Python code,
- schemas,
- routing rules,
- verifier logic,
- memory logic,
- constitution rules,
- API contracts,
- config values that affect runtime behavior,
- imports, dependencies, or packaging,
- examples if they rely on changed behavior.

### 5.3 When tests/lint may be skipped

You may skip test/lint execution only when changes are strictly one of these:

1. **comment-only change**
   - code comments only
   - no logic, conditions, imports, function signatures, classes, schemas, config values, public interfaces, or runtime strings used by the program are changed

2. **docs-only change**
   - `README.md`
   - `docs/`
   - markdown/text documentation
   - no executable code, config, tests, or runtime-facing strings are changed

If unsure whether a change is behavioral, assume it **is** behavioral and run at least targeted checks.

### 5.4 Minimum commands

For this repository, the default expected checks are:

```bash
pytest
```

If narrower targeted execution is clearly sufficient, prefer:
```bash
pytest tests/unit/...
pytest tests/integration/...
```

For lint/format:
- if a linter or formatter is explicitly configured in the repository, run the configured tool(s),
- if no lint tool is configured, do not invent a fake toolchain,
- if a new lint tool is introduced, document it and keep usage consistent.

At the time of writing, do not assume `ruff`, `black`, `mypy`, or other tools exist unless they are added to repository configuration.

### 5.5 Scope guidance

Use **targeted checks first** when possible.

Run broader checks when changes affect:
- shared schemas,
- orchestrator lifecycle,
- API contracts,
- routing policies,
- verifier aggregation,
- commit gate logic,
- memory policy,
- multi-path reasoning,
- topic state handling,
- repository-wide interfaces.

Examples:
- change in `src/logenesis/schemas/models.py` -> run broader tests
- change in `src/logenesis/runtime/orchestrator.py` -> run unit + integration tests
- change in `src/logenesis/memory/commit_gate.py` -> run memory + integration tests
- change only in markdown docs -> no code tests required

---

## 6. Turn-lifecycle expectations

Any change touching the runtime flow must preserve or improve this sequence:

1. receive input
2. constitution check
3. intent normalization
4. topic frame update
5. retrieval gate query
6. context compilation
7. ledger update
8. route fast vs deliberative path
9. optional bounded multi-path reasoning on eligible turns
10. verifier stack
11. aggregate verification
12. response planning
13. memory candidate generation
14. commit gate evaluation
15. allowed MIRAS memory updates
16. return response with confidence/abstain metadata

If a change breaks or bypasses this flow, it must be treated as a serious regression unless clearly intentional and documented.

---

## 7. Context Governor rules

Codex must preserve and improve these properties:

- compiled bounded context, not append-only transcript replay
- topic frame semantics
- topic switch and safe return
- contradiction-aware topic handling
- retrieval filtering by topic, time, confidence, and session scope
- drift detection integrated into actual runtime behavior

Avoid simplistic shortcuts that erase topic/ledger structure.

---

## 8. Verifier rules

Verifier behavior must remain modular and explicit.

Expected axes:
- process validity
- factual validity
- context consistency
- commitment consistency

Preferred properties:
- hard-fail vs soft-fail distinction
- uncertainty factors
- abstain-over-hallucinate behavior
- future-compatible step-level scoring hooks

Never allow user-facing output to be justified by hidden internal traces.

---

## 9. Memory and MIRAS rules

The memory system must remain policy-driven.

Preserve these principles:

- working memory is transient and turn/episode scoped
- episodic memory records interaction outcomes
- semantic memory stores only validated stable reusable knowledge
- DiffMem records auditable history and change lineage
- Commit Gate is the only writer to long-term memory
- RSI is post-episode only

Never permit long-term memory writes from:
- speculative claims
- unresolved contradictions
- raw hidden reasoning
- failed branches
- unsafe instructions
- unverified or unstable content

If changing memory logic, test:
- allowed commits
- blocked commits
- pollution-risk controls
- DiffMem lineage behavior
- RSI timing constraints

---

## 10. Multi-path reasoning rules

Multi-path reasoning is optional and internal-only.

It must be:
- bounded by budget
- verifier-aware
- risk-aware
- prunable
- non-user-facing

Do not expose the reasoning tree directly.
Do not enable deep search on every turn.
Do not allow invalid branches to influence memory commits.

If changing reasoning logic, add tests for:
- bounded termination
- invalid branch pruning
- optional activation
- no long-term memory writes from invalid/unverified branches

---

## 11. Response safety rules

Response planning must:
- derive user-facing text only from verified internal state,
- avoid hidden-trace leakage,
- support abstain-over-hallucinate,
- package uncertainty safely when needed,
- avoid overclaiming confidence.

Do not rely on naive string replacement as the sole safety mechanism if a stronger structure is feasible.

---

## 12. Documentation rules

Update docs when behavior changes materially.

At minimum, consider updating:
- `docs/rfc/RFC-LGN-1.5-001.md`
- `docs/architecture/module-map.md`
- `docs/architecture/request-lifecycle.md`
- relevant decision notes in `docs/decisions/`

If code and docs diverge, bring them back into alignment.

Docs must not describe behavior that the code clearly does not implement unless explicitly labeled as future work.

---

## 13. Backward compatibility

Preserve backward compatibility when reasonable.

However:
- correctness and RFC alignment are more important than preserving a weak placeholder interface,
- if a breaking change is necessary, update docs and tests clearly,
- avoid silent contract drift.

---

## 14. What to include in final summaries

When Codex completes a task, the final summary should include:

1. change classification
   - code change / comment-only / docs-only

2. files changed

3. behavioral impact
   - what part of the architecture changed

4. checks run
   - tests
   - lint/format checks

5. skipped checks
   - what was skipped
   - why it was safe to skip

6. remaining gaps
   - anything still stubbed
   - anything deferred intentionally

---

## 15. Default local commands

Use these defaults unless repository configuration changes:

Install:
```bash
pip install -e .[dev]
```

Run tests:
```bash
pytest
```

Run local API:
```bash
uvicorn logenesis.api.server:app --reload
```

If more tools are added later, prefer the repository-declared command set over ad hoc commands.

---

## 16. Final instruction

Use the existing repository architecture as the base.
Do not simplify it into a generic chatbot wrapper.
Do not stop at placeholder logic if a real local implementation is feasible.
When uncertain, prefer safer, more auditable, more RFC-aligned behavior.
