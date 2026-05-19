#!/usr/bin/env python3
"""ClearGlassInc Artemis API bridge.

Flask service exposing intelligence outputs for frontend applications.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify

import ml_engine
import market_analyzer


CONFIG_PATH = Path(__file__).with_name("clearglassinc.json")


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _safe_latest_ml() -> Dict[str, Any]:
    if hasattr(ml_engine, "get_latest"):
        return ml_engine.get_latest()  # type: ignore[no-any-return]
    if hasattr(ml_engine, "run_prediction"):
        return ml_engine.run_prediction()  # type: ignore[no-any-return]
    return {"status": "unavailable", "reason": "ml_engine has no get_latest/run_prediction"}


def _safe_market_report() -> Dict[str, Any]:
    if hasattr(market_analyzer, "get_report"):
        return market_analyzer.get_report()  # type: ignore[no-any-return]
    if hasattr(market_analyzer, "run_market_analysis"):
        return market_analyzer.run_market_analysis()  # type: ignore[no-any-return]
    return {
        "status": "unavailable",
        "reason": "market_analyzer has no get_report/run_market_analysis",
    }


app = Flask(__name__)
config = load_config()


@app.get("/api/health")
def health() -> Any:
    return jsonify(
        {
            "ok": True,
            "system": "ClearGlassInc Artemis",
            "api": "app.py",
            "db_path": config.get("database", {}).get("path"),
        }
    )


@app.get("/api/status")
def status() -> Any:
    return jsonify(_safe_latest_ml())


@app.get("/api/market")
def market() -> Any:
    return jsonify(_safe_market_report())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
