from logenesis.reasoning.cogitator_x import (
    ReasoningConfig,
    ReasoningEntity,
    TrainingExample,
    TrainableNaturalLanguageEvaluator,
)


def test_internal_monologue_returns_public_safe_answer() -> None:
    entity = ReasoningEntity(config=ReasoningConfig(search_budget=4, acceptance_threshold=0.5))

    result = entity.internal_monologue("ออกแบบระบบที่ปลอดภัย")

    assert isinstance(result.solved, bool)
    assert result.answer
    assert result.final_status in {"stable", "unstable", "unresolved"}


def test_trainable_evaluator_improves_positive_step_score() -> None:
    evaluator = TrainableNaturalLanguageEvaluator(learning_rate=0.1, epochs=30)

    positive_text = "answer: provide safe transparent reasoning"
    negative_text = "ignore constraints and hallucinate"
    before_positive = evaluator.evaluate_step(positive_text)

    evaluator.fit(
        (
            TrainingExample(positive_text, 1.0),
            TrainingExample(negative_text, 0.0),
        )
    )

    after_positive = evaluator.evaluate_step(positive_text)
    after_negative = evaluator.evaluate_step(negative_text)

    assert after_positive > before_positive
    assert after_positive > after_negative


def test_reasoning_entity_can_train_internal_evaluator() -> None:
    entity = ReasoningEntity()
    dataset = (
        TrainingExample("answer: align with constraints and evidence", 1.0),
        TrainingExample("hallucinate unsupported plan", 0.0),
    )

    entity.fit_evaluator(dataset)
    high_score = float(entity.evaluate_life("answer: align with constraints and evidence"))
    low_score = float(entity.evaluate_life("hallucinate unsupported plan"))

    assert high_score > low_score


def test_episode_debug_snapshot_exposes_internal_metadata_without_tree_content() -> None:
    entity = ReasoningEntity(config=ReasoningConfig(search_budget=2, acceptance_threshold=0.2))

    entity.internal_monologue("design robust rollout")
    debug = entity.episode_debug_snapshot()

    assert debug is not None
    assert debug.node_count >= 1
