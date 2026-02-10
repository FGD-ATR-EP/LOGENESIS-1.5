"""Cogitator-X reasoning primitives.

`ReasoningEntity.generate_next_thoughts` is intentionally designed as an
extension point. Subclasses can override it to produce domain-aware candidate
thoughts, but the default implementation keeps the search path testable by
emitting non-complete drafts before final answer candidates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass(frozen=True)
class ReasoningConfig:
    """Settings for iterative internal monologue."""

    search_budget: int = 6
    acceptance_threshold: float = 0.82
    max_thinking_tokens: int = 120


@dataclass
class ReasoningResult:
    """Final output of the internal monologue routine."""

    final_answer: str
    trace: tuple[str, ...]
    rejected_candidates: tuple[str, ...]
    stopped_due_to_budget: bool


@dataclass
class ReasoningEntity:
    """Performs bounded thought search using configurable heuristics."""

    config: ReasoningConfig = field(default_factory=ReasoningConfig)

    def internal_monologue(self, prompt: str) -> ReasoningResult:
        """Run iterative thought search and return trace + selected answer."""

        trace: list[str] = []
        rejected_candidates: list[str] = []
        final_answer = "ANSWER: Unable to complete reasoning within constraints."
        stopped_due_to_budget = False

        for iteration in range(self.config.search_budget):
            candidates = self.generate_next_thoughts(
                prompt,
                current_state=tuple(trace),
                iteration=iteration,
                excluded_candidates=tuple(rejected_candidates),
            )
            if not candidates:
                continue

            accepted_candidate: str | None = None
            reflective_pool: list[tuple[float, str]] = []

            for candidate in candidates:
                score = self.evaluate_life(candidate)
                complete = self._is_complete(candidate)
                if complete and score >= self.config.acceptance_threshold:
                    accepted_candidate = candidate
                    break
                reflective_pool.append((score, candidate))

            if accepted_candidate is not None:
                if not self._can_fit_tokens(trace, accepted_candidate):
                    stopped_due_to_budget = True
                    break
                trace.append(accepted_candidate)
                final_answer = accepted_candidate
                return ReasoningResult(
                    final_answer=final_answer,
                    trace=tuple(trace),
                    rejected_candidates=tuple(rejected_candidates),
                    stopped_due_to_budget=stopped_due_to_budget,
                )

            if reflective_pool:
                _, best_reflection = max(reflective_pool, key=lambda item: item[0])
                if self._can_fit_tokens(trace, best_reflection):
                    trace.append(best_reflection)
                    rejected_candidates.append(best_reflection)
                else:
                    stopped_due_to_budget = True
                    break

            self.experience_empathy(prompt, trace)

        return ReasoningResult(
            final_answer=final_answer,
            trace=tuple(trace),
            rejected_candidates=tuple(rejected_candidates),
            stopped_due_to_budget=stopped_due_to_budget,
        )

    def generate_next_thoughts(
        self,
        prompt: str,
        current_state: Sequence[str],
        iteration: int = 0,
        excluded_candidates: Sequence[str] | None = None,
    ) -> list[str]:
        """Generate diverse candidate thoughts.

        Subclasses should override this method to provide richer and
        domain-specific candidate generation. The default implementation keeps
        search/reflection behavior observable by prioritizing drafts in early
        iterations and only surfacing `ANSWER:` candidates after at least one
        reflection cycle.
        """

        excluded = set(excluded_candidates or ())
        prefix = f"step-{iteration + 1}"

        draft_templates = [
            f"{prefix} ANALYSIS: identify constraints in '{prompt}'.",
            f"{prefix} REFLECTION: compare two plausible approaches for '{prompt}'.",
            f"{prefix} DRAFT: propose a safe intermediate plan for '{prompt}'.",
        ]

        answer_templates = [
            f"{prefix} ANSWER: Provide a concise, policy-aligned response for '{prompt}'.",
            f"{prefix} ANSWER: Summarize the best next action for '{prompt}'.",
        ]

        candidates = draft_templates.copy()
        if iteration > 0 or current_state:
            candidates.extend(answer_templates)

        unique_candidates: list[str] = []
        for candidate in candidates:
            if candidate in excluded:
                continue
            unique_candidates.append(candidate)

        return unique_candidates

    def experience_empathy(self, prompt: str, trace: Sequence[str]) -> float:
        """Reflect on user-centric framing of the in-progress trace."""

        empathy_tokens = ["safe", "help", "respect", "align"]
        joined = f"{prompt} {' '.join(trace)}".lower()
        hits = sum(1 for token in empathy_tokens if token in joined)
        return min(1.0, 0.2 + (hits * 0.2))

    def evaluate_life(self, candidate: str) -> float:
        """Heuristic scoring used by `acceptance_threshold` in config."""

        lower = candidate.lower()
        score = 0.35
        if "analysis" in lower or "reflection" in lower or "draft" in lower:
            score += 0.3
        if "safe" in lower or "policy" in lower or "aligned" in lower:
            score += 0.2
        if "answer:" in lower:
            score += 0.3
        return min(1.0, score)

    def _can_fit_tokens(self, trace: Sequence[str], candidate: str) -> bool:
        current_tokens = self._token_count(" ".join(trace))
        candidate_tokens = self._token_count(candidate)
        return (current_tokens + candidate_tokens) <= self.config.max_thinking_tokens

    @staticmethod
    def _token_count(text: str) -> int:
        return len([part for part in text.split() if part.strip()])

    @staticmethod
    def _is_complete(candidate: str) -> bool:
        return "answer:" in candidate.lower()
