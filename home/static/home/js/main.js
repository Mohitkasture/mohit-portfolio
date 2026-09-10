(function () {
  const nav = document.getElementById("nav");
  const toggle = document.getElementById("nav-toggle");
  const menu = document.getElementById("nav-menu");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const onScroll = () => {
    nav.classList.toggle("is-scrolled", window.scrollY > 8);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  const closeMenu = () => {
    nav.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open menu");
  };

  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  });

  menu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && nav.classList.contains("is-open")) {
      closeMenu();
      toggle.focus();
    }
  });

  const navLinks = [...menu.querySelectorAll("a[href^='#']")];
  const sectionEls = navLinks
    .map((link) => document.getElementById(link.getAttribute("href").slice(1)))
    .filter(Boolean);

  const clearHashFromUrl = () => {
    if (!window.location.hash) return;
    const clean = window.location.pathname + window.location.search;
    window.history.replaceState(null, "", clean);
  };

  const getScrollOffset = () => {
    const raw = getComputedStyle(document.documentElement).scrollPaddingTop;
    const pad = Number.parseFloat(raw);
    return Number.isFinite(pad) ? pad : 88;
  };

  // Use section padding edge — ignores .reveal translateY which skews getBoundingClientRect
  const getSectionContentTop = (section) => {
    const padTop = Number.parseFloat(getComputedStyle(section).paddingTop) || 0;
    return section.getBoundingClientRect().top + padTop;
  };

  const setActiveFromId = (id) => {
    navLinks.forEach((link) => {
      const on = Boolean(id) && link.getAttribute("href") === "#" + id;
      link.classList.toggle("is-active", on);
      if (on) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  };

  const scrollToId = (id) => {
    const behavior = reduceMotion ? "auto" : "smooth";
    if (!id || id === "top") {
      window.scrollTo({ top: 0, behavior });
      clearHashFromUrl();
      setActiveFromId(null);
      return;
    }
    const section = document.getElementById(id);
    if (!section) return;
    const top =
      window.scrollY + getSectionContentTop(section) - getScrollOffset();
    window.scrollTo({ top: Math.max(0, top), behavior });
    clearHashFromUrl();
    setActiveFromId(id);
  };

  // In-page links scroll without leaving #section in the address bar
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      const href = link.getAttribute("href");
      if (!href || href === "#") return;
      const id = href.slice(1);
      if (!document.getElementById(id) && id !== "top") return;
      event.preventDefault();
      event.stopPropagation();
      scrollToId(id);
      closeMenu();
    });
  });

  if (window.location.hash) {
    const initialId = window.location.hash.slice(1);
    requestAnimationFrame(() => scrollToId(initialId));
  }

  const setActiveNav = () => {
    const offset = getScrollOffset() + 8;
    let current = null;
    sectionEls.forEach((section) => {
      if (getSectionContentTop(section) - offset <= 0) current = section;
    });

    // Last sections can't always reach sticky offset — activate last when at page end
    const maxScroll = Math.max(
      0,
      document.documentElement.scrollHeight - window.innerHeight
    );
    if (sectionEls.length && window.scrollY >= maxScroll - 2) {
      current = sectionEls[sectionEls.length - 1];
    }

    if (!current && window.scrollY < 40) {
      setActiveFromId(null);
      return;
    }
    setActiveFromId(current ? current.id : null);
  };
  setActiveNav();
  window.addEventListener("scroll", setActiveNav, { passive: true });

  const reveals = document.querySelectorAll(".reveal");
  if (reduceMotion) {
    reveals.forEach((el) => el.classList.add("is-in"));
  } else {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-in");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    reveals.forEach((el) => io.observe(el));
  }

  // Hero typing roles
  const typedEl = document.getElementById("typed-role");
  if (typedEl) {
    const roles = [
      "Python Backend Developer",
      "Django Developer",
      "AI Developer",
    ];
    if (reduceMotion) {
      typedEl.textContent = roles[0];
    } else {
      let roleIndex = 0;
      let charIndex = 0;
      let deleting = false;
      const typeSpeed = 70;
      const deleteSpeed = 40;
      const holdMs = 1600;

      const tickType = () => {
        const current = roles[roleIndex];
        if (!deleting) {
          charIndex += 1;
          typedEl.textContent = current.slice(0, charIndex);
          if (charIndex >= current.length) {
            deleting = true;
            setTimeout(tickType, holdMs);
            return;
          }
          setTimeout(tickType, typeSpeed);
          return;
        }
        charIndex -= 1;
        typedEl.textContent = current.slice(0, Math.max(0, charIndex));
        if (charIndex <= 0) {
          deleting = false;
          roleIndex = (roleIndex + 1) % roles.length;
          setTimeout(tickType, 280);
          return;
        }
        setTimeout(tickType, deleteSpeed);
      };
      tickType();
    }
  }

  // Experience timeline fill on scroll
  const timeline = document.getElementById("experience-timeline");
  const timelineProgress = document.getElementById("timeline-progress");
  if (timeline && timelineProgress) {
    const updateTimeline = () => {
      const rect = timeline.getBoundingClientRect();
      const view = window.innerHeight || 800;
      const start = view * 0.75;
      const end = view * 0.25;
      const raw = (start - rect.top) / (start - end + rect.height);
      const pct = Math.max(0, Math.min(1, raw)) * 100;
      timelineProgress.style.height = pct + "%";
    };
    updateTimeline();
    window.addEventListener("scroll", updateTimeline, { passive: true });
    window.addEventListener("resize", updateTimeline, { passive: true });
  }

  const canvas = document.getElementById("net-bg");

  if (canvas && !reduceMotion) {
    const ctx = canvas.getContext("2d");
    const mouse = { x: -9999, y: -9999 };
    let particles = [];
    let raf = 0;
    let running = false;

    const size = () => ({
      w: window.innerWidth,
      h: window.innerHeight,
    });

    const resize = () => {
      const { w, h } = size();
      const dpr = Math.min(window.devicePixelRatio || 1, 1.75);
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      canvas.style.width = w + "px";
      canvas.style.height = h + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const count = w < 640 ? 22 : w < 900 ? 36 : 48;
      particles = Array.from({ length: count }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.55,
        vy: (Math.random() - 0.5) * 0.55,
      }));
    };

    window.addEventListener(
      "mousemove",
      (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
      },
      { passive: true }
    );

    const tick = () => {
      if (!running) return;
      const { w, h } = size();
      ctx.clearRect(0, 0, w, h);
      const link = w < 640 ? 96 : 132;
      const repulse = 120;

      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > w) p.vx *= -1;
        if (p.y < 0 || p.y > h) p.vy *= -1;
        p.x = Math.max(0, Math.min(w, p.x));
        p.y = Math.max(0, Math.min(h, p.y));

        const dx = p.x - mouse.x;
        const dy = p.y - mouse.y;
        const dist = Math.hypot(dx, dy);
        if (dist < repulse && dist > 0.01) {
          const force = ((repulse - dist) / repulse) * 2.6;
          p.x += (dx / dist) * force;
          p.y += (dy / dist) * force;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
        const accent2 = getComputedStyle(document.documentElement)
          .getPropertyValue("--accent-2-rgb")
          .trim() || "20, 184, 166";
        ctx.fillStyle = `rgba(${accent2}, 0.85)`;
        ctx.fill();
      });

      for (let i = 0; i < particles.length; i++) {
        const a = particles[i];
        for (let j = i + 1; j < particles.length; j++) {
          const b = particles[j];
          const d = Math.hypot(a.x - b.x, a.y - b.y);
          if (d < link) {
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            const accent = getComputedStyle(document.documentElement)
              .getPropertyValue("--accent-rgb")
              .trim() || "34, 197, 94";
            ctx.strokeStyle = `rgba(${accent}, ${0.42 * (1 - d / link)})`;
            ctx.lineWidth = 1.05;
            ctx.stroke();
          }
        }
      }

      raf = requestAnimationFrame(tick);
    };

    const start = () => {
      if (running) return;
      running = true;
      raf = requestAnimationFrame(tick);
    };

    const stop = () => {
      running = false;
      cancelAnimationFrame(raf);
    };

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) stop();
      else start();
    });

    window.addEventListener("resize", resize, { passive: true });
    resize();
    start();
  }

  const form = document.querySelector(".contact-form");
  const successEl = document.getElementById("contact-success");
  const errorEl = document.getElementById("contact-error");
  const thanksEl = document.getElementById("contact-thanks");
  const sendAnother = document.getElementById("send-another");
  const submitBtn = document.getElementById("contact-submit");

  if (form) {
    const submitLabel = submitBtn && submitBtn.querySelector(".btn__label");
    const defaultLabel = (submitLabel && submitLabel.textContent.trim()) || "Send Message";
    const contactEmail = form.dataset.contactEmail || "";
    const nameInput = form.querySelector("#name");
    const emailInput = form.querySelector("#email");
    const messageInput = form.querySelector("#message");
    let submitting = false;

    const firstName = (value) => (value || "").trim().split(/\s+/)[0] || "";

    const setSubmitting = (on) => {
      submitting = on;
      form.setAttribute("aria-busy", on ? "true" : "false");
      if (!submitBtn) return;
      submitBtn.disabled = on;
      if (submitLabel) submitLabel.textContent = on ? "Sending..." : defaultLabel;
      else submitBtn.textContent = on ? "Sending..." : defaultLabel;
    };

    const panel = document.getElementById("contact-panel");

    const hideError = () => {
      if (!errorEl) return;
      errorEl.hidden = true;
      errorEl.replaceChildren();
    };

    const hideSuccess = () => {
      if (!successEl) return;
      successEl.hidden = true;
      successEl.setAttribute("aria-hidden", "true");
      successEl.setAttribute("inert", "");
      successEl.inert = true;
    };

    const revealSuccess = () => {
      if (!successEl) return;
      successEl.hidden = false;
      successEl.setAttribute("aria-hidden", "false");
      successEl.removeAttribute("inert");
      successEl.inert = false;
    };

    const showForm = () => {
      form.hidden = false;
      form.removeAttribute("aria-hidden");
      form.removeAttribute("inert");
      form.inert = false;
    };

    const hideForm = () => {
      form.hidden = true;
      form.setAttribute("aria-hidden", "true");
      form.setAttribute("inert", "");
      form.inert = true;
    };

    const showError = (text) => {
      hideSuccess();
      if (panel) panel.classList.remove("is-success");
      showForm();
      if (!errorEl) return;
      errorEl.hidden = false;
      errorEl.replaceChildren();
      errorEl.append(text);
      if (contactEmail) {
        errorEl.append(" Please try again, or email ");
        const link = document.createElement("a");
        link.href = "mailto:" + contactEmail;
        link.textContent = contactEmail;
        errorEl.append(link);
        errorEl.append(".");
      }
    };

    const setThanksName = (visitorName) => {
      if (!thanksEl) return;
      const first = firstName(visitorName);
      thanksEl.replaceChildren();
      if (!first) {
        thanksEl.textContent = "Thanks — I got it.";
        return;
      }
      thanksEl.append("Thanks, ");
      const nameSpan = document.createElement("span");
      nameSpan.className = "text-accent";
      nameSpan.textContent = first + ".";
      thanksEl.append(nameSpan);
    };

    const showSuccess = (visitorName) => {
      hideError();
      setThanksName(visitorName);
      revealSuccess();
      if (panel) panel.classList.add("is-success");
      hideForm();
      if (thanksEl) thanksEl.focus();
    };

    const showFormAgain = () => {
      hideSuccess();
      if (panel) panel.classList.remove("is-success");
      showForm();
      hideError();
      form.reset();
      setSubmitting(false);
      if (nameInput) nameInput.focus();
    };

    if (sendAnother) {
      sendAnother.addEventListener("click", showFormAgain);
    }

    document.querySelectorAll("[data-copy]").forEach((el) => {
      el.addEventListener("click", async () => {
        const value = el.getAttribute("data-copy");
        if (!value || !navigator.clipboard) return;
        try {
          await navigator.clipboard.writeText(value);
          const label = el.querySelector(".connect-label");
          if (!label) return;
          const previous = label.textContent;
          label.textContent = "Copied";
          label.classList.add("is-copied");
          window.setTimeout(() => {
            label.textContent = previous;
            label.classList.remove("is-copied");
          }, 1400);
        } catch (_) {
          /* keep the default mailto/tel action */
        }
      });
    });

    form.addEventListener("submit", async (event) => {
      if (submitting) {
        event.preventDefault();
        return;
      }

      const name = (nameInput && nameInput.value.trim()) || "";
      const email = (emailInput && emailInput.value.trim()) || "";
      const message = (messageInput && messageInput.value.trim()) || "";
      if (!name || !email || !message) return;

      hideError();

      if (!form.dataset.web3formsKey) {
        setSubmitting(true);
        return;
      }

      event.preventDefault();
      setSubmitting(true);
      try {
        const response = await fetch("https://api.web3forms.com/submit", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify({
            access_key: form.dataset.web3formsKey,
            name,
            email,
            message,
            subject: "Portfolio message from " + name,
            from_name: "Mohit Kasture Portfolio",
            replyto: email,
            botcheck: false,
          }),
        });
        const result = await response.json();
        if (!result.success) throw new Error(result.message || "Send failed");
        showSuccess(name);
      } catch (err) {
        showError("Message could not be sent.");
      } finally {
        setSubmitting(false);
      }
    });
  }

  const track = (eventType, label = "", metadata = {}) => {
    fetch("/api/analytics/track/", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({
        event_type: eventType,
        path: window.location.pathname,
        label,
        metadata,
      }),
    }).catch(() => {});
  };

  document.querySelectorAll("[data-track]").forEach((el) => {
    el.addEventListener("click", () => {
      track(el.getAttribute("data-track"), el.getAttribute("data-track-label") || el.textContent.trim());
    });
  });

  const askAssistant = async (question, logEl) => {
    const user = document.createElement("p");
    user.className = "ai-bubble ai-bubble--user";
    user.textContent = question;
    logEl.appendChild(user);
    const pending = document.createElement("p");
    pending.className = "ai-bubble";
    pending.textContent = "Thinking…";
    logEl.appendChild(pending);
    logEl.scrollTop = logEl.scrollHeight;
    try {
      const res = await fetch("/api/assistant/", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      pending.textContent = data.answer || data.detail || "No answer.";
      pending.style.whiteSpace = "pre-wrap";
    } catch (_) {
      pending.textContent = "Assistant is unavailable right now.";
    }
    logEl.scrollTop = logEl.scrollHeight;
  };

  const aiForm = document.getElementById("ai-form");
  const aiLog = document.getElementById("ai-log");
  if (aiForm && aiLog) {
    aiForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const input = document.getElementById("ai-question");
      const q = (input.value || "").trim();
      if (!q) return;
      input.value = "";
      askAssistant(q, aiLog);
    });
  }

  const fabBtn = document.getElementById("ai-fab-btn");
  const fabPanel = document.getElementById("ai-fab-panel");
  const fabBackdrop = document.getElementById("ai-fab-backdrop");
  const fabForm = document.getElementById("ai-fab-form");
  const fabLog = document.getElementById("ai-fab-log");
  if (fabBtn && fabPanel) {
    const setFabOpen = (open) => {
      if (open) {
        fabPanel.removeAttribute("hidden");
        if (fabBackdrop) fabBackdrop.removeAttribute("hidden");
      } else {
        fabPanel.setAttribute("hidden", "");
        if (fabBackdrop) fabBackdrop.setAttribute("hidden", "");
      }
      fabBtn.setAttribute("aria-expanded", String(open));
    };
    fabBtn.addEventListener("click", () => {
      setFabOpen(fabPanel.hasAttribute("hidden"));
    });
    if (fabBackdrop) {
      fabBackdrop.addEventListener("click", () => setFabOpen(false));
    }
  }
  if (fabForm && fabLog) {
    fabForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const input = document.getElementById("ai-fab-input");
      const q = (input.value || "").trim();
      if (!q) return;
      input.value = "";
      askAssistant(q, fabLog);
    });
  }

  const searchForm = document.getElementById("project-search-form");
  const searchOut = document.getElementById("project-search-results");
  if (searchForm && searchOut) {
    searchForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const q = (document.getElementById("project-search-q").value || "").trim();
      if (!q) return;
      searchOut.hidden = false;
      searchOut.innerHTML = "<p class='nl-search__hit'>Searching…</p>";
      try {
        const res = await fetch("/api/projects/search/?q=" + encodeURIComponent(q));
        const data = await res.json();
        if (!data.results || !data.results.length) {
          searchOut.innerHTML = "<p class='nl-search__hit'>No matching projects.</p>";
          return;
        }
        searchOut.innerHTML = data.results
          .map((hit) => {
            const p = hit.project;
            const tags = (p.tech_stack || []).slice(0, 6).join(" · ");
            return (
              "<article class='nl-search__hit'><strong>" +
              p.title +
              "</strong> <span style='opacity:.7'>(" +
              hit.score +
              ")</span><br>" +
              (p.tagline || p.overview || "").slice(0, 160) +
              "<br><span style='font-family:var(--mono);font-size:.8rem;color:var(--accent)'>" +
              tags +
              "</span></article>"
            );
          })
          .join("");
      } catch (_) {
        searchOut.innerHTML = "<p class='nl-search__hit'>Search failed.</p>";
      }
    });
  }

  const resumeForm = document.getElementById("resume-analyze-form");
  const resumeOut = document.getElementById("resume-analyze-out");

  const escapeHtml = (value) =>
    String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");

  const chipRow = (items, variant) => {
    const list = Array.isArray(items) ? items.filter(Boolean) : [];
    if (!list.length) return '<p class="analyzer__empty">None found</p>';
    const cls = variant ? `analyzer__chip analyzer__chip--${variant}` : "analyzer__chip";
    return `<div class="analyzer__chips">${list
      .map((item) => `<span class="${cls}">${escapeHtml(item)}</span>`)
      .join("")}</div>`;
  };

  const suggestionList = (raw) => {
    const text = String(raw || "").trim();
    if (!text) return '<p class="analyzer__empty">No suggestions yet.</p>';
    const lines = text
      .split(/\n+/)
      .map((line) => line.replace(/^[-*•\d.)\s]+/, "").trim())
      .filter(Boolean);
    if (!lines.length) return `<p class="analyzer__empty">${escapeHtml(text)}</p>`;
    return `<ul class="analyzer__list">${lines
      .map((line) => `<li>${escapeHtml(line)}</li>`)
      .join("")}</ul>`;
  };

  const renderResumeResult = (data) => {
    if (!data || data.detail) {
      return `<p class="analyzer__status analyzer__status--error">${escapeHtml(
        data?.detail || "Analysis failed."
      )}</p>`;
    }
    const scores = data.scores || {};
    const extracted = data.extracted || {};
    const ats = Number(scores.ats_score) || 0;
    const mode = data.mode || "rules";
    const contactBits = [
      ...(extracted.emails || []),
      ...(extracted.phones || []),
      ...(extracted.github || []),
      ...(extracted.linkedin || []),
    ];

    return `
      <div class="analyzer__results">
        <div class="analyzer__hero">
          <div class="analyzer__score-main">
            <div class="analyzer__score-ring" style="--pct:${Math.max(0, Math.min(100, ats))}">
              <strong>${escapeHtml(ats)}</strong>
            </div>
            <div class="analyzer__score-copy">
              <h4>ATS-style score</h4>
              <p>Deterministic scoring · mode: ${escapeHtml(mode)}</p>
            </div>
          </div>
          <div class="analyzer__score-grid">
            <div class="analyzer__metric"><span>Skills</span><strong>${escapeHtml(scores.skills_match ?? "—")}</strong></div>
            <div class="analyzer__metric"><span>Experience</span><strong>${escapeHtml(scores.experience ?? "—")}</strong></div>
            <div class="analyzer__metric"><span>Projects</span><strong>${escapeHtml(scores.projects ?? "—")}</strong></div>
            <div class="analyzer__metric"><span>Contact</span><strong>${escapeHtml(scores.contact ?? "—")}</strong></div>
          </div>
        </div>

        <div class="analyzer__block">
          <h4>Contact &amp; links</h4>
          ${
            contactBits.length
              ? `<div class="analyzer__facts">
                  <div class="analyzer__fact"><span>Email</span><strong>${escapeHtml((extracted.emails || []).join(", ") || "—")}</strong></div>
                  <div class="analyzer__fact"><span>Phone</span><strong>${escapeHtml((extracted.phones || []).join(", ") || "—")}</strong></div>
                  <div class="analyzer__fact"><span>GitHub</span><strong>${escapeHtml((extracted.github || []).join(", ") || "—")}</strong></div>
                  <div class="analyzer__fact"><span>LinkedIn</span><strong>${escapeHtml((extracted.linkedin || []).join(", ") || "—")}</strong></div>
                </div>`
              : '<p class="analyzer__empty">No contact details detected.</p>'
          }
        </div>

        <div class="analyzer__block">
          <h4>Technologies found</h4>
          ${chipRow(extracted.technologies, "ok")}
        </div>

        <div class="analyzer__block">
          <h4>Matched keywords</h4>
          ${chipRow(extracted.matched_keywords, "ok")}
        </div>

        <div class="analyzer__block">
          <h4>Missing keywords</h4>
          ${chipRow(extracted.missing_keywords, "miss")}
        </div>

        <div class="analyzer__block">
          <h4>Improvement suggestions</h4>
          ${suggestionList(data.suggestions)}
        </div>
      </div>
    `;
  };

  if (resumeForm && resumeOut) {
    resumeForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const fileInput = document.getElementById("resume-file");
      const text = (document.getElementById("resume-text").value || "").trim();
      const body = new FormData();
      if (fileInput.files && fileInput.files[0]) body.append("file", fileInput.files[0]);
      if (text) body.append("text", text);
      resumeOut.hidden = false;
      resumeOut.innerHTML = '<p class="analyzer__status">Analyzing…</p>';
      try {
        const res = await fetch("/api/resume/analyze/", { method: "POST", body });
        const data = await res.json();
        if (!res.ok) {
          resumeOut.innerHTML = `<p class="analyzer__status analyzer__status--error">${escapeHtml(
            data.detail || "Analysis failed."
          )}</p>`;
          return;
        }
        resumeOut.innerHTML = renderResumeResult(data);
      } catch (_) {
        resumeOut.innerHTML =
          '<p class="analyzer__status analyzer__status--error">Analysis failed.</p>';
      }
    });
  }

  const npcForm = document.getElementById("npc-form");
  const npcLog = document.getElementById("npc-log");
  if (npcForm && npcLog) {
    npcForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const input = document.getElementById("npc-message");
      const message = (input.value || "").trim();
      if (!message) return;
      input.value = "";
      const user = document.createElement("p");
      user.className = "npc-bubble npc-bubble--user";
      user.textContent = "You: " + message;
      npcLog.appendChild(user);
      try {
        const res = await fetch("/api/npc/", {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify({ message, npc: "guide" }),
        });
        const data = await res.json();
        const bubble = document.createElement("p");
        bubble.className = "npc-bubble";
        bubble.innerHTML = "<strong>" + (data.npc || "Asha") + ":</strong> " + (data.reply || "");
        npcLog.appendChild(bubble);
      } catch (_) {
        const bubble = document.createElement("p");
        bubble.className = "npc-bubble";
        bubble.textContent = "NPC is offline for a moment.";
        npcLog.appendChild(bubble);
      }
      npcLog.scrollTop = npcLog.scrollHeight;
    });
  }
})();
