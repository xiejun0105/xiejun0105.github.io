"""Offline integrity checks and a conservative inventory of public site assets.

Run: python3 tools/check_site.py --report tmp/site-audit.json
This command never modifies or deletes content. Unused candidates require review.
"""

import argparse
from collections import defaultdict
from datetime import date
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = {'・Blog draft', '・My publications', '・Site archive', 'tmp'}
SKIP = PRIVATE | {'.git', '__pycache__', '.venv', 'node_modules'}
MEDIA = {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.avif', '.ico',
         '.woff', '.woff2', '.ttf', '.mp4', '.webm', '.pdf'}


class PageReferences(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.images = []
        self.filters = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ('href', 'src', 'poster'):
            if attrs.get(key):
                self.references.append(attrs[key])
        if tag == 'img' and attrs.get('src'):
            self.images.append(attrs['src'])
        if 'data-blog-filter' in attrs:
            self.filters.add(attrs['data-blog-filter'])
        if attrs.get('srcset') and not attrs['srcset'].startswith('data:'):
            self.references.extend(item.strip().split()[0] for item in attrs['srcset'].split(',') if item.strip())

    handle_startendtag = handle_starttag


def public_files(root):
    return sorted(p for p in root.rglob('*') if p.is_file() and not SKIP.intersection(p.relative_to(root).parts))


def string_values(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from string_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from string_values(item)


def audit(root):
    root = root.resolve()
    errors, warnings = [], []
    usage = defaultdict(set)
    files = public_files(root)
    pages = {}
    documents = {}

    def reference(source, value):
        if not value or value.startswith(('#', 'data:', 'mailto:', 'tel:')):
            return
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc:
            return
        path = unquote(parsed.path)
        if not path:
            return
        target = (root / path.lstrip('/') if path.startswith('/') else source.parent / path).resolve()
        if not target.is_relative_to(root):
            errors.append(f'{source.relative_to(root)}: path escapes website: {value}')
            return
        relative = target.relative_to(root)
        if PRIVATE.intersection(relative.parts):
            errors.append(f'{source.relative_to(root)}: private path linked publicly: {value}')
            return
        if target.is_dir():
            target /= 'index.html'
        if not target.is_file():
            errors.append(f'{source.relative_to(root)}: missing local target: {value}')
            return
        usage[str(target.relative_to(root))].add(str(source.relative_to(root)))

    for source in files:
        if source.suffix == '.html':
            parser = PageReferences()
            parser.feed(source.read_text())
            pages[str(source.relative_to(root))] = parser
            for value in parser.references:
                reference(source, value)
        elif source.suffix == '.css':
            for value in re.findall(r'url\(\s*[\'"]?([^\)\'\"]+)', source.read_text()):
                reference(source, value.strip())
        elif source.suffix == '.json' and source.parent == root / 'data':
            try:
                values = json.loads(source.read_text())
            except json.JSONDecodeError as exc:
                errors.append(f'{source.relative_to(root)}: invalid JSON: {exc}')
                continue
            documents[str(source.relative_to(root))] = values
            for value in string_values(values):
                if value.startswith('/'):
                    reference(source, value)

    script = (
        "const fs=require('fs'),vm=require('vm');const c={window:{}};"
        "vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),c,{timeout:1000});"
        "process.stdout.write(JSON.stringify(c.window.BLOG_POSTS));"
    )
    try:
        posts = json.loads(subprocess.check_output(['node', '-e', script, str(root / 'assets/blog-data.js')], text=True))
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        errors.append(f'Cannot load Blog metadata (Node.js required): {exc}')
        posts = []
    if not isinstance(posts, list):
        errors.append('Blog metadata must be an array')
        posts = []
    manifest = documents.get('data/blog-assets.json')
    if not isinstance(manifest, dict):
        errors.append('data/blog-assets.json: missing or invalid object')
        manifest = {}
    seen = set()
    for post in posts:
        if not isinstance(post, dict):
            errors.append('Each Blog metadata entry must be an object')
            continue
        href = post.get('href', '')
        if not href.startswith('/blog/') or not href.endswith('/') or href in seen:
            errors.append(f'Invalid or duplicate Blog URL: {href}')
        seen.add(href)
        for key in ('publishedAt', 'updatedAt'):
            value = post.get(key)
            if value:
                try:
                    if date.fromisoformat(value).isoformat() != value:
                        raise ValueError(value)
                except (TypeError, ValueError):
                    errors.append(f'{href}: invalid {key}: {value}')
        if post.get('updatedAt') and post.get('publishedAt') and post['updatedAt'] < post['publishedAt']:
            errors.append(f'{href}: update date precedes publication date')
        for key in ('href', 'image'):
            reference(root / 'assets/blog-data.js', post.get(key, ''))
        slug = href.strip('/').split('/')[-1]
        record = manifest.get(slug)
        if not record or record.get('page') != href or record.get('cover') != post.get('image'):
            errors.append(f'{href}: Blog asset manifest missing or inconsistent')
        page = pages.get(href.lstrip('/') + 'index.html')
        if record and page and set(record.get('images', [])) != set(page.images):
            errors.append(f'{href}: article images differ from asset manifest')
        for locale in ('', 'ja/', 'zh/'):
            filters = pages.get(locale + 'blog/index.html')
            if filters:
                for tag in post.get('tags', []):
                    if tag not in filters.filters:
                        errors.append(f'{locale}blog/index.html: missing filter {tag}')

    assets = []
    duplicates = defaultdict(list)
    for path in files:
        if path.suffix.lower() not in MEDIA:
            continue
        relative = str(path.relative_to(root))
        size = path.stat().st_size
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        duplicates[checksum].append(relative)
        assets.append({'path': relative, 'bytes': size, 'sha256': checksum,
                       'referencedBy': sorted(usage[relative])})
        if size > 1_000_000:
            warnings.append(f'Large asset ({size:,} bytes): {relative}')
    unused = [a['path'] for a in assets if not a['referencedBy']]
    warnings.extend('Review unused candidate (not auto-deleted): ' + p for p in unused)
    duplicate_groups = [paths for paths in duplicates.values() if len(paths) > 1]
    warnings.extend('Byte-identical assets: ' + ', '.join(paths) for paths in duplicate_groups)
    # Ignore rules do not protect already-tracked files; inspect the Git index too.
    try:
        tracked = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z'], stderr=subprocess.DEVNULL).decode().split('\0')
        for value in tracked:
            if value and (PRIVATE.intersection(Path(value).parts) or Path(value).name == '.DS_Store'):
                warnings.append('Tracked private/system file; review index before upload: ' + value)
    except (OSError, subprocess.CalledProcessError):
        warnings.append('Git index not checked: repository unavailable')
    return {'errors': sorted(set(errors)), 'warnings': sorted(set(warnings)),
            'summary': {'htmlFiles': len(pages), 'blogPosts': len(posts), 'mediaFiles': len(assets),
                        'mediaBytes': sum(a['bytes'] for a in assets), 'unusedCandidates': len(unused)},
            'assets': assets, 'duplicates': duplicate_groups}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, help='Optional JSON inventory; save inside ignored tmp/')
    args = parser.parse_args()
    report = audit(ROOT)
    print(json.dumps(report['summary'], ensure_ascii=False))
    for level in ('errors', 'warnings'):
        for message in report[level]:
            print(f'{level.upper()}: {message}')
    if args.report:
        output = (ROOT / args.report).resolve()
        if not output.is_relative_to(ROOT / 'tmp'):
            parser.error('Reports must be saved under ignored tmp/ to avoid publishing inventories.')
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    raise SystemExit(bool(report['errors']))


if __name__ == '__main__':
    main()
