"""Placeholder for Flink real-time processing job.

In production, this would be a Flink job that updates race state per lap.
Here we provide a minimal transformation suitable for Kafka streaming.
"""
from __future__ import annotations

import time


def process_event(event: dict) -> dict:
    # Minimal example: add processing timestamp
    event = dict(event)
    event["processed_ts"] = time.time()
    return event


def to_features(event: dict) -> dict:
    return {
        "driver": event.get("driver"),
        "lap": event.get("lap"),
        "lap_time": event.get("lap_time"),
        "ts": event.get("ts"),
        "processed_ts": event.get("processed_ts"),
    }
