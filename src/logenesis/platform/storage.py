"""SQLite-backed state storage for platform extensions."""
from __future__ import annotations

from dataclasses import dataclass
import json
import sqlite3
from typing import Sequence
from uuid import uuid4


@dataclass(frozen=True)
class StateSnapshot:
    """Minimal state snapshot model persisted in storage."""

    source: str
    timestamp: float
    intent_vector_5d: tuple[float, float, float, float, float]
    strength: float
    clarity: float
    continuity_score: float
    coherence_score: float
    entropy_score: float
    allowed: bool
    action: str
    reason: str
    state_id: str | None = None


class LogenesisStateStore:
    """Normalize and persist state snapshots for analytics and replay."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._db = connection
        self._db.execute("PRAGMA foreign_keys = ON")

    def initialize_schema(self) -> None:
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS state_snapshot (
                state_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                timestamp REAL NOT NULL,
                schema_version TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS state_intent (
                state_id TEXT PRIMARY KEY,
                intent_vector_5d TEXT NOT NULL,
                strength REAL NOT NULL,
                clarity REAL NOT NULL,
                multiplicity INTEGER NOT NULL,
                FOREIGN KEY(state_id) REFERENCES state_snapshot(state_id)
            );

            CREATE TABLE IF NOT EXISTS state_temporal (
                state_id TEXT PRIMARY KEY,
                continuity_score REAL NOT NULL,
                FOREIGN KEY(state_id) REFERENCES state_snapshot(state_id)
            );

            CREATE TABLE IF NOT EXISTS state_coherence (
                state_id TEXT PRIMARY KEY,
                coherence_score REAL NOT NULL,
                FOREIGN KEY(state_id) REFERENCES state_snapshot(state_id)
            );

            CREATE TABLE IF NOT EXISTS state_entropy (
                state_id TEXT PRIMARY KEY,
                entropy_score REAL NOT NULL,
                FOREIGN KEY(state_id) REFERENCES state_snapshot(state_id)
            );

            CREATE TABLE IF NOT EXISTS state_gate (
                state_id TEXT PRIMARY KEY,
                allowed INTEGER NOT NULL,
                action TEXT NOT NULL,
                reason TEXT NOT NULL,
                FOREIGN KEY(state_id) REFERENCES state_snapshot(state_id)
            );

            CREATE TABLE IF NOT EXISTS state_lineage (
                parent_state_id TEXT NOT NULL,
                child_state_id TEXT NOT NULL,
                PRIMARY KEY(parent_state_id, child_state_id),
                FOREIGN KEY(parent_state_id) REFERENCES state_snapshot(state_id),
                FOREIGN KEY(child_state_id) REFERENCES state_snapshot(state_id)
            );
            """
        )
        self._db.commit()

    def write_snapshot(self, snapshot: StateSnapshot, parent_state_id: str | None = None) -> str:
        state_id = snapshot.state_id or str(uuid4())
        multiplicity = len([value for value in snapshot.intent_vector_5d if value != 0])

        with self._db:
            self._db.execute(
                "INSERT INTO state_snapshot(state_id, source, timestamp, schema_version) VALUES (?, ?, ?, ?)",
                (state_id, snapshot.source, snapshot.timestamp, "1.5-platform"),
            )
            self._db.execute(
                "INSERT INTO state_intent(state_id, intent_vector_5d, strength, clarity, multiplicity) VALUES (?, ?, ?, ?, ?)",
                (
                    state_id,
                    json.dumps(snapshot.intent_vector_5d),
                    snapshot.strength,
                    snapshot.clarity,
                    multiplicity,
                ),
            )
            self._db.execute(
                "INSERT INTO state_temporal(state_id, continuity_score) VALUES (?, ?)",
                (state_id, snapshot.continuity_score),
            )
            self._db.execute(
                "INSERT INTO state_coherence(state_id, coherence_score) VALUES (?, ?)",
                (state_id, snapshot.coherence_score),
            )
            self._db.execute(
                "INSERT INTO state_entropy(state_id, entropy_score) VALUES (?, ?)",
                (state_id, snapshot.entropy_score),
            )
            self._db.execute(
                "INSERT INTO state_gate(state_id, allowed, action, reason) VALUES (?, ?, ?, ?)",
                (state_id, int(snapshot.allowed), snapshot.action, snapshot.reason),
            )

            if parent_state_id is not None:
                self._db.execute(
                    "INSERT INTO state_lineage(parent_state_id, child_state_id) VALUES (?, ?)",
                    (parent_state_id, state_id),
                )
        return state_id

    def query_lineage_children(self, parent_state_id: str) -> Sequence[str]:
        rows = self._db.execute(
            "SELECT child_state_id FROM state_lineage WHERE parent_state_id = ? ORDER BY child_state_id",
            (parent_state_id,),
        ).fetchall()
        return tuple(row[0] for row in rows)
