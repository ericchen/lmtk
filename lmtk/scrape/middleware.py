# -*- coding: utf-8 -*-
"""
lmtk.scrape.middleware
~~~~~~~~~~~~~~~~~~~~~~

Downloader Middleware.

:copyright: Copyright 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import datetime

from pymongo import MongoClient
from scrapy import log
from scrapy.exceptions import IgnoreRequest


class MongoDBDuplicateMiddleware(object):
    """Duplicate filter that checks if the url exists in MongoDB and ignores the request if it was recently scraped.

    This can be used either instead or in conjunction with the regular session dupefilter.
    """

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

    def process_request(self, request, spider):
        lifetime = 0
        for parserule in spider.parserules:
            if parserule.url.search(request.url):
                lifetime = parserule.lifetime
        if lifetime:
            existing = self.collection.find({'scrape.url': request.url})
            if existing.count() > 0:
                age = max([(datetime.datetime.utcnow() - scrape['scrape']['updated']).days for scrape in existing])
                if age <= lifetime:
                    log.msg('Skipping existing (%s days old): %s' % (age, request.url), level=log.INFO, request=request, spider=spider)
                    raise IgnoreRequest
