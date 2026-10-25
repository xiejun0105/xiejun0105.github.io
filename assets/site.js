
(function () {
  const root = document.documentElement;
  let saved;
  try {
    saved = localStorage.getItem("theme");
  } catch (_) {
    // Theme switching still works when browser storage is unavailable.
  }
  const hour = new Date().getHours();
  const defaultTheme = hour >= 7 && hour < 18 ? "light" : "dark";
  root.setAttribute("data-theme", saved === "light" || saved === "dark" ? saved : defaultTheme);

  window.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("a[href]").forEach((link) => {
      const url = new URL(link.href, window.location.href);
      if ((url.protocol === "https:" || url.protocol === "http:") && url.origin !== window.location.origin) {
        link.target = "_blank";
        link.relList.add("noopener", "noreferrer");
      }
    });
    document.querySelectorAll(".scroll-home-nav").forEach((header) => {
      // Track the original position, not the moving edge of the sticky header.
      const marker = document.createElement("span");
      marker.setAttribute("aria-hidden", "true");
      marker.style.cssText = "display:block;height:0;pointer-events:none;";
      header.before(marker);
      function syncHeader() {
        header.classList.toggle("is-scrolled", marker.getBoundingClientRect().top < -1);
      }
      syncHeader();
      if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(syncHeader, { rootMargin: "1px 0px 0px" });
        observer.observe(marker);
      } else {
        window.addEventListener("scroll", syncHeader, { passive: true });
      }
      window.addEventListener("pageshow", syncHeader);
    });
    document.querySelectorAll(".news-thumb img").forEach((img) => {
      function showFallback() { img.style.display = "none"; }
      img.addEventListener("error", showFallback);
      if (img.complete && !img.naturalWidth) showFallback();
    });
    const themeButtons = document.querySelectorAll("[data-theme-toggle]");
    if (themeButtons.length) {
      function syncLabel() {
        const theme = root.getAttribute("data-theme");
        themeButtons.forEach((btn) => {
          btn.setAttribute("aria-label", theme === "dark" ? "Switch to light background" : "Switch to dark background");
          btn.setAttribute("title", theme === "dark" ? "Light" : "Dark");
        });
      }
      themeButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
          const current = root.getAttribute("data-theme") || "light";
          const next = current === "dark" ? "light" : "dark";
          root.setAttribute("data-theme", next);
          try {
            localStorage.setItem("theme", next);
          } catch (_) {
            // Keep the manual choice for this page even if it cannot be saved.
          }
          syncLabel();
        });
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

    const blogLocale = document.documentElement.lang || "en";
    const blogLabels = blogLocale.startsWith("ja")
      ? { pinned: "固定", published: "公開", updated: "更新" }
      : blogLocale.startsWith("zh")
      ? { pinned: "置顶", published: "发布", updated: "更新" }
      : { pinned: "Pinned", published: "Published", updated: "Updated" };

    function blogDate(value) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(value || "")) return null;
      const date = new Date(`${value}T00:00:00Z`);
      return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value ? date : null;
    }

    function dateMarkup(value, label) {
      const date = blogDate(value);
      if (!date) return "";
      const text = new Intl.DateTimeFormat(blogLocale, {
        year: "numeric", month: "short", day: "numeric", timeZone: "UTC"
      }).format(date);
      return `<time datetime="${escapeHtml(value)}" aria-label="${escapeHtml(label)} ${escapeHtml(text)}">${escapeHtml(text)}</time>`;
    }

    const sortedBlogPosts = [...posts].sort((a, b) => {
      if (!!a.pinned !== !!b.pinned) return a.pinned ? -1 : 1;
      if (a.pinned && b.pinned) {
        const rankA = Number.isFinite(a.pinOrder) ? a.pinOrder : Number.MAX_SAFE_INTEGER;
        const rankB = Number.isFinite(b.pinOrder) ? b.pinOrder : Number.MAX_SAFE_INTEGER;
        if (rankA !== rankB) return rankA - rankB;
      }
      return (blogDate(b.publishedAt)?.getTime() || 0) - (blogDate(a.publishedAt)?.getTime() || 0);
    });

    const articleHeader = document.querySelector(".blog-post .blog-post-hero");
    if (articleHeader) {
      const path = window.location.pathname.replace(/index\.html$/, "").replace(/\/$/, "");
      const post = posts.find(item => item.href.replace(/\/$/, "") === path);
      if (post && blogDate(post.publishedAt)) {
        const meta = document.createElement("div");
        meta.className = "blog-article-details";
        meta.innerHTML = `<span>${blogLabels.published} ${dateMarkup(post.publishedAt, blogLabels.published)}</span>`
          + (blogDate(post.updatedAt) && post.updatedAt !== post.publishedAt
            ? `<span>${blogLabels.updated} ${dateMarkup(post.updatedAt, blogLabels.updated)}</span>` : "");
        articleHeader.querySelector(".page-description")?.after(meta);
      }
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
        if (!filter || filter === "All") return sortedBlogPosts;
        return sortedBlogPosts.filter((post) => Array.isArray(post.tags) && post.tags.includes(filter));
      }

      function render(filter) {
        const visiblePosts = filteredPosts(filter);
        if (!visiblePosts.length) {
          list.innerHTML = '<div class="item-meta">No posts in this category yet.</div>';
          return;
        }

        list.innerHTML = visiblePosts.map((post) => `
          <a class="blog-index-card" href="${escapeHtml(post.href)}">
            <span class="blog-index-image"><img src="${escapeHtml(post.image)}" alt="" loading="lazy" decoding="async"></span>
            <div class="blog-index-body">
              <div class="blog-card-meta blog-list-meta">
                ${post.pinned ? `<span class="blog-pin">${blogLabels.pinned}</span>` : ""}
                <span>${escapeHtml(post.tag)}</span>
                ${dateMarkup(post.publishedAt, blogLabels.published)}
              </div>
              <h2>${escapeHtml(post.title)}</h2>
              <p>${escapeHtml(post.excerpt)}</p>
            </div>
          </a>
        `).join("");
      }

      const requestedTag = new URLSearchParams(window.location.search).get("tag");
      const queryTag = requestedTag === "Climate" ? "Climate Change" : requestedTag;
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
