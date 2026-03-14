"""Git-backed memory helpers (DiffMem) for auditable long-term memory."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitBasedDiffMemory:
    """Persist memory snapshots inside a dedicated git repository."""

    repo_path: Path

    def __post_init__(self) -> None:
        self.repo_path = Path(self.repo_path)
        self.repo_path.mkdir(parents=True, exist_ok=True)
        if not (self.repo_path / ".git").exists():
            self._run("git", "init")

    def write_snapshot(self, relative_file: str, content: str, message: str) -> str:
        if not message.strip():
            raise ValueError("commit message must not be empty")

        safe_relative = Path(relative_file)
        if safe_relative.is_absolute() or ".." in safe_relative.parts:
            raise ValueError("relative_file must stay within the memory repository")

        file_path = self.repo_path / safe_relative
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

        self._run("git", "add", str(safe_relative))
        commit_result = self._run(
            "git",
            "-c",
            "user.name=Logenesis Bot",
            "-c",
            "user.email=bot@logenesis.local",
            "commit",
            "-m",
            message,
            check=False,
        )
        if commit_result.returncode == 1:
            details = (commit_result.stderr + "\n" + commit_result.stdout).lower()
            if "nothing to commit" not in details and "no changes added" not in details:
                raise RuntimeError(commit_result.stderr.strip() or commit_result.stdout.strip())
        elif commit_result.returncode != 0:
            raise RuntimeError(commit_result.stderr.strip() or commit_result.stdout.strip())

        return self._run("git", "rev-parse", "HEAD").stdout.strip()

    def history(self, limit: int = 10) -> tuple[str, ...]:
        if limit <= 0:
            return ()
        result = self._run("git", "rev-parse", "--verify", "HEAD", check=False)
        if result.returncode != 0:
            return ()
        log = self._run("git", "log", "--pretty=format:%s", "-n", str(limit)).stdout
        return tuple(log.splitlines()) if log.strip() else ()

    def _run(self, *command: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(command, cwd=self.repo_path, text=True, capture_output=True, check=False)
        if check and result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        return result


class DiffMem:
    """Lightweight in-memory diff tracker used by MIRAS flow stubs."""

    def __init__(self):
        self.changes: list[str] = []

    def record(self, diff: str) -> None:
        self.changes.append(diff)
