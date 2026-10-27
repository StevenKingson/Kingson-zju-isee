"""Open external web links in a new tab, including raw HTML and no-script content."""
from html import escape
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit


class ExternalLinks(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=False)
        self.base = base
        self.origin = urlsplit(base)
        self.output = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        target = urlsplit(urljoin(self.base, values.get('href') or ''))
        if tag == 'a' and target.scheme in ('http', 'https') and (
            target.scheme, target.netloc.lower()
        ) != (self.origin.scheme, self.origin.netloc.lower()):
            rel = list(dict.fromkeys((values.get('rel') or '').split() + ['noopener', 'noreferrer']))
            attrs = [(k, v) for k, v in attrs if k not in ('target', 'rel')]
            attrs += [('target', '_blank'), ('rel', ' '.join(rel))]
            rendered = ''.join(' ' + k + ('' if v is None else '="' + escape(v, quote=True) + '"') for k, v in attrs)
            self.output.append('<a' + rendered + '>')
        else:
            self.output.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        self.output.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        self.output.append(f'</{tag}>')

    def handle_data(self, data):
        self.output.append(data)

    def handle_entityref(self, name):
        self.output.append('&' + name + ';')

    def handle_charref(self, name):
        self.output.append('&#' + name + ';')

    def handle_comment(self, data):
        self.output.append('<!--' + data + '-->')

    def handle_decl(self, decl):
        self.output.append('<!' + decl + '>')


def on_post_page(output, page, config, **kwargs):
    parser = ExternalLinks(config['site_url'])
    parser.feed(output)
    parser.close()
    return ''.join(parser.output)
