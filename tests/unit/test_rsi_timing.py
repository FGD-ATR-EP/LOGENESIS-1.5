from logenesis.memory.rsi import RSI


def test_rsi_runs_post_episode_only():
    rsi = RSI()
    assert rsi.summarize_episode(["event"], episode_closed=False) == "rsi_skipped_active_episode"
    assert "episode_summary" in rsi.summarize_episode(["event"], episode_closed=True)
