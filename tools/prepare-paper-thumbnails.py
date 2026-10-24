"""Prepare local PDF figure candidates and a persistent DOI-to-image mapping."""
import json
import re
from pathlib import Path
from difflib import SequenceMatcher
import fitz

ROOT = Path(__file__).resolve().parents[1]


def normalized(value):
    return re.sub(r'[^a-z0-9]', '', value.lower())


def main():
    papers = json.loads((ROOT / 'data/journal-publications.json').read_text())
    mapping_path = ROOT / 'data/paper-thumbnails.json'
    previous = json.loads(mapping_path.read_text()) if mapping_path.exists() else {}
    documents = []
    for path in (ROOT / '・My publications').glob('*.pdf'):
        doc = fitz.open(path)
        text = ''.join(page.get_text() for page in doc)
        documents.append((path, doc, text))
    reuse = {
        '10.1002/bse.2224': 'Xie_2019_nonlinear.png',
        '10.1002/csr.2524': 'Xie_2023_materiality_map.png',
        '10.1038/s41598-023-36493-7': 'Xie_2023_uneven_high_stress_risk.png',
        '10.1108/GM-09-2023-0307': 'Xie_2024_female_manager.png',
        '10.1038/s41598-025-18332-z': 'Xie_2025_stress_cluster.png',
        '10.1111/aepr.70006': 'Xie_2025_different_ESG_financial_impact.png',
        '10.1371/journal.pone.0315166': 'Chen_2025_global_HC_change.png',
    }
    output = ROOT / 'images/papers'
    selected_pages = {'10.1002/csr.3108': 2, '10.3389/frsus.2022.920955': 3}
    output.mkdir(exist_ok=True)
    mapping = {}
    for paper in papers:
        doi = paper['doi']
        selected = previous.get(doi)
        if selected and (ROOT / selected['image'].lstrip('/')).is_file():
            mapping[doi] = selected
            continue
        if doi in reuse:
            mapping[doi] = {'image': '/images/' + reuse[doi], 'selection': 'Existing curated blog figure'}
            continue
        matches = [(p,d,t) for p,d,t in documents if normalized(doi) in normalized(t)]
        if not matches:
            print('UNMATCHED', doi)
            continue
        path, doc, text = max(matches, key=lambda item: SequenceMatcher(None, normalized(paper['title']), normalized(item[0].stem)).ratio())
        candidates = []
        for index, page in enumerate(doc):
            if doi in selected_pages and index + 1 != selected_pages[doi]:
                continue
            caption = page.search_for('FIGURE 1') or page.search_for('Fig. 1') or page.search_for('Figure 1')
            for info in page.get_image_info(xrefs=True):
                box = fitz.Rect(info['bbox']) & page.rect
                if box.is_empty or box.width < 130 or box.height < 85 or box.get_area() > page.rect.get_area()*.85:
                    continue
                pix = page.get_pixmap(matrix=fitz.Matrix(.35,.35), clip=box, colorspace=fitz.csRGB)
                samples = pix.samples
                colored = sum(max(samples[i:i+3])-min(samples[i:i+3]) > 30 for i in range(0,len(samples),3)) / max(1,pix.width*pix.height)
                score = box.get_area()*(1+colored*12)*(1.4 if caption else 1)
                candidates.append((score,index,box))
            # Framework diagrams are often vector-only. Keep their labels intact.
            if index > 0 and (caption or not page.get_images()):
                drawings = [item['rect'] for item in page.get_drawings() if item['rect'].width>8 and item['rect'].height>8]
                above = [r for r in drawings if r.y1 <= (caption[0].y0+3 if caption else page.rect.height-40) and r.y0>45]
                if above:
                    box = fitz.Rect(above[0])
                    for r in above[1:]: box |= r
                    if box.width>130 and box.height>60:
                        candidates.append((box.get_area()*(1.5 if caption else .5),index,box))
        if not candidates:
            print('NO FIGURE', doi, path.name)
            continue
        _, index, box = max(candidates,key=lambda item:item[0])
        clip = (box+(-8,-8,8,8)) & doc[index].rect
        author = re.sub(r'[^a-zA-Z0-9]', '', paper['authors'].split(',')[0])
        description = re.sub(r'[^a-zA-Z0-9]+', '_', paper['title']).strip('_').lower()[:90].rstrip('_')
        slug = f"{author}_{paper['year']}_{description}.png"
        doc[index].get_pixmap(matrix=fitz.Matrix(1.7,1.7),clip=clip,alpha=False).save(output/slug)
        mapping[doi] = {'image': '/images/papers/'+slug, 'page': index+1, 'selection': 'Color / framework candidate; source figure region'}
        print('EXPORTED',doi,'page',index+1)
    mapping_path.write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n')
    print('Mapped',len(mapping),'of',len(papers))


if __name__ == '__main__':
    main()
