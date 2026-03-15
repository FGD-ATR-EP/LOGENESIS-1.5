from logenesis.reasoning.multipath import MultiPathReasoner


def test_multipath_reasoning_bounded_and_optional():
    reasoner = MultiPathReasoner(max_nodes=3)
    root, explored = reasoner.run("evaluate risk", enable=True)
    assert len(explored) <= 3
    assert root.terminal_status == "bounded_complete"

    root2, explored2 = reasoner.run("evaluate risk", enable=False)
    assert root2.terminal_status == "skipped"
    assert explored2 == []
