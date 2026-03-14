from __future__ import annotations


class CommitmentVerifier:
    def score(self, answer: str, commitments: list[str]) -> float:
        if not commitments:
            return 1.0
        missed = [c for c in commitments if c.lower() not in answer.lower()]
        return 1.0 - min(1.0, len(missed) / len(commitments))
