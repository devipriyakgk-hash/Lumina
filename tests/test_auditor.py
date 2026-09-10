"""Broken sample should fire every check category Lumina claims to run."""

import unittest

from src.auditor import audit_html
from src.sample_html import BROKEN_HTML

CLEAN_HTML = """<!DOCTYPE html>
<html lang="en">
  <head><title>Clean cafe</title></head>
  <body>
    <h1>Clean cafe</h1>
    <h2>Menu</h2>
    <p><a href="/about">About us</a></p>
    <img src="cake.jpg" alt="Slice of chocolate cake" />
    <form>
      <label for="email">Email</label>
      <input id="email" type="email" />
      <button type="submit">Join</button>
    </form>
  </body>
</html>
"""


class AuditorTests(unittest.TestCase):
    def test_broken_sample_hits_every_category(self):
        result = audit_html(BROKEN_HTML)
        checks = {i.check for i in result.issues}
        self.assertIn("Image alt text", checks)
        self.assertIn("Form labels", checks)
        self.assertIn("Heading hierarchy", checks)
        self.assertIn("Document language", checks)
        self.assertIn("Page title", checks)
        self.assertIn("Accessible names", checks)
        self.assertIn("Duplicate IDs", checks)
        self.assertLess(result.score, 80)
        self.assertEqual(result.checks_run, 6)

    def test_clean_page_is_quiet(self):
        result = audit_html(CLEAN_HTML)
        self.assertEqual(result.issues, [])
        self.assertEqual(result.score, 100)

    def test_empty_alt_is_low_not_high(self):
        html = '<html lang="en"><head><title>t</title></head><body><h1>Hi</h1><img src="x.png" alt=""></body></html>'
        result = audit_html(html)
        self.assertEqual(len(result.issues), 1)
        self.assertEqual(result.issues[0].severity, "low")


if __name__ == "__main__":
    unittest.main()
