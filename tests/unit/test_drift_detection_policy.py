from logenesis.context_governor.drift_detector import DriftDetector
from logenesis.schemas.models import DialogueLedger, TopicFrame


def test_drift_detects_unrelated_long_turn():
    detector = DriftDetector()
    topic = TopicFrame(active_topic="finance", canonical_terms=["budget", "cashflow"])
    ledger = DialogueLedger(turn_index=3)
    text = "this long message discusses astronomy galaxies and telescopes without matching money terms"
    assert detector.detect(topic, ledger, text=text) is True


def test_drift_not_detected_when_focus_terms_present():
    detector = DriftDetector()
    topic = TopicFrame(active_topic="finance", canonical_terms=["budget", "cashflow"])
    ledger = DialogueLedger(turn_index=3)
    text = "this long message stays on finance budget and cashflow planning for next quarter"
    assert detector.detect(topic, ledger, text=text) is False
