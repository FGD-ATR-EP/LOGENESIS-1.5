from logenesis.response.response_planner import ResponsePlanner
from logenesis.schemas.models import VerificationResult


def test_response_planner_strips_hidden_trace_markers():
    planner = ResponsePlanner()
    verification = VerificationResult(aggregate_score=0.9, abstain=False)
    text = planner.render("answer with hidden_trace and internal reasoning", verification)
    assert "hidden_trace" not in text
    assert "internal reasoning" not in text
