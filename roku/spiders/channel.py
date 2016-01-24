# -*- coding: utf-8 -*-
import scrapy
import sys
import os
from urlparse import urlparse
import httplib
from scrapy.http import Request
import mysql.connector
from mysql.connector import errorcode
from roku.items import RokuItem

config = {
	'user': 'root',
	'password': 'password',
	'host': 'localhost',
	'database': 'roku',
	'raise_on_warnings': True,
	'buffered': True,
}

class ChannelSpider(scrapy.Spider):
    name = "channel"
    allowed_domains = ["roku.com"]
    

    # override method
    def make_requests_from_url(self, url):
        item = RokuItem()
        #print str(url[0])
        # assign url
        item['req_url'] = url
        request = Request(url[0], dont_filter=False)

        # set the meta['item'] to use the item in the next call back
        request.meta['item'] = item
        return request

    def __init__(self, limit=0,*args, **kwargs):
        super(ChannelSpider, self).__init__(*args, **kwargs)
        try:
            cnx = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exists")
            else:
                print(err)
        else:
            cursor = cnx.cursor()
            l = []
            if limit > 0:
                query = "SELECT url as linkurl FROM channel_sitemap limit " + limit
            else:
                query = "SELECT url as linkurl FROM channel_sitemap"
            cursor.execute(query)
            for (linkurl) in cursor:
                l.append(linkurl)
            cursor.close()
            cnx.close()
        self.start_urls = l
   

    def start_requests(self):
        for url in self.start_urls:
            item = RokuItem()
            item['req_url'] = url[0]
            #print url[0]
            request = scrapy.Request(url[0], self.parse, meta={ #needed to add [0] as url was returning a tuple
                'splash': {
                    'endpoint': 'render.html',
                    'args': {'wait': 2} #up wait time as channelstore is sloooooooooow
                }
            })
            request.meta['item'] = item
            yield request

    def parse(self, response):
         item = response.meta['item']
         item['name'] = response.xpath('//div[@class="content-copy"]/h3//text()').extract()
         item['developer'] = response.xpath('//div[@class="content-copy"]//em//text()').extract()
         item['logo'] = response.xpath('//div[@class="Roku-Image"]//div//img//@src').extract() 
         l = []
         l.append(item['logo'][0]) # the first image is the logo
         item['file_urls'] = l
         item['desc'] = response.xpath('//div[@class="content-copy"]//p//text()').extract()
         item['rating'] = response.xpath('//span[@class="average-rating"]//text()').extract()
         item['category'] = response.xpath('//p[@class="categories"]//a/text()').extract()
         item['paid'] = response.xpath('//div[@class="container row"]//div//small//text()').extract()
         item['screenshots'] = response.xpath('//a[@class="cs-screenshot-thumb"]/@data-url').extract()
         l=[]
         for i in item['screenshots']:
             strcleaned = 'http://' + i #screenshot url is taken from data-url so we need add http
             string = str(strcleaned.strip('\n').strip('\t').strip())
             l.append(string)
         item['image_urls'] = l
         #print l
         yield item