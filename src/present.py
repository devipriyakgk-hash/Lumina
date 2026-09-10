"""
UI helpers only — does not change the audit rules.

Turns an AuditResult into JSON the prototype can show
(score cards, heading outline, "hear it" / "how to fix").
"""

from bs4 import BeautifulSoup

from src.auditor import AuditResult


def _hear_and_fix(issue):
    check = issue.check
    if check == "Image alt text":
        if "empty" in issue.message:
            return (
                "(image skipped — treated as decoration)",
                'Keep alt="" only for decoration. If the picture means something, describe it.',
            )
        src = "image"
        if 'src="' in issue.element:
            src = issue.element.split('src="', 1)[1].split('"', 1)[0]
            src = src.split("/")[-1] or src
        return (
            f"image, {src}",
            'Add alt="short description". If the image is purely decorative, use alt="".',
        )
    if check == "Form labels":
        return (
            "edit text, unlabeled",
            'Wrap the field in a <label>, or add <label for="the-id"> plus a matching id.',
        )
    if check == "Heading hierarchy":
        return (
            "heading, unexpected level",
            "Don't skip levels. Start with one <h1>, then h2, then h3.",
        )
    if check == "Document language":
        return (
            "(voice / language unknown)",
            'Write <html lang="en"> (or the real language of the page).',
        )
    if check == "Page title":
        return ("Untitled document", "Add <title>A clear page name</title> inside <head>.")
    if check == "Accessible names":
        kind = "link" if "<a" in issue.element else "button"
        return (
            kind,
            f"Put words inside the {kind}, or add aria-label=\"what it does\".",
        )
    if check == "Duplicate IDs":
        return (
            "(ambiguous target)",
            "Give every id a unique value on the page.",
        )
    return ("", "")


def _stats(html: str, result: AuditResult):
    soup = BeautifulSoup(html or "", "html.parser")
    headings = [
        {"level": int(h.name[1]), "text": h.get_text(" ", strip=True)[:140]}
        for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    ]
    images = []
    for img in soup.find_all("img")[:36]:
        alt = img.get("alt")
        images.append(
            {
                "src": img.get("src") or "",
                "alt": alt,
                "hasAlt": alt is not None,
                "decorative": alt == "",
            }
        )
    counts = {"high": 0, "medium": 0, "low": 0}
    by_check = {}
    for issue in result.issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1
        by_check[issue.check] = by_check.get(issue.check, 0) + 1
    title = soup.find("title")
    html_tag = soup.find("html")
    return {
        "title": title.get_text(strip=True) if title else "",
        "lang": (html_tag.get("lang") if html_tag else "") or "",
        "headingCount": len(headings),
        "h1Count": len(soup.find_all("h1")),
        "imageCount": len(soup.find_all("img")),
        "linkCount": len(soup.find_all("a", href=True)),
        "buttonCount": len(soup.find_all("button")),
        "inputCount": len(soup.find_all(["input", "textarea", "select"])),
        "headings": headings[:50],
        "images": images,
        "counts": counts,
        "byCheck": by_check,
    }


def to_report(result: AuditResult, html: str, label: str, source: str) -> dict:
    issues = []
    for issue in result.issues:
        hear, fix = _hear_and_fix(issue)
        issues.append(
            {
                "check": issue.check,
                "severity": issue.severity,
                "message": issue.message,
                "element": issue.element,
                "hear": hear,
                "fix": fix,
            }
        )
    return {
        "ok": True,
        "score": result.score,
        "checks_run": result.checks_run,
        "issues": issues,
        "stats": _stats(html, result),
        "label": label,
        "source": source,
    }
