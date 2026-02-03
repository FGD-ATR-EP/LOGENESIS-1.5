"""Learning module: resonance-weighted updates."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResonanceUpdate:
    """Represents a bounded learning update."""

    signal: str
    weight: float


class LearningModule:
    """Capture learning signals without collapsing into raw memory dumps."""

    def record(self, signal: str, weight: float) -> ResonanceUpdate:
        """Return a resonance update with normalized weight."""
        normalized_weight = max(0.0, min(weight, 1.0))
        return ResonanceUpdate(signal=signal, weight=normalized_weight)
