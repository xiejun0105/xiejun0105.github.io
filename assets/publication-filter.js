(function () {
  "use strict";

  document.querySelectorAll("[data-publication-filter]").forEach((panel) => {
    const scope = panel.closest("main");
    const buttons = Array.from(panel.querySelectorAll("[data-publication-topic]"));
    const papers = Array.from(scope.querySelectorAll("[data-publication-paper]"));
    const sections = Array.from(scope.querySelectorAll("[data-year-section]"));
    const years = Array.from(scope.querySelectorAll("[data-publication-year-link]"));
    const status = panel.querySelector("[data-publication-status]");
    const extra = panel.querySelector("[data-publication-topic-extra]");
    const toggle = panel.querySelector("[data-publication-topic-toggle]");
    const empty = scope.querySelector("[data-publication-empty]");
    const topics = new Set(buttons.map((button) => button.dataset.publicationTopic));
    let activeTopic = "all";

    function expand(show) {
      panel.dataset.expanded = String(show);
      extra.hidden = !show;
      toggle.setAttribute("aria-expanded", String(show));
      toggle.querySelector("[data-toggle-label]").textContent = show ? toggle.dataset.lessLabel : toggle.dataset.moreLabel;
      toggle.querySelector("[data-toggle-icon]").textContent = show ? "−" : "+";
    }

    function topicFromURL() {
      const value = new URL(window.location.href).searchParams.get("topic");
      return topics.has(value) ? value : "all";
    }

    function syncURL(topic, push) {
      const url = new URL(window.location.href);
      if (topic === "all") url.searchParams.delete("topic");
      else url.searchParams.set("topic", topic);
      const target = sections.find((section) => "#" + section.id === url.hash);
      if (target && target.hidden) url.hash = "";
      if (url.href !== window.location.href && window.history) {
        if (push && window.history.pushState) window.history.pushState({}, "", url);
        else if (window.history.replaceState) window.history.replaceState({}, "", url);
      }
      document.querySelectorAll(".lang-nav a").forEach((link) => {
        const destination = new URL(link.href, window.location.href);
        if (destination.origin !== url.origin) return;
        if (topic === "all") destination.searchParams.delete("topic");
        else destination.searchParams.set("topic", topic);
        link.setAttribute("href", destination.pathname + destination.search + destination.hash);
      });
    }

    function filter(topic, push) {
      activeTopic = topic;
      let count = 0;
      papers.forEach((paper) => {
        const matches = topic === "all" || paper.dataset.topics.split(/\s+/).includes(topic);
        paper.hidden = !matches;
        if (matches) count += 1;
      });
      sections.forEach((section) => {
        section.hidden = !Array.from(section.querySelectorAll("[data-publication-paper]")).some((paper) => !paper.hidden);
      });
      let firstYear = true;
      years.forEach((link) => {
        const section = sections.find((item) => "#" + item.id === link.getAttribute("href"));
        link.hidden = !section || section.hidden;
        link.classList.toggle("active", !link.hidden && firstYear);
        if (!link.hidden) firstYear = false;
      });
      const selected = buttons.find((button) => button.dataset.publicationTopic === topic);
      buttons.forEach((button) => {
        const selected = button.dataset.publicationTopic === topic;
        button.classList.toggle("active", selected);
        button.setAttribute("aria-pressed", String(selected));
      });
      const template = count === 1 ? status.dataset.countOne : status.dataset.countMany;
      status.textContent = selected.dataset.publicationLabel + " · " + template.replace("{count}", count);
      empty.hidden = count !== 0;
      if (extra.contains(selected)) expand(true);
      syncURL(topic, push);
    }

    buttons.forEach((button) => button.addEventListener("click", () => {
      const topic = button.dataset.publicationTopic;
      if (topic !== activeTopic) filter(topic, true);
    }));
    toggle.addEventListener("click", () => expand(extra.hidden));
    window.addEventListener("popstate", () => filter(topicFromURL(), false));
    expand(false);
    filter(topicFromURL(), false);
    panel.hidden = false;
  });
})();
