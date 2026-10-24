"""Archive served Blog content and image versions locally; never publish drafts."""
import argparse
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / '・Blog draft' / 'archive'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def posts():
    script = (
        "const fs=require('fs'),vm=require('vm'); const c={window:{}};"
        "vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),c,{timeout:1000});"
        "process.stdout.write(JSON.stringify(c.window.BLOG_POSTS));"
    )
    return json.loads(subprocess.check_output(
        ['node', '-e', script, str(ROOT / 'assets/blog-data.js')], text=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slug', help='One article slug; omit to archive all listed posts')
    parser.add_argument('--date', type=date.fromisoformat, help='Archive date; defaults to today in Japan')
    parser.add_argument('--event', choices=['snapshot', 'before-update', 'before-withdrawal'], default='snapshot')
    parser.add_argument('--note', default='')
    parser.add_argument('--force', action='store_true', help='Save a checkpoint even when unchanged')
    args = parser.parse_args()
    day = str(args.date or datetime.now(ZoneInfo('Asia/Tokyo')).date())
    selected = posts()
    if args.slug:
        selected = [p for p in selected if p['href'].strip('/').split('/')[-1] == args.slug]
        if not selected:
            raise SystemExit('No listed post with this slug. Archive before removing its list entry.')
    history_path = ARCHIVE / 'history.json'
    history = json.loads(history_path.read_text()) if history_path.exists() else []
    for post in selected:
        page = (ROOT / post['href'].lstrip('/') / 'index.html').resolve()
        if not page.is_relative_to(ROOT / 'blog'):
            raise ValueError('Article must be inside blog/')
        slug = page.parent.name
        soup = BeautifulSoup(page.read_text(), 'html.parser')
        article = soup.select_one('.blog-post article')
        if article is None:
            raise ValueError(f'Missing article: {page}')
        images = {}
        for src in dict.fromkeys([post['image']] + [img['src'] for img in article.select('img[src]')]):
            if src.startswith(('https://', 'http://', 'data:')):
                raise ValueError(f'Cannot preserve remote image automatically: {src}')
            path = ((ROOT / src.lstrip('/')) if src.startswith('/') else (page.parent / src)).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file():
                raise ValueError(f'Invalid image path: {src}')
            image_hash = digest(path.read_bytes())
            images[src] = {'path': path, 'hash': image_hash,
                           'copy': f'_assets/{image_hash[:16]}_{path.name}'}
        fingerprint = digest(json.dumps({
            'metadata': post, 'article': str(article),
            'images': {src: item['hash'] for src, item in images.items()},
        }, sort_keys=True, ensure_ascii=False).encode())
        previous = next((item for item in reversed(history) if item['slug'] == slug), None)
        if previous and previous['fingerprint'] == fingerprint and not args.force:
            print(f'UNCHANGED {slug}')
            continue
        folder = ARCHIVE / slug
        folder.mkdir(parents=True, exist_ok=True)
        for item in images.values():
            target = ARCHIVE / item['copy']
            target.parent.mkdir(exist_ok=True)
            if not target.exists():
                shutil.copyfile(item['path'], target)

        def render(node):
            if isinstance(node, NavigableString):
                return re.sub(r'\s+', ' ', str(node))
            tag = node.name
            if tag in ('script', 'style') or 'blog-post-meta' in node.get('class', []):
                return ''
            if tag == 'img':
                alt = node.get('alt', '').replace('[', '\\[').replace(']', '\\]')
                return f"\n\n![{alt}](../{images[node['src']]['copy']})\n\n"
            content = ''.join(render(child) for child in node.children).strip()
            if tag in ('h1', 'h2', 'h3', 'h4'):
                return '\n\n' + '#' * int(tag[1]) + ' ' + content + '\n\n'
            if tag in ('em', 'i', 'cite'):
                return '*' + content + '*'
            if tag in ('strong', 'b'):
                return '**' + content + '**'
            if tag == 'a':
                return f"[{content}]({node.get('href', '')})"
            if tag == 'li':
                return '\n- ' + re.sub(r'\n+', '\n  ', content) + '\n'
            if tag == 'figcaption':
                return '\n\n*' + content + '*\n\n'
            if tag == 'blockquote':
                return '\n\n> ' + content.replace('\n', '\n> ') + '\n\n'
            if tag == 'br':
                return '\n'
            if tag in ('p', 'div', 'header', 'figure', 'ul', 'ol', 'section', 'article'):
                return '\n\n' + content + '\n\n'
            return content

        version = 1
        while (folder / f'{day}_v{version:03}.md').exists():
            version += 1
        target = folder / f'{day}_v{version:03}.md'
        metadata = {
            'title': post['title'], 'slug': slug, 'originalPath': post['href'],
            'archivedOn': day, 'event': args.event, 'note': args.note,
            'publishedAt': post.get('publishedAt'), 'dateSource': post.get('dateSource'),
            'updatedAt': post.get('updatedAt'), 'pinned': post.get('pinned', False),
            'pinOrder': post.get('pinOrder'), 'tag': post.get('tag'), 'tags': post.get('tags', []),
            'cover': '../' + images[post['image']]['copy'],
        }
        frontmatter = '\n'.join(f'{key}: {json.dumps(value, ensure_ascii=False)}' for key, value in metadata.items())
        markdown = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', render(article)).strip()
        with target.open('x') as stream:
            stream.write('---\n' + frontmatter + '\n---\n\n' + markdown + '\n')
        history.append({'slug': slug, 'title': post['title'], 'archivedOn': day,
                        'event': args.event, 'note': args.note,
                        'file': str(target.relative_to(ARCHIVE)), 'fingerprint': fingerprint})
        print(f'ARCHIVED {target.relative_to(ROOT)}')
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n')
    rows = ['# Blog 历史存档', '', '仅本地保存。日期是存档日期，不是文章发布日期。', '',
            '| 存档日期 | 文章 | 操作 | 说明 |', '| --- | --- | --- | --- |']
    for item in reversed(history):
        title = item['title'].replace('|', '\\|')
        note = item['note'].replace('|', '\\|').replace('\n', ' ')
        rows.append(f"| {item['archivedOn']} | [{title}]({item['file']}) | {item['event']} | {note} |")
    (ARCHIVE / 'README.md').write_text('\n'.join(rows) + '\n')


if __name__ == '__main__':
    main()
