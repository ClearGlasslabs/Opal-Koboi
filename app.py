#!/usr/bin/env python3
"""ClearGlassInc Artemis API bridge.

Provides frontend-consumable endpoints that connect static HTML clients
with the Python analytics stack.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify

import ml_engine
import market_analyzer

CONFIG_PATH = Path(__file__).with_name("clearglassinc.json")
DEFAULT_DB_PATH = Path("../database/clearglassinc_aerospace.db")


def _load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {"database": {"path": str(DEFAULT_DB_PATH)}}


CONFIG = _load_config()
DB_PATH = Path(CONFIG.get("database", {}).get("path", DEFAULT_DB_PATH))

app = Flask(__name__)


@app.get("/api/status")
def status() -> Any:
    """System status and latest intelligence metadata."""
    return jsonify(
        {
            "organization": "ClearGlassInc Artemis",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "db_path": str(DB_PATH),
            "ml_engine_version": getattr(ml_engine, "CONFIG", {}).get("version", "unknown"),
            "market_analyzer_version": getattr(market_analyzer, "__version__", "unknown"),
            "service": "online",
        }
    )


@app.get("/api/market")
def market() -> Any:
    """Return a minimal market snapshot for UI and health checks."""
    return jsonify(
        {
            "organization": "ClearGlassInc Artemis",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": "Market analysis endpoint is active and ready for report payloads.",
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
