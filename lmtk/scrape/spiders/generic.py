# -*- coding: utf-8 -*-
"""
lmtk.scrape.spiders.generic
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generic spiders to subclass for specific sites or to use directly when less information about the content is known.

:copyright: Copyright 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import re

import six
from scrapy import Spider, Request, Item, log
from scrapy.contrib.loader import Identity, ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose, Compose
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.utils.iterators import xmliter
from scrapy.utils.spider import iterate_spider_output

from lmtk.bib import parse_bibtex
from lmtk.scrape.items import Paper, Figure, Reference, Supplement, Table, Substance, Peak
from lmtk.text import normalize


class LmtkItemLoader(ItemLoader):
    """Root lmtk ItemLoader"""
    #: Use `lmtk.text.normalize` on each input by default.  # TODO: Maybe not?
    default_input_processor = MapCompose(normalize)

    #: Take first match for each field by default.
    default_output_processor = TakeFirst()

    def add_loader_xpaths(self):
        """Allows default xpaths for item fields to be specified in the ItemLoader.

        Subclasses must define a default_item_class to use this method.
        """
        for field in self.default_item_class.fields:
            try:
                for xpath in self.__getattribute__(field):
                    self.add_xpath(field, xpath)
            except AttributeError:
                pass


def _strip_start(number):
    number = re.sub('^(Fig\.?|Scheme|Table)', '', number).strip()
    return number


class FigureLoader(LmtkItemLoader):
    """An ItemLoader for Figures. Can also be used for schemes by passing item=Scheme() as a parameter."""
    default_item_class = Figure
    # Strip "Fig" or "Scheme" prefix from figure numbers
    number_in = MapCompose(_strip_start)


class ReferenceLoader(LmtkItemLoader):
    """An ItemLoader for References."""
    default_item_class = Reference


class SupplementLoader(LmtkItemLoader):
    """An ItemLoader for Supplements."""
    default_item_class = Supplement


class TableLoader(LmtkItemLoader):
    """An ItemLoader for Tables."""
    default_item_class = Table
    # Strip "Table" prefix from table numbers
    number_in = MapCompose(_strip_start)


class SubstanceLoader(LmtkItemLoader):
    """An ItemLoader for Substances."""
    default_item_class = Substance


class PeakLoader(LmtkItemLoader):
    """An ItemLoader for Peaks."""
    default_item_class = Peak


class PaperLoader(LmtkItemLoader):
    """An ItemLoader for Papers.

    This class contains a default set of generic xpath selectors to extract paper metadata.

    This class defines some output processors for scraped paper fields. The default behaviour for Paper fields is to
    take the first successful match defined by a scraper. This allows scrapers to specify multiple different ways to
    scrape a piece of information in case one method fails. However, for fields that can occur multiple times for a
    single paper (author, institution, tag), every successful match by the scraper is retained.

    If necessary, subclass this for specific publishers to override or add processing steps.
    """
    default_item_class = Paper

    # Keep all matches for fields that can have multiple occurrences.  # TODO: Unique? (e.g. for authors, tags)
    tag_out = Identity()
    author_out = Identity()
    supplement_out = Identity()
    figure_out = Identity()
    table_out = Identity()
    reference_out = Identity()
    substance_out = Identity()
    peak_out = Identity()

    # Convert DOI to lowercase
    doi_out = Compose(TakeFirst(), six.text_type.lower)

    # Default XPaths for paper fields.
    doi = ['//meta[@name="citation_doi"]/@content', '//meta[@name="dc.identifier"]/@content', '//meta[@name="DC.identifier"]/@content']
    title = ['//meta[@name="citation_title"]/@content', '//meta[@name="dc.title"]/@content', '//meta[@name="DC.title"]/@content', '//meta[@name="title"]/@content']
    author = ['//meta[@name="citation_author"]/@content', '//meta[@name="dc.creator"]/@content', '//meta[@name="DC.creator"]/@content']
    published_date = ['//meta[@name="citation_publication_date"]/@content', '//meta[@name="prism.publicationDate"]/@content', '//meta[@name="citation_date"]/@content', '//meta[@name="dc.date"]/@content', '//meta[@name="DC.date"]/@content']
    online_date = ['//meta[@name="citation_online_date"]/@content']
    journal = ['//meta[@name="citation_journal_title"]/@content', '//meta[@name="citation_journal_abbrev"]/@content', '//meta[@name="prism.publicationName"]/@content', '//meta[@name="dc.source"]/@content', '//meta[@name="DC.source"]/@content']
    volume = ['//meta[@name="citation_volume"]/@content', '//meta[@name="prism.volume"]/@content']
    issue = ['//meta[@name="citation_issue"]/@content', '//meta[@name="prism.number"]/@content', '//meta[@name="citation_technical_report_number"]/@content']
    firstpage = ['//meta[@name="citation_firstpage"]/@content', '//meta[@name="prism.startingPage"]/@content']
    lastpage = ['//meta[@name="citation_lastpage"]/@content']
    abstract = ['//meta[@name="citation_abstract"]/@content']
    publisher = ['//meta[@name="citation_publisher"]/@content', '//meta[@name="dc.publisher"]/@content', '//meta[@name="DC.publisher"]/@content']
    issn = ['//meta[@name="citation_issn"]/@content', '//meta[@name="prism.issn"]/@content']
    language = ['//meta[@name="citation_language"]/@content', '//meta[@name="dc.language"]/@content', '//meta[@name="DC.language"]/@content']
    copyright = ['//meta[@name="dc.copyright"]/@content', '//meta[@name="DC.copyright"]/@content', '//meta[@name="prism.copyright"]/@content']
    license = ['//a[@rel="license"]/@href']
    html_url = ['//meta[@name="citation_fulltext_html_url"]/@content']
    pdf_url = ['//meta[@name="citation_pdf_url"]/@content']
    abstract_url = ['//meta[@name="citation_abstract_html_url"]/@content']


class ParseRule(object):

    def __init__(self, url, ignore=None, parser=None, subparsers=(), lifetime=0):
        self.url = re.compile(url)
        self.ignore = re.compile(ignore) if ignore else None
        self.parser = parser
        self.subparsers = subparsers
        self.lifetime = lifetime


class GenericSpider(Spider):
    """Generic spider."""

    #: A unique string that defines the name for this spider.
    name = 'generic'

    #: A list of URL pattern strings that this spider is able to crawl.
    crawl = ()

    #: An optional list of URL pattern strings that this spider is not able to crawl. Supersedes `crawl`.
    ignore = ()

    #: ItemLoaders allow common scraping and processing tasks to be shared between parse methods.
    paper_loader = PaperLoader
    figure_loader = FigureLoader
    reference_loader = ReferenceLoader
    supplement_loader = SupplementLoader
    table_loader = TableLoader
    peak_loader = PeakLoader
    substance_loader = SubstanceLoader

    def __init__(self, *a, **kw):
        super(GenericSpider, self).__init__(*a, **kw)
        self._compile_parserules()
        #: A `LinkExtractor` that extracts links allowed by `crawl` and `ignore`.
        self._link_extractor = LinkExtractor(allow=self.crawl, deny=self.ignore)

    def _compile_parserules(self):
        """Setup and validate the parserules that are defined as class attributes."""
        self.parserules = []
        # Add parserules defined as class attributes
        for attr, value in self.__class__.__dict__.iteritems():
            if attr.endswith('_url'):
                name = attr[:-4]
                ignore = getattr(self, '%s_ignore' % name, None)
                parser = getattr(self, '%s_parser' % name, 'parse_%s' % name)
                subparsers = getattr(self, '%s_subparsers' % name, [])
                lifetime = getattr(self, '%s_lifetime' % name, 0)
                self.parserules.append(ParseRule(value, ignore, parser, subparsers, lifetime))
        # Resolve parserule parser methods if necessary
        for rule in self.parserules:
            rule.parser = self._get_method(rule.parser)
            rule.subparsers = [self._get_method(sp) for sp in rule.subparsers]

    def _get_method(self, method):
        """Resolve method name string to actual method."""
        if callable(method):
            return method
        elif isinstance(method, six.string_types):
            return getattr(self, method, None)

    @classmethod
    def handles_request(cls, request):
        """Return True if this spider can handle the given request.

        This is used to choose the correct spider when scraping an arbitrary URL.
        """
        if not any(r.search(request.url) for r in [re.compile(regex) for regex in cls.crawl]):
            return False
        if any(r.search(request.url) for r in [re.compile(regex) for regex in cls.ignore]):
            return False
        return True

    def canonicalize(self, url):
        """Override to perform any additional url canonicalization that is specific to this spider."""
        return url

    def make_requests_from_url(self, url):
        return Request(self.canonicalize(url), dont_filter=True)

    def parse(self, response):
        """Parse page, yielding the items parsed and links to follow."""
        self.log('Parsing: %s' % response.url, level=log.INFO)
        # Extract all links allowed by `crawl` and `ignore`
        for l in self._link_extractor.extract_links(response):
            yield Request(self.canonicalize(l.url))
        # Find and run relevant parser methods
        for parserule in self.parserules:
            if parserule.url.search(response.url):
                results = parserule.parser(response) or ()
                for result in iterate_spider_output(results):
                    # For each item, run any relevant subparsers to add nested information
                    if isinstance(result, Item):
                        for subparser in parserule.subparsers:
                            result = subparser(response, result)
                        # Add the URL we parsed the item from
                        result['scrape'] = {
                            'url': self.canonicalize(response.url),
                            'spider': self.name,
                            'parser': parserule.parser.__name__
                        }
                    result = self.process_result(response, result)
                    yield result

    def process_result(self, response, results):
        """Hook to override to modify or filter a result from any parser.

        This is called for every result (Item or Request) that parsers yield. Use a subparser instead to target a
        specific parser.
        """
        return results

    def parse_html(self, response):
        """Scrape a generic html page for paper metadata."""
        self.log('Generic HTML parser: %s' % response.url)
        l = self.paper_loader(response=response)
        l.add_loader_xpaths()
        paper = l.load_item()
        yield paper
        # TODO: Store HTML fulltext? parsed? raw html?

    def parse_bibtex(self, response):
        """Scrape BibTeX record."""
        self.log('Generic BibTeX parser: %s' % response.url)
        bibtex_records = parse_bibtex(response.body_as_unicode())
        for bt in bibtex_records:
            l = self.paper_loader()
            l.add_value('doi', bt.get('doi', None))
            l.add_value('title', bt.get('title', None))
            l.add_value('journal', bt.get('journal', None))
            l.add_value('publisher', bt.get('publisher', None))
            l.add_value('issue', bt.get('issue', None))
            l.add_value('abstract', bt.get('abstract', None))
            l.add_value('pages', bt.get('pages', None))
            l.add_value('volume', bt.get('issue', None))
            l.add_value('year', bt.get('year', None))
            l.add_value('tag', bt.get('type', None))
            l.add_value('author', [bta['name'] for bta in bt['author']] if 'author' in bt else None)
            paper = l.load_item()
            yield paper

    def parse_rss(self, response):
        """Scrape RSS feed.

        This doesn't attempt to parse any paper information from the RSS feed itself. It simply adds each of the RSS
        item URLs to the queue. Subclass and override if you wish to parse items from the feed itself.
        """
        self.log('Generic RSS parser: %s' % response.url)
        for item in xmliter(response, 'item'):
            item.remove_namespaces()
            for url in item.xpath('./origLink/text()').extract():
                yield Request(self.canonicalize(url))
            for url in item.xpath('./link/text()').extract():
                yield Request(self.canonicalize(url))
