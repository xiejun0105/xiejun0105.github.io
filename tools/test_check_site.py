"""Focused regression tests for the offline site checker."""

import json
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from check_site import audit


class SiteAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.put('index.html', '<a href="/blog/">Blog</a>')
        self.put('blog/post/index.html', '<img src="/images/cover.png">')
        for prefix in ('', 'ja/', 'zh/'):
            self.put(prefix + 'blog/index.html', '<button data-blog-filter="Summary">Summary</button>')
        self.put('images/cover.png', 'image fixture')
        self.put('data/blog-assets.json', json.dumps({'post': {
            'page': '/blog/post/', 'cover': '/images/cover.png', 'images': ['/images/cover.png']}}))
        self.post = {'title': 'Post', 'href': '/blog/post/', 'image': '/images/cover.png',
                     'publishedAt': '2026-10-24', 'tags': ['Summary']}
        self.write_post()

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def write_post(self):
        self.put('assets/blog-data.js', 'window.BLOG_POSTS = ' + json.dumps([self.post]) + ';')

    def test_valid_site(self):
        result = audit(self.root)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['summary']['unusedCandidates'], 0)

    def test_missing_html_resource(self):
        self.put('index.html', '<img src="/images/missing.png">')
        self.assertTrue(any('missing local target' in x for x in audit(self.root)['errors']))

    def test_private_url_even_when_encoded(self):
        self.put('index.html', '<a href="/%E3%83%BBBlog%20draft/secret.md">Private</a>')
        self.assertTrue(any('private path' in x for x in audit(self.root)['errors']))

    def test_metadata_date_and_asset_mapping(self):
        self.post['publishedAt'] = '2026-02-30'
        self.post['image'] = '/images/other.png'
        self.write_post()
        messages = audit(self.root)['errors']
        self.assertTrue(any('invalid publishedAt' in x for x in messages))
        self.assertTrue(any('manifest' in x for x in messages))

    def test_each_language_needs_filter(self):
        self.put('zh/blog/index.html', '<button data-blog-filter="All">All</button>')
        self.assertIn('zh/blog/index.html: missing filter Summary', audit(self.root)['errors'])

    def test_unused_and_duplicate_are_review_only(self):
        self.put('images/copy.png', 'image fixture')
        result = audit(self.root)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['summary']['unusedCandidates'], 1)
        self.assertEqual(len(result['duplicates']), 1)
        self.assertTrue((self.root / 'images/copy.png').exists())

    def test_private_archive_excluded(self):
        self.put('・Site archive/old.html', '<img src="/missing-history.png">')
        self.assertEqual(audit(self.root)['errors'], [])

    def test_css_references_are_relative(self):
        self.put('assets/site.css', '.logo { background: url("../images/cover.png"); }')
        result = audit(self.root)
        self.assertEqual(result['errors'], [])
        item = next(a for a in result['assets'] if a['path'] == 'images/cover.png')
        self.assertIn('assets/site.css', item['referencedBy'])

    def test_invalid_json_is_reported(self):
        self.put('data/blog-assets.json', '{invalid')
        self.assertTrue(any('invalid JSON' in x for x in audit(self.root)['errors']))

    def test_full_page_requires_shared_analytics_when_configured(self):
        self.put('assets/analytics.js', '// test loader')
        self.put('index.html', '<html><head></head><body>Home</body></html>')
        self.assertTrue(any('shared analytics loader' in x for x in audit(self.root)['errors']))
        self.put('index.html', '<html><head><script defer src="/assets/analytics.js"></script></head><body>Home</body></html>')
        self.assertEqual(audit(self.root)['errors'], [])

    def archive(self, *paths):
        spec = importlib.util.spec_from_file_location('archive_assets_test', Path(__file__).with_name('archive-site-assets.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.ROOT = self.root.resolve()
        with patch('sys.argv', ['archive-site-assets.py', *paths, '--date', '2026-10-24', '--note', 'Test', '--move']):
            with contextlib.redirect_stdout(io.StringIO()):
                module.main()

    def test_archive_preserves_content_and_manifest(self):
        self.put('images/unused.png', 'recoverable original')
        self.archive('images/unused.png')
        target = self.root / '・Site archive/2026-10-24/images/unused.png'
        self.assertEqual(target.read_text(), 'recoverable original')
        self.assertFalse((self.root / 'images/unused.png').exists())
        manifest = json.loads((target.parent.parent / 'manifest.json').read_text())
        self.assertEqual(manifest[0]['originalPath'], 'images/unused.png')

    def test_archive_refuses_in_use_asset(self):
        with self.assertRaises(SystemExit):
            self.archive('images/cover.png')
        self.assertTrue((self.root / 'images/cover.png').exists())

    def test_archive_validates_entire_request_before_move(self):
        self.put('images/unused.png', 'keep until all paths validated')
        with self.assertRaises(SystemExit):
            self.archive('images/unused.png', 'images/not-found.png')
        self.assertTrue((self.root / 'images/unused.png').exists())
        self.assertFalse((self.root / '・Site archive').exists())


if __name__ == '__main__':
    unittest.main()
