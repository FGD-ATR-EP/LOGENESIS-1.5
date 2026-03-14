"""MIRAS memory policy: retention, contamination control, and audited commits."""
from __future__ import annotations

import math
from dataclasses import dataclass

from logenesis.memory.diffmem import GitBasedDiffMemory
from logenesis.memory.gems_of_wisdom import GemsOfWisdomStorage
from logenesis.platform.calibration import CalibrationBin, UncertaintyCalibrationTable
from logenesis.platform.lineage import StateLineageGraph, StateNode
from logenesis.platform.memory_compaction import AdaptiveMemoryCompactor, MemoryRecord
from logenesis.reasoning.public_contracts import PublicReasoningResult
from logenesis.reasoning.thought_node import ThoughtNode


ALLOWED_MEMORY_CLASSES = {
    "stable_solution",
    "reusable_strategy",
    "failure_lesson",
    "policy_update_hint",
    "calibration_signal",
    "episode_summary",
}


@dataclass(frozen=True)
class MemoryArtifact:
    memory_class: str
    key: str
    content: str
    score: float
    rsi_risk: float
    reuse: float
    novelty: float
    pollution_risk: float


@dataclass(frozen=True)
class MemoryCommitResult:
    committed: bool
    commit_ref: str | None
    reason: str


class MIRASPolicy:
    """Memory policy layer integrating Gems, DiffMem, compaction, lineage, calibration."""

    def __init__(
        self,
        gems: GemsOfWisdomStorage,
        diffmem: GitBasedDiffMemory,
        compactor: AdaptiveMemoryCompactor,
        lineage: StateLineageGraph,
        calibration: UncertaintyCalibrationTable,
    ) -> None:
        self._gems = gems
        self._diffmem = diffmem
        self._compactor = compactor
        self._lineage = lineage
        self._calibration = calibration
        self._records: list[MemoryRecord] = []

    def initial_importance(self, artifact: MemoryArtifact) -> float:
        return (
            0.45 * artifact.score
            + 0.2 * (1 - artifact.rsi_risk)
            + 0.2 * artifact.reuse
            + 0.15 * artifact.novelty
        )

    def retention_value(self, artifact: MemoryArtifact, age_hours: int, usage: float, reinforcement: float) -> float:
        i0 = self.initial_importance(artifact)
        return max(0.0, i0 * math.exp(-0.04 * age_hours) + 0.25 * usage + 0.15 * reinforcement - 0.3 * artifact.pollution_risk)

    def commit_allowed_artifact(self, artifact: MemoryArtifact, final_status: str) -> MemoryCommitResult:
        if artifact.memory_class not in ALLOWED_MEMORY_CLASSES:
            return MemoryCommitResult(False, None, "memory_class_not_allowed")
        if final_status != "stable" and artifact.memory_class == "stable_solution":
            return MemoryCommitResult(False, None, "stable_solution_requires_stable_episode")
        if artifact.pollution_risk > 0.6:
            return MemoryCommitResult(False, None, "pollution_risk_too_high")

        self._gems.add_gem(f"{artifact.memory_class}:{artifact.content}")
        ref = self._diffmem.write_snapshot(
            relative_file=f"{artifact.memory_class}/{artifact.key}.txt",
            content=artifact.content,
            message=f"miras:{artifact.memory_class}:{artifact.key}",
        )
        self._records.append(MemoryRecord(key=artifact.key, age_hours=0, salience=self.initial_importance(artifact)))
        return MemoryCommitResult(True, ref, "committed")

    def compact(self, max_items: int = 10) -> tuple[MemoryRecord, ...]:
        return self._compactor.compact(self._records, max_items=max_items)

    def register_episode_outcome(self, episode_id: str, node: ThoughtNode, result: PublicReasoningResult) -> None:
        self._lineage.add_node(StateNode(state_id=node.state_snapshot_id, timestamp=float(len(self._records)), coherence_score=node.verification_result.coherence_score))
        self._calibration.add_bin(
            CalibrationBin(
                lower_bound=max(0.0, result.confidence - 0.1),
                upper_bound=min(1.0, result.confidence + 0.1),
                expected_accuracy=result.confidence,
                observed_accuracy=max(0.0, result.confidence - result.risk * 0.5),
            )
        )
