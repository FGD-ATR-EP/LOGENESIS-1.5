"""Resonance Mapper: human language to intent physics vectors."""
from __future__ import annotations

from dataclasses import dataclass, field
import difflib
from typing import Iterable, Sequence

import numpy as np

from .atoms import DEFAULT_RESONANCE_ATOMS

INTENT_DIMENSIONS = 5


@dataclass
class ResonanceAtom:
    """Atomic resonance pattern with vector and affective weight."""

    pattern: str
    vector: tuple[float, float, float, float, float]
    urgency: float
    weight: float
    base_weight: float = field(init=False)

    def __post_init__(self) -> None:
        self.base_weight = self.weight


@dataclass(frozen=True)
class IntentVector:
    """Fixed 5D intent vector plus urgency signal."""

    values: tuple[float, float, float, float, float]
    urgency: float


def resonance_score(text: str, pattern: str) -> float:
    """Return fuzzy similarity score without embeddings."""
    return difflib.SequenceMatcher(None, text, pattern).ratio()


def build_default_atoms() -> tuple[ResonanceAtom, ...]:
    """Build mutable atom instances from default specs."""
    return tuple(
        ResonanceAtom(
            pattern=atom.pattern,
            vector=atom.vector,
            urgency=atom.urgency,
            weight=atom.weight,
        )
        for atom in DEFAULT_RESONANCE_ATOMS
    )


class ResonanceMapper:
    """Map text to intent physics using deterministic resonance."""

    def __init__(
        self,
        atoms: Iterable[ResonanceAtom] | None = None,
        threshold: float = 0.65,
    ) -> None:
        self._atoms = list(atoms if atoms is not None else build_default_atoms())
        self._threshold = threshold
        self._active: list[tuple[ResonanceAtom, float]] = []

    @property
    def atoms(self) -> Sequence[ResonanceAtom]:
        """Return the current resonance atoms."""
        return tuple(self._atoms)

    def calculate_resonance(self, text: str) -> dict[str, float]:
        """Calculate weighted fuzzy resonance score for each atom."""
        return {
            atom.pattern: resonance_score(text, atom.pattern) * atom.weight
            for atom in self._atoms
        }

    def generate_intent_vector(self, text: str) -> list[float]:
        """Generate normalized 5D vector from atoms above threshold."""
        total_force = np.zeros(INTENT_DIMENSIONS, dtype=np.float64)

        for atom in self._atoms:
            score = resonance_score(text, atom.pattern) * atom.weight
            if score <= self._threshold:
                continue
            total_force += score * np.array(atom.vector)

        norm = np.linalg.norm(total_force)
        if norm > 0:
            total_force = total_force / norm

        return total_force.tolist()

    def map(self, text: str) -> IntentVector:
        """Return the intent vector and urgency from the given text."""
        acc_vector = [0.0] * INTENT_DIMENSIONS
        acc_urgency = 0.0
        total_weight = 0.0
        self._active = []

        for atom in self._atoms:
            score = resonance_score(text, atom.pattern)
            if score < self._threshold:
                continue

            force = score * atom.weight
            acc_vector = _add_scaled(acc_vector, atom.vector, force)
            acc_urgency += atom.urgency * force
            total_weight += force
            self._active.append((atom, score))

        if total_weight == 0.0:
            return IntentVector(values=_zero_vector(), urgency=0.0)

        normalized = tuple(value / total_weight for value in acc_vector)
        clamped = tuple(_clamp(value, -1.0, 1.0) for value in normalized)
        urgency = _clamp(acc_urgency / total_weight, 0.0, 1.0)
        return IntentVector(values=clamped, urgency=urgency)

    def update_weights(
        self,
        outcome_feedback: float,
        learning_rate: float = 0.1,
        decay: float = 0.01,
        weight_floor: float = 0.1,
        weight_ceiling: float = 5.0,
    ) -> None:
        """Apply Hebbian-style updates with homeostatic regulation."""
        for atom, score in self._active:
            delta = learning_rate * (score * outcome_feedback)
            atom.weight += delta
            atom.weight -= decay * (atom.weight - atom.base_weight)
            atom.weight = _clamp(atom.weight, weight_floor, weight_ceiling)


def _add_scaled(
    base: list[float],
    vector: tuple[float, float, float, float, float],
    scale: float,
) -> list[float]:
    return [current + (value * scale) for current, value in zip(base, vector)]


def _zero_vector() -> tuple[float, float, float, float, float]:
    return (0.0, 0.0, 0.0, 0.0, 0.0)


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))
