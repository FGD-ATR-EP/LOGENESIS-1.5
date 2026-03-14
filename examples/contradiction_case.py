from logenesis.ledger.dialogue_ledger import DialogueLedgerService
from logenesis.schemas.models import DialogueLedger

ledger = DialogueLedgerService(DialogueLedger())
ledger.confirm_fact("Project deadline is Friday")
ledger.add_contradiction("User later claims deadline is Monday")
print(ledger.ledger.model_dump())
