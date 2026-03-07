"""AetherBusExtreme throughput benchmark for JetStream publishing."""
from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
import json
import time

import nats
from nats.js.api import DiscardPolicy, RetentionPolicy, StorageType, StreamConfig

try:
    import uvloop
except ImportError:  # pragma: no cover - optional for local optimization
    uvloop = None


@dataclass(frozen=True)
class IntentVector:
    """Minimal benchmark payload schema."""

    vector: list[float]
    urgency: float
    timestamp: float


def encode_payload(intent: IntentVector) -> bytes:
    """Encode payload as compact JSON bytes."""
    return json.dumps(asdict(intent), separators=(",", ":")).encode("utf-8")


async def run_benchmark(
    total_msgs: int = 100_000,
    batch_size: int = 1_000,
    server_url: str = "nats://localhost:4222",
) -> float:
    """Run producer-only benchmark and return req/s throughput."""
    if uvloop is not None:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    nc = await nats.connect(
        server_url,
        pending_size=1024 * 1024 * 64,
        name="AetherBus-Benchmarker",
    )
    js = nc.jetstream()

    stream_config = StreamConfig(
        name="LOGENESIS_BENCHMARK",
        subjects=["logenesis.cortex.intent"],
        storage=StorageType.MEMORY,
        retention=RetentionPolicy.LIMITS,
        max_msgs=100_000,
        discard=DiscardPolicy.OLD,
    )

    try:
        await js.add_stream(config=stream_config)
    except Exception:
        await js.update_stream(config=stream_config)

    payload = encode_payload(
        IntentVector(
            vector=[0.1, -0.5, 0.8, 0.2, -0.1],
            urgency=0.9,
            timestamp=time.time(),
        )
    )

    start_time = time.perf_counter()
    sent_count = 0

    while sent_count < total_msgs:
        current_batch_size = min(batch_size, total_msgs - sent_count)
        tasks = [js.publish("logenesis.cortex.intent", payload) for _ in range(current_batch_size)]
        await asyncio.gather(*tasks)
        sent_count += current_batch_size
        if sent_count % 10_000 == 0:
            print(f"Sent {sent_count}/{total_msgs} messages...")

    duration = time.perf_counter() - start_time
    throughput = sent_count / duration

    print(f"Total Sent: {sent_count:,} msgs")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Throughput: {throughput:,.2f} req/s")
    print("✅ Performance Target Met" if throughput >= 10_000 else "❌ Performance Under Target")

    await nc.close()
    return throughput


if __name__ == "__main__":
    asyncio.run(run_benchmark())
