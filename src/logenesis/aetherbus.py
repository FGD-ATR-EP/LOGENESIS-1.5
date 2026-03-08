"""AetherBus: lightweight event transport between agents, memory, and tools."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable

Handler = Callable[[dict[str, Any]], None]


@dataclass
class AetherBus:
    """In-process publish/subscribe event bus."""

    _handlers: dict[str, list[Handler]] = field(default_factory=lambda: defaultdict(list))

    def subscribe(self, topic: str, handler: Handler) -> None:
        self._handlers[topic].append(handler)

    def publish(self, topic: str, event: dict[str, Any]) -> None:
        for handler in self._handlers.get(topic, []):
            handler(event)
