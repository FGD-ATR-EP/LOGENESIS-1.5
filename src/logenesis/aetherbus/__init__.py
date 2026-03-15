"""AetherBus transport and envelope primitives."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable

from .bus import AetherBus as JetStreamAetherBus
from .envelope import AkashicEnvelope

Handler = Callable[[dict[str, Any]], None]


@dataclass
class AetherBus:
    """In-process publish/subscribe bus for local tests and offline runtime."""

    _handlers: dict[str, list[Handler]] = field(default_factory=lambda: defaultdict(list))

    def subscribe(self, topic: str, handler: Handler) -> None:
        self._handlers[topic].append(handler)

    def publish(self, topic: str, event: dict[str, Any]) -> None:
        for handler in self._handlers.get(topic, []):
            handler(event)


__all__ = ["AetherBus", "JetStreamAetherBus", "AkashicEnvelope"]
