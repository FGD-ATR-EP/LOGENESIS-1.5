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
            self._run("git init")

    def write_snapshot(self, relative_file: str, content: str, message: str) -> str:
        file_path = self.repo_path / relative_file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        self._run(f"git add {relative_file}")
        self._run(
            "git -c user.name='Logenesis Bot' -c user.email='bot@logenesis.local' "
            f"commit -m \"{message}\""
        )
        return self._run("git rev-parse HEAD").strip()

    def history(self, limit: int = 10) -> tuple[str, ...]:
        log = self._run(f"git log --pretty=format:%s -n {limit}")
        if not log.strip():
            return ()
        return tuple(log.splitlines())

    def _run(self, command: str) -> str:
        result = subprocess.run(
            command,
            cwd=self.repo_path,
            shell=True,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        return result.stdout
