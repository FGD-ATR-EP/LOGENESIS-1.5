from __future__ import annotations


class ProcessVerifier:
    def score(self, trace_meta: dict) -> tuple[float, list[str], bool]:
        failures: list[str] = []
        valid_hard = True
        if not trace_meta.get("policy_ok", True):
            failures.append("policy_violation")
            valid_hard = False
        if trace_meta.get("cot_leak_risk", False):
            failures.append("cot_leak_risk")
        score = 1.0
        if not valid_hard:
            score = 0.0
        elif failures:
            score = 0.6
        return score, failures, valid_hard
