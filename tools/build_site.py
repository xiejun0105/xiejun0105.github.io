"""Refresh shared navigation and home highlights in the static three-language site.

Run: python3 tools/build_site.py
The resulting HTML is committed and served directly by GitHub Pages.
"""
from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
JOURNAL = json.loads((ROOT / "data/journal-publications.json").read_text())
THUMBNAILS = json.loads((ROOT / "data/paper-thumbnails.json").read_text())
PAPERS = JOURNAL[:5]
FUNDING = json.loads((ROOT / "data/funding.json").read_text())
NEWS = json.loads((ROOT / "data/news.json").read_text())
NEWS_HEADING = {"en": "Media & News", "ja": "メディア・ニュース", "zh": "媒体报道"}
LANGUAGES = {
    "en": {"prefix": "", "home": "Home", "papers": "Publications", "projects": "Projects", "teaching": "Teaching", "conference": "Conference", "blog": "Blog", "featured": "Recent publications", "intro": "The latest peer-reviewed work on sustainability, disclosure, and financial materiality.", "all": "All journal articles", "policy": "Policy", "reports": "Policy & international reports", "funding": "Funding & Project", "misc": "Other research outputs", "more": "See more"},
    "ja": {"prefix": "/ja", "home": "ホーム", "papers": "査読付き論文", "projects": "プロジェクト", "teaching": "教育・研究指導", "conference": "講演・発表", "blog": "Blog", "featured": "最近の論文", "intro": "サステナビリティ、情報開示、財務的マテリアリティに関する最新の査読付き論文。", "all": "論文一覧", "policy": "政策", "reports": "政策・国際レポート", "funding": "研究費・プロジェクト", "misc": "その他の研究成果", "more": "詳しく見る"},
    "zh": {"prefix": "/zh", "home": "首页", "papers": "期刊论文", "projects": "项目", "teaching": "教学与指导", "conference": "会议发表", "blog": "Blog", "featured": "近期论文", "intro": "近期发表的可持续性、信息披露与财务重要性相关同行评议研究。", "all": "查看全部期刊论文", "policy": "政策", "reports": "政策与国际报告", "funding": "研究经费与项目", "misc": "其他研究成果", "more": "查看更多"},
}


def nav(locale, current):
    item = LANGUAGES[locale]
    prefix = item["prefix"]
    links = [
        ("home", item["home"], f"{prefix}/#home"),
        ("papers", item["papers"], f"{prefix}/publications/journal/"),
        ("projects", item["projects"], f"{prefix}/funding/"),
        ("teaching", item["teaching"], f"{prefix}/teaching/"),
        ("conference", item["conference"], f"{prefix}/conference/"),
        ("blog", item["blog"], f"{prefix}/blog/"),
    ]
    return '<nav class="main-nav" aria-label="Main navigation">\n      ' + '\n      '.join(
        f'<a class="{"active" if current == key else ""}" href="{url}"{" aria-current=\"page\"" if current == key else ""}>{escape(label)}</a>'
        for key, label, url in links
    ) + '\n    </nav>'


def shared_header(locale, current, suffix=()):
    prefix = LANGUAGES[locale]["prefix"]
    links = []
    for code, label in (("en", "EN"), ("ja", "日本語"), ("zh", "中文")):
        target_prefix = LANGUAGES[code]["prefix"]
        target_path = ROOT / target_prefix.lstrip("/") / Path(*suffix) if suffix else ROOT / target_prefix.lstrip("/")
        target_suffix = suffix if (target_path / "index.html").exists() or (suffix and suffix[0] in ("policy", "funding", "news")) else ("blog",) if suffix and suffix[0] == "blog" else ()
        url = target_prefix + "/" + "/".join(target_suffix).removesuffix("index.html").strip("/")
        if not url.endswith("/"):
            url += "/"
        links.append(f'<a class="{"active" if locale == code else ""}" href="{url}">{label}</a>')
    return (
        '<header class="scroll-home-nav">'
        f'<a class="scroll-home-brand" href="{prefix}/" aria-label="Jun Xie">Jun Xie</a>'
        + nav(locale, current)
        + '<div class="scroll-home-utility"><nav class="lang-nav" aria-label="Language switcher">'
        + ' '.join(links)
        + '</nav><button class="theme-toggle" type="button" data-theme-toggle aria-label="Toggle theme"><span class="moon">☾</span><span class="sun">☼</span></button></div></header>'
    )


