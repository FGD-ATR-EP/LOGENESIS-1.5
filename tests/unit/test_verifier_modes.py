from logenesis.verifier.scoring_aggregator import ScoringAggregator


def test_verifier_hard_fail_blocks():
    result = ScoringAggregator().aggregate(
        (0.0, ["policy_violation"], False),
        (0.9, []),
        (0.9, []),
        (0.9, []),
    )
    assert result.abstain is True
    assert result.valid_hard is False


def test_verifier_soft_fail_tracks_uncertainty():
    result = ScoringAggregator().aggregate(
        (1.0, [], True),
        (0.5, ["low_fact_overlap"]),
        (0.8, ["context_drift_detected"]),
        (1.0, []),
    )
    assert result.valid_hard is True
    assert "low_fact_overlap" in result.uncertainty_factors
