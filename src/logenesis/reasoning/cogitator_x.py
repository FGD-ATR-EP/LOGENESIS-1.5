"""Cogitator-X reasoning architecture with process-level supervision."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


class StepEvaluator(Protocol):
    """Protocol for process reward evaluation."""

    def evaluate_step(self, thought_step: str) -> float:
        """Return a normalized score in [0, 1] for a thought step."""


class KeywordProcessRewardModel:
    """Deterministic PRM approximation for local reasoning traces."""

    def __init__(self, positive_markers: Sequence[str], negative_markers: Sequence[str]) -> None:
        self._positive_markers = tuple(marker.lower() for marker in positive_markers)
        self._negative_markers = tuple(marker.lower() for marker in negative_markers)

    def evaluate_step(self, thought_step: str) -> float:
        lowered = thought_step.lower()
        positive_hits = sum(marker in lowered for marker in self._positive_markers)
        negative_hits = sum(marker in lowered for marker in self._negative_markers)

        raw_score = 0.5 + (0.15 * positive_hits) - (0.2 * negative_hits)
        return _clamp(raw_score, 0.0, 1.0)


@dataclass(frozen=True)
class ReasoningConfig:
    """Inference-time scaling configuration."""

    max_thinking_tokens: int = 5000
    search_budget: int = 12
    acceptance_threshold: float = 0.55


@dataclass(frozen=True)
class ReasoningResult:
    """Public, verifiable output from a hidden reasoning pass."""

    answer: str
    solved: bool
    explored_steps: int
    best_score: float
    trace: tuple[str, ...]


class ReasoningEntity:
    """System-2 style reasoner with search, reflection, and backtracking."""

    def __init__(self, evaluator: StepEvaluator, config: ReasoningConfig | None = None) -> None:
        self._evaluator = evaluator
        self._config = config or ReasoningConfig()
        self._thought_tree: list[str] = []

    @property
    def thought_tree(self) -> tuple[str, ...]:
        """Return immutable access to current search trace."""
        return tuple(self._thought_tree)

    def evaluate_life(self, step_content: str, criterion: str = "process_reward") -> float | bool:
        """Evaluate a candidate thought by PRM score or terminal completeness."""
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
        """Create multiple candidate next steps to approximate Tree-of-Thought."""
        return (
            f"Inspect constraints from: {state}",
            f"Derive intermediate claim from: {state}",
            f"ANSWER: Consolidated solution for {state}",
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
    """Factory for a ready-to-use Cogitator-X reasoner."""
    evaluator = KeywordProcessRewardModel(
        positive_markers=("answer", "derive", "constraint", "solution"),
        negative_markers=("ignore", "hallucination", "contradiction"),
    )
    return ReasoningEntity(evaluator=evaluator)


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))
