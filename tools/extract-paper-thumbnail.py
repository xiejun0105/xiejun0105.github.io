"""Export a representative embedded figure without publishing its source PDF."""
import argparse
from pathlib import Path

import fitz


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--page", type=int, help="Select a one-based page")
    args = parser.parse_args()
    with fitz.open(args.pdf) as doc:
        candidates = []
        for index, page in enumerate(doc):
            if args.page and index + 1 != args.page:
                continue
            for info in page.get_image_info(xrefs=True):
                box = fitz.Rect(info["bbox"]) & page.rect
                if box.is_empty or box.width < 100 or box.height < 70:
                    continue
                if box.get_area() > page.rect.get_area() * .85:
                    continue
                candidates.append((box.get_area(), index, box))
        if not candidates:
            raise SystemExit("No suitable embedded figure. Vector-only figures need manual cropping.")
        _, index, box = max(candidates, key=lambda item: item[0])
        args.output.parent.mkdir(parents=True, exist_ok=True)
        page = doc[index]
        clip = (box + (-4, -4, 4, 4)) & page.rect
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=clip, alpha=False)
        pix.save(args.output)
        print(f"{args.output}: page {index + 1}, {pix.width} x {pix.height}; review before use")


if __name__ == "__main__":
    main()
