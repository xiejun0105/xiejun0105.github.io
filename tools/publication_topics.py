"""Validate and render the shared research-topic vocabulary for journal filters."""

from collections import Counter
from html import escape
import re


LABELS = {
    'en': {'all': 'All', 'heading': 'Research topics', 'more': 'More topics', 'less': 'Fewer topics',
           'one': '{count} article', 'many': '{count} articles', 'empty': 'No articles in this topic.', 'view': 'View publications on {topic}'},
    'ja': {'all': 'すべて', 'heading': '研究テーマ', 'more': 'その他のテーマ', 'less': '閉じる',
           'one': '{count} 件', 'many': '{count} 件', 'empty': '該当する論文はありません。', 'view': '{topic}の論文を見る'},
    'zh': {'all': '全部', 'heading': '研究主题', 'more': '更多主题', 'less': '收起',
           'one': '{count} 篇论文', 'many': '{count} 篇论文', 'empty': '该主题暂无论文。', 'view': '查看{topic}相关论文'},
}


def validate_topics(papers, topics):
    if not isinstance(topics, list) or not topics or any(not isinstance(t, dict) or not isinstance(t.get('id'), str) for t in topics):
        raise ValueError('Research topics must be a nonempty array of topic objects')
    ids = [topic['id'] for topic in topics]
    if len(ids) != len(set(ids)) or any(not re.fullmatch(r'[a-z]+(?:-[a-z]+)*', value) or value == 'all' for value in ids):
        raise ValueError('Topic IDs must be unique stable slugs, excluding all')
    for topic in topics:
        if not isinstance(topic.get('primary'), bool):
            raise ValueError(f'Missing primary flag: {topic["id"]}')
        labels = topic.get('labels', {})
        if not isinstance(labels, dict) or any(not isinstance(labels.get(code), str) or not labels[code].strip() for code in LABELS):
            raise ValueError(f'Topic needs all three labels: {topic["id"]}')
        if not isinstance(topic.get('landing', False), bool):
            raise ValueError(f'Landing selection must be boolean: {topic["id"]}')
        row = topic.get('landingRow', 1)
        if type(row) is not int or row < 1:
            raise ValueError(f'Landing row must be a positive integer: {topic["id"]}')
        short = topic.get('landingLabels', {})
        if not isinstance(short, dict) or not set(short) <= set(LABELS) or any(not isinstance(label, str) or not label.strip() for label in short.values()):
            raise ValueError(f'Invalid landing label override: {topic["id"]}')
    used = set()
    dois = set()
    for paper in papers:
        if paper['doi'] in dois:
            raise ValueError(f'Duplicate DOI: {paper["doi"]}')
        dois.add(paper['doi'])
        assigned = paper.get('topics', [])
        if not isinstance(assigned, list) or not assigned or any(not isinstance(t, str) for t in assigned) or len(assigned) != len(set(assigned)) or not set(assigned) <= set(ids):
            raise ValueError(f'Missing, duplicate or unknown topics: {paper["doi"]}')
        used.update(assigned)
    if set(ids) - used:
        raise ValueError('Topics without papers: ' + ', '.join(sorted(set(ids) - used)))


def selected_landing_topics(topics):
    return sorted((topic for topic in topics if topic.get('landing')), key=lambda topic: topic.get('landingRow', 1))


def render_landing_topics(topics, locale):
    prefix = '' if locale == 'en' else '/' + locale

    def link(topic):
        label = topic.get('landingLabels', {}).get(locale, topic['labels'][locale])
        hint = escape(LABELS[locale]['view'].format(topic=label), quote=True)
        return (
            f'<a class="identity-topic" data-identity-topic="{topic["id"]}" '
            f'href="{prefix}/publications/journal/?topic={topic["id"]}" title="{hint}" aria-label="{hint}">'
            '<span class="identity-topic-hash" aria-hidden="true">#</span>'
            f'<span>{escape(label)}</span></a>'
        )

    selected = selected_landing_topics(topics)
    rows = ''.join(
        f'<div class="identity-topic-list" data-identity-row="{row}">'
        + ''.join(link(topic) for topic in selected if topic.get('landingRow', 1) == row)
        + '</div>'
        for row in sorted({topic.get('landingRow', 1) for topic in selected})
    )
    return (
        '<!-- landing-topics:start -->\n'
        f'<nav class="identity-topics" aria-label="{escape(LABELS[locale]["heading"], quote=True)}">'
        f'<div class="identity-topic-rows">{rows}</div></nav>\n'
        '<!-- landing-topics:end -->'
    )


def with_landing_topics(source, topics, locale):
    source = re.sub(r'\s*<!-- landing-topics:start -->.*?<!-- landing-topics:end -->\s*', '', source, flags=re.S)
    snippet = render_landing_topics(topics, locale).replace('\n', '\n            ')
    source, count = re.subn(
        r'(<p class="identity-summary">.*?</p>)\s*',
        lambda match: match.group(1) + '\n            ' + snippet + '\n          ',
        source, count=1, flags=re.S,
    )
    if count != 1:
        raise ValueError('Landing page needs one identity-summary paragraph')
    return source


def render_filters(papers, topics, locale):
    labels = LABELS[locale]
    counts = Counter(topic for paper in papers for topic in paper['topics'])

    def button(value, label, count, active=False):
        return (
            f'<button type="button" class="publication-topic{" active" if active else ""}" '
            f'data-publication-topic="{escape(value, quote=True)}" '
            f'data-publication-label="{escape(label, quote=True)}" '
            f'aria-pressed="{"true" if active else "false"}">'
            f'<span>{escape(label)}</span><span class="publication-topic-count" aria-hidden="true">{count}</span></button>'
        )

    primary = button('all', labels['all'], len(papers), True) + ''.join(
        button(t['id'], t['labels'][locale], counts[t['id']]) for t in topics if t['primary'])
    extra = ''.join(button(t['id'], t['labels'][locale], counts[t['id']]) for t in topics if not t['primary'])
    return (
        '<!-- publication-topics:start -->\n'
        '<section class="publication-filter" data-publication-filter hidden '
        f'aria-label="{escape(labels["heading"], quote=True)}">'
        '<div class="publication-filter-controls">'
        f'<div class="publication-topic-list" role="group" aria-label="{escape(labels["heading"], quote=True)}">{primary}'
        f'<span class="publication-topic-extra" id="publication-topic-extra" data-publication-topic-extra hidden>{extra}</span></div>'
        '<button class="publication-topic-toggle" type="button" data-publication-topic-toggle '
        f'data-more-label="{escape(labels["more"], quote=True)}" data-less-label="{escape(labels["less"], quote=True)}" '
        f'aria-controls="publication-topic-extra" aria-expanded="false"><span data-toggle-label>{escape(labels["more"])}</span>'
        '<span data-toggle-icon aria-hidden="true">+</span></button></div>'
        '<p class="publication-filter-status" data-publication-status role="status" aria-live="polite" '
        f'data-count-one="{escape(labels["one"], quote=True)}" data-count-many="{escape(labels["many"], quote=True)}"></p></section>'
        f'<p class="publication-empty" data-publication-empty hidden>{escape(labels["empty"])}</p>\n'
        '<!-- publication-topics:end -->\n'
    )
