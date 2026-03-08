"""Default resonance atoms and helper builders."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResonanceAtomSpec:
    """Immutable resonance atom specification."""

    pattern: str
    weight: float
    vector: tuple[float, float, float, float, float]
    urgency: float


DEFAULT_RESONANCE_ATOMS: tuple[ResonanceAtomSpec, ...] = (
    ResonanceAtomSpec("explore", 0.8, (0.1, 0.2, 0.3, 0.4, 0.5), 0.7),
    ResonanceAtomSpec("resolve", 0.9, (-0.1, -0.2, 0.3, 0.4, 0.5), 0.8),
    ResonanceAtomSpec("abstract", 0.7, (0.5, 0.4, 0.3, 0.2, 0.1), 0.5),
    ResonanceAtomSpec("concrete", 0.6, (-0.5, -0.4, 0.3, 0.2, 0.1), 0.4),
    ResonanceAtomSpec("sub-obj", 0.5, (0.1, 0.2, -0.3, 0.4, 0.5), 0.6),
    ResonanceAtomSpec("div-conv", 0.4, (-0.1, 0.2, 0.3, -0.4, 0.5), 0.4),
    ResonanceAtomSpec("pass-act", 0.3, (0.1, -0.2, 0.3, 0.4, -0.5), 0.3),
)
