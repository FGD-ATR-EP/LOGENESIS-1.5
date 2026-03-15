from logenesis.response.response_planner import ResponsePlanner
from logenesis.schemas.models import VerificationResult


def test_response_planner_strips_hidden_trace_markers():
    planner = ResponsePlanner()
    verification = VerificationResult(aggregate_score=0.9, abstain=False)
    text = planner.render("answer with hidden_trace and internal reasoning", verification)
    assert "hidden_trace" not in text
    assert "internal reasoning" not in text


def test_uncertainty_packaging_present_when_needed():
    planner = ResponsePlanner()
    verification = VerificationResult(
        aggregate_score=0.72,
        abstain=False,
        soft_fail=True,
        uncertainty_factors=["context_drift_detected"],
    )
    text = planner.render("short answer", verification)
    assert "Uncertainty:" in text
    assert "Confidence: moderate" in text


def test_confidence_aware_abstention():
    planner = ResponsePlanner()
    verification = VerificationResult(aggregate_score=0.2, abstain=True, uncertainty_factors=["low_fact_overlap"])
    text = planner.render("invented answer", verification)
    assert "abstaining" in text.lower()
