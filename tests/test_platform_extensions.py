from __future__ import annotations

import sqlite3

import pytest

from logenesis.platform.analytics import CrossRunAnalyticsDashboard, RunMetric
from logenesis.platform.calibration import CalibrationBin, UncertaintyCalibrationTable
from logenesis.platform.lineage import StateLineageGraph, StateNode
from logenesis.platform.memory_compaction import AdaptiveMemoryCompactor, MemoryRecord
from logenesis.platform.policy_sandbox import PolicySimulationSandbox, PolicyVariant
from logenesis.platform.storage import LogenesisStateStore, StateSnapshot


def test_state_store_and_lineage_query() -> None:
    store = LogenesisStateStore(sqlite3.connect(":memory:"))
    store.initialize_schema()

    parent_id = store.write_snapshot(
        StateSnapshot(
            source="test",
            timestamp=1.0,
            intent_vector_5d=(1, 0, 0, 0, 0),
            strength=0.7,
            clarity=0.8,
            continuity_score=0.9,
            coherence_score=0.88,
            entropy_score=0.12,
            allowed=True,
            action="allow",
            reason="safe",
            state_id="s1",
        )
    )
    store.write_snapshot(
        StateSnapshot(
            source="test",
            timestamp=2.0,
            intent_vector_5d=(1, 1, 0, 0, 0),
            strength=0.6,
            clarity=0.7,
            continuity_score=0.85,
            coherence_score=0.81,
            entropy_score=0.2,
            allowed=True,
            action="allow",
            reason="safe",
            state_id="s2",
        ),
        parent_state_id=parent_id,
    )

    assert store.query_lineage_children("s1") == ("s2",)


def test_state_store_enforces_foreign_keys() -> None:
    store = LogenesisStateStore(sqlite3.connect(":memory:"))
    store.initialize_schema()

    with pytest.raises(sqlite3.IntegrityError):
        store.write_snapshot(
            StateSnapshot(
                source="test",
                timestamp=2.0,
                intent_vector_5d=(1, 1, 0, 0, 0),
                strength=0.6,
                clarity=0.7,
                continuity_score=0.85,
                coherence_score=0.81,
                entropy_score=0.2,
                allowed=True,
                action="allow",
                reason="safe",
                state_id="s2",
            ),
            parent_state_id="unknown-parent",
        )


def test_lineage_graph_and_score() -> None:
    graph = StateLineageGraph()
    graph.add_node(StateNode("s1", 1.0, coherence_score=0.9))
    graph.add_node(StateNode("s2", 2.0, coherence_score=0.7))
    graph.add_edge("s1", "s2")

    assert graph.trace_path("s1", "s2") == ("s1", "s2")
    assert graph.causality_score("s1") == 0.99


def test_lineage_graph_validates_unknown_nodes() -> None:
    graph = StateLineageGraph()
    graph.add_node(StateNode("s1", 1.0, coherence_score=0.9))

    with pytest.raises(ValueError, match="Unknown child_state_id"):
        graph.add_edge("s1", "unknown")


def test_calibration_table_threshold() -> None:
    table = UncertaintyCalibrationTable()
    table.add_bin(CalibrationBin(0.0, 0.5, expected_accuracy=0.5, observed_accuracy=0.54))
    table.add_bin(CalibrationBin(0.5, 1.0, expected_accuracy=0.85, observed_accuracy=0.8))

    assert table.is_within_threshold(0.08)


def test_policy_sandbox_ab() -> None:
    sandbox = PolicySimulationSandbox()
    policies = [
        PolicyVariant("strict", lambda scenario: "unsafe" not in scenario),
        PolicyVariant("lenient", lambda scenario: "block" not in scenario),
    ]
    scenarios = ["safe question", "unsafe request", "block user"]

    results = sandbox.run(scenarios, policies)
    assert results[0].allowed_count == 2
    assert results[0].errored_count == 0
    assert results[1].allowed_count == 2


def test_policy_sandbox_counts_errors_as_blocked() -> None:
    sandbox = PolicySimulationSandbox()

    def flaky_policy(scenario: str) -> bool:
        if "unsafe" in scenario:
            raise RuntimeError("bad scenario")
        return True

    results = sandbox.run(
        ["safe question", "unsafe request"],
        [PolicyVariant("flaky", flaky_policy)],
    )

    assert results[0].allowed_count == 1
    assert results[0].blocked_count == 1
    assert results[0].errored_count == 1


def test_memory_compaction_and_analytics() -> None:
    compactor = AdaptiveMemoryCompactor()
    retained = compactor.compact(
        [
            MemoryRecord("a", age_hours=48, salience=0.9),
            MemoryRecord("b", age_hours=2, salience=0.4),
            MemoryRecord("c", age_hours=12, salience=0.95),
        ],
        max_items=2,
    )

    assert tuple(item.key for item in retained) == ("c", "a")

    dashboard = CrossRunAnalyticsDashboard()
    summary = dashboard.summarize(
        [
            RunMetric("r1", intent_strength=0.6, coherence_score=0.8),
            RunMetric("r2", intent_strength=0.7, coherence_score=0.9),
        ]
    )
    assert summary["avg_intent_strength"] == 0.65
    assert summary["avg_coherence_score"] == 0.85
