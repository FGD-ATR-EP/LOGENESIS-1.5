from logenesis.reasoning.cogitator_x import ReasoningEntity


def test_public_result_hides_internal_reasoning_tree() -> None:
    reasoner = ReasoningEntity()
    public = reasoner.run_public_episode("Plan constrained migration")

    assert hasattr(public, "stable_summary")
    assert not hasattr(public, "trace")
    assert "node" not in public.stable_summary.lower()
