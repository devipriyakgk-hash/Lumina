"""
Lumina — fetches HTML from a live URL for auditing.

Kept separate from auditor.py so the core audit logic has zero
network dependency and can be unit tested on raw HTML strings alone.
"""

import requests


def fetch_html(url: str, timeout: int = 10) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; A11yAuditor/1.0)"
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.text
