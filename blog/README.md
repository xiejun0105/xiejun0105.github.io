# Blog content and assets

Follow the [site-wide maintenance rules](../docs/MAINTENANCE.md) for all updates.

## Naming

Use a stable descriptive slug, not a sequential code such as `blog-001`.
The slug identifies an article even when its display title or list order changes.
Keep existing published URLs stable to preserve incoming links.
Use dates in local draft/archive filenames instead of renaming published folders.

```text
blog/
  supply-chain/
    index.html       # Published article served by GitHub Pages
data/
  blog-assets.json   # Article slug -> cover and in-article image paths
assets/
  blog-data.js       # Titles, dates, categories, filter tags and pinned ordering
images/
  papers/            # Shared paper-derived figures: Author_Year_content.png
```

Drafts and original PDFs remain in the ignored local directories:
`・Blog draft/` and `・My publications/`.
Never link to these local directories from a published page.

## Images

Keep the author-year-content filename for paper-derived images. That name
identifies the source; `data/blog-assets.json` identifies which articles use it.
Shared images can appear in several articles without duplicate copies or a
Blog-specific suffix. Existing images under `/images/` keep their current URLs.

For future artwork used only by one article, use a local `assets/` subdirectory
under that article, for example `blog/climate-change/assets/cover.webp`.
Paper-derived figures that may be reused belong in `/images/papers/` instead.
Do not move already published assets solely to fit this convention.

## Publishing and updates

1. Review the local Markdown draft and selected images. For revisions, archive
   the current served version before changing it.
2. Create/update `blog/<slug>/index.html` following an existing article layout.
3. Keep published HTML as the served source. Markdown versions belong only in
   the ignored local archive, not as duplicate sources in the public directory.
4. Add/update its record in `assets/blog-data.js`. List ordering follows the
   publication and pinning rules below. The homepage uses Recent Publications;
   Blog pinning does not change that section.
5. Update `data/blog-assets.json` with its cover and all in-article images.
6. New filter tags also need matching buttons in `blog/index.html`,
   `ja/blog/index.html` and `zh/blog/index.html`.
7. Run `python3 tools/build_site.py` to refresh shared navigation and footers.
   This does not upload or deploy the site and does not convert Markdown bodies.
8. Verify links, figures, filters and mobile layout. Archive the completed version
   with `python3 tools/archive-blog.py`, preserve editorial notes separately, then
   remove its completed working draft after checking the archive is complete.
   Drafts remain only for unpublished work or active revisions.

Article bodies remain in English across the three language-specific lists.
Do not add invented translations or change existing article URLs.

## Dates, pinned posts and tags

```js
publishedAt: "2026-10-24", // YYYY-MM-DD, original publication date
updatedAt: "2026-11-02",   // Optional, only for substantive later revisions
pinned: true,             // Keep this article ahead of unpinned articles
pinOrder: 1,              // Smaller numbers first when several are pinned
tag: "Supply Chains & Sustainability", // Display category
tags: ["ESG", "Human Capital", "Supply Chains"] // Filter membership
```

Lists show pinned posts first, then publication date descending. Equal pin
orders use the same date rule; ties preserve file order. Undated posts come
after dated posts within their group and do not display a fabricated date.
Filters use the same ordering. Pinning is an editorial setting, not a topic tag.
Use `Climate Change`, not `Climate`, for the climate topic. Existing
`?tag=Climate` links remain supported through a client-side alias.
The original array order and obsolete homepage `featured` flag no longer
control the Blog list. Unpin a post with `pinned: false`; do not change its date.

About My Research is currently the only pinned post. At the user's request,
its republication date is 2026-10-24; earlier metadata remains in local archives.
Ordinary revisions retain the original date unless republication is requested.
The three older posts'
dates were backfilled from their earliest Git records, not independently
verified deployment dates (`dateSource: "first-git-record"`). Replace these
with confirmed publication dates when available. About My Research, Supply Chain
and Climate Change dates record local site preparation (`dateSource: "site-prepared"`),
not a GitHub push.
All dates are formatted without timezone-based day shifts. Article pages read
the same metadata as the list and can show a separate optional update date.

Visible captions contain the explanation and author-year credit, without PDF
filenames or page numbers. Keep detailed figure/page provenance in local
editorial notes. References link to the paper DOI.

## Local history before updates or withdrawal

Run `python3 tools/archive-blog.py` to snapshot all listed articles into the
ignored `・Blog draft/archive/` directory. Use `--slug supply-chain` for one post.
Each `YYYY-MM-DD_v001.md` version records metadata and links to preserved local
image copies. Repeated runs skip unchanged posts; `--force` creates a checkpoint.
The date is the archive date in Japan, independent of `publishedAt`.

For withdrawal, run the archive command before removing its list entry:

```sh
python3 tools/archive-blog.py --slug supply-chain --event before-withdrawal --force --note 'Pending revision'
```

This command saves history only; it does not withdraw, restore or publish a page.
Public HTML is the archive source. Finished Markdown lives only in the local
archive; revisions create new versions without overwriting existing snapshots.
