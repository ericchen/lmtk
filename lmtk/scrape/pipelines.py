# -*- coding: utf-8 -*-
"""
lmtk.scrape.pipelines
~~~~~~~~~~~~~~~~~~~~~

Item processing pipelines for scraped information.

:copyright: Copyright 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import datetime

from pymongo.mongo_client import MongoClient
from scrapy import log, Item


class MongoDBPipeline(object):
    """MongoDB ItemPipeline to save scraped items in a MongoDB collection."""

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize with settings from crawler."""
        settings = crawler.settings
        return cls(settings)

    def __init__(self, settings):
        # Get crawler settings
        self._uri = settings.get('MONGODB_URI', 'mongodb://localhost:27017')
        self._database = settings.get('MONGODB_DATABASE', 'lmtk')
        self._collection = settings.get('MONGODB_COLLECTION', 'scrape')
        # Connect to MongoDB and ensure unique index on url key
        connection = MongoClient(self._uri)
        self.collection = connection[self._database][self._collection]
        log.msg('Connected to MongoDB: {0}/{1}/{2}'.format(self._uri, self._database, self._collection))

    def _to_dict(self, item):
        """Convert Scrapy item to python dictionary. Handles nested items."""
        doc = dict(item)
        for key, value in doc.items():
            if isinstance(value, Item):
                doc[key] = self._to_dict(value)
            if isinstance(value, list):
                for i, el in enumerate(value):
                    if isinstance(el, Item):
                        value[i] = self._to_dict(el)
        return doc

    def process_item(self, item, spider):
        """Add item to MongoDB."""
        doc = self._to_dict(item)
        now = datetime.datetime.utcnow()
        doc['scrape']['created'] = now
        doc['scrape']['updated'] = now
        # Update existing document if paper has already been scraped by this parser. Otherwise add as new.
        existing = self.collection.find_one({
            'doi': doc['doi'],
            'scrape.spider': doc['scrape']['spider'],
            'scrape.parser': doc['scrape']['parser'],
        })
        if existing:
            doc['_id'] = existing['_id']
            doc['scrape']['created'] = existing['scrape']['created']
        self.collection.save(doc)
        log.msg('Saved item to MongoDB', level=log.DEBUG, spider=spider)
        return item
