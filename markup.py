#!/usr/bin/env python
# encoding: utf-8
"""
Core classes

Created by Rui Carmo on 2006-09-10.
Published under the MIT license.
"""

import logging

log = logging.getLogger()


def sanitize_title(title):
    """Generate a usable anchor from a title string"""

    return re.sub("[\W+]","-",title.lower())


def parse_rfc822(buffer, mime_type='text/plain'):
    """Helper function for parsing metadata out of a plaintext buffer"""

    headers = {}
    markup  = ''
    if mime_type in ['text/plain', 'text/x-textile', 'text/x-markdown']:
        try:
            (header_lines,markup) = buffer.split("\n\n", 1)
            for header in header_lines.strip().split("\n"):
                (name, value) = header.strip().split(":", 1)
                headers[name.lower().strip()] = unicode(value.strip())
            if 'content-type' in headers:
                mime_type = headers['content-type']
        except:
            raise TypeError, "Invalid file format."
    return headers, markup, mime_type


def render_markup(raw, markup=u'text/html'):
    """Turn markup into nice HTML"""

    # Allow module to load regardless of textile or markdown support
    try:
        import textile
        import smartypants
        import markdown
    except ImportError:
        pass

    def _markdown(raw):
        log.debug("Rendering Markdown")
        return markdown.Markdown(extensions=['extra','toc','smarty','codehilite','meta','sane_lists'], safe_mode=False).convert(raw)

    def _plaintext(raw):
        log.debug("Rendering plaintext")
        return u'<pre>\n%s</pre>' % raw

    def _textile(raw):
        log.debug("Rendering Textile")
        return smartypants.smartyPants(textile.textile(unicode(raw), head_offset=0, validate=0, sanitize=1, encoding='utf-8', output='utf-8'))

    def _html(raw):
        return raw

    return {
        u'text/plain'         : _plaintext,
        u'text/x-web-markdown': _markdown,
        u'text/x-markdown'    : _markdown,
        u'text/markdown'      : _markdown,
        u'text/textile'       : _textile,
        u'text/x-textile'     : _textile,
        u'text/html'          : _html}[markup](raw)

