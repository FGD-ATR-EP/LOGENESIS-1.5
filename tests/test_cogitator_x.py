from logenesis.reasoning.cogitator_x import ReasoningConfig, ReasoningEntity


def test_internal_monologue_runs_multi_step_before_answer() -> None:
    entity = ReasoningEntity(
        ReasoningConfig(search_budget=4, acceptance_threshold=0.82, max_thinking_tokens=100)
    )

    result = entity.internal_monologue("explain safe rollout")

    assert len(result.trace) >= 2
    assert any("ANALYSIS" in step for step in result.trace)
    assert result.final_answer.startswith("step-2 ANSWER:")


def test_generate_next_thoughts_changes_with_iteration_and_exclusions() -> None:
    entity = ReasoningEntity()

    first = entity.generate_next_thoughts("task", current_state=(), iteration=0)
    second = entity.generate_next_thoughts(
        "task", current_state=("dummy",), iteration=1, excluded_candidates=first
    )

    assert first
    assert second
    assert set(first).isdisjoint(set(second))


def test_max_thinking_tokens_limits_trace_growth() -> None:
    entity = ReasoningEntity(
        ReasoningConfig(search_budget=6, acceptance_threshold=0.95, max_thinking_tokens=6)
    )

    result = entity.internal_monologue("very constrained prompt")

    assert result.stopped_due_to_budget is True
    assert len(result.trace) <= 1
