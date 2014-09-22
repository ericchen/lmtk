#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
lmtk.scrape.spiders.rsc
~~~~~~~~~~~~~~~~~~~~~~~

Tools for literature from The Royal Society of Chemistry (RSC).

:copyright: Copyright 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import re
import urllib

from scrapy import Request
from scrapy.contrib.loader.processor import MapCompose, Compose, TakeFirst
from scrapy.utils.iterators import xmliter

from lmtk.html import HtmlCleaner
from lmtk.scrape.items import Figure, Scheme
from lmtk.scrape.spiders.generic import GenericSpider, PaperLoader, FigureLoader, ReferenceLoader, TableLoader, SubstanceLoader
from lmtk.text import normalize


def fix_rsc_escapes(t):
    """Replace placeholder text with actual unicode characters.

    Some text on the RSC website has placeholder text in place of unicode characters. This function replaces all
    instances of placeholder text with the actual unicode character.
    """
    for reg, uni in CHAR_REPLACEMENTS:
        t = reg.sub(uni, t)
    return t


def strip_dash(x):
    """Return None if input is '-'. Used to filter when RSC BibTeX has pages set to '-'."""
    return None if x == '-' else x


class RscPaperLoader(PaperLoader):
    """RSC-specific processing stages for various Paper fields."""
    # Convert RSC placeholder text to unicode entities
    title_in = MapCompose(fix_rsc_escapes, normalize)
    abstract_in = MapCompose(HtmlCleaner(), fix_rsc_escapes, normalize)
    # RSC BibTeX can have pages set to '-', filter this out.
    pages_out = Compose(TakeFirst(), strip_dash)


class RscFigureLoader(FigureLoader):
    """RSC-specific processing stages for various Figure/Scheme fields."""
    caption_in = MapCompose(HtmlCleaner(), normalize)


class RscSubstanceLoader(SubstanceLoader):
    """RSC-specific processing stages for various Substance fields."""
    label_in = MapCompose(HtmlCleaner(), normalize)


class RscTableLoader(TableLoader):
    """RSC-specific processing stages for various Table fields."""
    caption_in = MapCompose(HtmlCleaner(), normalize)


class RscReferenceLoader(ReferenceLoader):
    """RSC-specific processing stages for various Reference fields."""
    # Additionally strip the contents of 'a' tags in citation HTML
    citation_in = MapCompose(HtmlCleaner(banned_tags=['script', 'style', 'a']), normalize)