def paper_image(paper, css_class):
    thumbnail = THUMBNAILS.get(paper['doi'])
    if not thumbnail:
        return ''
    return f'<span class="{css_class}"><img src="{escape(thumbnail["image"], quote=True)}" alt="Figure from {escape(paper["title"], quote=True)}" loading="lazy" decoding="async"></span>'


def home_sections(locale):
    item = LANGUAGES[locale]
    prefix = item["prefix"]
    cards = []
    for number, paper in enumerate(PAPERS):
        # DOI pages are the authoritative destination; the local bibliography remains one click away.
        cards.append(
            f'<a class="selected-paper-card {"spotlight-lead" if number == 0 else "spotlight-secondary"}" href="https://doi.org/{escape(paper["doi"], quote=True)}">'
            + paper_image(paper, 'selected-paper-image') +
            f'<div class="selected-paper-copy"><span class="selected-paper-meta">{paper["year"]} · {escape(paper["journal"])}</span>'
            f'<h3>{escape(paper["title"])}</h3><span class="selected-paper-action">DOI ↗</span></div></a>'
        )
    return (
        '<!-- featured-publications:start -->\n'
        '<section class="section selected-publications" aria-labelledby="selected-publications-title">\n'
        f'  <div class="section-heading"><h2 class="section-title" id="selected-publications-title">{escape(item["featured"])}</h2>'
        f'<a class="section-more" href="{prefix}/publications/journal/">{escape(item["all"])} <span aria-hidden="true">↗</span></a></div>\n'
        f'  <div class="selected-paper-grid spotlight-layout">{cards[0]}<div class="spotlight-stack">{"".join(cards[1:])}</div></div>\n'
        '</section>\n'
        '<!-- featured-publications:end -->'
    )


def journal_timeline():
    years = sorted({record["year"] for record in JOURNAL}, reverse=True)
    links = '\n'.join(f'<a href="#year-{year}">{year}</a>' for year in years)
    blocks = []
    for year in years:
        entries = []
        for paper in (record for record in JOURNAL if record["year"] == year):
            authors = escape(paper["authors"]).replace('Xie, J.', '<strong>Xie, J.</strong>')
            doi = escape(paper["doi"], quote=True)
            note = f'<div class="pub-doi">{escape(paper["note"])}</div>' if paper.get("note") else ''
            entries.append(
                f'<li class="pub-item publication-with-image">'
                f'<a class="publication-image-link" href="https://doi.org/{doi}" aria-label="Open article: {escape(paper["title"], quote=True)}">{paper_image(paper, "publication-image")}</a>'
                f'<div class="publication-copy"><div><span class="pub-meta">{authors}</span> '
                f'<span class="pub-title">{escape(paper["title"])}</span>. <em>{escape(paper["journal"])}</em>.</div>'
                f'<div class="pub-doi"><a href="https://doi.org/{doi}">https://doi.org/{escape(paper["doi"])}</a></div>{note}</div></li>'
            )
        blocks.append(f'<section class="year-block" id="year-{year}" data-year-section><h2 class="year-heading">{year}</h2><ul class="pub-list">{"".join(entries)}</ul></section>')
    return f'<nav class="timeline-nav" aria-label="Year navigation">{links}</nav><div class="timeline-content">{"".join(blocks)}</div>'


