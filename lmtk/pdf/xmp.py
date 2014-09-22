#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Parses metadata stored as XMP (Extensible Metadata Platform).

More information is available on the Adobe website:

    http://www.adobe.com/products/xmp/index.html

"""

from collections import defaultdict
try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        import xml.etree.ElementTree as etree

from lmtk.utils import memoized_property

RDF_NS = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
XML_NS = '{http://www.w3.org/XML/1998/namespace}'
NS_MAP = {
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#'    : 'rdf',
    'http://purl.org/dc/elements/1.1/'               : 'dc',
    'http://ns.adobe.com/xap/1.0/'                   : 'xap',
    'http://ns.adobe.com/pdf/1.3/'                   : 'pdf',
    'http://ns.adobe.com/xap/1.0/mm/'                : 'xapmm',
    'http://ns.adobe.com/pdfx/1.3/'                  : 'pdfx',
    'http://prismstandard.org/namespaces/basic/2.0/' : 'prism',
    'http://crossref.org/crossmark/1.0/'             : 'crossmark',
    'http://ns.adobe.com/xap/1.0/rights/'            : 'rights',
    'http://www.w3.org/XML/1998/namespace'           : 'xml'
}


class XmpParser(object):
    """A parser that converts an XMP metadata string into a dictionary.

    The output is evaluated lazily, when requested.

    Usage:

        parser = XmpParser(xmpstring)
        metadata = parser.meta

    Common namespaces are abbreviated in the output using the definitions in xmp.NS_MAP. If an abbreviation for a
    namespace is not defined in NS_MAP, the full URL is used as the key in the output dictionary. It is possible to
    override NS_MAP when initializing the parser:

        parser = XmpParser(xmpstring, ns_map=None)
        metadata = parser.meta

    """
    def __init__(self, xmp, ns_map=NS_MAP):
        self.raw = xmp
        self.ns_map = ns_map

    @memoized_property
    def meta(self):
        """Run parser and return a dictionary of all the parsed metadata. """
        meta = defaultdict(dict)
        for desc in self.rdftree.findall(RDF_NS + 'Description'):
            for el in desc.getchildren():
                ns, tag = self._parse_tag(el)
                value = self._parse_value(el)
                meta[ns][tag] = value
        return dict(meta)

    @memoized_property
    def tree(self):
        return etree.fromstring(self.raw)

    @memoized_property
    def rdftree(self):
        return self.tree.find(RDF_NS + 'RDF')

    def _parse_tag(self, el):
        """Extract the namespace and tag from an element."""
        ns = None
        tag = el.tag
        if tag[0] == "{":
            ns, tag = tag[1:].split('}', 1)
            if self.ns_map and ns in self.ns_map:
                ns = self.ns_map[ns]
        return ns, tag

    def _parse_value(self, el):
        """Extract the metadata value from an element."""
        if el.find(RDF_NS + 'Bag') is not None:
            value = []
            for li in el.findall(RDF_NS + 'Bag/' + RDF_NS + 'li'):
                value.append(li.text)
        elif el.find(RDF_NS + 'Seq') is not None:
            value = []
            for li in el.findall(RDF_NS + 'Seq/' + RDF_NS + 'li'):
                value.append(li.text)
        elif el.find(RDF_NS + 'Alt') is not None:
            value = {}
            for li in el.findall(RDF_NS + 'Alt/' + RDF_NS + 'li'):
                value[li.get(XML_NS + 'lang')] = li.text
        else:
            value = el.text
        return value


def xmpparse(xmp):
    """Shorthand function for parsing an XMP string into a python dictionary.

    If there are any errors during parsing, this function suppresses any exceptions that are raised and just returns an
    empty dictionary.

    """
    try:
        return XmpParser(xmp).meta
    except etree.ParseError:
        return {}
