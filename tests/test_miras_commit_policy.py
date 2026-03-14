from pathlib import Path

from logenesis.memory import GitBasedDiffMemory, GemsOfWisdomStorage
from logenesis.memory.miras import MIRASPolicy, MemoryArtifact
from logenesis.platform.calibration import UncertaintyCalibrationTable
from logenesis.platform.lineage import StateLineageGraph
from logenesis.platform.memory_compaction import AdaptiveMemoryCompactor


def _policy(tmp_path: Path) -> MIRASPolicy:
    return MIRASPolicy(
        gems=GemsOfWisdomStorage(),
        diffmem=GitBasedDiffMemory(tmp_path / "memory_repo"),
        compactor=AdaptiveMemoryCompactor(),
        lineage=StateLineageGraph(),
        calibration=UncertaintyCalibrationTable(),
    )


def test_miras_commits_only_allowed_artifacts(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    rejected = policy.commit_allowed_artifact(
        MemoryArtifact("unknown", "k1", "bad", 0.9, 0.1, 0.6, 0.3, 0.1),
        final_status="stable",
    )
    assert rejected.committed is False

    accepted = policy.commit_allowed_artifact(
        MemoryArtifact("stable_solution", "k2", "safe plan", 0.9, 0.1, 0.6, 0.3, 0.1),
        final_status="stable",
    )
    assert accepted.committed is True
    assert accepted.commit_ref is not None


def test_no_intermediate_branch_commit_for_unstable_episode(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    outcome = policy.commit_allowed_artifact(
        MemoryArtifact("stable_solution", "k3", "branch draft", 0.8, 0.2, 0.5, 0.2, 0.1),
        final_status="unstable",
    )
    assert outcome.committed is False
    assert outcome.reason == "stable_solution_requires_stable_episode"
