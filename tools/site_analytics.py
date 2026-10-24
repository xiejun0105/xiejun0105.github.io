"""Inject the shared analytics loader into full, non-redirect public pages."""

from html.parser import HTMLParser
import re


class PageType(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_head = False
        self.has_body = False
        self.redirect = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.has_head |= tag == 'head'
        self.has_body |= tag == 'body'
        if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh':
            self.redirect = True

    handle_startendtag = handle_starttag


def with_analytics(source):
    # Replace the managed block so repeated builds cannot add duplicate trackers.
    source = re.sub(r'<!-- analytics:start -->.*?<!-- analytics:end -->\s*', '', source, flags=re.S)
    page = PageType()
    page.feed(source)
    if not page.has_head or not page.has_body or page.redirect:
        return source
    snippet = ('<!-- analytics:start -->\n'
               '  <script defer src="/assets/analytics.js"></script>\n'
               '<!-- analytics:end -->\n')
    return re.sub(r'</head\s*>', lambda _: snippet + '</head>', source, count=1, flags=re.I)
