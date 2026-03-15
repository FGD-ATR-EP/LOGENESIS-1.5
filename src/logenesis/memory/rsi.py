from __future__ import annotations

from logenesis.schemas.models import EpisodicEvent


class RSI:
    """Reflective self-improvement summaries; post-episode only."""

    def summarize_episode(self, events: list[EpisodicEvent], episode_closed: bool = False) -> str:
        if not episode_closed:
            return "rsi_skipped_active_episode"

        failures = [e for e in events if e.event_type in {"failure", "abstain"}]
        successes = [e for e in events if e.event_type in {"success", "commit"}]
        gems = [e.summary for e in events if e.significant][:2]
        return f"episode_summary:{len(events)}_events:lessons={len(failures)}:successes={len(successes)}:gems={';'.join(gems) if gems else 'none'}"
