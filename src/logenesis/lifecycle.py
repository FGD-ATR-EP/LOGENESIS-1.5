"""Lifecycle orchestrator for Logenesis."""
from __future__ import annotations

from logenesis.core.checker import Checker
from logenesis.core.firma import Firma
from logenesis.core.inspira import Inspira
from logenesis.learning.ai_learning_module import LearningModule


def run_lifecycle() -> None:
    """Run a sample lifecycle pass to validate wiring."""
    inspira = Inspira(values=["non-harm", "transparency"])
    firma = Firma()
    checker = Checker(rules=("respect-ethical-boundary",))
    learner = LearningModule()

    intent = inspira.validate("assist with system setup")
    feasibility = firma.evaluate(intent.statement)
    report = checker.assess(intent, feasibility)
    update = learner.record("bootstrap", weight=0.5)

    if report.allowed:
        outcome = "approved"
    else:
        outcome = "blocked"

    summary = {
        "intent": intent,
        "feasibility": feasibility,
        "report": report,
        "learning": update,
        "outcome": outcome,
    }
    print(summary)
