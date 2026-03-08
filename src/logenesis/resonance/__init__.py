"""Resonance mapping components for intent physics."""

from .atoms import DEFAULT_RESONANCE_ATOMS, ResonanceAtomSpec
from .mapper import IntentVector, ResonanceAtom, ResonanceMapper, build_default_atoms

__all__ = [
    "DEFAULT_RESONANCE_ATOMS",
    "IntentVector",
    "ResonanceAtom",
    "ResonanceAtomSpec",
    "ResonanceMapper",
    "build_default_atoms",
]
