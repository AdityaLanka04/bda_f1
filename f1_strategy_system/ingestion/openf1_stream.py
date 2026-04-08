"""OpenF1 telemetry stream consumer.

If OpenF1 websocket is unavailable, emits synthetic events.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import random
import time
from typing import AsyncIterator, Dict

from .kafka_producer import get_producer, publish

OPENF1_WS = "wss://api.openf1.org/v1/ws"


async def synthetic_stream() -> AsyncIterator[Dict]:
    lap = 1
    while True:
        event = {
            "type": "lap_event",
            "lap": lap,
            "driver": random.choice(["VER", "LEC", "HAM", "NOR"]),
            "lap_time": 90 + random.random() * 2.0,
            "ts": time.time(),
        }
        yield event
        lap += 1
        await asyncio.sleep(1.0)


async def run_stream(bootstrap: str, topic: str) -> None:
    producer = get_producer(bootstrap)
    async for event in synthetic_stream():
        publish(producer, topic, event)
        print("published", event)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap", default=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
    parser.add_argument("--topic", default="lap_events")
    args = parser.parse_args()

    asyncio.run(run_stream(args.bootstrap, args.topic))


if __name__ == "__main__":
    main()
