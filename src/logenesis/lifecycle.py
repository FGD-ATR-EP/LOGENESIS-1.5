"""Lifecycle orchestrator for Logenesis."""
from __future__ import annotations

from logenesis.core.checker import Checker
from logenesis.core.firma import Firma
from logenesis.core.inspira import Inspira
from logenesis.learning.ai_learning_module import LearningModule
from logenesis.resonance.mapper import ResonanceAtom, ResonanceMapper


def run_lifecycle() -> None:
    """Run a sample lifecycle pass to validate wiring."""
    inspira = Inspira(values=["non-harm", "transparency"])
    firma = Firma()
    checker = Checker(rules=("respect-ethical-boundary",))
    learner = LearningModule()
    mapper = ResonanceMapper(
        atoms=(
            ResonanceAtom("ทำยังไง", (1, 1, 0, -1, 1), 0.6, 1.0),
            ResonanceAtom("อธิบาย", (1, 1, 1, -1, 0), 0.5, 0.8),
            ResonanceAtom("ช่วยที", (0, 0, -1, 0, 1), 0.9, 1.5),
        )
    )

    resonance = mapper.map("ช่วยที อธิบาย")
    intent = inspira.validate("assist with system setup")
    feasibility = firma.evaluate(intent.statement)
    report = checker.assess(intent, feasibility)
    update = learner.record("bootstrap", weight=0.5)
    mapper.update_weights(outcome_feedback=1.0 if report.allowed else -0.1)

    if report.allowed:
        outcome = "approved"
    else:
        outcome = "blocked"

    summary = {
        "intent": intent,
        "feasibility": feasibility,
        "report": report,
        "learning": update,
        "resonance": resonance,
        "outcome": outcome,
    }
    print(summary)
