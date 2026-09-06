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

  const setActiveNav = () => {
    let current = null;
    const offset = 120;
    sectionEls.forEach((section) => {
      if (section.getBoundingClientRect().top - offset <= 0) current = section;
    });
    navLinks.forEach((link) => {
      const on = current && link.getAttribute("href") === "#" + current.id;
      link.classList.toggle("is-active", Boolean(on));
      if (on) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
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
        ctx.fillStyle = "rgba(212, 255, 63, 0.85)";
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
            ctx.strokeStyle = `rgba(212, 255, 63, ${0.38 * (1 - d / link)})`;
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
})();
