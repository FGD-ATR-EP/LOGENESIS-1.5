from logenesis.reasoning.cogitator_x import ReasoningEntity


def test_public_result_hides_internal_reasoning_tree() -> None:
    reasoner = ReasoningEntity()
    public = reasoner.run_public_episode("Plan constrained migration")

    assert hasattr(public, "answer_summary")
    assert hasattr(public, "best_node")
    assert not hasattr(public, "tree")
    assert "node" not in public.answer_summary.lower()
