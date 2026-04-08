"""Model persistence utilities for pipeline."""
from __future__ import annotations

import json
import os
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def append_parquet(path: str, df: pd.DataFrame) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    table = pa.Table.from_pandas(df)
    if os.path.exists(path):
        with pq.ParquetWriter(path, table.schema, compression="snappy", use_dictionary=True) as writer:
            existing = pq.read_table(path)
            writer.write_table(existing)
            writer.write_table(table)
    else:
        pq.write_table(table, path, compression="snappy")


def register_local_model(registry_path: str, name: str, model_path: str, metadata: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(registry_path), exist_ok=True)
    registry = []
    if os.path.exists(registry_path):
        with open(registry_path, "r") as f:
            registry = json.load(f)
    registry.append({"name": name, "path": model_path, "metadata": metadata})
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=2)
