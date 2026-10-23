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

`tools/prepare-paper-thumbnails.py` regenerates candidates from the local
library and overwrites the mapping. Use it deliberately; preserve manual
selections before running it again. Figures were reviewed as a contact sheet;
the small journal preview is for recognition, with DOI links for full detail.

Source PDFs remain in the Git-ignored `/・My publications/` library.
Only selected, reviewed figure images belong in this directory.
These exported images can be committed and published with the website.

## Current sample

- `xie-2025-inclusive-wealth-preview.png`: page 8 of Xie (2025),
  Inclusive Wealth and ESG Practices. Country-level financial impacts on
  ROA and Tobin's Q; both panels are retained. Not yet linked on the website.

## Extract another preview

Requires Python and PyMuPDF (`fitz`). From the repository root:

```sh
python3 tools/extract-paper-thumbnail.py '・My publications/paper.pdf' images/papers/paper-preview.png
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
