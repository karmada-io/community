#!/usr/bin/env python3
"""Shared helpers for deterministic Karmada Agent Skills scenarios."""

import json
from pathlib import Path


def load_scenario(path: str) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("id"), str):
        raise ValueError("scenario requires a string id")
    return data


def emit(result: dict) -> None:
    print(json.dumps(result, indent=2, sort_keys=True))
