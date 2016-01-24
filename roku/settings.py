# -*- coding: utf-8 -*-

# Scrapy settings for roku project

BOT_NAME = 'roku'

SPIDER_MODULES = ['roku.spiders']
NEWSPIDER_MODULE = 'roku.spiders'
SPLASH_URL = 'http://192.168.99.100:8050/'


FILES_STORE = '/Users/guyvandenberg/Documents/Development/roku/images'
IMAGES_STORE = '/Users/guyvandenberg/Documents/Development/roku/images'

USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8'
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_DELAY = 3


DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware' : None,
    'roku.rotate_useragent.RotateUserAgentMiddleware' :200,
    'scrapyjs.SplashMiddleware': 725,
}

ITEM_PIPELINES = {
    'scrapy.pipelines.images.ImagesPipeline': 1,
    'scrapy.pipelines.files.FilesPipeline': 1,
    'roku.pipelines.RokuPipeline': 800,
    'roku.pipelines.MySQLStorePipeline': 900,
}

DUPEFILTER_CLASS = 'scrapyjs.SplashAwareDupeFilter'

LOG_LEVEL = 'ERROR'