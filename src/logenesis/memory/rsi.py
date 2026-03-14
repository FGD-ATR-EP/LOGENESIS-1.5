from __future__ import annotations


class RSI:
    """Reflective self-improvement summaries; post-episode only."""

    def summarize_episode(self, events: list[str]) -> str:
        return f"episode_summary:{len(events)}_events"