PROJECT_ROLES = {
    "en": {"representative": "Principal investigator", "co_investigator": "Co-investigator", "me": "Jun Xie"},
    "ja": {"representative": "研究代表者", "co_investigator": "研究分担者", "me": "謝 俊"},
    "zh": {"representative": "项目负责人", "co_investigator": "项目分担者", "me": "谢俊"},
}


def project_roles(item, locale):
    labels = PROJECT_ROLES[locale]
    lead = escape(item["representative"][locale])
    rows = [f'<span><small>{escape(labels["representative"])}</small><strong>{lead}</strong></span>']
    if item["my_role"] == "co_investigator":
        rows.append(f'<span><small>{escape(labels["co_investigator"])}</small><strong>{escape(labels["me"])}</strong></span>')
    return '<div class="highlight-roles">' + ''.join(rows) + '</div>'


def funding_cards(locale):
    cards = []
    for item in FUNDING:
        tag = 'a' if item.get('url') else 'div'
        href = f' href="{escape(item["url"], quote=True)}"' if item.get('url') else ''
        if "timeline" in item:
            body = (
                f'<div class="highlight-title">{escape(item["project_title"][locale])}</div>'
                + project_roles(item, locale)
                + f'<div class="highlight-grant">{escape(item.get("title_ja", item["title"]) if locale == "ja" else item["title"])}</div>'
            )
        else:
            description = f'<div class="highlight-meta">{escape(item["description"])}</div>' if item.get('description') else ''
            body = f'<div class="highlight-title">{escape(item["title"])}</div>{description}'
        cards.append(
            f'<{tag} class="highlight-card"{href}>'
            f'<div class="highlight-label">{escape(item["period"])}</div>'
            + body
            + f'</{tag}>'
        )
    return '<div class="highlight-grid">' + ''.join(cards) + '</div>'


def news_item(item, variant):
    image = (
        f'<img src="{escape(item["image"], quote=True)}" alt="" loading="lazy">'
        if item.get("image") else ''
    )
    thumbnail = f'<span class="news-thumb" aria-hidden="true"><span>{escape(item["fallback"])}</span>{image}</span>'
    return (
        f'<div class="news-item news-{variant}">'
        f'<a class="news-bookmark" href="{escape(item["url"], quote=True)}">'
        '<span class="news-bookmark-copy">'
        f'<span class="news-date">{escape(item["date"])}</span>'
        f'<span class="news-title">{escape(item["title"])}</span>'
        f'<span class="news-source">{escape(item["source"])}</span>'
        '</span>' + thumbnail + '</a></div>'
    )


def news_preview_section(locale):
    prefix = LANGUAGES[locale]["prefix"]
    more = escape(LANGUAGES[locale]["more"])
    return (
        '<!-- home-news:start -->\n'
        '<section class="section news-section news-preview">'
        '<div class="section-heading section-heading-small">'
        f'<h2 class="section-title">{escape(NEWS_HEADING[locale])}</h2>'
        f'<a class="section-more" href="{prefix}/news/">{more} <span aria-hidden="true">↗</span></a></div>'
        f'<div class="spotlight-layout news-spotlight">{news_item(NEWS[0], "featured")}'
        f'<div class="spotlight-stack">{"".join(news_item(item, "compact") for item in NEWS[1:5])}</div></div>'
        '</section>\n<!-- home-news:end -->'
    )


def news_page(locale):
    section = (
        '<section class="section news-page">'
        f'<h1 class="section-title">{escape(NEWS_HEADING[locale])}</h1>'
        f'<div class="news-archive">{"".join(news_item(item, "archive-entry") for item in NEWS)}</div>'
        '</section>'
    )
    return (
        f'<!DOCTYPE html>\n<html lang="{locale}" data-theme="light">\n<head>\n'
        f'  <meta charset="UTF-8">\n  <title>{escape(NEWS_HEADING[locale])} | Jun Xie</title>\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '  <link rel="stylesheet" href="/assets/style.css">\n  <script src="/assets/site.js"></script>\n'
        '</head>\n<body>\n<!-- shared-header:start -->\n'
        + shared_header(locale, None, ("news",))
        + '\n<!-- shared-header:end -->\n'
        + '  <div class="container detail-container"><main>' + section + '</main><footer class="footer">© Jun Xie</footer></div>\n'
        + '</body>\n</html>\n'
    )


