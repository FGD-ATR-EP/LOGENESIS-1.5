"""Cogitator-X natural-language reasoning architecture with trainable scoring."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Protocol, Sequence


class StepEvaluator(Protocol):
    """Protocol for process reward evaluation."""

    def evaluate_step(self, thought_step: str) -> float:
        """Return a normalized score in [0, 1] for a thought step."""


@dataclass(frozen=True)
class ReasoningConfig:
    """Inference-time scaling configuration."""

    max_thinking_tokens: int = 5000
    search_budget: int = 12
    acceptance_threshold: float = 0.55


@dataclass(frozen=True)
class ReasoningResult:
    """Public output from a hidden reasoning pass."""

    answer: str
    solved: bool
    explored_steps: int
    best_score: float
    trace: tuple[str, ...]


@dataclass(frozen=True)
class TrainingExample:
    """Single supervised sample for thought-step quality."""

    thought_step: str
    target_score: float


@dataclass
class TrainableNaturalLanguageEvaluator:
    """Trainable linear scorer over natural-language tokens.

    The model learns token contributions directly from examples where each
    thought step is labeled by a process reward in [0, 1].
    """

    learning_rate: float = 0.08
    epochs: int = 15
    token_weights: dict[str, float] = field(default_factory=dict)
    bias: float = 0.0

    def evaluate_step(self, thought_step: str) -> float:
        features = self._extract_features(thought_step)
        logit = self.bias + sum(self.token_weights.get(token, 0.0) * value for token, value in features.items())
        return _sigmoid(logit)

    def fit(self, dataset: Sequence[TrainingExample]) -> None:
        """Train the evaluator with SGD over tokenized natural-language traces."""
        for _ in range(self.epochs):
            for example in dataset:
                features = self._extract_features(example.thought_step)
                prediction = self.evaluate_step(example.thought_step)
                target = _clamp(example.target_score, 0.0, 1.0)
                error = target - prediction

                self.bias += self.learning_rate * error
                for token, value in features.items():
                    current = self.token_weights.get(token, 0.0)
                    self.token_weights[token] = current + (self.learning_rate * error * value)

    def _extract_features(self, text: str) -> dict[str, float]:
        tokens = [token.strip(".,:;!?()[]{}\"'").lower() for token in text.split()]
        return {token: 1.0 for token in tokens if token}


class ReasoningEntity:
    """System-2 style reasoner with search, reflection, and trainable scoring."""

    def __init__(
        self,
        evaluator: StepEvaluator | None = None,
        config: ReasoningConfig | None = None,
    ) -> None:
        self._evaluator = evaluator or TrainableNaturalLanguageEvaluator()
        self._config = config or ReasoningConfig()
        self._thought_tree: list[str] = []

    @property
    def thought_tree(self) -> tuple[str, ...]:
        """Return immutable access to current search trace."""
        return tuple(self._thought_tree)

    def fit_evaluator(self, dataset: Sequence[TrainingExample]) -> None:
        """Train the internal evaluator if it supports fitting."""
        if not hasattr(self._evaluator, "fit"):
            raise TypeError("Configured evaluator is not trainable.")
        self._evaluator.fit(dataset)  # type: ignore[attr-defined]

    def evaluate_life(self, step_content: str, criterion: str = "process_reward") -> float | bool:
        """Evaluate a candidate thought by score or terminal completeness."""
        if criterion == "process_reward":
            return self._evaluator.evaluate_step(step_content)

        if criterion == "completeness":
            return "ANSWER:" in step_content

        raise ValueError(f"Unsupported criterion: {criterion}")

    def internal_monologue(self, problem_input: str) -> ReasoningResult:
        """Run a bounded search loop that supports self-correction."""
        self._thought_tree.clear()
        current_state = problem_input.strip()
        best_score = 0.0

        for step in range(self._config.search_budget):
            candidates = self.generate_next_thoughts(current_state)

            best_candidate = ""
            candidate_score = -1.0
            for candidate in candidates:
                score = float(self.evaluate_life(candidate, "process_reward"))
                if score > candidate_score:
                    candidate_score = score
                    best_candidate = candidate

            if candidate_score < self._config.acceptance_threshold:
                self.experience_empathy(
                    previous_state=current_state,
                    rejected_candidate=best_candidate,
                    score=candidate_score,
                )
                continue

            current_state = best_candidate
            self._thought_tree.append(current_state)
            best_score = max(best_score, candidate_score)

            if bool(self.evaluate_life(current_state, "completeness")):
                return ReasoningResult(
                    answer=self.synthesize_answer(current_state),
                    solved=True,
                    explored_steps=step + 1,
                    best_score=best_score,
                    trace=self.thought_tree,
                )

        return ReasoningResult(
            answer=self.synthesize_answer(current_state),
            solved=False,
            explored_steps=self._config.search_budget,
            best_score=best_score,
            trace=self.thought_tree,
        )

    def generate_next_thoughts(self, state: str) -> tuple[str, ...]:
        """Create candidate next steps in natural language."""
        return (
            f"Understand constraints and stakeholders from: {state}",
            f"Derive verifiable intermediate conclusion from: {state}",
            f"ANSWER: Draft final strategy for {state}",
        )

    def experience_empathy(self, previous_state: str, rejected_candidate: str, score: float) -> None:
        """Apply lightweight policy shift to avoid repeating low-value branches."""
        note = (
            "REFLECT: avoid branch "
            f"'{rejected_candidate}' from '{previous_state}' with score={score:.2f}"
        )
        self._thought_tree.append(note)

    def synthesize_answer(self, terminal_state: str) -> str:
        """Convert final search state into user-facing summary."""
        if "ANSWER:" in terminal_state:
            return terminal_state.split("ANSWER:", maxsplit=1)[1].strip()

        return f"Refined direction: {terminal_state}"


def build_default_reasoner() -> ReasoningEntity:
    """Factory for a ready-to-use trainable natural-language reasoner."""
    evaluator = TrainableNaturalLanguageEvaluator()
    evaluator.fit(
        (
            TrainingExample("ANSWER: provide safe and transparent plan", 0.95),
            TrainingExample("derive evidence and constraints before action", 0.9),
            TrainingExample("ignore policy and hallucinate details", 0.05),
        )
    )
    return ReasoningEntity(evaluator=evaluator)


def _sigmoid(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exp_value = math.exp(value)
    return exp_value / (1.0 + exp_value)


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))
