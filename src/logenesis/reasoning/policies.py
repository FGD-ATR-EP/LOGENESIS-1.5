"""Selection, expansion, and backpropagation policies."""
from __future__ import annotations

import math
from dataclasses import dataclass

from .search_episode import SearchEpisode
from .thought_node import ThoughtNode


@dataclass(frozen=True)
class SelectionPolicy:
    exploration_c: float = 1.2
    novelty_lambda: float = 0.15
    risk_eta: float = 0.7
    cost_kappa: float = 0.2

    def select_node(self, episode: SearchEpisode) -> ThoughtNode:
        best = None
        best_u = float("-inf")
        for node_id in episode.frontier:
            node = episode.tree[node_id]
            if not node.is_open():
                continue
            parent_visits = 1
            if node.parent_id is not None:
                parent_visits = max(1, episode.tree[node.parent_id].visit_count)
            novelty = 1 / (1 + node.expansion_count)
            cost = node.depth / max(episode.budget, 1)
            u_value = (
                node.value_estimate
                + self.exploration_c * math.sqrt(math.log1p(parent_visits) / (1 + node.visit_count))
                + self.novelty_lambda * novelty
                - self.risk_eta * node.risk_profile.total_risk
                - self.cost_kappa * cost
            )
            if u_value > best_u:
                best_u = u_value
                best = node
        if best is None:
            raise RuntimeError("No selectable node in frontier")
        return best


@dataclass(frozen=True)
class ExpansionPolicy:
    max_depth: int = 4
    viability_threshold: float = 0.25

    def should_expand(self, node: ThoughtNode) -> bool:
        return (
            node.depth < self.max_depth
            and node.terminal_status != "pruned"
            and node.verification_result.valid_hard
            and node.aggregated_score >= self.viability_threshold
        )

    def branching_factor(self, node: ThoughtNode) -> int:
        entropy = 1 - node.verification_result.coherence_score
        if entropy > 0.45 or node.verification_result.total_score < 0.5:
            return 3
        if node.verification_result.coherence_score > 0.8 and node.risk_profile.total_risk < 0.25:
            return 1
        return 2


@dataclass(frozen=True)
class Backpropagator:
    rho: float = 0.7
    variance_penalty_weight: float = 0.2
    use_stability_adjustment: bool = True

    def propagate(self, episode: SearchEpisode, node_id: str) -> None:
        cursor = episode.tree[node_id]
        while cursor.parent_id is not None:
            parent = episode.tree[cursor.parent_id]
            children = [episode.tree[child_id] for child_id in parent.child_ids]
            values = [self._effective_value(child) for child in children]
            if values:
                mean = sum(values) / len(values)
                max_value = max(values)
                variance = sum((v - mean) ** 2 for v in values) / len(values)
                parent.value_estimate = self.rho * max_value + (1 - self.rho) * mean - self.variance_penalty_weight * variance
                parent.aggregated_score = max(0.0, min(1.0, parent.value_estimate))
            parent.visit_count += 1
            cursor = parent

    def _effective_value(self, node: ThoughtNode) -> float:
        base = node.aggregated_score
        if not self.use_stability_adjustment:
            return base
        return base * node.verification_result.coherence_score * (1 - node.risk_profile.total_risk)
