from logenesis.resonance import ResonanceMapper


def test_calculate_resonance_returns_weighted_scores() -> None:
    mapper = ResonanceMapper()

    scores = mapper.calculate_resonance("explore this domain")

    assert "explore" in scores
    assert scores["explore"] > 0.0


def test_generate_intent_vector_returns_5d_vector() -> None:
    mapper = ResonanceMapper(threshold=0.0)

    vector = mapper.generate_intent_vector("explore and resolve")

    assert len(vector) == 5
    assert any(value != 0.0 for value in vector)
