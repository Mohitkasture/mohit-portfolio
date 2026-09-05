(function () {
  const nav = document.getElementById("nav");
  const toggle = document.getElementById("nav-toggle");
  const menu = document.getElementById("nav-menu");

  const onScroll = () => {
    nav.classList.toggle("is-scrolled", window.scrollY > 8);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  });

  menu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Open menu");
    });
  });

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
  document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

  const canvas = document.getElementById("net-bg");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (canvas && !reduceMotion) {
    const ctx = canvas.getContext("2d");
    const mouse = { x: -9999, y: -9999 };
    let particles = [];
    let raf = 0;

    const size = () => ({
      w: window.innerWidth,
      h: window.innerHeight,
    });

    const resize = () => {
      const { w, h } = size();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      canvas.style.width = w + "px";
      canvas.style.height = h + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const count = w < 640 ? 36 : 70;
      particles = Array.from({ length: count }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.7,
        vy: (Math.random() - 0.5) * 0.7,
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
      if (document.hidden) {
        raf = requestAnimationFrame(tick);
        return;
      }
      const { w, h } = size();
      ctx.clearRect(0, 0, w, h);
      const link = w < 640 ? 110 : 150;
      const repulse = 140;

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
          const force = ((repulse - dist) / repulse) * 3.2;
          p.x += (dx / dist) * force;
          p.y += (dy / dist) * force;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, 2.2, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(212, 255, 63, 0.85)";
        ctx.fill();
      });

      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const a = particles[i];
          const b = particles[j];
          const d = Math.hypot(a.x - b.x, a.y - b.y);
          if (d < link) {
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.strokeStyle = `rgba(212, 255, 63, ${0.38 * (1 - d / link)})`;
            ctx.lineWidth = 1.15;
            ctx.stroke();
          }
        }
      }

      raf = requestAnimationFrame(tick);
    };

    window.addEventListener("resize", resize, { passive: true });
    resize();
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(tick);
  }

  const form = document.querySelector(".contact-form");
  if (form && form.dataset.web3formsKey) {
    const resultHost = document.getElementById("contact-result");
    const contactEmail = form.dataset.contactEmail || "mkymohitkumaryadav0@gmail.com";
    const showResult = (ok, visitorName) => {
      if (!resultHost) return;
      const first = (visitorName || "").split(" ")[0].replace(/[<>&"'`]/g, "");
      const thanks = first
        ? `Thanks, ${first}.`
        : "Thanks — I got it.";
      resultHost.hidden = false;
      resultHost.innerHTML = ok
        ? `<div class="form-result form-result--ok" role="status">
            <span class="form-result__icon" aria-hidden="true">✓</span>
            <h3>${thanks}</h3>
            <p>Your message is in. I’ll reply to your email soon.</p>
            <button class="btn btn--ghost" type="button" id="send-another">Send another message</button>
          </div>`
        : `<div class="form-result form-result--error" role="status">
            <span class="form-result__icon" aria-hidden="true">!</span>
            <h3>Couldn’t send that</h3>
            <p>Please email me directly at <a href="mailto:${contactEmail}">${contactEmail}</a>.</p>
          </div>`;
      if (ok) form.hidden = true;
      const again = document.getElementById("send-another");
      if (again) {
        again.addEventListener("click", () => {
          resultHost.hidden = true;
          resultHost.innerHTML = "";
          form.hidden = false;
        });
      }
    };

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = form.querySelector("button[type=submit]");
      const name = form.name.value.trim();
      const email = form.email.value.trim();
      const message = form.message.value.trim();
      if (!name || !email || !message) return;
      if (button) button.disabled = true;
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
        showResult(true, name);
        form.reset();
      } catch (err) {
        showResult(false);
      } finally {
        if (button) button.disabled = false;
      }
    });
  }
})();
