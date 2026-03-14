from logenesis.ledger.dialogue_ledger import DialogueLedgerService
from logenesis.schemas.models import DialogueLedger


def test_contradiction_added_to_ledger():
    svc = DialogueLedgerService(DialogueLedger())
    svc.add_contradiction("A != B")
    assert "A != B" in svc.ledger.contradictions_detected
