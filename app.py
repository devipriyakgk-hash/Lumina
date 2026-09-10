"""
Lumina — interactive prototype.
Run with:  python app.py
"""

from flask import Flask, jsonify, request, send_from_directory

from src.auditor import audit_html
from src.fetcher import fetch_html
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
            payload = result.to_dict()
            payload["ok"] = True
            payload["source"] = "sample"
            payload["label"] = "Demo page with planted mistakes"
            return jsonify(payload)

        html = body.get("html")
        url = (body.get("url") or "").strip()

        if html and str(html).strip():
            if len(html) > 2_000_000:
                return jsonify({"ok": False, "error": "That HTML is too large."}), 400
            result = audit_html(html)
            payload = result.to_dict()
            payload["ok"] = True
            payload["source"] = "html"
            payload["label"] = "Pasted HTML"
            return jsonify(payload)

        if not url:
            return jsonify({"ok": False, "error": "Paste a URL, or some HTML."}), 400
        if len(url) > 2048:
            return jsonify({"ok": False, "error": "That URL is too long."}), 400

        fetched = fetch_html(url)
        result = audit_html(fetched)
        payload = result.to_dict()
        payload["ok"] = True
        payload["source"] = "url"
        payload["label"] = url if url.startswith("http") else "https://" + url
        return jsonify(payload)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception as exc:
        message = str(exc)
        if "timeout" in message.lower():
            message = "That page took too long to load. Try another URL, or paste the HTML."
        else:
            message = "Could not fetch that page. Try pasting the HTML instead."
        return jsonify({"ok": False, "error": message}), 502


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "name": "Lumina"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)
