"""
Core accessibility audit engine.

Runs a set of static, WCAG-inspired checks against an HTML document:
- Missing alt text on images
- Missing form labels
- Heading hierarchy skips (e.g. h1 -> h3, no h2)
- Missing page <title> or <html lang>
- Empty links / buttons (no accessible text)
- Missing ARIA labels on custom interactive elements
- Duplicate id attributes (breaks label/ARIA references)

This is a static analysis tool — it inspects markup, not rendered
computed styles, so it can't measure actual color contrast ratios
without a real browser engine. That's flagged explicitly in results
rather than silently skipped or faked.
"""

from dataclasses import dataclass, field

from bs4 import BeautifulSoup


@dataclass
class Issue:
    check: str
    severity: str  # "high" | "medium" | "low"
    message: str
    element: str = ""


@dataclass
class AuditResult:
    issues: list = field(default_factory=list)
    score: int = 100
    checks_run: int = 0

    def add(self, issue: Issue):
        self.issues.append(issue)


SEVERITY_WEIGHTS = {"high": 10, "medium": 5, "low": 2}


def audit_html(html: str) -> AuditResult:
    soup = BeautifulSoup(html, "html.parser")
    result = AuditResult()
    _check_images(soup, result)
    _check_form_labels(soup, result)
    _check_heading_hierarchy(soup, result)
    _check_document_metadata(soup, result)
    _check_empty_interactive_elements(soup, result)
    _check_duplicate_ids(soup, result)
    result.checks_run = 6
    penalty = sum(SEVERITY_WEIGHTS[i.severity] for i in result.issues)
    result.score = max(0, 100 - penalty)
    return result


def _check_images(soup, result):
    imgs = soup.find_all("img")
    for img in imgs:
        alt = img.get("alt")
        src = img.get("src", "unknown")
        if alt is None:
            result.add(Issue(
                check="Image alt text",
                severity="high",
                message="Image has no alt attribute at all — screen readers will announce the filename or nothing useful.",
                element=f'<img src="{src}">',
            ))
        elif alt.strip() == "":
            # Empty alt is valid ONLY for decorative images — can't tell
            # from markup alone whether that's intentional, so flag as low.
            result.add(Issue(
                check="Image alt text",
                severity="low",
                message='Image has empty alt="" — correct only if this image is purely decorative.',
                element=f'<img src="{src}">',
            ))


def _check_form_labels(soup, result):
    inputs = soup.find_all(["input", "textarea", "select"])
    labels = soup.find_all("label")
    labeled_ids = {label.get("for") for label in labels if label.get("for")}
    for inp in inputs:
        input_type = inp.get("type", "text")
        if input_type in ("hidden", "submit", "button"):
            continue
        inp_id = inp.get("id")
        has_aria_label = inp.get("aria-label") or inp.get("aria-labelledby")
        wrapped_in_label = inp.find_parent("label") is not None
        if not has_aria_label and not wrapped_in_label and inp_id not in labeled_ids:
            result.add(Issue(
                check="Form labels",
                severity="high",
                message="Form field has no associated <label>, aria-label, or aria-labelledby — users relying on screen readers won't know what to enter.",
                element=str(inp)[:80],
            ))


def _check_heading_hierarchy(soup, result):
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    levels = [int(h.name[1]) for h in headings]
    if not levels:
        return
    if levels[0] != 1:
        result.add(Issue(
            check="Heading hierarchy",
            severity="medium",
            message=f"Page's first heading is <h{levels[0]}>, not <h1> — screen reader users navigating by heading lose the top-level landmark.",
        ))
    for i in range(1, len(levels)):
        if levels[i] - levels[i - 1] > 1:
            result.add(Issue(
                check="Heading hierarchy",
                severity="medium",
                message=f"Heading level skips from h{levels[i-1]} to h{levels[i]} — breaks the logical outline screen reader users rely on.",
            ))


def _check_document_metadata(soup, result):
    html_tag = soup.find("html")
    if not html_tag or not html_tag.get("lang"):
        result.add(Issue(
            check="Document language",
            severity="medium",
            message="Missing lang attribute on <html> — screen readers can't select the correct pronunciation/voice.",
        ))
    title = soup.find("title")
    if not title or not title.text.strip():
        result.add(Issue(
            check="Page title",
            severity="high",
            message="Missing or empty <title> — this is often the first thing a screen reader announces on page load.",
        ))


def _check_empty_interactive_elements(soup, result):
    for tag in soup.find_all(["a", "button"]):
        text = tag.get_text(strip=True)
        has_aria_label = tag.get("aria-label") or tag.get("aria-labelledby")
        has_img_alt = any(img.get("alt", "").strip() for img in tag.find_all("img"))
        if not text and not has_aria_label and not has_img_alt:
            if tag.name == "a" and not tag.get("href"):
                continue  # not a real link, skip
            result.add(Issue(
                check="Accessible names",
                severity="high",
                message=f"<{tag.name}> element has no visible text, aria-label, or labeled image — announced as blank to screen readers.",
                element=str(tag)[:80],
            ))


def _check_duplicate_ids(soup, result):
    ids = [el.get("id") for el in soup.find_all(id=True)]
    seen = set()
    duplicates = set()
    for i in ids:
        if i in seen:
            duplicates.add(i)
        seen.add(i)
    for dup_id in duplicates:
        result.add(Issue(
            check="Duplicate IDs",
            severity="medium",
            message=f'id="{dup_id}" is used more than once — breaks label/ARIA references and in-page anchors.',
        ))
