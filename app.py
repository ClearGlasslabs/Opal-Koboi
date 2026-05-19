#!/usr/bin/env python3
"""ClearGlassInc Artemis Flask API bridge.

Connects frontend pages with backend intelligence modules.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify

import data_collector
import market_analyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clearglassinc.api")

CONFIG_PATH = Path("clearglassinc.json")
DATA_CACHE_PATH = Path("artemis_latest_data.json")
ANALYSIS_CACHE_PATH = Path("artemis_latest_analysis.json")


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


app = Flask(__name__)
config = load_config()


@app.get("/api/status")
def status() -> Any:
    payload = {
        "system": "ClearGlassInc Artemis",
        "service": "api",
        "status": "ok",
        "config_loaded": bool(config),
        "latest_collection": _read_json(DATA_CACHE_PATH),
    }
    return jsonify(payload)


@app.get("/api/collect")
def collect() -> Any:
    collector = data_collector.ClearglassDataCollector()
    data = collector.collect_all_data()
    DATA_CACHE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return jsonify({"status": "collected", "records": len(data.get("companies", []))})


@app.get("/api/market")
def market() -> Any:
    data = _read_json(DATA_CACHE_PATH)
    if not data:
        return jsonify({"error": "No collected data found. Run /api/collect first."}), 404

    analyzer = market_analyzer.ClearglassMarketAnalyzer(data)
    report = analyzer.run_full_analysis()
    ANALYSIS_CACHE_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return jsonify(report)


@app.get("/api/analysis/latest")
def latest_analysis() -> Any:
    report = _read_json(ANALYSIS_CACHE_PATH)
    if not report:
        return jsonify({"error": "No analysis report found. Run /api/market first."}), 404
    return jsonify(report)


if __name__ == "__main__":
    port = config.get("api", {}).get("port", 5000)
    app.run(host="0.0.0.0", port=port)
