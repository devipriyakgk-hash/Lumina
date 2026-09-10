"""
Lumina — interactive prototype (UI only).

The checks live in src/auditor.py.
The download lives in src/fetcher.py.

Run with:  python app.py
Then open http://localhost:3000
"""

from flask import Flask, jsonify, request, send_from_directory

from src.auditor import audit_html
from src.fetcher import fetch_html
from src.present import to_report
from src.sample_html import BROKEN_HTML

app = Flask(__name__, static_folder="public", static_url_path="")


@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/audit")
def api_audit():
    body = request.get_json(silent=True) or {}
    try:
        if body.get("sample"):
            result = audit_html(BROKEN_HTML)
            return jsonify(
                to_report(result, BROKEN_HTML, "Demo page with planted mistakes", "sample")
            )

        html = body.get("html")
        url = (body.get("url") or "").strip()

        if html and str(html).strip():
            if len(html) > 2_000_000:
                return jsonify({"ok": False, "error": "That HTML is too large."}), 400
            result = audit_html(html)
            return jsonify(to_report(result, html, "Pasted HTML", "html"))

        if not url:
            return jsonify({"ok": False, "error": "Paste a URL, or some HTML."}), 400

        fetched = fetch_html(url)
        result = audit_html(fetched)
        label = url if url.startswith("http") else "https://" + url
        return jsonify(to_report(result, fetched, label, "url"))
    except Exception as exc:
        raw = str(exc)
        if "timeout" in raw.lower():
            message = "That page took too long to load. Try another URL, or paste the HTML."
        else:
            message = "Could not fetch that page. Try pasting the HTML instead."
        return jsonify({"ok": False, "error": message}), 502


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "name": "Lumina"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)
