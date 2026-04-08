"""Simple health checks."""
from __future__ import annotations

import os
import requests


def mlflow_health() -> bool:
    uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    try:
        resp = requests.get(f"{uri}/health", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False
