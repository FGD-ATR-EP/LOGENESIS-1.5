from logenesis.memory.rsi import RSI
from logenesis.schemas.models import EpisodicEvent


def test_rsi_runs_post_episode_only():
    rsi = RSI()
    events = [EpisodicEvent(conversation_id="c", turn_id="t", event_type="success", summary="event")]
    assert rsi.summarize_episode(events, episode_closed=False) == "rsi_skipped_active_episode"
    assert "episode_summary" in rsi.summarize_episode(events, episode_closed=True)


def test_rsi_post_episode_extracts_lessons_and_gems():
    rsi = RSI()
    events = [
        EpisodicEvent(conversation_id="c", turn_id="1", event_type="failure", summary="failed due to contradiction", significant=True),
        EpisodicEvent(conversation_id="c", turn_id="2", event_type="commit", summary="reusable strategy", significant=True),
    ]
    summary = rsi.summarize_episode(events, episode_closed=True)
    assert "lessons=1" in summary
    assert "successes=1" in summary
    assert "gems=" in summary
