from __future__ import annotations


class ProcessVerifier:
    def score(self, trace_meta: dict) -> tuple[float, list[str], bool]:
        failures: list[str] = []
        valid_hard = True

        if not trace_meta.get("policy_ok", True):
            failures.append("policy_violation")
            valid_hard = False
        if trace_meta.get("cot_leak_risk", False):
            failures.append("trace_leakage_risk")
        if trace_meta.get("drift_detected", False):
            failures.append("drift_detected")

        if not valid_hard:
            return 0.0, failures, False
        if failures:
            return 0.62, failures, True
        return 1.0, failures, True
