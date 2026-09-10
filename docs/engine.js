/* Same checks as src/auditor.py, plus UI extras from src/present.py.
   Runs in the browser so the GitHub Pages demo needs no Python server. */
(function (root) {
  const WEIGHTS = { high: 10, medium: 5, low: 2 };

  const SAMPLE_HTML = `<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      body { margin: 0; font-family: Georgia, serif; background: #f3eee6; color: #5c5348; }
      .top { display: flex; justify-content: space-between; padding: 18px 40px; background: #ebe4d8; }
      .logo { letter-spacing: 0.28em; text-transform: uppercase; font-size: 13px; }
      nav a { margin-left: 22px; color: #8a7f70; text-decoration: none; }
      .hero { padding: 64px 40px 40px; background: #e7dfd2; }
      .hero h2 { font-weight: 400; font-size: 42px; margin: 0 0 12px; max-width: 14ch; }
      .cta { margin-top: 16px; padding: 12px 22px; background: #ddd4c6; border: 0; color: #6a5f52; }
      .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; padding: 28px 40px; }
      figure { margin: 0; background: #e8e0d4; }
      figcaption { padding: 10px 12px; font-size: 13px; }
      form { padding: 8px 40px 48px; }
      input { display: block; width: 280px; margin: 8px 0 14px; padding: 10px; }
    </style>
  </head>
  <body>
    <div class="top">
      <div class="logo">Summit Atelier</div>
      <nav>
        <a href="/menu">Menu</a>
        <a href="/book">Reservations</a>
        <a href="/more"></a>
      </nav>
    </div>
    <div class="hero">
      <h2>A quieter table, season by season.</h2>
      <p>Private dining in the old mill. Low light, linen, and a kitchen that changes with the valley.</p>
      <button class="cta"></button>
    </div>
    <div class="grid">
      <figure>
        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='360'%3E%3Crect fill='%23c9b496' width='640' height='360'/%3E%3Ctext x='50%25' y='54%25' fill='%238c7358' font-size='28' text-anchor='middle' font-family='Georgia'%3EOrchard%3C/text%3E%3C/svg%3E" width="640" height="360" />
        <figcaption>Late orchard fruit</figcaption>
      </figure>
      <figure>
        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='360'%3E%3Crect fill='%23b7c3b0' width='640' height='360'/%3E%3Ctext x='50%25' y='54%25' fill='%23788870' font-size='28' text-anchor='middle' font-family='Georgia'%3EHerb%3C/text%3E%3C/svg%3E" width="640" height="360" />
        <figcaption>Herb oil</figcaption>
      </figure>
      <figure>
        <img alt="" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='360'%3E%3Crect fill='%23c1a090' width='640' height='360'/%3E%3Ctext x='50%25' y='54%25' fill='%23886658' font-size='28' text-anchor='middle' font-family='Georgia'%3EFire%3C/text%3E%3C/svg%3E" width="640" height="360" />
        <figcaption>Open fire</figcaption>
      </figure>
    </div>
    <form>
      <h4>Join the list</h4>
      <input type="text" placeholder="Name" />
      <input id="mail" type="email" placeholder="Email" />
      <input id="mail" type="text" placeholder="Party size" />
      <button type="button" class="cta">Submit</button>
    </form>
  </body>
</html>`;

  function snippet(el, limit) {
    const html = (el.outerHTML || "").replace(/\s+/g, " ").trim();
    return html.length <= (limit || 80) ? html : html.slice(0, (limit || 80) - 1) + "…";
  }

  function hearAndFix(issue) {
    const check = issue.check;
    if (check === "Image alt text") {
      if (issue.message.indexOf("empty") !== -1) {
        return {
          hear: "(image skipped — treated as decoration)",
          fix: 'Keep alt="" only for decoration. If the picture means something, describe it.',
        };
      }
      let src = "image";
      const m = /src="([^"]*)"/.exec(issue.element || "");
      if (m) src = m[1].split("/").pop() || m[1];
      return {
        hear: "image, " + src,
        fix: 'Add alt="short description". If the image is purely decorative, use alt="".',
      };
    }
    if (check === "Form labels") {
      return {
        hear: "edit text, unlabeled",
        fix: 'Wrap the field in a <label>, or add <label for="the-id"> plus a matching id.',
      };
    }
    if (check === "Heading hierarchy") {
      return {
        hear: "heading, unexpected level",
        fix: "Don't skip levels. Start with one <h1>, then h2, then h3.",
      };
    }
    if (check === "Document language") {
      return {
        hear: "(voice / language unknown)",
        fix: 'Write <html lang="en"> (or the real language of the page).',
      };
    }
    if (check === "Page title") {
      return {
        hear: "Untitled document",
        fix: "Add <title>A clear page name</title> inside <head>.",
      };
    }
    if (check === "Accessible names") {
      const kind = (issue.element || "").indexOf("<a") !== -1 ? "link" : "button";
      return {
        hear: kind,
        fix: 'Put words inside the ' + kind + ', or add aria-label="what it does".',
      };
    }
    if (check === "Duplicate IDs") {
      return {
        hear: "(ambiguous target)",
        fix: "Give every id a unique value on the page.",
      };
    }
    return { hear: "", fix: "" };
  }

  function stats(doc, issues) {
    const headings = [...doc.querySelectorAll("h1,h2,h3,h4,h5,h6")].map((h) => ({
      level: Number(h.tagName[1]),
      text: (h.textContent || "").trim().slice(0, 140),
    }));
    const images = [...doc.querySelectorAll("img")].slice(0, 36).map((img) => {
      const hasAlt = img.hasAttribute("alt");
      const alt = hasAlt ? img.getAttribute("alt") : null;
      return {
        src: img.getAttribute("src") || "",
        alt,
        hasAlt,
        decorative: alt === "",
      };
    });
    const counts = { high: 0, medium: 0, low: 0 };
    const byCheck = {};
    issues.forEach((issue) => {
      counts[issue.severity] = (counts[issue.severity] || 0) + 1;
      byCheck[issue.check] = (byCheck[issue.check] || 0) + 1;
    });
    const htmlTag = doc.querySelector("html");
    const title = doc.querySelector("title");
    return {
      title: title ? (title.textContent || "").trim() : "",
      lang: (htmlTag && htmlTag.getAttribute("lang")) || "",
      headingCount: headings.length,
      h1Count: doc.querySelectorAll("h1").length,
      imageCount: doc.querySelectorAll("img").length,
      linkCount: doc.querySelectorAll("a[href]").length,
      buttonCount: doc.querySelectorAll("button").length,
      inputCount: doc.querySelectorAll("input, textarea, select").length,
      headings: headings.slice(0, 50),
      images,
      counts,
      byCheck,
    };
  }

  function auditHtml(html) {
    const doc = new DOMParser().parseFromString(html || "", "text/html");
    const issues = [];
    const add = (issue) => issues.push(issue);

    doc.querySelectorAll("img").forEach((img) => {
      const src = img.getAttribute("src") || "unknown";
      if (!img.hasAttribute("alt")) {
        add({
          check: "Image alt text",
          severity: "high",
          message:
            "Image has no alt attribute at all — screen readers will announce the filename or nothing useful.",
          element: '<img src="' + src + '">',
        });
      } else if ((img.getAttribute("alt") || "").trim() === "") {
        add({
          check: "Image alt text",
          severity: "low",
          message: 'Image has empty alt="" — correct only if this image is purely decorative.',
          element: '<img src="' + src + '">',
        });
      }
    });

    const labeledIds = new Set(
      [...doc.querySelectorAll("label[for]")].map((l) => l.getAttribute("for")).filter(Boolean)
    );
    doc.querySelectorAll("input, textarea, select").forEach((inp) => {
      const inputType = inp.getAttribute("type") || "text";
      if (["hidden", "submit", "button"].indexOf(inputType) !== -1) return;
      const inpId = inp.getAttribute("id");
      const hasAria = inp.getAttribute("aria-label") || inp.getAttribute("aria-labelledby");
      const wrapped = !!inp.closest("label");
      if (!hasAria && !wrapped && !labeledIds.has(inpId)) {
        add({
          check: "Form labels",
          severity: "high",
          message:
            "Form field has no associated <label>, aria-label, or aria-labelledby — users relying on screen readers won't know what to enter.",
          element: snippet(inp),
        });
      }
    });

    const headingEls = [...doc.querySelectorAll("h1,h2,h3,h4,h5,h6")];
    const levels = headingEls.map((h) => Number(h.tagName[1]));
    if (levels.length) {
      if (levels[0] !== 1) {
        add({
          check: "Heading hierarchy",
          severity: "medium",
          message:
            "Page's first heading is <h" +
            levels[0] +
            ">, not <h1> — screen reader users navigating by heading lose the top-level landmark.",
          element: "",
        });
      }
      for (let i = 1; i < levels.length; i += 1) {
        if (levels[i] - levels[i - 1] > 1) {
          add({
            check: "Heading hierarchy",
            severity: "medium",
            message:
              "Heading level skips from h" +
              levels[i - 1] +
              " to h" +
              levels[i] +
              " — breaks the logical outline screen reader users rely on.",
            element: "",
          });
        }
      }
    }

    const htmlTag = doc.querySelector("html");
    if (!htmlTag || !htmlTag.getAttribute("lang")) {
      add({
        check: "Document language",
        severity: "medium",
        message:
          "Missing lang attribute on <html> — screen readers can't select the correct pronunciation/voice.",
        element: "",
      });
    }
    const title = doc.querySelector("title");
    if (!title || !(title.textContent || "").trim()) {
      add({
        check: "Page title",
        severity: "high",
        message:
          "Missing or empty <title> — this is often the first thing a screen reader announces on page load.",
        element: "",
      });
    }

    doc.querySelectorAll("a, button").forEach((tag) => {
      const text = (tag.textContent || "").trim();
      const hasAria = tag.getAttribute("aria-label") || tag.getAttribute("aria-labelledby");
      const hasImgAlt = [...tag.querySelectorAll("img")].some(
        (img) => (img.getAttribute("alt") || "").trim()
      );
      if (!text && !hasAria && !hasImgAlt) {
        if (tag.tagName.toLowerCase() === "a" && !tag.getAttribute("href")) return;
        const name = tag.tagName.toLowerCase();
        add({
          check: "Accessible names",
          severity: "high",
          message:
            "<" +
            name +
            "> element has no visible text, aria-label, or labeled image — announced as blank to screen readers.",
          element: snippet(tag),
        });
      }
    });

    const seen = new Set();
    const duplicates = new Set();
    doc.querySelectorAll("[id]").forEach((el) => {
      const id = el.getAttribute("id");
      if (seen.has(id)) duplicates.add(id);
      seen.add(id);
    });
    duplicates.forEach((dupId) => {
      add({
        check: "Duplicate IDs",
        severity: "medium",
        message:
          'id="' + dupId + '" is used more than once — breaks label/ARIA references and in-page anchors.',
        element: "",
      });
    });

    let penalty = 0;
    issues.forEach((issue) => {
      penalty += WEIGHTS[issue.severity] || 0;
    });
    const score = Math.max(0, 100 - penalty);
    const decorated = issues.map((issue) => Object.assign({}, issue, hearAndFix(issue)));
    return {
      ok: true,
      score,
      checks_run: 6,
      issues: decorated,
      stats: stats(doc, issues),
    };
  }

  async function fetchUrl(url) {
    let target = url;
    if (!/^https?:\/\//i.test(target)) target = "https://" + target;
    const proxies = [
      "https://api.allorigins.win/raw?url=" + encodeURIComponent(target),
      "https://corsproxy.io/?" + encodeURIComponent(target),
    ];
    let lastErr = null;
    for (let i = 0; i < proxies.length; i += 1) {
      try {
        const res = await fetch(proxies[i]);
        if (!res.ok) throw new Error("bad status");
        const text = await res.text();
        if (text && text.length > 20) return text;
      } catch (err) {
        lastErr = err;
      }
    }
    throw lastErr || new Error("fetch failed");
  }

  root.LuminaEngine = {
    SAMPLE_HTML,
    auditHtml,
    fetchUrl,
  };
})(window);
