from logenesis.response.response_planner import ResponsePlanner
from logenesis.schemas.models import VerificationResult


def test_abstain_over_hallucinate_behavior():
    planner = ResponsePlanner()
    verification = VerificationResult(aggregate_score=0.2, abstain=True)
    text = planner.render("invented answer", verification)
    assert "abstaining" in text.lower()


def test_contradiction_aware_response_shaping():
    planner = ResponsePlanner()
    verification = VerificationResult(
        aggregate_score=0.55,
        abstain=False,
        soft_fail=True,
        uncertainty_factors=["context_drift_detected", "commitment_gap"],
    )
    text = planner.render("answer candidate", verification)
    assert "Public rationale:" in text
    assert "Uncertainty:" in text
