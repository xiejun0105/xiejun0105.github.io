
(function () {
  const root = document.documentElement;
  const saved = localStorage.getItem("theme");
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const initial = saved || (prefersDark ? "dark" : "light");

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    const button = document.querySelector("[data-theme-toggle]");
    if (button) {
      const isDark = theme === "dark";
      button.querySelector(".icon").textContent = isDark ? "☀" : "☾";
      button.querySelector(".theme-label").textContent = isDark ? "Warm" : "Dark";
      button.setAttribute("aria-label", isDark ? "Switch to warm light background" : "Switch to dark background");
    }
  }

  applyTheme(initial);

  document.addEventListener("DOMContentLoaded", function () {
    const button = document.querySelector("[data-theme-toggle]");
    if (!button) return;
    button.addEventListener("click", function () {
      const current = root.getAttribute("data-theme") || "light";
      applyTheme(current === "dark" ? "light" : "dark");
    });
    applyTheme(root.getAttribute("data-theme") || initial);
  });
})();
