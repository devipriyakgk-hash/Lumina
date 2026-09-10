"""
Core accessibility audit engine.

Runs static, WCAG-inspired checks against HTML markup:
- Missing / empty alt text on images
- Form fields with no label
- Heading hierarchy skips (e.g. h1 → h3)
- Missing page <title> or <html lang>
- Links / buttons with no accessible name
- Duplicate id attributes

This inspects markup, not a real browser's computed styles,
so it cannot measure color contrast. That limit is reported
honestly rather than guessed.
"""

from dataclasses import dataclass, field, asdict

from bs4 import BeautifulSoup


@dataclass
class Issue:
    check: str
    severity: str  # "high" | "medium" | "low"
    message: str
    element: str = ""
    hear: str = ""
    fix: str = ""


@dataclass
class AuditResult:
    issues: list = field(default_factory=list)
    score: int = 100
    checks_run: int = 0
    stats: dict = field(default_factory=dict)

    def add(self, issue: Issue):
        self.issues.append(issue)

    def to_dict(self):
        return {
            "score": self.score,
            "checks_run": self.checks_run,
            "issues": [asdict(i) for i in self.issues],
            "stats": self.stats,
        }


SEVERITY_WEIGHTS = {"high": 10, "medium": 5, "low": 2}


def audit_html(html: str) -> AuditResult:
    soup = BeautifulSoup(html or "", "html.parser")
    result = AuditResult()

    _check_images(soup, result)
    _check_form_labels(soup, result)
    _check_heading_hierarchy(soup, result)
    _check_document_metadata(soup, result)
    _check_empty_interactive_elements(soup, result)
    _check_duplicate_ids(soup, result)

    result.checks_run = 6
    penalty = sum(SEVERITY_WEIGHTS.get(i.severity, 0) for i in result.issues)
    result.score = max(0, 100 - penalty)
    result.stats = _collect_stats(soup, result)
    return result


def _snippet(el, limit=120):
    text = str(el).replace("\n", " ").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _check_images(soup, result):
    for img in soup.find_all("img"):
        alt = img.get("alt")
        src = img.get("src", "unknown")
        if alt is None:
            result.add(
                Issue(
                    check="Image alt text",
                    severity="high",
                    message=(
                        "Image has no alt attribute at all — a screen reader will "
                        "announce the filename, or nothing useful."
                    ),
                    element=f'<img src="{src}">',
                    hear=f"image, {src.split('/')[-1] or 'unlabeled'}",
                    fix='Add alt="short description". If the image is purely decorative, use alt="".',
                )
            )
        elif alt.strip() == "":
            result.add(
                Issue(
                    check="Image alt text",
                    severity="low",
                    message=(
                        'Image has empty alt="" — correct only if this image is '
                        "purely decorative."
                    ),
                    element=f'<img src="{src}" alt="">',
                    hear="(image skipped — treated as decoration)",
                    fix='Keep alt="" only for decoration. If the picture means something, describe it.',
                )
            )


def _check_form_labels(soup, result):
    labels = soup.find_all("label")
    labeled_ids = {label.get("for") for label in labels if label.get("for")}
    for inp in soup.find_all(["input", "textarea", "select"]):
        input_type = (inp.get("type") or "text").lower()
        if input_type in ("hidden", "submit", "button", "reset", "image"):
            continue
        inp_id = inp.get("id")
        has_aria = inp.get("aria-label") or inp.get("aria-labelledby")
        wrapped = inp.find_parent("label") is not None
        if not has_aria and not wrapped and inp_id not in labeled_ids:
            result.add(
                Issue(
                    check="Form labels",
                    severity="high",
                    message=(
                        "Form field has no associated <label>, aria-label, or "
                        "aria-labelledby — people using a screen reader won't know what to enter."
                    ),
                    element=_snippet(inp),
                    hear=f"{input_type} field, unlabeled",
                    fix='Wrap it in a <label>, or add <label for="the-id"> plus a matching id.',
                )
            )


def _check_heading_hierarchy(soup, result):
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    levels = [int(h.name[1]) for h in headings]
    if not levels:
        return
    if levels[0] != 1:
        result.add(
            Issue(
                check="Heading hierarchy",
                severity="medium",
                message=(
                    f"Page's first heading is <h{levels[0]}>, not <h1> — screen reader "
                    "users navigating by heading lose the top-level landmark."
                ),
                element=_snippet(headings[0]),
                hear=f"heading level {levels[0]}, {headings[0].get_text(strip=True)[:60]}",
                fix="Start the page with a single <h1> that names the main topic.",
            )
        )
    for i in range(1, len(levels)):
        if levels[i] - levels[i - 1] > 1:
            result.add(
                Issue(
                    check="Heading hierarchy",
                    severity="medium",
                    message=(
                        f"Heading level skips from h{levels[i - 1]} to h{levels[i]} — "
                        "breaks the outline screen reader users rely on."
                    ),
                    element=_snippet(headings[i]),
                    hear=f"heading level {levels[i]}, {headings[i].get_text(strip=True)[:60]}",
                    fix="Don't skip levels. After an h2, the next heading should be h2 or h3, not h4.",
                )
            )


def _check_document_metadata(soup, result):
    html_tag = soup.find("html")
    if not html_tag or not html_tag.get("lang"):
        result.add(
            Issue(
                check="Document language",
                severity="medium",
                message=(
                    "Missing lang attribute on <html> — screen readers can't pick "
                    "the correct pronunciation or voice."
                ),
                element="<html>",
                hear="(voice / language unknown)",
                fix='Write <html lang="en"> (or the real language of the page).',
            )
        )
    title = soup.find("title")
    if not title or not title.get_text(strip=True):
        result.add(
            Issue(
                check="Page title",
                severity="high",
                message=(
                    "Missing or empty <title> — this is often the first thing a "
                    "screen reader announces on page load."
                ),
                element="<title>",
                hear="Untitled document",
                fix="Add <title>A clear page name</title> inside <head>.",
            )
        )


def _check_empty_interactive_elements(soup, result):
    for tag in soup.find_all(["a", "button"]):
        text = tag.get_text(strip=True)
        has_aria = tag.get("aria-label") or tag.get("aria-labelledby")
        has_img_alt = any(
            (img.get("alt") or "").strip() for img in tag.find_all("img")
        )
        if not text and not has_aria and not has_img_alt:
            if tag.name == "a" and not tag.get("href"):
                continue
            result.add(
                Issue(
                    check="Accessible names",
                    severity="high",
                    message=(
                        f"<{tag.name}> has no visible text, aria-label, or labeled "
                        "image — announced as blank to screen readers."
                    ),
                    element=_snippet(tag),
                    hear=f"{'link' if tag.name == 'a' else 'button'}",
                    fix=f"Put words inside the <{tag.name}>, or add aria-label=\"what it does\".",
                )
            )


def _check_duplicate_ids(soup, result):
    seen = set()
    duplicates = set()
    for el in soup.find_all(id=True):
        i = el.get("id")
        if i in seen:
            duplicates.add(i)
        seen.add(i)
    for dup_id in sorted(duplicates):
        result.add(
            Issue(
                check="Duplicate IDs",
                severity="medium",
                message=(
                    f'id="{dup_id}" is used more than once — breaks label/ARIA '
                    "references and in-page anchors."
                ),
                element=f'id="{dup_id}"',
                hear=f"(ambiguous target: {dup_id})",
                fix="Give every id a unique value on the page.",
            )
        )


def _collect_stats(soup, result):
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