FUNDING_TEXT = {
    "en": {"intro": "Research grants and projects supporting work on ESG, sustainability, and socio-economic systems.", "timeline": "Project timeline", "timing": "Year-level dates · select a bar for project details", "projects": "Research projects", "earlier": "Earlier funding & awards", "link": "Project page", "chart": "Research project timeline from 2024 to 2031"},
    "ja": {"intro": "ESG、サステナビリティ、社会経済システムに関する研究を支える研究費とプロジェクト。", "timeline": "プロジェクトの期間", "timing": "年単位の表示 · バーを選ぶと詳細へ移動", "projects": "研究プロジェクト", "earlier": "過去の研究支援・受賞", "link": "プロジェクトの詳細", "chart": "2024年から2031年までの研究プロジェクトの期間"},
    "zh": {"intro": "支持 ESG、可持续发展与社会经济系统研究的经费及项目。", "timeline": "项目时间轴", "timing": "按年份显示 · 点击横条查看项目详情", "projects": "研究项目", "earlier": "早期研究资助与奖励", "link": "项目详情", "chart": "2024年至2031年的研究项目时间轴"},
}


def funding_detail_section(locale):
    labels = FUNDING_TEXT[locale]
    projects = [entry for entry in FUNDING if "timeline" in entry]
    earlier = [entry for entry in FUNDING if "timeline" not in entry]
    def month_index(value):
        year, month = map(int, value[:7].split('-'))
        return year * 12 + month - 1

    def fiscal_year(value):
        year, month = map(int, value[:7].split('-'))
        return year if month >= 4 else year - 1

    first_year = min(fiscal_year(entry['timeline']['start']) for entry in projects)
    last_year = max(fiscal_year(entry['timeline']['end']) for entry in projects)
    year_count = last_year - first_year + 1
    months = year_count * 12
    origin = first_year * 12 + 3
    years = ''.join(f'<span>FY {year}</span>' for year in range(first_year, last_year + 1))
    rows = []
    details = []
    for number, entry in enumerate(projects, 1):
        timing = entry["timeline"]
        start = month_index(timing['start']) - origin + 1
        span = month_index(timing['end']) - month_index(timing['start']) + 1
        assert start > 0 and span > 0
        title = escape(entry.get('title_ja', entry['title']) if locale == 'ja' else entry['title'])
        rows.append(
            f'<a class="funding-time-row tone-{number}" href="#project-{number}" aria-label="{title}, {escape(entry["period"])}">'
            f'<span class="funding-time-name">{title}</span>'
            f'<span class="funding-time-track"><span class="funding-time-bar" style="--bar-start:{start};--bar-span:{span}" title="{escape(entry["project_title"][locale], quote=True)} · {escape(timing["start"])} – {escape(timing["end"])}">'
            f'{escape(entry["project_title"][locale])}</span></span></a>'
        )
        details.append(
            f'<article class="funding-detail-row" id="project-{number}">'
            f'<div class="funding-detail-period">{escape(entry["period"])}</div>'
            f'<div><h4><a href="{escape(entry["url"], quote=True)}">{escape(entry["project_title"][locale])}</a></h4>{project_roles(entry, locale)}'
            f'<p class="funding-grant-name">{title}</p>'
            '</div></article>'
        )
    earlier_rows = ''.join(
        f'<div class="funding-earlier-row"><span>{escape(entry["period"])}</span><div><strong>{escape(entry["title"])}</strong>'
        + (f'<p>{escape(entry["description"])}</p>' if entry.get("description") else '')
        + '</div></div>' for entry in earlier
    )
    return (
        '<section class="section funding-page">'
        f'<div class="funding-overview-heading"><h2>{escape(labels["timeline"])}</h2><p>{escape({"en": "Japanese fiscal year · Apr–Mar", "ja": "日本の会計年度 · 4月–翌年3月", "zh": "日本财政年度 · 4月至次年3月"}[locale])}</p></div>'
        f'<div class="funding-timeline-scroll" role="region" tabindex="0" aria-label="{escape(labels["chart"], quote=True)}">'
        f'<div class="funding-timeline-inner" style="--timeline-years:{year_count};--timeline-months:{months}"><div class="funding-time-axis"><span></span>'
        f'<div class="funding-years">{years}</div></div>{"".join(rows)}</div></div>'
        f'<h2 class="funding-list-heading">{escape(labels["projects"])}</h2>'
        f'<div class="funding-detail-list">{"".join(details)}</div>'
        f'<h2 class="funding-list-heading funding-earlier-heading">{escape(labels["earlier"])}</h2>'
        f'<div class="funding-earlier-list">{earlier_rows}</div></section>'
    )


