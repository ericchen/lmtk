# -*- coding: utf-8 -*-
"""
items.py
~~~~~~~~

Definitions of the items that can be scraped.

:copyright: Copyright 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from scrapy import Field, Item




class Paper(Item):
    scrape = Field()
    # Simple strings
    doi = Field()
    title = Field()
    author = Field()
    abstract = Field()
    volume = Field()
    issue = Field()
    firstpage = Field()
    lastpage = Field()
    pages = Field()
    year = Field()
    journal = Field()
    issn = Field()
    language = Field()
    publisher = Field()
    license = Field()
    copyright = Field()
    advance = Field()
    scopus = Field()
    tag = Field()
    # URLs
    abstract_url = Field()
    html_url = Field()
    xml_url = Field()
    pdf_url = Field()
    # Dates
    received_date = Field()
    accepted_date = Field()
    online_date = Field()
    published_date = Field()
    # Nested items
    supplement = Field()
    figure = Field()
    table = Field()
    scheme = Field()
    reference = Field()
    substance = Field()
    peak = Field()


class Supplement(Item):
    name = Field()
    url = Field()


class Figure(Item):
    number = Field()
    caption = Field()
    url = Field()


class Scheme(Item):
    number = Field()
    caption = Field()
    url = Field()


class Table(Item):
    number = Field()
    caption = Field()
    src = Field()


class Reference(Item):
    number = Field()
    citation = Field()
    doi = Field()


class Substance(Item):
    label = Field()
    name = Field()
    sdf = Field()
    smiles = Field()
    inchi = Field()
    inchikey = Field()
    cas = Field()
    pubchem_cid = Field()
    chemspider_id = Field()
    reaxys_id = Field()


class Peak(Item):
    substance = Field()
    wavelength = Field()
    extinction = Field()
