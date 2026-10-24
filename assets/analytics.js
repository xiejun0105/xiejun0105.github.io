(function () {
  "use strict";

  const location = window.location;
  if (location.protocol !== "https:" || location.hostname !== "xiejun0105.github.io") return;
  if (navigator.doNotTrack === "1" || navigator.globalPrivacyControl === true) return;

  let path;
  try {
    path = decodeURIComponent(location.pathname);
  } catch (_) {
    return;
  }
  if (/(?:^|\/)(?:tmp|data|preview\.html|・Blog draft|・My publications|・Site archive)(?:\/|$)/.test(path)) return;
  if (document.querySelector("script[data-goatcounter]")) return;

  let referrer = "";
  try {
    const source = new URL(document.referrer);
    if (source.protocol === "https:" || source.protocol === "http:") referrer = source.origin;
  } catch (_) {
    // Direct visits and restricted referrers have no source domain.
  }

  // Count one canonical page path, without search terms or filter parameters.
  window.goatcounter = {
    no_events: true,
    path: location.pathname.replace(/\/index\.html$/, "/"),
    referrer: referrer
  };
  const script = document.createElement("script");
  script.async = true;
  script.src = "https://gc.zgo.at/count.js";
  script.setAttribute("data-goatcounter", "https://junxie.goatcounter.com/count");
  document.head.appendChild(script);
})();
