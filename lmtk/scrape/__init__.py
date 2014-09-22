# from twisted.internet import reactor
# from scrapy.crawler import Crawler
# from scrapy import log
# from scrapy.utils.project import get_project_settings
#
# from lmtk.scrape.spiders.rsc import RscSpider
#
#
# def setup_crawler(cls):
#     spider = cls()
#     settings = get_project_settings()
#     crawler = Crawler(settings)
#     crawler.configure()
#     crawler.crawl(spider)
#     crawler.start()
#
# for spider in [RscSpider]:
#     setup_crawler(spider)
#
# log.start()
# reactor.run()