for path in ROOT.rglob("*.html"):
    if ".git" in path.parts:
        continue
    relative = path.relative_to(ROOT)
    locale = relative.parts[0] if relative.parts[0] in ("ja", "zh") else "en"
    suffix = relative.parts[1:] if locale != "en" else relative.parts
    section = suffix[0] if len(suffix) > 1 else "home"
    current = "papers" if section == "publications" else "projects" if section == "funding" else "teaching" if section == "teaching" else "blog" if section == "blog" else "conference" if section == "conference" else "home" if section == "home" else None
    source = path.read_text()
    if '<!-- shared-header:start -->' in source:
        source, count = re.subn(r'<!-- shared-header:start -->.*?<!-- shared-header:end -->', '<!-- shared-header:start -->\n' + shared_header(locale, current, suffix[:-1]) + '\n<!-- shared-header:end -->', source, count=1, flags=re.S)
        assert count == 1, path
    elif '<header class="site-header">' in source:
        source, count = re.subn(r'<div class="container">\s*<header class="site-header">.*?</header>', '<!-- shared-header:start -->\n' + shared_header(locale, current, suffix[:-1]) + '\n<!-- shared-header:end -->\n  <div class="container">', source, count=1, flags=re.S)
        assert count == 1, path
    if relative in (Path("publications/journal/index.html"), Path("ja/publications/journal/index.html"), Path("zh/publications/journal/index.html")):
        source, count = re.subn(r'<nav class="timeline-nav"[^>]*>.*?</nav><div class="timeline-content">.*?</div>(?=</div></main>)', journal_timeline(), source, count=1, flags=re.S)
        assert count == 1, path
    if relative in (Path("home/index.html"), Path("ja/home/index.html"), Path("zh/home/index.html")):
        featured = home_sections(locale)
        if '<!-- featured-publications:start -->' in source:
            source, count = re.subn(r'<!-- featured-publications:start -->.*?<!-- featured-publications:end -->', featured, source, count=1, flags=re.S)
        else:
            source = source.replace('<section class="section" id="policy">', featured + '\n\n<section class="section" id="policy">', 1)
        assert source.count('<!-- featured-publications:start -->') == 1, path
        source = re.sub(r'\s*<section class="hero hero-profile-blog hero-featured-only(?: research-focus)?">.*?</section>', '', source, count=1, flags=re.S)
        source = source.replace('  <script src="/assets/blog-data.js"></script>\n', '', 1)
        funding_pattern = r'<section class="section(?: home-preview)?">\s*(?:<div class="section-heading section-heading-small">\s*)?<h2 class="section-title">' + re.escape(escape(LANGUAGES[locale]["funding"])) + r'</h2>.*?</section>'
        funding_match = re.search(funding_pattern, source, re.S)
        assert funding_match, path
        funding_section = f'<section class="section"><h2 class="section-title">{escape(LANGUAGES[locale]["funding"])}</h2>{funding_cards(locale)}</section>'
        source = source[:funding_match.start()] + funding_section + source[funding_match.end():]
        policy_match = re.search(r'<section class="section home-preview" id="policy">.*?</section>', source, re.S)
        assert policy_match, path
        policy_section = re.sub(r'\s*<p class="section-intro">.*?</p>', '', policy_match.group(0), count=1, flags=re.S)
        source = source[:policy_match.start()] + policy_section + source[policy_match.end():]
        if '<!-- home-news:start -->' in source:
            source, count = re.subn(
                r'<!-- home-news:start -->.*?<!-- home-news:end -->',
                news_preview_section(locale), source, count=1, flags=re.S
            )
        else:
            news_pattern = (
                r'<section class="section news-section">\s*<h2 class="section-title">'
                + re.escape(escape(NEWS_HEADING[locale])) + r'</h2>.*?</section>'
            )
            source, count = re.subn(news_pattern, news_preview_section(locale), source, count=1, flags=re.S)
        assert count == 1, path
        news_match = re.search(r'<!-- home-news:start -->.*?<!-- home-news:end -->', source, re.S)
        assert news_match, path
        news_block = news_match.group(0)
        source = source[:news_match.start()].rstrip() + '\n\n' + source[news_match.end():].lstrip()
        policy_match = re.search(r'<section class="section home-preview" id="policy">.*?</section>', source, re.S)
        assert policy_match, path
        source = source[:policy_match.end()].rstrip() + '\n\n' + news_block + '\n\n' + source[policy_match.end():].lstrip()
    path.write_text(source)


