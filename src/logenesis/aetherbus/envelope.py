"""AkashicEnvelope serialization helpers for AetherBus."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import time
from typing import Any


@dataclass(frozen=True)
class AkashicEnvelope:
    """A canonical event envelope for AetherBus payloads."""

    subject: str
    source: str
    payload: dict[str, Any]
    urgency: float
    timestamp: float

    @classmethod
    def build(
        cls,
        subject: str,
        source: str,
        payload: dict[str, Any],
        urgency: float,
    ) -> "AkashicEnvelope":
        """Construct envelope with monotonic creation timestamp."""
        return cls(
            subject=subject,
            source=source,
            payload=payload,
            urgency=max(0.0, min(urgency, 1.0)),
            timestamp=time.time(),
        )

    def to_bytes(self) -> bytes:
        """Serialize envelope to compact UTF-8 JSON bytes."""
        return json.dumps(asdict(self), separators=(",", ":")).encode("utf-8")