class RscSpider(GenericSpider):
    """Spider for The Royal Society of Chemistry."""
    name = 'rsc'

    # Crawl rules
    crawl = ['http://pubs\.rsc\.org/en/(content|journals)/', 'http://(xlink|feeds)\.rsc\.org/']
    ignore = ['articlepdf', 'makemyfavourite', 'federatedaccess', 'requestpermission', '/en/error/', 'coiresolver']
    start_urls = [
        'http://pubs.rsc.org/en/content/articlehtml/2013/nr/c2nr33840h',
        'http://pubs.rsc.org/en/content/articlehtml/2014/cc/c4cc04457f',
        'http://pubs.rsc.org/en/content/articlehtml/2014/cc/c4cc04421e',
        'http://feeds.rsc.org/rss/cc',
        'http://pubs.rsc.org/en/content/formatedresult?markedids=C4CC04457F&downloadtype=article&managertype=bibtex',
        'http://pubs.rsc.org/en/Content/ArticleLanding/2014/CC/C4CC05342G',
        'http://pubs.rsc.org/en/journals/journalissues/cc#!recentarticles&all'
    ]

    # Parse rules
    bibtex_url = 'http://pubs\.rsc\.org/en/content/formatedresult\?markedids=.+&downloadtype=article&managertype=bibtex'
    rss_url = 'http://feeds\.rsc\.org/rss/'
    abstract_url = 'http://pubs\.rsc\.org/en/[Cc]ontent/[Aa]rticle[Ll]anding/'
    abstract_subparsers = ['parse_abstract_supplement']
    html_url = 'http://pubs\.rsc\.org/en/[Cc]ontent/[Aa]rticle[Hh]tml/'
    html_subparsers = ['parse_html_figure', 'parse_html_reference', 'parse_html_table', 'parse_html_substance']

    # Custom ItemLoaders
    paper_loader = RscPaperLoader
    figure_loader = RscFigureLoader
    reference_loader = RscReferenceLoader
    table_loader = RscTableLoader
    substance_loader = RscSubstanceLoader

    # Lifetimes (prevents pages from being re-crawled within n days)
    bibtex_lifetime = 7
    html_lifetime = 7
    abstract_lifetime = 7

    def canonicalize(self, url):
        """Perform additional RSC-specific URL canonicalization."""
        if re.match('http://pubs\.rsc\.org/en/content/article(landing|html)/', url, re.I):
            url = url.lower()
        return url

    # Parsers
    def parse_abstract(self, response):
        """Scrape abstract page for paper metadata."""
        self.log('RSC parse_abstract: %s' % response.url)
        l = self.paper_loader(response=response)
        l.add_xpath('title', '//h2[@class="alpH1"]/text()')
        l.add_xpath('tag', '//div[@class="peptide_top"]/text()')
        l.add_loader_xpaths()
        paper = l.load_item()
        yield paper
        # Queue the fulltext HTML URL and BibTeX URL for scraping
        yield Request(self.canonicalize(paper['html_url']))
        yield Request(self.canonicalize(BIBTEX_URL.format(paper['doi'].split('/', 1)[1])))

    def parse_abstract_supplement(self, response, result):
        """Add supplementary information to papers scraped from the abstract page."""
        self.log('RSC parse_abstract_supplement: %s' % response.url)
        supplements = []
        for sup in response.xpath('//li[starts-with(@class, "ESIright_highlight_txt_red")]'):
            l = self.supplement_loader(selector=sup)
            l.add_xpath('name', './a/text()')
            l.add_xpath('url', './a/@href')
            supplements.append(l.load_item())
        result['supplement'] = supplements
        return result

    def parse_rss(self, response):
        """Scrape RSS feed for basic paper metadata."""
        self.log('RSC parse_rss: %s' % response.url)
        for item in xmliter(response, 'item'):
            item.remove_namespaces()
            l = self.paper_loader(selector=item)
            l.add_xpath('title', './title/text()')
            l.add_xpath('author', './creator/text()')
            l.add_xpath('abstract_url', './origLink/text()')
            paper = l.load_item()
            # Determine DOI from abstract URL
            m = re.match(r'http://pubs.rsc.org/en/content/articlelanding/\d+/[a-z]+/(.+)', paper['abstract_url'], re.I)
            if m:
                paper['doi'] = '10.1039/%s' % m.group(1).lower()
            yield paper
            yield Request(self.canonicalize(paper['abstract_url']))

    def parse_html(self, response):
        """Scrape fulltext HTML page."""
        self.log('RSC parse_html: %s' % response.url)
        l = self.paper_loader(response=response)
        l.add_xpath('abstract', './/p[@class="abstract"]')
        l.add_loader_xpaths()
        paper = l.load_item()
        yield paper

    def parse_html_figure(self, response, result):
        """Add figures to papers scraped from fulltext HTML page."""
        self.log('RSC parse_html_figure: %s' % response.url)
        figures = []
        schemes = []
        for image_table in response.xpath('//div[@class="image_table"]'):
            id = image_table.xpath('.//td[@class="image_title"]/b/text()').extract()
            if not id:
                continue
            item = Scheme() if id[0].startswith('Scheme') else Figure()
            l = self.figure_loader(item=item, selector=image_table)
            l.add_value('number', id)
            l.add_xpath('url', './/td[@class="imgHolder"]/a/@href')
            l.add_xpath('url', './/td[@class="imgHolder"]//img/@src')
            l.add_xpath('caption', './/span[@class="graphic_title"]')
            l.add_xpath('caption', './/td[@class="imgHolder"]//img/@alt')
            figures.append(l.load_item()) if isinstance(l.item, Figure) else schemes.append(l.load_item())
        result['figure'] = figures
        result['scheme'] = schemes
        return result

    def parse_html_table(self, response, result):
        """Add tables to papers scraped from fulltext HTML page."""
        self.log('RSC parse_html_table: %s' % response.url)
        tables = []
        for table in response.xpath('//div[@class="table_caption"]'):
            l = self.table_loader(selector=table)
            l.add_xpath('number', './b/text()')
            l.add_xpath('caption', './span')
            l.add_xpath('src', './following-sibling::table')
            tables.append(l.load_item())
        result['table'] = tables
        return result

    def parse_html_substance(self, response, result):
        """Add substances to papers scraped from fulltext HTML page."""
        self.log('RSC parse_html_substance: %s' % response.url)
        substances = []
        for substance in response.xpath('//span[@class="TC"]'):
            l = self.substance_loader(selector=substance)
            l.add_xpath('label', './a')
            url = substance.xpath('./a/@href').extract()[0]
            if 'http://www.chemspider.com/Chemical-Structure.' in url:
                l.add_value('chemspider_id', url.lstrip('http://www.chemspider.com/Chemical-Structure.').rstrip('.html'))
            elif 'http://www.chemspider.com/Search.aspx?q=InChI' in url:
                l.add_value('inchi', ''.join(urllib.unquote(url.lstrip('http://www.chemspider.com/Search.aspx?q=')).strip().split()))
            substances.append(l.load_item())
        result['substance'] = substances
        return result

    def parse_html_reference(self, response, result):
        """Add references to papers scraped from fulltext HTML page."""
        self.log('RSC parse_html_reference: %s' % response.url)
        refs = []
        for cit in response.xpath('//span[starts-with(@id, "cit")]'):
            l = self.reference_loader(selector=cit)
            l.add_xpath('number', './@id', re='cit(.*)')
            l.add_xpath('citation', '.')
            l.add_xpath('doi', './a[@class="DOILink"]/@href', re='http://dx.doi.org/(.*)')
            refs.append(l.load_item())
        result['reference'] = refs
        return result