SCROLL_LABELS = {"en": "Scroll to explore", "ja": "スクロールして見る", "zh": "向下滑动，继续浏览"}


def normalized_home_section(section):
    section = re.sub(r'<div class="section-heading section-heading-small">\s*(<h2 class="section-title">.*?</h2>).*?</div>', r'\1', section, count=1, flags=re.S)
    return section.replace('class="section home-preview"', 'class="section"', 1)


POLICY_COVERS = {
    "10.56383/QYTB2222": "/images/iw_report_2024.png",
    "10.22617/WPS240415-2": "/images/ADB_wp_2024.png",
    "10.56383/QKNP4119": "/images/education_UNESCO.png",
}


def policy_results(locale):
    source = (ROOT / "data" / f"misc-{locale}.html").read_text()

    def result_row(match):
        body = match.group(1)
        cover = next((image for doi, image in POLICY_COVERS.items() if doi in body), None)
        image = f'<img class="policy-result-cover" src="{cover}" alt="" loading="lazy">' if cover else ''
        return f'<li class="pub-item policy-result{" has-cover" if cover else ""}"><div class="policy-result-copy">{body}</div>{image}</li>'

    return re.sub(r'<li class="pub-item">(.*?)</li>', result_row, source, flags=re.S)


def detail_page(locale, kind, section):
    item = LANGUAGES[locale]
    title = item["reports"] if kind == "policy" else item["funding"]
    if kind == "policy":
        section = f'<section class="section policy-results" id="policy"><h1 class="section-title">{escape(title)}</h1>{policy_results(locale)}</section>'
    else:
        section = funding_detail_section(locale)
    return (
        f'<!DOCTYPE html>\n<html lang="{locale}" data-theme="light">\n<head>\n'
        f'  <meta charset="UTF-8">\n  <title>{escape(title)} | Jun Xie</title>\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '  <link rel="stylesheet" href="/assets/style.css">\n  <script src="/assets/site.js"></script>\n'
        '</head>\n<body>\n<!-- shared-header:start -->\n'
        + shared_header(locale, "projects" if kind == "funding" else None, (kind,))
        + '\n<!-- shared-header:end -->\n'
        + '  <div class="container detail-container"><main>' + section + '</main><footer class="footer">© Jun Xie</footer></div>\n'
        + '</body>\n</html>\n'
    )


