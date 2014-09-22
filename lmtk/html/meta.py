# -*- coding: utf-8 -*-
"""
lmtk.html.meta
~~~~~~~~~~~~~~

Tools for extracting metadata from HTML.

:copyright: Copyright 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import re

from bs4 import BeautifulSoup

from lmtk.text import u
from lmtk.bib import PersonName


def extract_metadata(html):
    """Parse a HTML page to extract embedded metadata.

    TODO: Is this obsolete due to lmtk.scrape package?

    :param html: The HTML to parse. Either as a string or BeautifulSoup object.
    """
    def resolve_meta(names):
        """Given a list of meta names, return the content of the first that is found."""
        for name in names:
            try:
                return u(html.find('meta', attrs={'name': name, 'content': True})['content'].strip())
            except TypeError:
                continue

    if isinstance(html, basestring):
        html = BeautifulSoup(html, 'lxml')

    meta = {
        u'title': resolve_meta(['citation_title', 'dc.title', 'DC.title', 'title', 'citation_dissertation_name']),
        u'journal': resolve_meta(['citation_journal_title', 'prism.publicationName', 'dc.source', 'DC.source']),
        u'volume': resolve_meta(['citation_volume', 'prism.volume']),
        u'issue': resolve_meta(['citation_issue', 'prism.number', 'citation_technical_report_number']),
        u'page': resolve_meta(['citation_firstpage', 'prism.startingPage']),
        u'abstract': resolve_meta(['description', 'dc.description', 'DC.description']),
        u'publisher': resolve_meta(['citation_publisher', 'dc.publisher', 'DC.publisher']),
        u'conference': resolve_meta(['citation_conference_title', 'citation_conference']),
        u'institution': resolve_meta(['citation_dissertation_institution', 'citation_technical_report_institution']),
        u'doi': resolve_meta(['citation_doi', 'dc.identifier', 'DC.identifier']),
        u'issn': resolve_meta(['citation_issn', 'prism.issn']),
        u'isbn': resolve_meta(['citation_isbn']),
        u'pmid': resolve_meta(['citation_pmid']),
        u'language': resolve_meta(['citation_language', 'dc.language', 'DC.language']),
        u'copyright': resolve_meta(['dc.copyright', 'DC.copyright', 'prism.copyright']),
        u'rights_agent': resolve_meta(['dc.rightsAgent', 'DC.rightsAgent', 'prism.rightsAgent']),
        u'patent_number': resolve_meta(['citation_patent_number']),
        u'patent_country': resolve_meta(['citation_patent_country']),
        u'abstract_url': resolve_meta(['citation_abstract_html_url']),
        u'html_url': resolve_meta(['citation_fulltext_html_url']),
        u'pdf_url': resolve_meta(['citation_pdf_url']),
        u'date': resolve_meta(['citation_publication_date', 'prism.publicationDate', 'citation_date', 'dc.date',
                               'DC.date', 'citation_online_date'])
    }

    # authors
    persons = []
    for metaname in ['citation_author', 'dc.creator', 'DC.creator']:
        for el in html.find_all('meta', attrs={'name': metaname, 'content': True}):
            person = PersonName(el['content'])
            if person and not any(person.could_be(other) for other in persons):
                persons.append(person)
    persons = [dict(p) for p in persons]
    affiliations = [el.get('content', None) for el in html.find_all('meta', attrs={'name': 'citation_author_institution'})]
    if len(affiliations) == len(persons):
        for i, aff in enumerate(affiliations):
            persons[i][u'affiliation'] = [u(aff)]
    meta[u'authors'] = persons

    # keywords
    keywords = set()
    for metaname in ['dc.type', 'prism.section', 'citation_keywords']:
        for el in html.find_all('meta', attrs={'name': metaname, 'content': True}):
            kcomps = [u(k.strip()) for k in el['content'].split(',')]
            keywords.update(kcomps)
    meta[u'keywords'] = list(keywords)

    # last page
    last = html.find('meta', attrs={'name': 'citation_lastpage', 'content': True})
    if last and 'content' in last.attrs and 'page' in meta:
        meta[u'page'] = '%s-%s' % (meta[u'page'], u(last['content']))

    # XML URL
    xml = html.find('link', attrs={'rel': 'alternate',  'href': True,
                                   'type': re.compile(r'^(text/xml|application/rdf\+xml)$')})
    if xml:
        meta[u'xml_url'] = u(xml['href'])

    # PDF URL backup
    pdf = html.find('link', attrs={'rel': 'alternate', 'type': 'application/pdf', 'href': True})
    if not 'pdf_url' in meta and pdf:
        meta[u'pdf_url'] = u(pdf['href'])

    # title backup
    if not 'title' in meta and html.title:
        meta[u'title'] = html.title.string.strip()

    for el in html.find_all(attrs={'rel': 'license', 'href': True}):
        meta[u'license'] = u(el['href'])
    if not 'license' in meta:
        lic = html.find('meta', attrs={'name': re.compile(r'^dc\.rights$', re.I), 'content': True})
        if lic:
            meta[u'license'] = u(lic['content'])
    meta = dict([(k, v) for k, v in meta.items() if v])
    return meta
