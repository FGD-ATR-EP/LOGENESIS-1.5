from logenesis.response.response_planner import ResponsePlanner
from logenesis.schemas.models import VerificationResult


def test_abstain_over_hallucinate_behavior():
    planner = ResponsePlanner()
    verification = VerificationResult(aggregate_score=0.2, abstain=True)
    text = planner.render("invented answer", verification)
    assert "not confident" in text.lower()
