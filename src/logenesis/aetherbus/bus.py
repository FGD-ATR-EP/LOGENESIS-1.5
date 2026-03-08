"""NATS JetStream transport for LOGENESIS AetherBus."""
from __future__ import annotations

from collections.abc import Awaitable, Callable

import nats
from nats.aio.client import Client as NATS
from nats.js import JetStreamContext
from nats.js.api import DiscardPolicy, RetentionPolicy, StorageType, StreamConfig

from .envelope import AkashicEnvelope


class AetherBus:
    """High-throughput wrapper for publishing/subscribing via JetStream."""

    def __init__(
        self,
        server_url: str = "nats://localhost:4222",
        stream_name: str = "LOGENESIS_CORTEX",
        subjects: tuple[str, ...] = ("logenesis.cortex.*",),
    ) -> None:
        self.server_url = server_url
        self.stream_name = stream_name
        self.subjects = subjects
        self.nc: NATS | None = None
        self.js: JetStreamContext | None = None

    async def connect(self) -> None:
        """Connect to NATS and ensure high-performance stream is available."""
        self.nc = await nats.connect(
            self.server_url,
            pending_size=1024 * 1024 * 64,
            name="AetherBus",
        )
        self.js = self.nc.jetstream()

        stream_config = StreamConfig(
            name=self.stream_name,
            subjects=list(self.subjects),
            storage=StorageType.MEMORY,
            retention=RetentionPolicy.LIMITS,
            max_msgs=100_000,
            discard=DiscardPolicy.OLD,
        )

        try:
            await self.js.add_stream(config=stream_config)
        except Exception:
            await self.js.update_stream(config=stream_config)

    async def close(self) -> None:
        """Close active connection."""
        if self.nc is not None:
            await self.nc.close()

    async def publish_envelope(self, envelope: AkashicEnvelope) -> None:
        """Publish an envelope to the configured subject."""
        await self.publish(envelope.subject, envelope.to_bytes())

    async def publish(self, subject: str, data: bytes) -> None:
        """Publish raw bytes to JetStream subject."""
        if self.js is None:
            raise RuntimeError("AetherBus is not connected")
        await self.js.publish(subject, data)

    async def subscribe(
        self,
        subject: str,
        callback: Callable[..., Awaitable[None]],
    ):
        """Subscribe with callback; returns NATS subscription."""
        if self.js is None:
            raise RuntimeError("AetherBus is not connected")
        return await self.js.subscribe(subject, cb=callback)
