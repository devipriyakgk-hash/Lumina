(() => {
  const landing = document.getElementById("landing");
  const scanning = document.getElementById("scanning");
  const report = document.getElementById("report");
  const form = document.getElementById("audit-form");
  const urlInput = document.getElementById("url");
  const htmlInput = document.getElementById("html");
  const formError = document.getElementById("form-error");
  const scanSteps = document.getElementById("scan-steps");
  const urlMode = document.getElementById("url-mode");
  const htmlMode = document.getElementById("html-mode");

  let mode = "url";
  let lastResult = null;
  let activeFilter = "all";
  let stepTimer = null;

  const SNIPPET = `<!DOCTYPE html>
<html>
  <head></head>
  <body>
    <h2>Welcome</h2>
    <img src="hero.jpg">
    <a href="/go"></a>
    <input type="email" placeholder="Email">
  </body>
</html>`;

  function show(panel) {
    landing.hidden = panel !== landing;
    scanning.hidden = panel !== scanning;
    report.hidden = panel !== report;
  }

  function setError(msg) {
    formError.hidden = !msg;
    formError.textContent = msg || "";
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function setMode(next) {
    mode = next;
    urlMode.hidden = next !== "url";
    htmlMode.hidden = next !== "html";
    document.querySelectorAll(".mode-btn").forEach((btn) => {
      btn.setAttribute("aria-selected", String(btn.dataset.mode === next));
    });
  }

  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => setMode(btn.dataset.mode));
  });

  document.getElementById("load-snippet").addEventListener("click", () => {
    htmlInput.value = SNIPPET;
    htmlInput.focus();
  });

  urlInput.addEventListener("input", () => {
    const v = urlInput.value.trim();
    if (/^https?:\/\//i.test(v)) urlInput.value = v.replace(/^https?:\/\//i, "");
  });

  function startSteps() {
    const items = [...scanSteps.querySelectorAll("li")];
    items.forEach((li) => li.classList.remove("active", "done"));
    items[0].classList.add("active");
    let i = 0;
    clearInterval(stepTimer);
    stepTimer = setInterval(() => {
      if (i < items.length) {
        items[i].classList.remove("active");
        items[i].classList.add("done");
      }
      i += 1;
      if (i < items.length) items[i].classList.add("active");
      else clearInterval(stepTimer);
    }, 350);
  }

  function normalizeUrl(raw) {
    const t = (raw || "").trim();
    if (!t) return "";
    if (/^https?:\/\//i.test(t)) return t;
    return "https://" + t.replace(/^\/\//, "");
  }

  async function runInBrowser(payload, label) {
    const engine = window.LuminaEngine;
    if (!engine) throw new Error("Checker failed to load.");
    let html = "";
    let source = payload.source;
    if (payload.sample) {
      html = engine.SAMPLE_HTML;
      source = "sample";
    } else if (payload.html) {
      html = payload.html;
      source = "html";
    } else {
      html = await engine.fetchUrl(payload.url);
      source = "url";
    }
    const data = engine.auditHtml(html);
    data.label = label;
    data.source = source;
    return data;
  }

  async function runAudit(payload, label) {
    setError("");
    show(scanning);
    document.getElementById("scan-url").textContent = label;
    startSteps();
    try {
      let data = null;
      try {
        const res = await fetch("/api/audit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (res.ok) {
          const json = await res.json();
          if (json && json.ok !== false) data = json;
        }
      } catch (err) {
        data = null;
      }
      if (!data) data = await runInBrowser(payload, label);
      lastResult = data;
      renderReport(data);
      show(report);
      document.getElementById("new-audit").focus();
    } catch (err) {
      show(landing);
      setError(
        err.message && /fetch|Failed|Network|CORS|status/i.test(err.message)
          ? "Could not open that website from the browser. Paste the HTML instead, or try the demo page."
          : err.message || "Something went wrong."
      );
    } finally {
      clearInterval(stepTimer);
    }
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (mode === "html") {
      const html = htmlInput.value;
      if (!html.trim()) {
        setError("Paste some HTML first.");
        htmlInput.focus();
        return;
      }
      runAudit({ html }, "Pasted HTML");
      return;
    }
    const url = normalizeUrl(urlInput.value);
    if (!url) {
      setError("Paste a website link.");
      urlInput.focus();
      return;
    }
    runAudit({ url }, url);
  });

  document.querySelector("[data-sample]").addEventListener("click", () => {
    runAudit({ sample: true }, "Demo page with planted mistakes");
  });

  document.querySelectorAll("[data-url]").forEach((btn) => {
    btn.addEventListener("click", () => {
      urlInput.value = btn.getAttribute("data-url").replace(/^https?:\/\//, "");
      setMode("url");
      runAudit({ url: btn.getAttribute("data-url") }, btn.getAttribute("data-url"));
    });
  });

  document.getElementById("new-audit").addEventListener("click", () => {
    show(landing);
    (mode === "html" ? htmlInput : urlInput).focus();
  });
  document.getElementById("print-btn").addEventListener("click", () => window.print());
  document.getElementById("json-btn").addEventListener("click", () => {
    if (!lastResult) return;
    const blob = new Blob([JSON.stringify(lastResult, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "lumina-report.json";
    a.click();
    URL.revokeObjectURL(a.href);
  });

  function gradeOf(score) {
    if (score >= 80) return ["good", "Good start"];
    if (score >= 50) return ["needs", "Needs work"];
    return ["poor", "Fix the high-severity items"];
  }

  function setRing(score, grade) {
    const circ = 2 * Math.PI * 52;
    const ring = document.getElementById("ring-value");
    const colors = { good: "var(--good)", needs: "var(--needs)", poor: "var(--poor)" };
    ring.style.stroke = colors[grade];
    ring.style.strokeDasharray = String(circ);
    ring.style.strokeDashoffset = String(circ);
    requestAnimationFrame(() => {
      ring.style.strokeDashoffset = String(circ * (1 - score / 100));
    });
    document.getElementById("score-value").textContent = score;
  }

  function speak(text) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.95;
    window.speechSynthesis.speak(u);
  }

  function renderFacts(stats) {
    const rows = [
      ["Language", stats.lang ? esc(stats.lang) : `<span class="bad">Missing</span>`],
      ["Title", stats.title ? "Yes" : `<span class="bad">Missing</span>`],
      ["H1s", stats.h1Count === 1 ? "1" : `<span class="${stats.h1Count === 0 ? "bad" : "warn"}">${stats.h1Count}</span>`],
      ["Headings", String(stats.headingCount || 0)],
      ["Images", String(stats.imageCount || 0)],
      ["Links", String(stats.linkCount || 0)],
    ];
    document.getElementById("doc-facts").innerHTML = rows
      .map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`)
      .join("");
  }

  function renderOutline(headings) {
    const el = document.getElementById("heading-outline");
    if (!headings || !headings.length) {
      el.innerHTML = `<li class="muted-empty">No headings found.</li>`;
      return;
    }
    let prev = 0;
    el.innerHTML = headings
      .map((h) => {
        const skip = prev && h.level > prev + 1;
        prev = h.level;
        return `<li style="padding-left:${(h.level - 1) * 14}px">
          <span class="lvl">H${h.level}</span>${esc(h.text || "(empty)")}
          ${skip ? `<span class="skip-flag">skipped level</span>` : ""}
        </li>`;
      })
      .join("");
  }

  function renderImages(images) {
    const el = document.getElementById("img-grid");
    if (!images || !images.length) {
      el.innerHTML = `<p class="muted-empty">No images in this HTML.</p>`;
      return;
    }
    el.innerHTML = images
      .map((img) => {
        const status = !img.hasAlt
          ? `<span class="pill bad">No alt</span>`
          : img.decorative
            ? `<span class="pill warn">Decorative</span>`
            : `<span class="pill ok">Has alt</span>`;
        const alt = img.hasAlt ? (img.alt ? esc(img.alt) : "Empty alt") : "Attribute missing";
        const thumb = img.src
          ? `<img class="thumb" src="${esc(img.src)}" alt="" />`
          : `<div class="thumb"></div>`;
        return `<div class="img-card">${thumb}<div class="meta">${status}<span class="alt">${alt}</span></div></div>`;
      })
      .join("");
  }

  function renderFilters(data) {
    const by = (data.stats && data.stats.byCheck) || {};
    const items = [
      ["all", `All · ${data.issues.length}`],
      ["high", `High · ${(data.stats.counts || {}).high || 0}`],
      ["medium", `Medium · ${(data.stats.counts || {}).medium || 0}`],
      ["low", `Low · ${(data.stats.counts || {}).low || 0}`],
      ...Object.keys(by).map((c) => [c, `${c} · ${by[c]}`]),
    ];
    const el = document.getElementById("filters");
    el.innerHTML = items
      .map(
        ([id, label]) =>
          `<button type="button" class="filter" data-filter="${esc(id)}" aria-selected="${
            id === activeFilter
          }">${esc(label)}</button>`
      )
      .join("");
    el.querySelectorAll(".filter").forEach((btn) => {
      btn.addEventListener("click", () => {
        activeFilter = btn.getAttribute("data-filter");
        el.querySelectorAll(".filter").forEach((b) =>
          b.setAttribute("aria-selected", String(b === btn))
        );
        renderIssues(lastResult);
      });
    });
  }

  function matches(issue, filter) {
    if (filter === "all") return true;
    if (["high", "medium", "low"].includes(filter)) return issue.severity === filter;
    return issue.check === filter;
  }

  function renderIssues(data) {
    const list = document.getElementById("issue-list");
    const items = (data.issues || []).filter((i) => matches(i, activeFilter));
    if (!items.length) {
      list.innerHTML =
        data.issues && data.issues.length
          ? `<p class="muted-empty">Nothing in this filter.</p>`
          : `<p class="muted-empty">No structural issues found by these checks. Still test with a real screen reader.</p>`;
      return;
    }
    list.innerHTML = items
      .map((issue, idx) => {
        const hear = issue.hear
          ? `<div class="hear">
              <p class="k">A screen reader might say</p>
              <blockquote>“${esc(issue.hear)}”</blockquote>
              <div class="hear-row">
                <button type="button" class="speak" data-speak="${esc(issue.hear)}">Hear it</button>
              </div>
            </div>`
          : "";
        return `<article class="issue" style="--tone: var(--${issue.severity})">
          <button type="button" class="issue-btn" aria-expanded="false" data-issue="${idx}">
            <span class="sev">${esc(issue.severity)}</span>
            <div>
              <h4>${esc(issue.check)}</h4>
              <p>${esc(issue.message)}</p>
            </div>
            <span class="count">open</span>
          </button>
          <div class="issue-body" hidden>
            ${hear}
            ${issue.element ? `<code class="html-snip">${esc(issue.element)}</code>` : ""}
            ${issue.fix ? `<p class="fix"><strong>How to fix:</strong> ${esc(issue.fix)}</p>` : ""}
          </div>
        </article>`;
      })
      .join("");

    list.querySelectorAll(".issue-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const body = btn.nextElementSibling;
        const open = body.hidden;
        body.hidden = !open;
        btn.setAttribute("aria-expanded", String(open));
      });
    });
    list.querySelectorAll("[data-speak]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        speak(btn.getAttribute("data-speak"));
      });
    });
  }

  function renderReport(data) {
    activeFilter = "all";
    const stats = data.stats || {};
    const [grade, gradeLabel] = gradeOf(data.score);
    setRing(data.score, grade);
    const g = document.getElementById("grade-label");
    g.textContent = gradeLabel;
    g.className = "grade " + grade;
    document.getElementById("page-title").textContent =
      stats.title || (data.source === "sample" ? "Summit Atelier (demo)" : "Untitled page");
    document.getElementById("page-url").textContent = data.label || "";
    document.getElementById("score-meta").textContent =
      `${data.issues.length} issue${data.issues.length === 1 ? "" : "s"} · ${data.checks_run} check groups`;

    const counts = stats.counts || { high: 0, medium: 0, low: 0 };
    document.getElementById("impact-row").innerHTML = [
      ["high", "Fix first"],
      ["medium", "Should fix"],
      ["low", "Double-check"],
    ]
      .map(
        ([k, s]) => `<li style="--tone: var(--${k})">
          <span class="k">${k} · ${s}</span>
          <span class="n">${counts[k] || 0}</span>
        </li>`
      )
      .join("");

    renderFacts(stats);
    renderOutline(stats.headings || []);
    renderImages(stats.images || []);
    renderFilters(data);
    renderIssues(data);
  }
})();
