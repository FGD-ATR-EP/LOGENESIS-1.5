import json

from logenesis.aetherbus import AkashicEnvelope


def test_akashic_envelope_serialization_produces_json_bytes() -> None:
    envelope = AkashicEnvelope.build(
        subject="logenesis.cortex.intent",
        source="unit-test",
        payload={"vector": [0.1, 0.2, 0.3, 0.4, 0.5]},
        urgency=1.7,
    )

    data = json.loads(envelope.to_bytes())

    assert data["subject"] == "logenesis.cortex.intent"
    assert data["source"] == "unit-test"
    assert data["urgency"] == 1.0
