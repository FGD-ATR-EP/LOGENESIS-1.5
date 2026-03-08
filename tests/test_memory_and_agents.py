from pathlib import Path

import pytest

from logenesis.aetherbus import AetherBus
from logenesis.agents import PangenesAgent
from logenesis.memory import GemsOfWisdomStorage, GitBasedDiffMemory


def test_gems_of_wisdom_stores_and_returns_context() -> None:
    storage = GemsOfWisdomStorage()

    storage.add_gem("Always verify source quality before publishing")

    assert storage.retrieve_active_context() == (
        "Always verify source quality before publishing",
    )


def test_gems_of_wisdom_rejects_empty_lesson() -> None:
    storage = GemsOfWisdomStorage()

    with pytest.raises(ValueError, match="must not be empty"):
        storage.add_gem("   ")


def test_pangenes_agent_learns_from_validation_failure() -> None:
    storage = GemsOfWisdomStorage()
    agent = PangenesAgent(memory_storage=storage)

    event = agent.execute_and_audit(
        {
            "intent_id": "INTENT-1",
            "payload": {"summary": "unsafe summary", "source_list": []},
        }
    )

    assert event["status"] == "FAILED"
    assert storage.retrieve_active_context()


def test_diffmem_persists_history_with_git(tmp_path: Path) -> None:
    diffmem = GitBasedDiffMemory(repo_path=tmp_path / "memory_repo")

    _ = diffmem.write_snapshot("gems/lesson.txt", "learned lesson", "add first gem")

    assert "add first gem" in diffmem.history(limit=1)


def test_diffmem_returns_empty_history_before_first_commit(tmp_path: Path) -> None:
    diffmem = GitBasedDiffMemory(repo_path=tmp_path / "memory_repo")

    assert diffmem.history() == ()


def test_diffmem_rejects_path_traversal(tmp_path: Path) -> None:
    diffmem = GitBasedDiffMemory(repo_path=tmp_path / "memory_repo")

    with pytest.raises(ValueError, match="must stay within"):
        _ = diffmem.write_snapshot("../escape.txt", "bad", "reject traversal")


def test_diffmem_allows_idempotent_write_without_crash(tmp_path: Path) -> None:
    diffmem = GitBasedDiffMemory(repo_path=tmp_path / "memory_repo")
    first = diffmem.write_snapshot("gems/lesson.txt", "same", "first")
    second = diffmem.write_snapshot("gems/lesson.txt", "same", "same content")

    assert first == second


def test_aetherbus_publish_subscribe() -> None:
    bus = AetherBus()
    captured: list[str] = []

    def _collect(event: dict[str, str]) -> None:
        captured.append(event["message"])

    bus.subscribe("memory.events", _collect)
    bus.publish("memory.events", {"message": "Gem added"})

    assert captured == ["Gem added"]
