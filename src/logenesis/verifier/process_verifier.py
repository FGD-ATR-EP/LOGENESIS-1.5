from __future__ import annotations


class ProcessVerifier:
    def score(self, hidden_trace: dict) -> float:
        return 1.0 if hidden_trace.get("policy_ok", True) else 0.0
