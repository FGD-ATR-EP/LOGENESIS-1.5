# CODEX /CREATE_PLATFORM_WORK

## Initiative context
- **Initiative**: Logenesis Platform Hardening & Operability Expansion
- **Scope**: services/modules/infra for lineage, calibration, policy simulation, memory compaction, analytics
- **Drivers**: reliability, security, latency predictability, developer experience
- **Current state (as-is)**: core reasoning exists; platform observability and pre-rollout policy validation were proposal-only
- **Target state (to-be)**: executable platform modules + normalized storage + test-backed operational workflows
- **Constraints**: p95 decision path < 50ms for in-memory operations, SQLite baseline compatibility, no external service dependency for MVP
- **Dependencies**: reasoning/core maintainers, infra owner for rollout automation, policy owner for gate rules

## Workstreams
1. **Architecture**: normalized state schema + platform module boundaries
2. **Protocol**: policy simulation and result contract (`SimulationResult`)
3. **Reliability**: calibration drift gating + lineage replay checks
4. **Benchmark**: baseline runtime checks for sandbox and analytics aggregation
5. **Ops**: readiness checklist, runbook drafts, observability metrics map
6. **Migration**: README proposal removal and docs replacement with implemented status

## Backlog (Epic → Story → Task + measurable acceptance criteria)

### Epic A: State Persistence & Lineage
- **Story A1**: Persist state snapshot with normalized tables
  - Task A1.1: Implement `LogenesisStateStore.initialize_schema`
    - AC: `state_snapshot`, `state_intent`, `state_lineage` tables created in clean DB.
  - Task A1.2: Implement `write_snapshot` + lineage link
    - AC: Child snapshot query returns deterministic tuple of child IDs.
- **Story A2**: Causality path tracing
  - Task A2.1: Implement BFS lineage traversal
    - AC: Path from root to descendant resolved in <= O(V+E) traversal.

### Epic B: Policy & Confidence Control
- **Story B1**: Uncertainty calibration monitoring
  - Task B1.1: Add calibration bins + threshold gate
    - AC: drift threshold check returns boolean gate signal.
- **Story B2**: Policy A/B simulation
  - Task B2.1: Evaluate scenario corpus across policy variants
    - AC: Each variant reports allow/block counts + allow_rate.

### Epic C: Memory & Analytics
- **Story C1**: Adaptive memory compaction
  - Task C1.1: Rank by salience + recency
    - AC: selected set size equals `max_items`; high-salience retained first.
- **Story C2**: Cross-run trend dashboard core
  - Task C2.1: Aggregate run metrics
    - AC: returns rounded average intent/coherence values.

### Epic D: Operational Readiness
- **Story D1**: Regression tests
  - Task D1.1: Add platform extension tests
    - AC: pytest suite passes for storage, lineage, calibration, policy sandbox, compaction, analytics.

## Options, tradeoffs, and recommendation
1. **Option 1: In-memory only modules**
   - Pros: lowest complexity, fast prototype
   - Cons: no replay durability, weak auditability
2. **Option 2: SQLite-normalized store + in-memory services (Chosen)**
   - Pros: deterministic local durability, easy CI execution, no external dependency
   - Cons: limited horizontal scale
3. **Option 3: External OLTP + stream analytics**
   - Pros: high-scale, richer observability
   - Cons: infra cost and integration overhead

**Why chosen**: Option 2 gives strongest reliability-to-cost ratio for current maturity and supports immediate testability.

## Risks, failure modes, mitigation
- **Risk**: policy evaluator divergence from production checker
  - Mitigation: shared rule fixtures + parity tests.
- **Risk**: calibration bins become stale under domain drift
  - Mitigation: scheduled recalibration and drift alert threshold reviews.
- **Risk**: memory compaction drops rare critical context
  - Mitigation: protected-tag override path and minimum retention floor.
- **Failure mode**: lineage cycles introduced by bad ingest
  - Mitigation: DAG validation before write and cycle-detection test.

## Rollout / Rollback plan
- **Owner**: Platform Engineering (primary), Policy Team (co-owner for sandbox rules)
- **Timeline**:
  - Week 1: merge modules + tests
  - Week 2: enable calibration gating in staging
  - Week 3: run policy A/B simulation on production shadow corpus
  - Week 4: promote as default path
- **Rollout steps**:
  1. Deploy schema initialization and module package.
  2. Enable write-path to state store in staging.
  3. Activate calibration gate warnings (non-blocking).
  4. Switch policy sandbox from sample corpus to live replay corpus.
- **Rollback steps**:
  1. Disable platform extension entrypoints via feature flag.
  2. Revert to legacy reasoning flow without gating enforcement.
  3. Preserve DB tables for forensic analysis; stop writes.

## Definition of Done (production)
- **Tests**: unit tests for all platform modules green in CI.
- **SLO gates**: in-memory graph/sandbox operations maintain p95 < 50ms on baseline dataset.
- **Benchmarking gates**: repeatable benchmark script with threshold assertions.
- **Observability**: emit counters for policy allow-rate, calibration drift max, compaction retention ratio.
- **Runbooks**: incident steps for drift breach, policy mismatch, lineage corruption.
- **Security checks**: schema write paths parameterized; no dynamic SQL string interpolation.

## Single-source-of-truth cleanup
Redundant proposal sections have been removed from `README.md`; implemented capability list now points to concrete modules and tests.
