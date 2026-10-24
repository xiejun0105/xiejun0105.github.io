# Paper figure previews

## Website integration

`data/paper-thumbnails.json` maps each article DOI to its selected image.
It currently covers all 27 journal articles, including curated Blog figures.
To replace a thumbnail, change its `image` path in that mapping, then run:

```sh
python3 tools/build_site.py
```

This updates all three journal lists and the five recent-publication items
on each homepage. Source PDF files are never referenced by the website.

`tools/prepare-paper-thumbnails.py` generates candidates from the local
library for papers without an existing valid image. Existing mappings and
manual selections are preserved. Figures were reviewed as a contact sheet;
the small journal preview is for recognition, with DOI links for full detail.

Source PDFs remain in the Git-ignored `/・My publications/` library.
Only selected, reviewed figure images belong in this directory.
These exported images can be committed and published with the website.

## Candidate storage

Only selected images referenced by the current site or its asset mappings stay
here. Unused alternatives were moved to the ignored local
`・Site archive/2026-10-24/images/papers/` with checksums and original paths.
The country-level financial-impact candidate from Xie (2025) remains there
for future selection; it is not a live website dependency.

## Naming convention

Use an author-year-based filename, following the existing Blog image style:

```text
FirstAuthor_Year_image_content.png
Xie_2026_supply_chain_human_capital_map.png
Keeley_2026_climate_disclosure_decomposition.png
Ida_2024_local_government_sdg_framework.png
```

This is a filename convention inspired by APA author-year citations, not a
complete APA reference. Author and year follow `data/journal-publications.json`;
the content description distinguishes papers by the same author in the same
year. DOI keys in `data/paper-thumbnails.json` preserve the exact article match.

Files ending in `_alternative` belong in the local archive until selected;
they do not replace curated Blog figures. Existing images in `/images/` keep their names.
Renaming a file does not change its pixels or crop.

## Extract another preview

Requires Python and PyMuPDF (`fitz`). From the repository root:

```sh
python3 tools/extract-paper-thumbnail.py '・My publications/paper.pdf' images/papers/FirstAuthor_Year_image_content.png
```

Optionally add `--page 8` to select a specific page. The script chooses the
largest suitable embedded image and renders its region with surrounding
vector labels preserved. This is a candidate, not an automatic editorial
selection. Review the result and figure caption before publishing.

Vector-only figures need a manually selected crop. Preserve axes, legends,
and panel labels. Check the paper's reuse terms and provide attribution
when placing a figure on the website.

Git ignore rules do not remove files already committed. Keep source PDFs
untracked; this library was untracked when the rule was added.
