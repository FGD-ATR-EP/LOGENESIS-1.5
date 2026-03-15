from __future__ import annotations

from dataclasses import dataclass

from logenesis.reasoning.backpropagation import backpropagate
from logenesis.reasoning.expansion import expand_node
from logenesis.reasoning.pruning import prune_nodes
from logenesis.reasoning.selection import select_node
from logenesis.reasoning.termination import TerminationPolicy, should_terminate
from logenesis.reasoning.thought_node import RiskProfile, ThoughtNode, VerificationResult
from logenesis.reasoning.verifier import VerificationPolicy
from logenesis.schemas.models import RoutePath


@dataclass(frozen=True)
class SearchConfig:
    search_budget: int = 10
    branching_limit: int = 2
    max_depth: int = 3
    risk_threshold: float = 0.7
    deliberative_only: bool = True
    target_confidence: float = 0.82
    max_stagnant_rounds: int = 3


class BoundedSearchController:
    def __init__(self, config: SearchConfig | None = None):
        self.config = config or SearchConfig()
        self.verifier = VerificationPolicy()
        self.termination_policy = TerminationPolicy(
            target_confidence=self.config.target_confidence,
            max_stagnant_rounds=self.config.max_stagnant_rounds,
        )

    def run(self, hypothesis: str, *, enable: bool = True, route: RoutePath | str | None = None) -> tuple[ThoughtNode, list[ThoughtNode]]:
        root = ThoughtNode(
            node_id="root",
            parent_id=None,
            state_snapshot_id="s-0",
            content=hypothesis,
            action_type="infer",
            depth=0,
            local_score=0.65,
            aggregated_score=0.65,
            verification_result=VerificationResult(
                valid_hard=True,
                process_score=0.7,
                truthfulness_score=0.65,
                coherence_score=0.7,
                constraint_score=0.65,
            ),
            risk_profile=RiskProfile(0.2, 0.15, 0.1, 0.1, 0.15, 0.14),
            commit_eligible=True,
        )

        if not enable:
            root.terminal_status = "stalled"
            root.commit_eligible = False
            return root, []

        normalized_route = RoutePath(route).value if isinstance(route, str) and route in {"fast", "deliberative"} else route
        if self.config.deliberative_only and normalized_route not in {None, RoutePath.DELIBERATIVE}:
            root.terminal_status = "stalled"
            root.commit_eligible = False
            return root, []

        frontier: list[ThoughtNode] = [root]
        explored: list[ThoughtNode] = []
        pruned_nodes: list[ThoughtNode] = []
        score_history: list[float] = []
        termination_reason: str | None = None

        while frontier:
            current = select_node(frontier)
            if current is None:
                termination_reason = "stagnation"
                break
            frontier.remove(current)
            explored.append(current)
            current.visit_count += 1
            score_history.append(current.aggregated_score)

            termination_reason = should_terminate(
                explored_count=len(explored),
                budget=self.config.search_budget,
                score_history=score_history,
                target_confidence=self.termination_policy.target_confidence,
                max_stagnant_rounds=self.termination_policy.max_stagnant_rounds,
            )
            if termination_reason:
                break

            if current.depth >= self.config.max_depth:
                continue

            children = expand_node(
                current,
                branching_limit=self.config.branching_limit,
                verifier=self.verifier,
                constraints=(),
            )
            kept, pruned = prune_nodes(children, risk_threshold=self.config.risk_threshold)
            current.child_ids.extend(child.node_id for child in kept)
            frontier.extend(kept)
            pruned_nodes.extend(pruned)

        root = backpropagate(root, explored)
        if termination_reason == "confidence_reached":
            root.terminal_status = "solved"
        elif termination_reason == "budget_exhausted":
            root.terminal_status = "stalled"
        elif termination_reason == "stagnation":
            root.terminal_status = "stalled"

        root.commit_eligible = len(pruned_nodes) == 0 and root.verification_result.valid_hard
        return root, explored + pruned_nodes
