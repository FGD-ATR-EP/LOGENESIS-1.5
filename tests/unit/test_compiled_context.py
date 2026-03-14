from logenesis.context_governor.context_compiler import ContextCompiler
from logenesis.schemas.models import DialogueLedger, DialogueState, IntentFrame, TopicFrame


def test_compiled_context_generation():
    state = DialogueState(
        conversation_id="c1",
        turn_id="t1",
        intent=IntentFrame(raw_text="hi", normalized_intent="hi"),
        topic=TopicFrame(active_topic="x"),
        ledger=DialogueLedger(confirmed_facts=["f1"], unresolved_items=["u1"]),
    )
    packet = ContextCompiler().compile(state)
    assert packet.active_topic == "x"
    assert packet.confirmed_facts == ["f1"]
