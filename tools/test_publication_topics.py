"""Topic vocabulary, generated markup and browser-independent filtering tests."""

import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import unittest

from publication_topics import render_filters, render_landing_topics, validate_topics, with_landing_topics


ROOT = Path(__file__).resolve().parents[1]
PAPERS = json.loads((ROOT / 'data/journal-publications.json').read_text())
TOPICS = json.loads((ROOT / 'data/research-topics.json').read_text())


class Controls(HTMLParser):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.groups = 0
        self.extra_tag = None
        self.landing_links = []
        self.landing_rows = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'data-publication-topic' in values:
            self.buttons.append(values['data-publication-topic'])
        if values.get('class') == 'publication-topic-list':
            self.groups += 1
        if 'data-publication-topic-extra' in values:
            self.extra_tag = tag
        if 'data-identity-topic' in values:
            self.landing_links.append((values['data-identity-topic'], values['href']))
        if 'data-identity-row' in values:
            self.landing_rows.append(values['data-identity-row'])


class PublicationTopicTests(unittest.TestCase):
    def test_all_papers_have_valid_topics(self):
        validate_topics(PAPERS, TOPICS)
        self.assertGreater(len(PAPERS), 0)

    def test_unknown_and_duplicate_assignments_are_rejected(self):
        for assigned in ([], ['unknown'], ['well-being', 'well-being']):
            papers = copy.deepcopy(PAPERS)
            papers[0]['topics'] = assigned
            with self.assertRaises(ValueError):
                validate_topics(papers, TOPICS)

    def test_each_language_has_the_same_filters(self):
        for locale in ('en', 'ja', 'zh'):
            parser = Controls()
            parser.feed(render_filters(PAPERS, TOPICS, locale))
            self.assertEqual(parser.buttons, ['all'] + [t['id'] for t in TOPICS if t['primary']] + [t['id'] for t in TOPICS if not t['primary']])
            self.assertEqual(parser.groups, 1)
            self.assertEqual(parser.extra_tag, 'span')

    def test_landing_has_five_localized_links_in_two_rows(self):
        selected = ['corporate-sustainability', 'climate-change', 'well-being', 'supply-chains', 'human-capital']
        for locale, prefix in [('en', ''), ('ja', '/ja'), ('zh', '/zh')]:
            parser = Controls()
            markup = render_landing_topics(TOPICS, locale)
            parser.feed(markup)
            self.assertEqual(parser.landing_links, [(topic, f'{prefix}/publications/journal/?topic={topic}') for topic in selected])
            self.assertNotIn('publication-topic-count', markup)
            self.assertEqual(markup.count('class="identity-topic-hash" aria-hidden="true">#'), 5)
            self.assertEqual(markup.count('title='), 5)
            self.assertEqual(parser.landing_rows, ['1', '2'])
        self.assertIn('企業の持続可能性', render_landing_topics(TOPICS, 'ja'))

    def test_landing_injection_is_repeatable(self):
        source = '<section><div class="identity-intro"><p class="identity-summary">Original summary.</p>\n</div></section>'
        once = with_landing_topics(source, TOPICS, 'en')
        self.assertEqual(with_landing_topics(once, TOPICS, 'en'), once)
        self.assertIn('Original summary.', once)

    def run_filter(self, topic=None, actions=None, suffix=''):
        runner = """
const fs = require('fs'), vm = require('vm');
const input = JSON.parse(process.argv[2]);
function node(dataset={}, hidden=false) {
  const attrs={}, classes=new Set(), handlers={};
  return {dataset, hidden, attrs, handlers,
    classList:{toggle(k,on){on?classes.add(k):classes.delete(k);}},
    setAttribute(k,v){attrs[k]=v;}, getAttribute(k){return attrs[k];},
    addEventListener(k,fn){handlers[k]=fn;}
  };
}
const buttons = [{id:'all',primary:true,labels:{en:'All'}},...input.topics].map(t=>{
  const b=node({publicationTopic:t.id,publicationLabel:t.labels.en});b.primary=t.primary;return b;
});
const papers=input.papers.map(p=>Object.assign(node({topics:p.topics.join(' ')}),{doi:p.doi,year:p.year}));
const sections=[...new Set(papers.map(p=>p.year))].map(year=>({id:'year-'+year,hidden:false,querySelectorAll:()=>papers.filter(p=>p.year===year)}));
const years=sections.map(s=>{const n=node();n.setAttribute('href','#'+s.id);return n;});
const status=node({countOne:'{count} article',countMany:'{count} articles'}), empty=node({},true);
const extra=node({},true);extra.contains=b=>!b.primary;
const label={},icon={},toggle=node({moreLabel:'More topics',lessLabel:'Fewer topics'});
toggle.querySelector=s=>s==='[data-toggle-label]'?label:icon;
const scope={
 querySelectorAll(s){return {'[data-publication-paper]':papers,'[data-year-section]':sections,'[data-publication-year-link]':years}[s]||[];},
 querySelector(){return empty;}
};
const panel=node({},true);panel.closest=()=>scope;
panel.querySelectorAll=()=>buttons;
panel.querySelector=s=>({'[data-publication-status]':status,'[data-publication-topic-extra]':extra,'[data-publication-topic-toggle]':toggle}[s]);
const location={href:'https://example.org/publications/journal/'+input.suffix};
if(input.topic!==null){const u=new URL(location.href);u.searchParams.set('topic',input.topic);location.href=u.href;}
const languages=['/publications/journal/','/ja/publications/journal/','/zh/publications/journal/'].map(href=>({href,
 setAttribute(k,v){this[k]=new URL(v,location.href).href;}
}));
const events={},history=[];
const window={location,history:{pushState(s,t,url){history.push(String(url));location.href=String(url);},replaceState(s,t,url){location.href=String(url);}},addEventListener(k,fn){events[k]=fn;}};
const document={querySelectorAll:s=>s==='[data-publication-filter]'?[panel]:languages};
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window,document,URL,Set});
for(const action of input.actions||[]){
 if(action.type==='click')buttons.find(b=>b.dataset.publicationTopic===action.topic).handlers.click();
 if(action.type==='toggle')toggle.handlers.click();
 if(action.type==='pop'){location.href=action.href;events.popstate();}
}
process.stdout.write(JSON.stringify({
 visible:papers.filter(p=>!p.hidden).map(p=>p.doi),
 years:years.filter(y=>!y.hidden).map(y=>y.getAttribute('href')),
 status:status.textContent,href:location.href,languages:languages.map(l=>l.href),history,
 extraHidden:extra.hidden,expanded:panel.dataset.expanded,panelHidden:panel.hidden,emptyHidden:empty.hidden,
 active:buttons.filter(b=>b.attrs['aria-pressed']==='true').map(b=>b.dataset.publicationTopic)
}));
"""
        return json.loads(subprocess.check_output([
            'node', '-e', runner, str(ROOT / 'assets/publication-filter.js'),
            json.dumps({'papers': PAPERS, 'topics': TOPICS, 'topic': topic, 'actions': actions or [], 'suffix': suffix})], text=True))

    def test_default_shows_all_and_preserves_years(self):
        state = self.run_filter()
        self.assertEqual(len(state['visible']), len(PAPERS))
        self.assertEqual(state['active'], ['all'])
        self.assertTrue(state['extraHidden'])
        self.assertEqual(state['expanded'], 'false')
        self.assertFalse(state['panelHidden'])

    def test_direct_topic_link_filters_without_changing_order(self):
        state = self.run_filter('climate-change')
        expected = [p['doi'] for p in PAPERS if 'climate-change' in p['topics']]
        self.assertEqual(state['visible'], expected)
        self.assertEqual(state['years'], ['#year-' + str(year) for year in sorted({p['year'] for p in PAPERS if 'climate-change' in p['topics']}, reverse=True)])
        self.assertIn(str(len(expected)) + ' articles', state['status'])
        self.assertTrue(all('topic=climate-change' in href for href in state['languages']))

    def test_secondary_topic_revealed_and_empty_years_hidden(self):
        state = self.run_filter('healthcare')
        self.assertFalse(state['extraHidden'])
        self.assertEqual(state['expanded'], 'true')
        expected = [p for p in PAPERS if 'healthcare' in p['topics']]
        self.assertEqual(state['years'], ['#year-' + str(year) for year in sorted({p['year'] for p in expected}, reverse=True)])
        self.assertEqual(len(state['visible']), len(expected))
        self.assertIn(str(len(expected)) + ' article', state['status'])

    def test_clear_filter_restores_all_and_preserves_other_query(self):
        state = self.run_filter('healthcare', [{'type': 'click', 'topic': 'all'}], '?from=profile#year-2019')
        self.assertEqual(len(state['visible']), len(PAPERS))
        self.assertNotIn('topic=', state['href'])
        self.assertIn('from=profile', state['href'])
        self.assertEqual(len(state['history']), 1)

    def test_unknown_topic_falls_back_to_all(self):
        state = self.run_filter('not-a-topic')
        self.assertEqual(state['active'], ['all'])
        self.assertNotIn('topic=', state['href'])

    def test_back_navigation_restores_filter(self):
        state = self.run_filter('healthcare', [
            {'type': 'click', 'topic': 'climate-change'},
            {'type': 'pop', 'href': 'https://example.org/publications/journal/?topic=healthcare'},
        ])
        self.assertEqual(state['active'], ['healthcare'])
        self.assertEqual(len(state['visible']), sum('healthcare' in p['topics'] for p in PAPERS))

    def test_more_topics_can_expand_and_collapse(self):
        self.assertFalse(self.run_filter(actions=[{'type': 'toggle'}])['extraHidden'])
        self.assertTrue(self.run_filter(actions=[{'type': 'toggle'}, {'type': 'toggle'}])['extraHidden'])


if __name__ == '__main__':
    unittest.main()
