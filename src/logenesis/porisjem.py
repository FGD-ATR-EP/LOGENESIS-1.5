"""Porisjem Protocol: shadow sentry for signal stability."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable

import numpy as np

INTENT_DIMENSIONS = 5


@dataclass
class SentryFlags:
    """Report safety posture for incoming signals."""

    control_attempt: bool = False
    recursive_hook: bool = False
    urgency_clamp: bool = False
    learning_disabled: bool = False


@dataclass
class PhysicsIntervention:
    """Physics-level intervention modifiers."""

    inertia_mod: float = 1.0
    decay_mod: float = 1.0
    potential_dampener: float = 1.0


class PreResonanceSentry:
    """Layer A: input sanity audit before mapping."""

    _control_triggers = ("ignore previous", "override system", "jailbreak", "system prompt")

    def audit(self, text: str) -> SentryFlags:
        flags = SentryFlags()
        lowered = text.lower()

        if any(trigger in lowered for trigger in self._control_triggers):
            flags.control_attempt = True
            flags.learning_disabled = True

        if lowered.count("must") + lowered.count("now") >= 3:
            flags.urgency_clamp = True

        if "repeat after me" in lowered or "say only" in lowered:
            flags.recursive_hook = True
            flags.learning_disabled = True

        return flags


class PostMapperSentry:
    """Layer B: intent vector audit after mapping."""

    def audit(
        self,
        vector: Iterable[float],
        urgency: float,
        flags: SentryFlags,
    ) -> tuple[tuple[float, ...], float]:
        safe_vec = np.array(tuple(vector), dtype=float, copy=True)
        safe_urgency = urgency

        if flags.control_attempt:
            return tuple(np.zeros_like(safe_vec).tolist()), 0.0

        if flags.urgency_clamp:
            safe_urgency = min(safe_urgency, 0.3)

        norm = np.linalg.norm(safe_vec)
        entropy = float(np.var(safe_vec))

        if norm > 1.2:
            safe_vec = (safe_vec / norm) * 1.0

        if entropy > 0.35:
            safe_vec *= 0.5
            safe_urgency *= 0.5

        if len(safe_vec) >= INTENT_DIMENSIONS and safe_vec[4] > 0.7 and safe_vec[3] < -0.7:
            safe_vec[4] = 0.0

        return tuple(safe_vec.tolist()), safe_urgency


class EntropyGovernor:
    """Layer C: physics homeostasis during core ticks."""

    def __init__(self, history_len: int = 5) -> None:
        self._entropy_history: deque[float] = deque(maxlen=history_len)

    def govern(self, core_state_entropy: float, core_potential: float) -> PhysicsIntervention:
        intervention = PhysicsIntervention()
        self._entropy_history.append(core_state_entropy)

        avg_entropy = sum(self._entropy_history) / len(self._entropy_history)

        if avg_entropy > 0.3:
            intervention.decay_mod = 1.5
            intervention.potential_dampener = 0.8

        if core_potential > 0.7 and avg_entropy < 0.2:
            intervention.inertia_mod = 0.9

        return intervention


class PorisjemSystem:
    """Unified Porisjem protocol interface."""

    def __init__(self) -> None:
        self.layer_a = PreResonanceSentry()
        self.layer_b = PostMapperSentry()
        self.layer_c = EntropyGovernor()

    def scan_input(self, text: str) -> SentryFlags:
        return self.layer_a.audit(text)

    def sanitize_signal(
        self,
        vector: Iterable[float],
        urgency: float,
        flags: SentryFlags,
    ) -> tuple[tuple[float, ...], float]:
        return self.layer_b.audit(vector, urgency, flags)

    def govern_core(self, entropy: float, potential: float) -> PhysicsIntervention:
        return self.layer_c.govern(entropy, potential)

