from __future__ import annotations


class RSI:
    """Reflective self-improvement summaries; post-episode only."""

    def summarize_episode(self, events: list[str], episode_closed: bool = False) -> str:
        if not episode_closed:
            return "rsi_skipped_active_episode"
        lessons = len([e for e in events if "fail" in e.lower() or "abstain" in e.lower()])
        return f"episode_summary:{len(events)}_events:lessons={lessons}"
