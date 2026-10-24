"""Offline analytics regression tests; no network or real pageviews are sent."""

import json
from pathlib import Path
import subprocess
import unittest

from site_analytics import with_analytics


ROOT = Path(__file__).resolve().parents[1]


class AnalyticsTests(unittest.TestCase):
    def test_injection_is_idempotent(self):
        source = '<!doctype html><html><head><title>Post</title></head><body>Content</body></html>'
        once = with_analytics(source)
        self.assertEqual(with_analytics(once), once)
        self.assertEqual(once.count('src="/assets/analytics.js"'), 1)

    def test_redirects_and_fragments_are_not_counted(self):
        for source in ('<div>Fragment</div>',
                       '<html><head><meta content="0;url=/" http-equiv="Refresh"></head><body></body></html>'):
            self.assertEqual(with_analytics(source), source)

    def run_loader(self, **overrides):
        settings = {'protocol': 'https:', 'hostname': 'xiejun0105.github.io',
                    'pathname': '/blog/about-me/index.html', 'search': '?tag=ESG',
                    'referrer': 'https://example.org/article?private=value',
                    'doNotTrack': '0', 'globalPrivacyControl': False, 'existing': False}
        settings.update(overrides)
        runner = """
const fs = require('fs'), vm = require('vm');
const input = JSON.parse(process.argv[2]), appended = [];
const document = {
  referrer: input.referrer,
  querySelector: () => input.existing ? {} : null,
  createElement: () => ({setAttribute(name, value) { this[name] = value; }}),
  head: {appendChild(script) { appended.push(script); }}
};
const window = {location: input};
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), {
  window, document, URL,
  navigator: {doNotTrack: input.doNotTrack, globalPrivacyControl: input.globalPrivacyControl}
});
process.stdout.write(JSON.stringify({appended, options: window.goatcounter}));
"""
        return json.loads(subprocess.check_output([
            'node', '-e', runner, str(ROOT / 'assets/analytics.js'), json.dumps(settings)], text=True))

    def test_production_endpoint_and_data_minimization(self):
        result = self.run_loader()
        self.assertEqual(len(result['appended']), 1)
        script = result['appended'][0]
        self.assertTrue(script['async'])
        self.assertEqual(script['src'], 'https://gc.zgo.at/count.js')
        self.assertEqual(script['data-goatcounter'], 'https://junxie.goatcounter.com/count')
        self.assertEqual(result['options'], {'path': '/blog/about-me/', 'referrer': 'https://example.org', 'no_events': True})

    def test_local_and_other_hosts_never_load_third_party(self):
        for change in ({'hostname': 'localhost'}, {'hostname': '127.0.0.1'},
                       {'protocol': 'file:'}, {'hostname': 'preview.example.org'}):
            self.assertEqual(self.run_loader(**change)['appended'], [])

    def test_privacy_preferences_and_duplicate_tracker(self):
        for change in ({'doNotTrack': '1'}, {'globalPrivacyControl': True}, {'existing': True}):
            self.assertEqual(self.run_loader(**change)['appended'], [])

    def test_drafts_and_previews_never_load(self):
        for path in ('/preview.html', '/tmp/test.html', '/%E3%83%BBBlog%20draft/preview.html', '/bad%ZZ'):
            self.assertEqual(self.run_loader(pathname=path)['appended'], [])

    def test_direct_visit(self):
        result = self.run_loader(pathname='/', referrer='')
        self.assertEqual(result['options']['path'], '/')
        self.assertEqual(result['options']['referrer'], '')

    def test_unusable_referrer_does_not_break_loading(self):
        for referrer in ('not a url', 'about:blank'):
            result = self.run_loader(referrer=referrer)
            self.assertEqual(len(result['appended']), 1)
            self.assertEqual(result['options']['referrer'], '')


if __name__ == '__main__':
    unittest.main()
