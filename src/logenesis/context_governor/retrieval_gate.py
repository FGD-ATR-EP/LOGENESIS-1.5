from __future__ import annotations


class RetrievalGate:
    def allowed(self, risk_flags: list[str], policy: dict) -> bool:
        if "high_stakes" in risk_flags:
            return policy.get("allow_high_stakes_retrieval", True)
        return True
