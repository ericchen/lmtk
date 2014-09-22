# -*- coding: utf-8 -*-
"""
lmtk.html.clean
~~~~~~~~~~~~~~~

Tools for stripping HTML tags and extracting text.

:copyright: Copyright 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import re

from bs4 import BeautifulSoup, Comment

from lmtk.text import normalize, u


BLOCK_ELEMENTS = {
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'pre', 'dd', 'dl', 'div', 'noscript', 'blockquote', 'form',
    'hr', 'table', 'fieldset', 'address', 'article', 'aside', 'audio', 'canvas', 'figcaption', 'figure', 'footer',
    'header', 'hgroup', 'output', 'section', 'body', 'head', 'title', 'tr', 'td', 'th', 'thead', 'tfoot'
}

INLINE_ELEMENTS = {
    'b', 'big', 'i', 'small', 'tt', 'abbr', 'acronym', 'cite', 'code', 'dfn', 'em', 'kbd', 'strong', 'samp', 'var', 'a',
    'bdo', 'br', 'img', 'map', 'object', 'q', 'script', 'span', 'sub', 'sup', 'button', 'input', 'label', 'select',
    'textarea'
}


class HtmlCleaner(object):
    """HTML sanitizer that strips HTML tags.

    By default, each HTML tag is simply replaced with its text contents. The two exceptions are 'script' and 'style'
    tags, which are removed entirely along with their contents by default.

    There are two ways to customize the behaviour of HtmlCleaner. For simple cases, pass custom parameters when
    initializing using the `allowed_tags`, `banned_tags` and `allowed_attrs` parameters.

    For more complex cases, subclass HtmlCleaner and override the `allowed`, `banned` and `transform` methods. `allowed`
    and `banned` should take a tag as their only parameter and return True or False. If `allowed` returns True, the tag
    is retained in the output. If `banned` returns True, the entire tag contents is removed along with the tag.
    `transform` can be used to modify the allowed tags. It takes a tag as its only parameter, and performs some
    operation on it. A common usage is stripping specific attributes from tags.

    :param allowed_tags: Tags to allow in output.
    :param banned_tags: Tags to remove completely from output, including their entire contents.
    :param allowed_attrs: Attributes to allow on the allowed tags.

    """

    def __init__(self, allowed_tags=None, banned_tags={'script', 'style'}, allowed_attrs=None):
        self.allowed_tags = allowed_tags
        self.banned_tags = banned_tags
        self.allowed_attrs = allowed_attrs

    def __call__(self, html):
        return self.clean(html)

    def allowed(self, tag):
        """Return True if tag should be allowed in output."""
        if self.allowed_tags and tag.name in self.allowed_tags:
            return True

    def banned(self, tag):
        """Return True if tag should be removed completely from output, including the entire contents."""
        if self.banned_tags and tag.name in self.banned_tags:
            return True

    def transform(self, tag):
        """This method is applied to each allowed tag."""
        tag.attrs = dict((k, v) for k, v in tag.attrs.items() if self.allowed_attrs and k in self.allowed_attrs)

    def clean(self, html):
        """Clean the given HTML and return it.

        :param html: The HTML to clean. Either as a string or BeautifulSoup object.
        """
        html = BeautifulSoup(normalize(u(html)), 'lxml')
        for comment in html.find_all(text=lambda text: isinstance(text, Comment)):
            comment.extract()
        for tag in html.find_all():
            if self.banned and self.banned(tag):
                tag.decompose()
            elif self.allowed and self.allowed(tag):
                if self.transform:
                    self.transform(tag)
            else:
                # We don't use tag.unwrap() here because we want to ensure newlines around block elements
                parent = tag.parent
                if parent:
                    i = parent.index(tag)
                    tag.extract()
                    if tag.name.lower() in BLOCK_ELEMENTS:
                        parent.insert(i, '\n')
                    for child in reversed(tag.contents[:]):
                        parent.insert(i, child)
                    if tag.name.lower() in BLOCK_ELEMENTS:
                        parent.insert(i, '\n')
        html = re.sub(r'\s*\n\s*', '\n', html.decode_contents(formatter=None))
        html = re.sub(r'[ \t]+', ' ', html).strip()
        return html
