"""Kafka -> Flink-like processing -> Feature store + model persistence."""
from __future__ import annotations

import argparse
import json
import os
from typing import List

import pandas as pd

from kafka import KafkaConsumer

from preprocessing.flink_processor import process_event, to_features
from abpwo.posterior_updater import PitPosteriorStore
from pipeline.model_persistence import append_parquet


def run(
    bootstrap: str,
    topic: str,
    group_id: str,
    batch_size: int,
    out_path: str,
    posterior_dir: str,
) -> None:
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap,
        group_id=group_id,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    buffer: List[dict] = []
    posteriors = PitPosteriorStore()
    posteriors.load_dir(posterior_dir)

    for msg in consumer:
        event = process_event(msg.value)
        buffer.append(to_features(event))

        # Update ABPWO posterior with lap_time as loss proxy
        if event.get("driver") and event.get("lap") and event.get("lap_time"):
            posteriors.update(str(event["driver"]), int(event["lap"]), float(event["lap_time"]))

        if len(buffer) >= batch_size:
            df = pd.DataFrame(buffer)
            append_parquet(out_path, df)
            posteriors.save_dir(posterior_dir)
            buffer.clear()
            print(f"Flushed {batch_size} events to {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap", default=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
    parser.add_argument("--topic", default="lap_events")
    parser.add_argument("--group", default="streaming_pipeline")
    parser.add_argument("--batch", type=int, default=50)
    parser.add_argument("--out", default="data/processed/race_states/streamed.parquet")
    parser.add_argument("--posterior", default="models/abpwo/posteriors")
    args = parser.parse_args()

    run(args.bootstrap, args.topic, args.group, args.batch, args.out, args.posterior)


if __name__ == "__main__":
    main()
