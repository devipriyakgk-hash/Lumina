# Lumina

**Find problems people might not see.**

A static website checker for **accessibility** — paste a URL or some HTML, get a score out of 100, and a color-coded list of real issues, explained in plain language (including what a screen reader might say).

Built by **Devipriya G.**

---

## What is this, in easy words?

**Accessibility** means: *can everyone use this website?*

That includes people who:

- cannot see the screen well (they may use a **screen reader** — software that *speaks* the page)
- use a **keyboard** instead of a mouse
- find unclear buttons or unlabeled forms confusing

Lumina does a **first pass**. It reads the HTML (the page’s structure) and looks for common mistakes.

### What it checks

| Check | Easy meaning |
| --- | --- |
| **Alt text** | A picture with no description. The screen reader doesn’t know what it is. |
| **Form labels** | An input box with no name. The user hears “edit text”, not “email”. |
| **Heading order** | Jumping from `h1` to `h4`. The page outline is broken. |
| **Page language** | Missing `lang` on `<html>`. The wrong voice / pronunciation may be used. |
| **Page title** | Missing `<title>`. Often the first thing announced on load. |
| **Blank links / buttons** | A control with no words. Announced as just “link” or “button”. |
| **Duplicate IDs** | The same `id` twice. Labels and jump-links can point at the wrong thing. |

### What it honestly does **not** check

These need a **real browser** or a **real screen reader**, not just HTML:

- **Color contrast** (text vs background)
- Keyboard tab order and focus rings
- How a screen reader actually moves through the live page

Passing every Lumina check is a **good sign**, not a certificate.

---

## Run the interactive prototype

You need [Python 3.10+](https://www.python.org/).

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://localhost:3000**

1. Click **Try a demo page with mistakes** — a pretty restaurant page that fails on purpose.
2. Or paste any public URL.
3. Or paste raw HTML (good for homework / local files).
4. Click an issue, then **Hear it** to play what a screen reader might say.

```bash
python -m unittest tests/test_auditor.py
```

---

## Project structure

```
lumina/
├── src/
│   ├── auditor.py      # checks HTML — no internet needed
│   ├── fetcher.py      # downloads a live URL
│   └── sample_html.py  # demo page with planted bugs
├── public/             # interactive prototype (UI)
├── tests/
├── app.py              # small Flask server
└── requirements.txt
```

The auditor has **zero network code**, so you can test it with a string of HTML alone.

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
