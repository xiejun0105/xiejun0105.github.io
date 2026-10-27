"""Check shared resource metadata and the generated three-language library."""

import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Elements(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.items = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.items.append((tag, dict(attrs)))


class LearningResourcesTests(unittest.TestCase):
    def test_metadata(self):
        resources = json.loads((ROOT / 'data/learning-resources.json').read_text())
        topics = json.loads((ROOT / 'data/learning-resource-topics.json').read_text())
        ids = {topic['id'] for topic in topics}
        self.assertEqual(len(ids), len(topics))
        self.assertEqual(len({item['id'] for item in resources}), len(resources))
        for topic in topics:
            self.assertEqual(set(topic['labels']), {'en', 'ja', 'zh'})
        for item in resources:
            self.assertTrue(item['topics'])
            self.assertEqual(len(set(item['topics'])), len(item['topics']))
            self.assertTrue(set(item['topics']) <= ids)
            self.assertTrue((ROOT / item['thumbnail'].lstrip('/')).is_file())
            self.assertEqual(set(item['description']), {'en', 'ja', 'zh'})

    def test_generated_previews_and_filters(self):
        resources = json.loads((ROOT / 'data/learning-resources.json').read_text())
        topics = json.loads((ROOT / 'data/learning-resource-topics.json').read_text())
        ordered = sorted(resources, key=lambda item: item.get('previewOrder', 1000))
        for prefix in ('', 'ja/', 'zh/'):
            preview = Elements((ROOT / prefix / 'teaching/index.html').read_text())
            links = [a['href'] for tag, a in preview.items if a.get('class') == 'learning-resource']
            self.assertEqual(links, [item['url'] for item in ordered])
            self.assertGreater(len(links), 5)
            library = Elements((ROOT / prefix / 'teaching/resources/index.html').read_text())
            buttons = [a['data-resource-topic'] for tag, a in library.items if 'data-resource-topic' in a]
            self.assertEqual(buttons, ['all'] + [topic['id'] for topic in topics])
            rows = [a for tag, a in library.items if 'data-resource-topics' in a]
            self.assertEqual(len(rows), len(resources))

    def test_filter_navigation_and_carousel_edges(self):
        runner = r"""
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const events = {}, buttons = ['all','writing','design'].map(topic => ({
  dataset: {resourceTopic:topic}, attributes:{},
  setAttribute(k,v) {this.attributes[k]=v;},
  addEventListener(k,fn) {this[k]=fn;}
}));
const rows = ['writing','design','writing design'].map(topics => ({dataset:{resourceTopics:topics}}));
const filters = {hidden:true, querySelectorAll:()=>buttons}, status = {}, empty = {};
const library = {dataset:{countLabel:'{count} resources'},
 querySelector(s) {return s==='.resource-filters'?filters:s==='.resource-filter-status'?status:empty;},
 querySelectorAll:()=>rows};
const steps = [-1,1].map(step=>({dataset:{resourceStep:String(step)},addEventListener(k,fn){this[k]=fn;}}));
const controls = {querySelectorAll:()=>steps};
const strip = {scrollWidth:1800,clientWidth:1000,scrollLeft:0,
 addEventListener(k,fn){this[k]=fn;},scrollBy(o){this.last=o;}};
const carousel = {querySelector(s){return s==='.learning-resource-strip'?strip:controls;}};
const window = {location:{href:'https://example.com/teaching/resources/?topic=writing&keep=1'},
 matchMedia:()=>({matches:true}),addEventListener(k,fn){events[k]=fn;},
 history:{pushState(a,b,url){window.location.href=url.href;},replaceState(a,b,url){window.location.href=url.href;}}};
const document = {documentElement:{setAttribute(){}},querySelector(){return null;},
 querySelectorAll(s){return s==='[data-resource-library]'?[library]:s==='[data-resource-carousel]'?[carousel]:[];}};
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window,document,URL,localStorage:{getItem(){return null;}}});
events.DOMContentLoaded();
assert.equal(status.textContent,'2 resources'); assert.equal(rows[1].hidden,true);
buttons[2].click(); assert.equal(rows[0].hidden,true); assert.equal(rows[1].hidden,false);
assert.ok(window.location.href.includes('topic=design')); assert.ok(window.location.href.includes('keep=1'));
buttons[0].click(); assert.ok(rows.every(r=>!r.hidden)); assert.ok(!window.location.href.includes('topic='));
window.location.href='https://example.com/teaching/resources/?topic=unknown'; events.popstate();
assert.ok(rows.every(r=>!r.hidden)); assert.ok(!window.location.href.includes('topic='));
assert.equal(steps[0].disabled,true); assert.equal(steps[1].disabled,false);
steps[1].click(); assert.equal(strip.last.left,1000); assert.equal(strip.last.behavior,'instant');
strip.scrollLeft=800; strip.scroll(); assert.equal(steps[1].disabled,true); assert.equal(steps[0].disabled,false);
strip.scrollWidth=1000; strip.scrollLeft=0; strip.scroll(); assert.equal(controls.hidden,true);
"""
        subprocess.run(['node', '-e', runner, str(ROOT / 'assets/site.js')], check=True)


if __name__ == '__main__':
    unittest.main()
