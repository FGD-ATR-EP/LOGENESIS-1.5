from logenesis.context_governor.context_compiler import ContextCompiler
from logenesis.schemas.models import DialogueLedger, DialogueState, IntentFrame, TopicFrame


def test_compiled_context_generation_and_bounded_packet():
    state = DialogueState(
        conversation_id="c1",
        turn_id="t1",
        intent=IntentFrame(raw_text="hi", normalized_intent="hi"),
        topic=TopicFrame(active_topic="x", anchor_summary="topic=x;terms=x;unresolved=1;contradictions=0"),
        ledger=DialogueLedger(
            turn_index=20,
            confirmed_facts=[f"f{i}" for i in range(10)],
            unresolved_items=[f"u{i}" for i in range(10)],
            contradictions_detected=["c1"],
        ),
    )
    packet = ContextCompiler().compile(state, turn_window=12)
    assert packet.active_topic == "x"
    assert len(packet.confirmed_facts) == 6
    assert len(packet.unresolved_items) == 6
    assert packet.turn_window == 12
    assert packet.excluded_prior_turns == 8
    assert packet.packet_truncated is True
    assert packet.ledger_turn_index == 20
    assert packet.contradiction_count == 1
    assert packet.includes_raw_transcript is False
