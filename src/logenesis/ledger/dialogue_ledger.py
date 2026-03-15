from __future__ import annotations

from logenesis.schemas.models import DialogueLedger


class DialogueLedgerService:
    def __init__(self, ledger: DialogueLedger | None = None):
        self.ledger = ledger or DialogueLedger()

    def add_unverified_claim(self, claim: str) -> None:
        self.ledger.unverified_claims.append(claim)

    def confirm_fact(self, fact: str) -> None:
        if fact not in self.ledger.confirmed_facts:
            self.ledger.confirmed_facts.append(fact)
        if fact in self.ledger.unverified_claims:
            self.ledger.unverified_claims.remove(fact)

    def add_commitment(self, commitment: str) -> None:
        self.ledger.commitments_made.append(commitment)

    def revoke_commitment(self, commitment: str) -> None:
        self.ledger.commitments_revoked.append(commitment)

    def add_unresolved(self, item: str) -> None:
        self.ledger.unresolved_items.append(item)

    def add_contradiction(self, contradiction: str) -> None:
        if contradiction not in self.ledger.contradictions_detected:
            self.ledger.contradictions_detected.append(contradiction)

    def update_from_turn(self, user_text: str, model_output: str) -> None:
        if "i will" in model_output.lower():
            self.add_commitment(model_output[:120])
        if "not sure" in model_output.lower() or "cannot verify" in model_output.lower():
            self.add_unresolved(user_text[:120])
        if "contradict" in user_text.lower():
            self.add_contradiction(user_text[:120])
        self.add_unverified_claim(user_text[:160])

    def contradiction_repair_hint(self) -> str:
        if not self.ledger.contradictions_detected:
            return "no_repair_needed"
        return f"repair_required:{len(self.ledger.contradictions_detected)}"
