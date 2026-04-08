"""MLflow model registry integration (placeholder) and local registry."""
from __future__ import annotations

import json
import os
from typing import Any


def get_tracking_uri() -> str:
    return os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")


def register_local_model(name: str, model_path: str, metadata: dict[str, Any]) -> str:
    registry_path = os.getenv("MODEL_REGISTRY_PATH", "models/registry.json")
    os.makedirs(os.path.dirname(registry_path), exist_ok=True)
    registry = []
    if os.path.exists(registry_path):
        with open(registry_path, "r") as f:
            registry = json.load(f)
    registry.append({"name": name, "path": model_path, "metadata": metadata})
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=2)
    return registry_path