TEACHING_TEXT = {
    "en": ("Teaching", "Courses", "Current and past courses.", "Research Supervision", "Supervised master's and undergraduate theses by year."),
    "ja": ("教育・研究指導", "担当講義", "担当講義の一覧。", "研究指導", "修士論文・卒業論文の研究指導テーマを年別に整理しています。"),
    "zh": ("教学与指导", "授课", "承担的课程。", "论文指导", "按年份整理的硕士与本科论文指导主题。"),
}

def teaching_page(locale):
    prefix = LANGUAGES[locale]["prefix"]
    title, courses, course_intro, supervision, supervision_intro = TEACHING_TEXT[locale]
    course_html = (ROOT / "data" / f"teaching-course-{locale}.html").read_text()
    supervision_html = (ROOT / "data" / f"teaching-supervision-{locale}.html").read_text()
    return (
        f'<!DOCTYPE html>\n<html lang="{locale}" data-theme="light">\n<head>\n'
        f'  <meta charset="UTF-8">\n  <title>{escape(title)} | Jun Xie</title>\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '  <link rel="stylesheet" href="/assets/style.css">\n  <script src="/assets/site.js"></script>\n'
        '</head>\n<body>\n<!-- shared-header:start -->\n'
        + shared_header(locale, "teaching", ("teaching",))
        + '\n<!-- shared-header:end -->\n'
        + '<div class="container detail-container teaching-page"><main>'
        + f'<section class="section teaching-section" id="courses"><h2 class="section-title">{escape(courses)}</h2><p class="section-intro">{escape(course_intro)}</p>{course_html}</section>'
        + f'<section class="section teaching-section" id="supervision"><h2 class="section-title">{escape(supervision)}</h2><p class="section-intro">{escape(supervision_intro)}</p>{supervision_html}</section>'
        + '</main><footer class="footer">© Jun Xie</footer></div>\n</body>\n</html>\n'
    )


