# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RokuItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    req_url = scrapy.Field()
    developer = scrapy.Field()
    logo = scrapy.Field()
    desc = scrapy.Field()
    rating = scrapy.Field()
    category = scrapy.Field()
    paid = scrapy.Field()
    screenshots = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()
    #pass
