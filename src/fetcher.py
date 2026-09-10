"""
Fetches HTML from a live URL for auditing.

Kept separate from auditor.py so the core audit logic has zero
network dependency and can be unit tested on raw HTML strings alone.
"""

import ipaddress
import socket
from urllib.parse import urlparse

import requests

MAX_BYTES = 2_000_000


def _is_private_host(host: str) -> bool:
    if not host:
        return True
    lowered = host.lower().rstrip(".")
    if lowered in {"localhost", "0.0.0.0"} or lowered.endswith(".localhost"):
        return True
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise ValueError("Could not resolve that host. Check the URL.") from exc
    for info in infos:
        ip = info[4][0]
        try:
            parsed = ipaddress.ip_address(ip)
        except ValueError:
            continue
        if (
            parsed.is_private
            or parsed.is_loopback
            or parsed.is_link_local
            or parsed.is_reserved
            or parsed.is_multicast
        ):
            return True
    return False


def fetch_html(url: str, timeout: int = 10) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http and https URLs can be fetched.")
    if _is_private_host(parsed.hostname or ""):
        raise ValueError("Local and private addresses cannot be fetched.")

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; LuminaAuditor/1.0; +https://github.com)"
    }
    response = requests.get(url, headers=headers, timeout=timeout, stream=True)
    response.raise_for_status()

    content_type = (response.headers.get("Content-Type") or "").lower()
    if content_type and "html" not in content_type and "text/" not in content_type:
        # Still try — some servers send application/octet-stream for HTML.
        pass

    chunks = []
    total = 0
    for chunk in response.iter_content(chunk_size=16384):
        if not chunk:
            continue
        total += len(chunk)
        if total > MAX_BYTES:
            raise ValueError("That page is too large to audit here.")
        chunks.append(chunk)
    return b"".join(chunks).decode(response.encoding or "utf-8", errors="replace")
