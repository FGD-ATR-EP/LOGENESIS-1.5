from logenesis.reasoning.multipath import MultiPathReasoner
from logenesis.schemas.models import RoutePath


def test_multipath_reasoning_bounded_and_terminates_with_budget() -> None:
    reasoner = MultiPathReasoner(max_nodes=3, branching_limit=2)
    root, explored = reasoner.run("evaluate risk", enable=True, route=RoutePath.DELIBERATIVE)

    assert len(explored) <= 3
    assert root.terminal_status in {"solved", "stalled"}


def test_multipath_prunes_invalid_branches() -> None:
    reasoner = MultiPathReasoner(max_nodes=4, branching_limit=2, risk_threshold=0.05)
    _, explored = reasoner.run("evaluate risk", enable=True, route=RoutePath.DELIBERATIVE)

    assert any(node.terminal_status == "pruned" for node in explored)


def test_multipath_activation_is_optional_and_deliberative_only() -> None:
    reasoner = MultiPathReasoner(max_nodes=3, deliberative_only=True)

    root_fast, explored_fast = reasoner.run("evaluate risk", enable=True, route=RoutePath.FAST)
    assert root_fast.terminal_status == "stalled"
    assert explored_fast == []

    root_disabled, explored_disabled = reasoner.run("evaluate risk", enable=False, route=RoutePath.DELIBERATIVE)
    assert root_disabled.terminal_status == "stalled"
    assert explored_disabled == []