BIBTEX_URL = 'http://pubs.rsc.org/en/content/formatedresult?markedids={}&downloadtype=article&managertype=bibtex'

#: Map placeholder text to unicode characters.
CHAR_REPLACEMENTS = [
    (u'1 with combining macron', u'1\u0304'),
    (u'2 with combining macron', u'2\u0304'),
    (u'3 with combining macron', u'3\u0304'),
    (u'4 with combining macron', u'4\u0304'),
    (u'approximate', u'\u2248'),
    (u'bottom', u'\u22a5'),
    (u'c with combining tilde', u'C\u0303'),
    (u'capital delta', u'\u0394'),
    (u'capital lambda', u'\u039b'),
    (u'capital omega', u'\u03a9'),
    (u'capital phi', u'\u03a6'),
    (u'capital pi', u'\u03a0'),
    (u'capital psi', u'\u03a8'),
    (u'capital sigma', u'\u03a3'),
    (u'caret', u'^'),
    (u'congruent with', u'\u2245'),
    (u'curly or open phi', u'\u03d5'),
    (u'dagger', u'\u2020'),
    (u'dbl greater-than', u'\u226b'),
    (u'dbl vertical bar', u'\u2016'),
    (u'degree', u'\xb0'),
    (u'double bond, length as m-dash', u'='),
    (u'double bond, length half m-dash', u'='),
    (u'double dagger', u'\u2021'),
    (u'double equals', u'\u2267'),
    (u'double less-than', u'\u226a'),
    (u'double prime', u'\u2033'),
    (u'downward arrow', u'\u2193'),
    (u'fraction five-over-two', u'5/2'),
    (u'fraction three-over-two', u'3/2'),
    (u'gamma', u'\u03b3'),
    (u'greater-than-or-equal', u'\u2265'),
    (u'greater, similar', u'\u2273'),
    (u'gt-or-equal', u'\u2265'),
    (u'identical with', u'\u2261'),
    (u'infinity', u'\u221e'),
    (u'intersection', u'\u2229'),
    (u'iota', u'\u03b9'),
    (u'is proportional to', u'\u221d'),
    (u'leftrightarrow', u'\u2194'),
    (u'leftrightarrows', u'\u21c4'),
    (u'less-than-or-equal', u'\u2264'),
    (u'less, similar', u'\u2272'),
    (u'logical and', u'\u2227'),
    (u'middle dot', u'\xb7'),
    (u'not equal', u'\u2260'),
    (u'parallel', u'\u2225'),
    (u'per thousand', u'\u2030'),
    (u'prime or minute', u'\u2032'),
    (u'quadruple bond, length as m-dash', u'\u2263'),
    (u'radical dot', u' \u0307'),
    (u'ratio', u'\u2236'),
    (u'registered sign', u'\xae'),
    (u'reverse similar', u'\u223d'),
    (u'right left arrows', u'\u21C4'),
    (u'right left harpoons', u'\u21cc'),
    (u'rightward arrow', u'\u2192'),
    (u'round bullet, filled', u'\u2022'),
    (u'sigma', u'\u03c3'),
    (u'similar', u'\u223c'),
    (u'small alpha', u'\u03b1'),
    (u'small beta', u'\u03b2'),
    (u'small chi', u'\u03c7'),
    (u'small delta', u'\u03b4'),
    (u'small eta', u'\u03b7'),
    (u'small gamma, Greek, dot above', u'\u03b3\u0307'),
    (u'small kappa', u'\u03ba'),
    (u'small lambda', u'\u03bb'),
    (u'small micro', u'\xb5'),
    (u'small mu ', u'\u03bc'),
    (u'small nu', u'\u03bd'),
    (u'small omega', u'\u03c9'),
    (u'small phi', u'\u03c6'),
    (u'small pi', u'\u03c0'),
    (u'small psi', u'\u03c8'),
    (u'small tau', u'\u03c4'),
    (u'small theta', u'\u03b8'),
    (u'small upsilon', u'\u03c5'),
    (u'small xi', u'\u03be'),
    (u'small zeta', u'\u03b6'),
    (u'space', u' '),
    (u'square', u'\u25a1'),
    (u'subset or is implied by', u'\u2282'),
    (u'summation operator', u'\u2211'),
    (u'times', u'\xd7'),
    (u'trade mark sign', u'\u2122'),
    (u'triple bond, length as m-dash', u'\u2261'),
    (u'triple bond, length half m-dash', u'\u2261'),
    (u'triple prime', u'\u2034'),
    (u'upper bond 1 end', u''),
    (u'upper bond 1 start', u''),
    (u'upward arrow', u'\u2191'),
    (u'varepsilon', u'\u03b5'),
    (u'x with combining tilde', u'X\u0303'),
]
CHAR_REPLACEMENTS = [(re.compile('\[?\[{}\]\]?'.format(re.escape(code)), re.I), uni) for code, uni in CHAR_REPLACEMENTS]