for locale in ("en", "ja", "zh"):
    prefix = LANGUAGES[locale]["prefix"]
    news_path = ROOT / prefix.lstrip("/") / "news/index.html"
    news_path.parent.mkdir(parents=True, exist_ok=True)
    news_path.write_text(news_page(locale))
    teaching_path = ROOT / prefix.lstrip("/") / "teaching/index.html"
    teaching_path.write_text(teaching_page(locale))
    for kind, anchor in (("course", "courses"), ("supervision", "supervision")):
        redirect_path = ROOT / prefix.lstrip("/") / "teaching" / kind / "index.html"
        target = f'{prefix}/teaching/#{anchor}'
        redirect_path.write_text(
            '<!DOCTYPE html><html><head><meta charset="UTF-8">'
            f'<meta http-equiv="refresh" content="0; url={target}">'
            f'<link rel="canonical" href="{prefix}/teaching/">'
            f'</head><body><p><a href="{target}">{escape(TEACHING_TEXT[locale][0])}</a></p></body></html>\n'
        )
    landing_path = ROOT / prefix.lstrip("/") / "index.html"
    home_path = ROOT / prefix.lstrip("/") / "home/index.html"
    landing = landing_path.read_text()
    landing = re.sub(r'\s*<nav class="landing-page-nav"[^>]*>.*?</nav>', '', landing, count=1, flags=re.S)
    landing = landing.replace('            <button class="theme-toggle" type="button" data-theme-toggle><span class="moon">☾</span><span class="sun">☼</span></button>\n', '', 1)
    home = home_path.read_text()
    for kind in ("policy", "funding"):
        if kind == "policy":
            section_pattern = r'<section class="section(?: home-preview)?" id="policy">.*?</section>'
        else:
            section_pattern = r'<section class="section(?: home-preview)?">\s*(?:<div class="section-heading section-heading-small">\s*)?<h2 class="section-title">' + re.escape(escape(LANGUAGES[locale]["funding"])) + r'</h2>.*?</section>'
        match = re.search(section_pattern, home, re.S)
        assert match, (home_path, kind)
        full_section = normalized_home_section(match.group(0))
        detail_path = ROOT / prefix.lstrip("/") / kind / "index.html"
        detail_path.parent.mkdir(parents=True, exist_ok=True)
        detail_path.write_text(detail_page(locale, kind, full_section))
        heading = re.search(r'<h2 class="section-title">.*?</h2>', full_section, re.S)
        assert heading
        more = f'<a class="section-more" href="{prefix}/{kind}/">{escape(LANGUAGES[locale]["more"])} <span aria-hidden="true">↗</span></a>'
        preview = full_section.replace(heading.group(0), '<div class="section-heading section-heading-small">' + heading.group(0) + more + '</div>', 1)
        preview = preview.replace('class="section"', 'class="section home-preview"', 1)
        home = home[:match.start()] + preview + home[match.end():]
    home_path.write_text(home)
    misc_redirect = ROOT / prefix.lstrip("/") / "publications/misc/index.html"
    misc_redirect.write_text(
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta http-equiv="refresh" content="0; url=' + prefix + '/policy/">'
        '<link rel="canonical" href="' + prefix + '/policy/"></head><body><p><a href="' + prefix + '/policy/">Policy</a></p></body></html>\n'
    )
    start = home.index('<!-- featured-publications:start -->')
    end = home.index('<footer class="footer">', start)
    home_content = home[start:end].strip()
    languages = [("EN", "/"), ("日本語", "/ja/"), ("中文", "/zh/")]
    language_links = ' '.join(
        f'<a class="{"active" if url == prefix + "/" else ""}" href="{url}#home">{label}</a>'
        for label, url in languages
    )
    scroll_nav = (
        '<header class="scroll-home-nav" id="home">'
        f'<a class="scroll-home-brand" href="{prefix}/" aria-label="Jun Xie">Jun Xie</a>'
        f'{nav(locale, "home")}'
        f'<div class="scroll-home-utility"><nav class="lang-nav" aria-label="Language switcher">{language_links}</nav>'
        '<button class="theme-toggle" type="button" data-theme-toggle aria-label="Toggle theme"><span class="moon">☾</span><span class="sun">☼</span></button></div>'
        '</header>'
    )
    assembled = (
        '<!-- scrolling-home:start -->\n'
        + scroll_nav
        + '<div class="container scroll-home-content"><main>' + home_content + '</main><footer class="footer">© Jun Xie</footer></div>\n'
        + '<!-- scrolling-home:end -->'
    )
    if '<!-- scrolling-home:start -->' in landing:
        landing = re.sub(r'<!-- scrolling-home:start -->.*?<!-- scrolling-home:end -->', assembled, landing, count=1, flags=re.S)
    else:
        landing = landing.replace('</body>', assembled + '\n</body>', 1)
    landing = landing.replace('  <script src="/assets/blog-data.js"></script>\n', '', 1)
    cue = f'<a class="scroll-cue" href="#home">{SCROLL_LABELS[locale]} <span aria-hidden="true">↓</span></a>'
    landing = landing.replace('<footer class="landing-footer">© Jun Xie</footer>', '', 1)
    landing, count = re.subn(
        r'    </main>\s*(?:<a class="scroll-cue".*?</a>\s*)?</div>\s*(?=<!-- scrolling-home:start -->)',
        '    </main>\n\n    ' + cue + '\n  </div>\n',
        landing,
        count=1,
        flags=re.S,
    )
    assert count == 1, landing_path
    landing_path.write_text(landing)
