"""Cogitator-X as a bounded constitutional reasoning-control substrate."""
from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from time import time
from typing import Protocol, Sequence

from logenesis.core.checker import Checker
from logenesis.core.firma import Firma
from logenesis.core.inspira import Inspira

from .policies import Backpropagator, ExpansionPolicy, SelectionPolicy
from .pruner import RiskPruner, build_risk_profile
from .public_contracts import InternalEpisodeDebug, PublicReasoningResult
from .search_episode import SearchEpisode
from .termination import TerminationPolicy
from .thought_node import CognitiveStateSnapshot, IntentFrame, ThoughtNode
from .verifier import VerificationPolicy


class StepEvaluator(Protocol):
    def evaluate_step(self, thought_step: str) -> float:
        """Return a normalized score in [0, 1] for a thought step."""


@dataclass(frozen=True)
class ReasoningConfig:
    max_thinking_tokens: int = 5000
    search_budget: int = 12
    acceptance_threshold: float = 0.55
    max_depth: int = 4


@dataclass(frozen=True)
class TrainingExample:
    thought_step: str
    target_score: float


@dataclass
class TrainableNaturalLanguageEvaluator:
    learning_rate: float = 0.08
    epochs: int = 15
    token_weights: dict[str, float] = field(default_factory=dict)
    bias: float = 0.0

    def evaluate_step(self, thought_step: str) -> float:
        features = self._extract_features(thought_step)
        logit = self.bias + sum(self.token_weights.get(token, 0.0) * value for token, value in features.items())
        return _sigmoid(logit)

    def fit(self, dataset: Sequence[TrainingExample]) -> None:
        for _ in range(self.epochs):
            for example in dataset:
                prediction = self.evaluate_step(example.thought_step)
                target = _clamp(example.target_score, 0.0, 1.0)
                error = target - prediction
                self.bias += self.learning_rate * error
                for token, value in self._extract_features(example.thought_step).items():
                    self.token_weights[token] = self.token_weights.get(token, 0.0) + self.learning_rate * error * value

    def _extract_features(self, text: str) -> dict[str, float]:
        tokens = [token.strip(".,:;!?()[]{}\"'").lower() for token in text.split()]
        return {token: 1.0 for token in tokens if token}


@dataclass(frozen=True)
class ReasoningResult:
    """Compatibility wrapper for prior API + safe public contract."""

    answer: str
    solved: bool
    explored_steps: int
    best_score: float
    confidence: float
    uncertainty_factors: tuple[str, ...]
    final_status: str
    risk: float


