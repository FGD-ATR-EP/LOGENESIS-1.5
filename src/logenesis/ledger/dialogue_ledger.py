from __future__ import annotations

from logenesis.schemas.models import DialogueLedger


class DialogueLedgerService:
    def __init__(self, ledger: DialogueLedger | None = None):
        self.ledger = ledger or DialogueLedger()

    def add_unverified_claim(self, claim: str) -> None:
        self.ledger.unverified_claims.append(claim)

    def confirm_fact(self, fact: str) -> None:
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
        self.ledger.contradictions_detected.append(contradiction)
