"""Kafka producer helper."""
from __future__ import annotations

import json
from typing import Any


def get_producer(bootstrap_servers: str):
    try:
        from kafka import KafkaProducer
    except Exception as exc:
        raise RuntimeError("kafka-python not installed or not available") from exc

    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )


def publish(producer, topic: str, payload: dict[str, Any]) -> None:
    producer.send(topic, payload)
    producer.flush()
