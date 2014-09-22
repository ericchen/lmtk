# -*- coding: utf-8 -*-

# Scrapy settings


BOT_NAME = 'lmtk'

SPIDER_MODULES = ['lmtk.scrape.spiders']
NEWSPIDER_MODULE = 'lmtk.scrape.spiders'

USER_AGENT = 'lmtk (+http://www.lmtk.org)'
#USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.77.4 (KHTML, like Gecko) Version/7.0.5 Safari/537.77.4'


DOWNLOAD_DELAY = 1
#DEPTH_LIMIT = 0

DOWNLOADER_MIDDLEWARES = {
    'lmtk.scrape.middleware.MongoDBDuplicateMiddleware': 1
}

ITEM_PIPELINES = {
    'lmtk.scrape.pipelines.MongoDBPipeline': 100
}

MONGODB_URI = 'mongodb://localhost:27017'
MONGODB_DATABASE = 'lmtk'
MONGODB_COLLECTION = 'scrape'
