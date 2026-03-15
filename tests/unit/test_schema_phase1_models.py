from logenesis.schemas.models import (
    ContextPacket,
    DialogueLedger,
    DialogueState,
    EpisodicEvent,
    IntentFrame,
    MemoryImportanceWeights,
    MemoryPolicyDecision,
    MemoryRecord,
    MemoryTier,
    TopicFrame,
)


def test_dialogue_ledger_defaults_preserve_compatibility_with_new_fields():
    ledger = DialogueLedger()
    assert ledger.turn_index == 0
    assert ledger.observed_claims == []


def test_context_packet_and_memory_record_new_fields_have_safe_defaults():
    packet = ContextPacket(conversation_id="c", active_topic="t", intent_summary="i")
    assert packet.retrieval_count == 0
    assert packet.retrieval_policy_blocked is False

    record = MemoryRecord(memory_id="m1", tier=MemoryTier.WORKING, payload={}, provenance="turn:c")
    assert record.commit_candidate is True
    assert record.blocked_reasons == []
    assert record.policy_approved is False
    assert record.constitution_allowed is False


def test_dialogue_state_supports_extended_metadata_fields():
    state = DialogueState(
        conversation_id="c1",
        turn_id="t1",
        intent=IntentFrame(raw_text="hi", normalized_intent="hi"),
        topic=TopicFrame(),
        ledger=DialogueLedger(),
        retrieval_metadata={"allowed": True},
        verification_metadata={"aggregate": 0.9},
    )
    assert state.retrieval_metadata["allowed"] is True
    assert state.verification_metadata["aggregate"] == 0.9


def test_phase1_memory_policy_models_defaults():
    event = EpisodicEvent(conversation_id="c", turn_id="t", event_type="success", summary="ok")
    assert event.significant is False

    weights = MemoryImportanceWeights()
    assert weights.confidence_weight > 0

    decision = MemoryPolicyDecision()
    assert decision.allowed is False
