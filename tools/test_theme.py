"""Test local-time defaults and manual theme preference without a browser."""

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ThemeTests(unittest.TestCase):
    def theme(self, hour, saved=None, clicks=0, blocked=False):
        runner = """
const fs = require('fs'), vm = require('vm');
const input = JSON.parse(process.argv[2]);
const attributes = {}, labels = [{}, {}], clicks = [], stored = [];
let ready;
const buttons = labels.map(label => ({
  setAttribute(key, value) { label[key] = value; },
  addEventListener(type, fn) { if (type === 'click') clicks.push(fn); }
}));
const document = {
  documentElement: {lang: 'en', setAttribute(k,v) {attributes[k]=v;}, getAttribute(k) {return attributes[k];}},
  querySelectorAll(selector) {return selector === '[data-theme-toggle]' ? buttons : [];},
  querySelector() {return null;}
};
class LocalDate extends Date {getHours() {return input.hour;}}
const window = {
  addEventListener(type, fn) {if (type === 'DOMContentLoaded') ready = fn;},
  matchMedia() {return {matches: true};},
  location: {pathname: '/', search: ''}
};
const localStorage = {
  getItem() {if (input.blocked) throw Error('blocked'); return input.saved;},
  setItem(key, value) {if (input.blocked) throw Error('blocked'); stored.push({key,value});}
};
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), {
  window, document, localStorage, Date: LocalDate, URL, URLSearchParams, Intl
});
ready();
for (let i=0; i<input.clicks; i++) clicks[i % clicks.length]();
process.stdout.write(JSON.stringify({theme: attributes['data-theme'], stored, labels}));
"""
        return json.loads(subprocess.check_output([
            'node', '-e', runner, str(ROOT / 'assets/site.js'),
            json.dumps({'hour': hour, 'saved': saved, 'clicks': clicks, 'blocked': blocked})], text=True))

    def test_daytime_boundaries(self):
        for hour in (7, 12, 17):
            self.assertEqual(self.theme(hour)['theme'], 'light')

    def test_nighttime_boundaries(self):
        for hour in (0, 6, 18, 23):
            self.assertEqual(self.theme(hour)['theme'], 'dark')

    def test_manual_preference_overrides_time(self):
        self.assertEqual(self.theme(12, saved='dark')['theme'], 'dark')
        self.assertEqual(self.theme(23, saved='light')['theme'], 'light')

    def test_invalid_preference_uses_time(self):
        self.assertEqual(self.theme(12, saved='invalid')['theme'], 'light')

    def test_manual_toggle_and_all_button_labels(self):
        result = self.theme(12, clicks=1)
        self.assertEqual(result['theme'], 'dark')
        self.assertEqual(result['stored'], [{'key': 'theme', 'value': 'dark'}])
        self.assertTrue(all(label['title'] == 'Light' for label in result['labels']))
        result = self.theme(12, clicks=2)
        self.assertEqual(result['theme'], 'light')
        self.assertTrue(all(label['title'] == 'Dark' for label in result['labels']))

    def test_storage_blocked_does_not_break_theme_switching(self):
        self.assertEqual(self.theme(23, blocked=True)['theme'], 'dark')
        self.assertEqual(self.theme(23, clicks=1, blocked=True)['theme'], 'light')


if __name__ == '__main__':
    unittest.main()