#: Map image URL components to unicode characters.
RSC_IMG_CHARS = {
    '2041': u'^',              # caret
    '224a': u'\u2248',         # almost equal
    'e001': u'=',              # equals
    'e002': u'\u2261',         # equivalent
    'e003': u'\u2263',         # strictly equivalent
    'e006': u'=',              # equals
    'e007': u'\u2261',         # equivalent
    'e009': u'>',              # greater than
    'e00a': u'<',              # less than
    'e00c': u'\u269f',         # three lines converging left
    'e00d': u'\u269e',         # three lines converging right
    'e010': u'\u250c',         # box down and right
    'e011': u'\u2510',         # box down and left
    'e012': u'\u2514',         # box up and right
    'e013': u'\u2518',         # box up and left
    'e038': u'\u2b21',         # white hexagon
    'e059': u'\u25cd',         # ?
    'e05a': u'\u25cd',         # ?
    'e069': u'\u25a9',         # square with diagonal crosshatch fill
    'e077': u'\u2b13',         # square with bottom half black
    'e082': u'\u2b18',         # diamond with top half black
    'e083': u'\u2b19',         # diamond with bottom half black
    'e084': u'\u27d0',         # white diamond with centred do
    'e090': u'\u2504',         # box drawings light triple dash horizontal (not exactly)
    'e091': u'\u2504',         # box drawings light triple dash horizontal
    'e0a2': u'\u03b3\u0307',   # small gamma with dot
    'e0b3': u'\u03bc\u0342',   # small mu with circumflex
    'e0b7': u'\u03c1\u0342',   # small rho with circumflex
    'e0c2': u'\u03b1\u0305',   # small alpha with macron
    'e0c3': u'\u03b2\u0305',   # small beta with macron
    'e0c5': u'\u03b4\u0305',   # small delta with macron
    'e0c6': u'\u03b5\u0305',   # small epsilon with macron
    'e0ce': u'v\u0305',        # small v with macron
    'e0c9': u'\u03b8\u0305',   # small theta with macron
    'e0cb': u'\u03ba\u0305',   # small kappa with macron
    'e0cc': u'\u03bb\u0305',   # small lambda with macron
    'e0cd': u'\u03bc\u0305',   # small mu with macron
    'e0d1': u'\u03c1\u0305',   # small rho with macron
    'e0d4': u'\u03c4\u0305',   # small tau with macron
    'e0d5': u'\u03bd\u0305',   # small nu with macron
    'e0d6': u'\u03d5\u0305',   # small phi with macron (stroked)
    'e0d7': u'\u03c6\u0305',   # small phi with macron
    'e0d8': u'\u03c7\u0305',   # small chi with macron
    'e0da': u'\u03bd\u0305',   # small omega with macron
    'e0db': u'\u03a6\u0303',   # capital phi with tilde
    'e0dd': u'\u03b3\u0303',   # small lambda with tilde
    'e0de': u'\u03b5\u0303',   # small epsilon with tilde
    'e0e0': u'\u03bc\u0303',   # small mu with tilde
    'e0e1': u'v\u0303',        # small v with tilde
    'e0e4': u'\u03c1\u0303',   # small rho with tilde
    'e0e7': u'\u03b5\u20d7',   # small epsilon with rightwards arrow above
    'e0e9': u'\u03bc\u20d7',   # small mu with rightwards arrow above
    'e0eb': u'\u29b5',         # circle with horizontal bar
    'e0ec': u'|',              # ? http://www.rsc.org/images/entities/char_e0ec.gif
    'e0ed': u'|',              # ? http://www.rsc.org/images/entities/char_e0ed.gif
    'e0ee': u'3/2',            # 3/2
    'e0f1': u'\U0001d302',     # ?
    'e0f5': u'\u03bd',         # small nu
    'e0f6': u'\u27ff',         # long rightwards squiggle arrow
    'e100': u'\u2506',         # box drawings light triple dash vertical
    'e103': u'\u2605',         # Black Star
    'e107': u'\u03b5\u0342',   # small epsilon with circumflex
    'e108': u'\u03b7\u0342',   # small eta with circumflex
    'e109': u'\u03ba\u0342',   # small kappa with circumflex
    'e10d': u'\u03c3\u0303',   # small sigma with tilde
    'e110': u'\u03b7\u0303',   # small eta with tilde
    'e112': u'\U0001d4a2',     # script G
    'e113': u'\U0001d219',     # ? greek vocal notation symbol-51
    'e116': u'\u2933',         # wave arrow pointing directly right
    'e117': u'\u2501',         # box drawings heavy horizontal
    'e11a': u'\u03bb\u0342',   # small lambda with circumflex
    'e11b': u'\u03c7\u0303',   # small chi with tilde
    'e11f': u'5/2',            # 5/2
    'e120': u'5/4',            # 5/4
    'e124': u'\u2b22',         # black hexagon
    'e131': u'\u03bd\u0303',   # small nu with tilde
    'e132': u'\u0393\u0342',   # capital gamma with circumflex
    'e13d': u'\u2b1f',         # black pentagon
    'e142': u'\u210b',         # script capital H
    'e144': u'\u2112',         # script capital L
    'e146': u'\u2113',         # script small l
    'e170': u'\U0001d544',     # double-struck capital M
    'e175': u'\u211d',         # double-struck capital R
    'e177': u'\U0001d54b',     # double-struck capital T
    'e17e': u'\U0001D580',     # fraktur bold capital U
    'e18f': u'\U0001d57d',     # fraktur bold capital R
    'e1c0': u'\u2b21',         # white hexagon
    'e520': u'\U0001d49c',     # script capital A
    'e523': u'\U0001d49f',     # script capital D
    'e529': u'\U0001d4a5',     # script capital J
    'e52d': u'\U0001d4a9',     # script capital N
    'e52f': u'\U0001d4ab',     # script capital P
    'e531': u'\u211b',         # script capital R
    'e533': u'\U0001d4af',     # script capital T
}
