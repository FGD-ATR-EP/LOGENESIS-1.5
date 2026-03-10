"""Confidence calibration primitives and drift monitoring."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationBin:
    lower_bound: float
    upper_bound: float
    expected_accuracy: float
    observed_accuracy: float

    @property
    def drift(self) -> float:
        return self.observed_accuracy - self.expected_accuracy


class UncertaintyCalibrationTable:
    """Track and evaluate confidence drift across repeated runs."""

    def __init__(self) -> None:
        self._bins: list[CalibrationBin] = []

    def add_bin(self, calibration_bin: CalibrationBin) -> None:
        self._bins.append(calibration_bin)

    def max_drift(self) -> float:
        if not self._bins:
            return 0.0
        return max(abs(bucket.drift) for bucket in self._bins)

    def is_within_threshold(self, threshold: float = 0.08) -> bool:
        return self.max_drift() <= threshold
