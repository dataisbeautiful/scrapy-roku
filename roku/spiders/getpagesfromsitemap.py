# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import SitemapSpider
from scrapy.spiders import Spider
from scrapy.http import Request, XmlResponse
from scrapy.utils.sitemap import Sitemap, sitemap_urls_from_robots
from scrapy.utils.gz import gunzip, is_gzipped
import re
import requests
import mysql.connector
from mysql.connector import errorcode

config = {
	'user': 'root',
	'password': 'password',
	'host': 'localhost',
	'database': 'roku',
	'raise_on_warnings': True,
	'buffered': True,
}

class GetpagesfromsitemapSpider(SitemapSpider):
    name = "crawlsitemap"
    handle_httpstatus_list = [404]

    def parse(self, response):
       print response.url

    def _parse_sitemap(self, response):
        if response.url.endswith('/robots.txt'):
            for url in sitemap_urls_from_robots(response.body):
                yield Request(url, callback=self._parse_sitemap)
        else:
            body = self._get_sitemap_body(response)
            if body is None:
                self.logger.info('Ignoring invalid sitemap: %s', response.url)
                return

            s = Sitemap(body)
            if s.type == 'sitemapindex':
                for loc in iterloc(s, self.sitemap_alternate_links):
                    if any(x.search(loc) for x in self._follow):
                        yield Request(loc, callback=self._parse_sitemap)
            elif s.type == 'urlset':
                cnx = mysql.connector.connect(**config)
                cursor = cnx.cursor()
                truncate = "truncate table channel_sitemap"
                cursor.execute(truncate)
                cnx.commit()
                for loc in iterloc(s):
                    for r, c in self._cbs:
                        if r.search(loc):
                            print loc
                            cursor.execute("insert into channel_sitemap (url) values (%s)", (loc,))
                            cnx.commit()
                            break


    def __init__(self, spider=None, *a, **kw):
        super(GetpagesfromsitemapSpider, self).__init__(*a, **kw)
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
            self.spider = spider
            cursor = cnx.cursor()
            l = []
            url = "https://channelstore.roku.com"
            resp = requests.head(url + "/sitemap.xml")
            if (resp.status_code != 404):
                l.append(resp.url)
            else:
                resp = requests.head(url + "/robots.txt")
                if (resp.status_code == 200):
                    l.append(resp.url)
        self.sitemap_urls = l
        print self.sitemap_urls

def iterloc(it, alt=False):
    for d in it:
        yield d['loc']

        # Also consider alternate URLs (xhtml:link rel="alternate")
        if alt and 'alternate' in d:
            for l in d['alternate']:
                yield l