from flask import Flask, request, jsonify, send_file
from scanner1 import scan_website

import json
from pathlib import Path
from urllib.parse import urlparse

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"


@app.route("/")
def dashboard():
    return send_file(BASE_DIR / "dashboard.html")


@app.route("/scan", methods=["POST"])
def start_scan():

    data = request.get_json(silent=True) or {}
    target_url = data.get("url", "").strip()

    # URL validation
    parsed = urlparse(target_url)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return jsonify({
            "error": "Please enter a valid HTTP or HTTPS URL"
        }), 400

    try:
        # Run existing scanner
        scan_website(target_url)

        # Find latest JSON report
        reports = list(REPORT_DIR.glob("*.json"))

        if not reports:
            return jsonify({
                "message": "Scan finished, but no JSON report found."
            })

        latest_report = max(
            reports,
            key=lambda file: file.stat().st_mtime
        )

        with open(latest_report, "r", encoding="utf-8") as file:
            report = json.load(file)

        return jsonify({
            "message": "Scan completed successfully",
            "report": report
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


if __name__== "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )