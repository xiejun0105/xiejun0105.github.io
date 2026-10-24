# Website Maintenance Instructions

Read `docs/MAINTENANCE.md` before changing site content or asset paths.
Use the source-of-truth table in `README.md`; do not edit generated lists instead
of their data or HTML fragments. Preserve unrelated worktree changes.

## Required Workflow

- Archive an existing Blog before substantive edits or withdrawal using
  `tools/archive-blog.py`. Keep its URL stable unless explicitly asked otherwise.
- Preserve the original publication date for ordinary revisions. Reset it only
  on an explicit republication request; save the former metadata locally first.
- Keep article content, `assets/blog-data.js` and `data/blog-assets.json` aligned.
  Add new filter buttons to all three Blog indexes when adding a filter tag.
- Use shared assets once. Prefer reviewed paper-author/year/topic filenames;
  keep article-only artwork under `blog/<slug>/assets/` and new course images
  under `images/teaching/`. Never upload source PDFs or draft/export variants.
- Preserve figure labels, colors and pixels unless a visual change is requested.
  Lossless format conversion is preferred for paper and course diagrams.
- Before removing a public resource, run `tools/check_site.py`, review runtime
  and source references, then archive with `tools/archive-site-assets.py`.
  Unused candidates are not authorization for blind deletion.
- Keep PDFs, drafts, site archives and generated audit reports in the ignored
  local directories. Never link public pages to those directories.
- Run `python3 tools/build_site.py` after changing generated content or shared
  chrome, then `python3 tools/check_site.py --report tmp/site-audit.json`, the
  focused unit tests, both JavaScript syntax checks and `git diff --check`.
- Review affected desktop/mobile and light/dark views when browser access is
  available. State clearly when visual verification could not be performed.
- Archive the final article after integration; keep editorial notes locally and
  remove completed standalone working drafts only after verifying the archive.
- Do not commit, push or claim remote deployment merely because the local build
  passed. Report source integration and GitHub deployment separately.

## Scope

Keep existing article URLs and shared assets stable. Do not redesign or rewrite
unrelated content as part of resource maintenance. Do not rewrite Git history.
`check_site.py` is offline; a passing result does not verify external links,
copyright permissions, browser rendering or remote deployment.
