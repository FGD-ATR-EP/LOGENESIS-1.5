from __future__ import annotations

from itertools import count

from logenesis.reasoning.pruner import build_risk_profile
from logenesis.reasoning.verifier import VerificationPolicy
from logenesis.reasoning.thought_node import ThoughtNode

_counter = count(1)


def expand_node(
    node: ThoughtNode,
    *,
    branching_limit: int,
    verifier: VerificationPolicy,
    constraints: tuple[str, ...],
) -> list[ThoughtNode]:
    """Expand a node with bounded branching and branch-level verification."""
    children: list[ThoughtNode] = []
    for idx in range(max(1, branching_limit)):
        content = f"{node.content} | candidate_path_{idx + 1}"
        verification = verifier.verify(content=content, gate_allowed=True, constraints=constraints)
        risk_profile = build_risk_profile(content=content, depth=node.depth + 1, uncertainty_count=len(verification.uncertainty_factors))

        child = ThoughtNode(
            node_id=f"n{next(_counter)}",
            parent_id=node.node_id,
            state_snapshot_id=f"s-{node.depth + 1}-{idx + 1}",
            content=content,
            action_type="decompose",
            depth=node.depth + 1,
            local_score=max(0.0, node.local_score - (0.03 * idx)),
            aggregated_score=max(0.0, node.aggregated_score - (0.02 * idx)),
            verification_result=verification,
            risk_profile=risk_profile,
        )
        children.append(child)

    node.expansion_count += 1
    return children
