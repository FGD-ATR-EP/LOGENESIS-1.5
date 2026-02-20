"""Reasoning subsystem for System-2 style cognition."""

from .cogitator_x import (
    ReasoningConfig,
    ReasoningEntity,
    ReasoningResult,
    TrainableNaturalLanguageEvaluator,
    TrainingExample,
    build_default_reasoner,
)

__all__ = [
    "ReasoningConfig",
    "ReasoningEntity",
    "ReasoningResult",
    "TrainableNaturalLanguageEvaluator",
    "TrainingExample",
    "build_default_reasoner",
]