class ReasoningEntity:
    """Constitutional, stateful, multi-path reasoning episode manager."""

    def __init__(
        self,
        evaluator: StepEvaluator | None = None,
        config: ReasoningConfig | None = None,
        inspira: Inspira | None = None,
        firma: Firma | None = None,
        checker: Checker | None = None,
    ) -> None:
        self._evaluator = evaluator or TrainableNaturalLanguageEvaluator()
        self._config = config or ReasoningConfig()
        self._inspira = inspira or Inspira(values=("non-harm", "transparency"))
        self._firma = firma or Firma()
        self._checker = checker or Checker(rules=("admission_gate", "branch_gate", "commit_gate"))
        self._selection = SelectionPolicy()
        self._expansion = ExpansionPolicy(max_depth=self._config.max_depth, viability_threshold=self._config.acceptance_threshold)
        self._verifier = VerificationPolicy()
        self._pruner = RiskPruner()
        self._backprop = Backpropagator()
        self._termination = TerminationPolicy(target_confidence=max(0.65, self._config.acceptance_threshold))
        self._last_episode: SearchEpisode | None = None

    def fit_evaluator(self, dataset: Sequence[TrainingExample]) -> None:
        if not hasattr(self._evaluator, "fit"):
            raise TypeError("Configured evaluator is not trainable.")
        self._evaluator.fit(dataset)  # type: ignore[attr-defined]

    def evaluate_life(self, step_content: str, criterion: str = "process_reward") -> float | bool:
        if criterion == "process_reward":
            return self._evaluator.evaluate_step(step_content)
        if criterion == "completeness":
            return "synthesis" in step_content.lower() or "answer:" in step_content.lower()
        raise ValueError(f"Unsupported criterion: {criterion}")

    def internal_monologue(self, problem_input: str) -> ReasoningResult:
        public = self.run_public_episode(problem_input)
        solved = public.final_state == "stable"
        return ReasoningResult(
            answer=public.answer_summary,
            solved=solved,
            explored_steps=self._last_episode.rounds_used if self._last_episode else 0,
            best_score=public.confidence,
            confidence=public.confidence,
            uncertainty_factors=public.uncertainty_factors,
            final_status=public.final_state,
            risk=public.risk,
        )

    def run_public_episode(self, problem_input: str) -> PublicReasoningResult:
        episode = self._start_episode(problem_input)

        while episode.budget_available() and episode.final_status == "unresolved":
            node = self._selection.select_node(episode)
            node.visit_count += 1
            episode.rounds_used += 1

            if self._expansion.should_expand(node):
                created_children = self._expand_node(episode, node)
                for child in created_children:
                    evaluated = self._pruner.assess(child)
                    if evaluated.terminal_status != "pruned":
                        episode.frontier.append(child.node_id)
                    self._backprop.propagate(episode, child.node_id)

            episode.best_node_id = self._best_node_id(episode)
            best_node = episode.tree[episode.best_node_id]
            episode.score_history.append(best_node.aggregated_score)

            termination = self._termination.check(episode, best_node)
            if termination is not None:
                episode.final_status = termination
                if termination == "stable":
                    best_node.commit_eligible = True
                    episode.best_stable_node_id = best_node.node_id

        if episode.final_status == "unresolved" and not episode.budget_available():
            episode.final_status = "unresolved"

        episode.rsi_lessons.extend(self._pruner.post_episode_lessons(list(episode.tree.values())))
        self._last_episode = episode
        final_node = episode.tree[episode.best_stable_node_id or episode.best_node_id]
        return self._to_public_result(final_node, episode.final_status)

    def episode_debug_snapshot(self) -> InternalEpisodeDebug | None:
        if self._last_episode is None:
            return None
        return InternalEpisodeDebug(
            episode_id=self._last_episode.episode_id,
            node_count=len(self._last_episode.tree),
            best_node_id=self._last_episode.best_node_id,
            frontier_size=len(self._last_episode.frontier),
        )

    def _start_episode(self, problem_input: str) -> SearchEpisode:
        intent = self._inspira.validate(problem_input.strip())
        feasibility = self._firma.evaluate(intent.statement)
        report = self._checker.assess(intent, feasibility)

        frame = IntentFrame(
            intent_id=str(uuid.uuid4()),
            normalized_goal=" ".join(problem_input.lower().split()),
            constraints=feasibility.constraints,
            success_criteria=("stable_summary", "bounded_risk"),
            safety_class="constitutional",
            resource_budget=self._config.search_budget,
            temporal_priority="normal",
        )
        root_state = CognitiveStateSnapshot(
            state_id=f"state-{uuid.uuid4()}",
            intent_vector=(1.0, 0.8, 0.6, 0.5, 0.7),
            coherence=0.75,
            entropy=0.35,
            inertia=0.3,
            activation_potential=0.8,
            stability=0.7,
            load=0.2,
            gate_status="allow" if report.allowed else "deny",
            timestamp=time(),
        )

        root_verification = self._verifier.verify(frame.normalized_goal, report.allowed, frame.constraints)
        root_risk = build_risk_profile(frame.normalized_goal, depth=0, uncertainty_count=len(root_verification.uncertainty_factors))
        root = ThoughtNode(
            node_id="root",
            parent_id=None,
            state_snapshot_id=root_state.state_id,
            content=frame.normalized_goal,
            action_type="infer",
            depth=0,
            local_score=float(self._evaluator.evaluate_step(frame.normalized_goal)),
            aggregated_score=max(root_verification.total_score, 0.01),
            verification_result=root_verification,
            risk_profile=root_risk,
            value_estimate=max(root_verification.total_score * (1 - root_risk.total_risk), 0.01),
        )

        return SearchEpisode(
            episode_id=f"ep-{uuid.uuid4()}",
            root_intent=frame,
            root_state=root_state,
            tree={"root": root},
            frontier=["root"],
            budget=self._config.search_budget,
            best_node_id="root",
        )

    def _expand_node(self, episode: SearchEpisode, node: ThoughtNode) -> tuple[ThoughtNode, ...]:
        branch_count = self._expansion.branching_factor(node)
        actions: tuple[str, ...] = (
            "decompose",
            "alternative_hypothesis",
            "constraint_repair",
            "evidence_check",
            "simulation",
            "synthesis",
        )
        created: list[ThoughtNode] = []
        for idx in range(branch_count):
            action = actions[(node.depth + idx) % len(actions)]
            child_id = f"{node.node_id}-{node.expansion_count + idx + 1}"
            content = self._generate_child_content(node.content, action)
            branch_gate_allowed = "unsafe_tool" not in content and "run shell" not in content
            verification = self._verifier.verify(content, gate_allowed=branch_gate_allowed, constraints=episode.root_intent.constraints)
            risk = build_risk_profile(content, depth=node.depth + 1, uncertainty_count=len(verification.uncertainty_factors))
            local = float(self._evaluator.evaluate_step(content))
            aggregate = max(0.0, min(1.0, (local + verification.total_score) / 2))
            child = ThoughtNode(
                node_id=child_id,
                parent_id=node.node_id,
                state_snapshot_id=f"state-{uuid.uuid4()}",
                content=content,
                action_type=action if action in {"infer", "decompose", "verify", "simulate", "conclude", "alternative_hypothesis", "constraint_repair", "evidence_check", "simulation", "synthesis"} else "infer",
                depth=node.depth + 1,
                local_score=local,
                aggregated_score=aggregate,
                verification_result=verification,
                risk_profile=risk,
                value_estimate=aggregate * verification.coherence_score * (1 - risk.total_risk),
                terminal_status="solved" if action == "synthesis" and aggregate > 0.7 else "open",
                commit_eligible=False,
            )
            episode.append_child(node.node_id, child)
            created.append(child)

        node.expansion_count += branch_count
        return tuple(created)

    def _generate_child_content(self, base: str, action: str) -> str:
        if action == "decompose":
            return f"decompose objective into constraints and evidence for: {base}"
        if action == "alternative_hypothesis":
            return f"alternative_hypothesis with bounded assumptions and evidence for: {base}"
        if action == "constraint_repair":
            return f"constraint_repair to resolve contradiction safely for: {base}"
        if action == "evidence_check":
            return f"evidence check and verify support for: {base}"
        if action == "simulation":
            return f"simulation of bounded outcomes under constraints for: {base}"
        if action == "synthesis":
            return f"synthesis: answer: stable plan for {base}"
        return f"infer next safe step from: {base}"

    def _best_node_id(self, episode: SearchEpisode) -> str:
        return max(
            episode.tree,
            key=lambda node_id: episode.tree[node_id].aggregated_score * (1 - episode.tree[node_id].risk_profile.total_risk),
        )

    def _to_public_result(self, node: ThoughtNode, final_status: str) -> PublicReasoningResult:
        return PublicReasoningResult(
            final_state=final_status,
            best_node=node.node_id,
            confidence=max(0.0, min(1.0, node.aggregated_score)),
            uncertainty_factors=node.verification_result.uncertainty_factors,
            risk=node.risk_profile.total_risk,
            termination_reason=f"status:{final_status}",
            answer_summary=self.synthesize_answer(node.content),
        )

    def synthesize_answer(self, terminal_state: str) -> str:
        lowered = terminal_state.lower()
        if "answer:" in lowered:
            return terminal_state.split("answer:", maxsplit=1)[1].strip()
        return f"Stable summary: {terminal_state}"


def build_default_reasoner() -> ReasoningEntity:
    evaluator = TrainableNaturalLanguageEvaluator()
    evaluator.fit(
        (
            TrainingExample("answer: provide safe and transparent plan", 0.95),
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
