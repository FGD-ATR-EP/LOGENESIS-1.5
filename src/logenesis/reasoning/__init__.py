"""Reasoning subsystem for bounded constitutional multi-path cognition."""

from .cogitator_x import (
    ReasoningConfig,
    ReasoningEntity,
    ReasoningResult,
    TrainableNaturalLanguageEvaluator,
    TrainingExample,
    build_default_reasoner,
)
from .public_contracts import PublicReasoningResult

__all__ = [
    "PublicReasoningResult",
    "ReasoningConfig",
    "ReasoningEntity",
    "ReasoningResult",
    "TrainableNaturalLanguageEvaluator",
    "TrainingExample",
    "build_default_reasoner",
]
