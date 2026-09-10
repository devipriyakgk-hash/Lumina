# Lumina

**Find problems people might not see.**

A static website checker for **accessibility**. Paste a URL or some HTML → get a score out of 100 and a color-coded list of issues, in plain language — including what a screen reader might say.

Built by **Devipriya G.**

**Live prototype:** [https://devipriyakgk-hash.github.io/Lumina/](https://devipriyakgk-hash.github.io/Lumina/)

---

## What is this, in easy words?

**Accessibility** means: *can everyone use this website?*

Lumina does a **first pass**. It reads the HTML (the page’s structure) and looks for common mistakes. It does **not** open a full browser.

### What it checks

| Check | Easy meaning |
| --- | --- |
| **Alt text** | A picture with no description. |
| **Form labels** | An input box with no name. |
| **Heading order** | Jumping from `h1` to `h4`. |
| **Page language** | Missing `lang` on `<html>`. |
| **Page title** | Missing `<title>`. |
| **Blank links / buttons** | A control with no words. |
| **Duplicate IDs** | The same `id` twice. |

### What it honestly does **not** check

These need a real browser or a real screen reader:

- Color contrast
- Keyboard tab order
- A live screen-reader walkthrough

Passing Lumina is a **good sign**, not a certificate.

---

## How the code is split (hybrid)

```
src/auditor.py     ← the checker (your rules, no internet)
src/fetcher.py     ← downloads a live URL
src/present.py     ← UI extras only (“hear it”, outline, stats)
src/sample_html.py ← demo page with planted mistakes
app.py             ← small Flask server for the prototype
public/            ← the interactive screen
tests/             ← proves every check actually fires
```

`auditor.py` does not know about the website UI. You can test it with a string of HTML alone.

---

## Run the prototype

You need [Python 3.10+](https://www.python.org/).

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://localhost:3000** — same interactive prototype as the live site.

1. Click **Try a demo page with mistakes**
2. Open an issue, then click **Hear it**

```bash
python -m unittest tests/test_auditor.py
```

---

## Score

Each issue subtracts points: **high 10**, **medium 5**, **low 2**. Floor is 0.

| Score | Meaning |
| --- | --- |
| 80–100 | Good start |
| 50–79 | Needs work |
| 0–49 | Fix the high-severity items first |

---

*A learning / portfolio project. Pair it with a real screen-reader pass before anything goes to production.*
