from dotenv import load_dotenv
load_dotenv()

import os
import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS

from .data_pipeline import run_data_pipeline
from .search_engine import search as run_search
from .database import db

print("[app] Starting backend app module")

app = Flask(__name__)
CORS(app)


@app.route("/api/health", methods=["GET"])
def health():
    """Health-check endpoint."""
    return jsonify({"status": "healthy"})


@app.route("/api/search", methods=["POST"])
def api_search():
    """Accepts JSON payload: {"prompt": "..."} and returns search results."""
    try:
        payload = request.get_json() or {}
        prompt = payload.get("prompt", "")
        print(f"[app] /api/search prompt={prompt}")

        result = run_search(prompt)
        return jsonify({"ok": True, "data": result})
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[app] /api/search error: {e}\n{tb}")
        # Return a user-friendly message without internal details
        return jsonify({"ok": False, "error": "Internal server error during search"}), 500


@app.route("/api/sync-data", methods=["POST"])
def api_sync_data():
    """Trigger the data pipeline to insert fake (or real) data."""
    try:
        print("[app] /api/sync-data triggered")
        run_data = request.get_json() or {}
        # run_data_pipeline is synchronous and returns when done
        run_data_pipeline()
        return jsonify({"ok": True, "message": "Data pipeline run complete"})
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[app] /api/sync-data error: {e}\n{tb}")
        return jsonify({"ok": False, "error": "Internal server error during data sync"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[app] Running on port {port}")
    # Only for development — use gunicorn for production
    app.run(host="0.0.0.0", port=port, debug=True)
