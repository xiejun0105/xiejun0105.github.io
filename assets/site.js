
(function () {
  const root = document.documentElement;
  const saved = localStorage.getItem("theme");
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  root.setAttribute("data-theme", saved || (prefersDark ? "dark" : "light"));

  window.addEventListener("DOMContentLoaded", function () {
    const btn = document.querySelector("[data-theme-toggle]");
    if (btn) {
      function syncLabel() {
        const theme = root.getAttribute("data-theme");
        btn.setAttribute("aria-label", theme === "dark" ? "Switch to warm light background" : "Switch to dark background");
        btn.setAttribute("title", theme === "dark" ? "Warm light" : "Dark");
      }
      btn.addEventListener("click", function () {
        const current = root.getAttribute("data-theme") || "light";
        const next = current === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        localStorage.setItem("theme", next);
        syncLabel();
      });
      syncLabel();
    }

    const posts = Array.isArray(window.BLOG_POSTS) ? window.BLOG_POSTS : [];
    const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function escapeHtml(value) {
      return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    document.querySelectorAll("[data-featured-blog-carousel]").forEach((carousel) => {
      const featuredPosts = posts.filter((post) => post.featured).slice(0, 5);
      const carouselPosts = featuredPosts.length ? featuredPosts : posts.slice(0, 5);
      if (!carouselPosts.length) return;

      const wrap = carousel.closest(".featured-blog");
      const prev = wrap ? wrap.querySelector("[data-featured-blog-prev]") : null;
      const next = wrap ? wrap.querySelector("[data-featured-blog-next]") : null;
      const dotsWrap = wrap ? wrap.querySelector("[data-featured-blog-dots]") : null;
      let current = 0;
      let timer = null;

      carousel.innerHTML = carouselPosts.map((post) => `
        <a class="featured-blog-slide" href="${escapeHtml(post.href)}">
          <div class="featured-blog-image"><img src="${escapeHtml(post.image)}" alt=""></div>
          <div class="featured-blog-content">
            <div class="blog-card-meta">${escapeHtml(post.tag)}</div>
            <h2>${escapeHtml(post.featuredTitle || post.title)}</h2>
            <p>${escapeHtml(post.excerpt)}</p>
            <span class="blog-card-status">${escapeHtml(post.status)}</span>
          </div>
        </a>
      `).join("");

      if (dotsWrap) {
        dotsWrap.innerHTML = carouselPosts.map((post) => (
          `<button type="button" data-featured-blog-dot aria-label="Show ${escapeHtml(post.title)}"></button>`
        )).join("");
      }

      const slides = Array.from(carousel.querySelectorAll(".featured-blog-slide"));
      const dots = dotsWrap ? Array.from(dotsWrap.querySelectorAll("[data-featured-blog-dot]")) : [];

      function showSlide(index, behavior) {
        current = (index + slides.length) % slides.length;
        slides.forEach((slide, slideIndex) => {
          slide.setAttribute("aria-hidden", slideIndex === current ? "false" : "true");
        });
        carousel.scrollTo({
          left: carousel.clientWidth * current,
          behavior: behavior || "smooth"
        });
        dots.forEach((dot, dotIndex) => {
          dot.classList.toggle("active", dotIndex === current);
          dot.setAttribute("aria-current", dotIndex === current ? "true" : "false");
        });
      }

      function startAuto() {
        if (prefersReducedMotion || slides.length < 2) return;
        stopAuto();
        timer = window.setInterval(() => showSlide(current + 1), 6200);
      }

      function stopAuto() {
        if (timer) window.clearInterval(timer);
        timer = null;
      }

      if (prev) prev.addEventListener("click", () => {
        showSlide(current - 1);
        startAuto();
      });
      if (next) next.addEventListener("click", () => {
        showSlide(current + 1);
        startAuto();
      });
      dots.forEach((dot, dotIndex) => {
        dot.addEventListener("click", () => {
          showSlide(dotIndex);
          startAuto();
        });
      });

      carousel.addEventListener("mouseenter", stopAuto);
      carousel.addEventListener("mouseleave", startAuto);
      carousel.addEventListener("focusin", stopAuto);
      carousel.addEventListener("focusout", startAuto);

      const keepSlideAligned = () => showSlide(current, "auto");
      if ("ResizeObserver" in window) {
        new ResizeObserver(keepSlideAligned).observe(carousel);
      } else {
        window.addEventListener("resize", keepSlideAligned);
      }

      showSlide(0, "auto");
      startAuto();
    });

    document.querySelectorAll("[data-blog-list]").forEach((list) => {
      const scope = list.closest("main") || document;
      const filters = Array.from(scope.querySelectorAll("[data-blog-filter]"));

      function filteredPosts(filter) {
        if (!filter || filter === "All") return posts;
        return posts.filter((post) => Array.isArray(post.tags) && post.tags.includes(filter));
      }

      function render(filter) {
        const visiblePosts = filteredPosts(filter);
        if (!visiblePosts.length) {
          list.innerHTML = '<div class="item-meta">No posts in this category yet.</div>';
          return;
        }

        list.innerHTML = visiblePosts.map((post) => `
          <a class="blog-index-card" href="${escapeHtml(post.href)}">
            <div class="blog-index-image"><img src="${escapeHtml(post.image)}" alt=""></div>
            <div class="blog-index-body">
              <div class="blog-card-meta">${escapeHtml(post.tag)}</div>
              <h2>${escapeHtml(post.title)}</h2>
              <p>${escapeHtml(post.excerpt)}</p>
              <span class="blog-card-status">${escapeHtml(post.status)}</span>
            </div>
          </a>
        `).join("");
      }

      const queryTag = new URLSearchParams(window.location.search).get("tag");
      const initialFilter = filters.some((filter) => filter.dataset.blogFilter === queryTag) ? queryTag : "All";

      filters.forEach((filter) => {
        const value = filter.dataset.blogFilter || "All";
        filter.classList.toggle("active", value === initialFilter);
        filter.setAttribute("aria-pressed", value === initialFilter ? "true" : "false");
        filter.addEventListener("click", () => {
          filters.forEach((item) => {
            item.classList.remove("active");
            item.setAttribute("aria-pressed", "false");
          });
          filter.classList.add("active");
          filter.setAttribute("aria-pressed", "true");
          render(value);
          if (window.history && window.history.replaceState) {
            const url = new URL(window.location.href);
            if (value === "All") {
              url.searchParams.delete("tag");
            } else {
              url.searchParams.set("tag", value);
            }
            window.history.replaceState({}, "", url);
          }
        });
      });

      render(initialFilter);
    });

    const timelineLinks = Array.from(document.querySelectorAll(".timeline-nav a"));
    const sections = Array.from(document.querySelectorAll("[data-year-section]"));
    if (timelineLinks.length && sections.length && "IntersectionObserver" in window) {
      const byId = new Map(timelineLinks.map(a => [a.getAttribute("href").replace("#",""), a]));
      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            timelineLinks.forEach(a => a.classList.remove("active"));
            const active = byId.get(entry.target.id);
            if (active) active.classList.add("active");
          }
        });
      }, { rootMargin: "-20% 0px -65% 0px", threshold: 0.01 });
      sections.forEach(section => observer.observe(section));
    }
    // Mobile: make Publications / Teaching go directly to default pages
    document.querySelectorAll(".nav-item .nav-trigger").forEach((trigger) => {
      trigger.addEventListener("click", (event) => {
        if (window.innerWidth > 900) return;

        const item = trigger.closest(".nav-item");
        if (!item || !item.querySelector(".dropdown")) return;

        const text = trigger.textContent.trim();

        event.preventDefault();
        event.stopPropagation();

        const path = window.location.pathname;
        const prefix =
          path.startsWith("/ja/") ? "/ja" :
          path.startsWith("/zh/") ? "/zh" :
          "";

        if (
          text === "Publications" ||
          text === "業績" ||
          text === "发表成果"
        ) {
          window.location.href = `${prefix}/publications/journal/`;
        }

        if (
          text === "Teaching" ||
          text === "教育・研究指導" ||
          text === "教学与指导"
        ) {
          window.location.href = `${prefix}/teaching/supervision/`;
        }
      });
    });
  });
})();
