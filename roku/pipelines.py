# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import mysql.connector
from mysql.connector import errorcode
from pprint import pprint

config = {
	'user': 'root',
	'password': 'password',
	'host': 'localhost',
	'database': 'roku',
	'raise_on_warnings': True,
	'buffered': True,
}


class RokuPipeline(object):
    def process_item(self, item, spider):
        if len(item['developer']) == 2:
            strcleaned = ''.join([x for x in item['developer'][1] if ord(x) < 128])
            item['developer'] = str(strcleaned.strip('\n').strip('\t').strip())
            #item['developer'] = item['developer'][1].strip()
        else:
            item['developer'] = ''
        item['desc'] = item['desc'][-1] # Description is last element in <p>
        rating = str(item['rating'][0].strip('\n').strip('\t').strip().replace('average','').strip())
        item['rating'] = rating
        if 'SERVICE MAY REQUIRE ADDITIONAL FEES' in item['paid']:
            item['paid'] = 1
        else:
            item['paid'] = 0
        return item



class MySQLStorePipeline(object):
    def __init__(self, img_path):
        self.img_path = img_path
        try:
            self.cnx = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exists")
            else:
	            print(err)
        else:
            self.cursor = self.cnx.cursor()
            

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        img_path = settings.get("IMAGES_STORE")
        return cls(img_path)

    def cleanup(self):
        self.cnx.commit()
        
    def process_item(self, item, spider):                 
        try:
           vurl = str(item['req_url'])
           vname = str(item['name'][0]).strip()
           vdeveloper = str(item['developer'])
           prep = str(item['files']).strip('[').strip(']').replace("'",'"').strip()
           logo = json.loads(prep)
           vlogo = self.img_path + '/' + logo['path']
           ss_1 = None
           ss_2 = None
           ss_3 = None
           ss_4 = None
           ss_5 = None
           ss_6 = None
           cat_1 = None
           cat_2 = None
           cat_3 = None
           if len(item['category']):
               if len(item['category']) == 1:
                   cat_1 = item['category'][0]
               if len(item['category']) == 2:
                   cat_1 = item['category'][0]
                   cat_2 = item['category'][1]
               if len(item['category']) >= 3:
                   cat_1 = item['category'][0]
                   cat_2 = item['category'][1]
                   cat_3 = item['category'][2]
           if len(item['image_urls']):
               screen_prep = str(item['images']).strip('[').strip(']').replace("'",'"').strip()
               screen_prep = '[' + screen_prep + ']'
               screenshots = json.loads(screen_prep)
               if len(screenshots) == 1:
                   ss_1 = self.img_path + '/' + screenshots[0]['path']
               elif len(screenshots) == 2:
                   ss_1 = self.img_path + '/' + screenshots[0]['path']
                   ss_2 = self.img_path + '/' + screenshots[1]['path']
               elif len(screenshots) == 3:
                   ss_1 = self.img_path + '/' + screenshots[0]['path']
                   ss_2 = self.img_path + '/' + screenshots[1]['path']
                   ss_3 = self.img_path + '/' + screenshots[2]['path']
               elif len(screenshots) == 4:
                   ss_1 = self.img_path + '/' + screenshots[0]['path']
                   ss_2 = self.img_path + '/' + screenshots[1]['path']
                   ss_3 = self.img_path + '/' + screenshots[2]['path']
                   ss_4 = self.img_path + '/' + screenshots[3]['path']
               elif len(screenshots) == 5:
                   ss_1 = self.img_path + '/' + screenshots[0]['path']
                   ss_2 = self.img_path + '/' + screenshots[1]['path']
                   ss_3 = self.img_path + '/' + screenshots[2]['path']
                   ss_4 = self.img_path + '/' + screenshots[3]['path']
                   ss_5 = self.img_path + '/' + screenshots[4]['path']
               elif len(screenshots) > 5:
                   ss_1 = self.img_path + '/' + screenshots[0]['path']
                   ss_2 = self.img_path + '/' + screenshots[1]['path']
                   ss_3 = self.img_path + '/' + screenshots[2]['path']
                   ss_4 = self.img_path + '/' + screenshots[3]['path']
                   ss_5 = self.img_path + '/' + screenshots[4]['path']
                   ss_6 = self.img_path + '/' + screenshots[5]['path']
           strcleaned = ''.join([x for x in item['desc'] if ord(x) < 128])
           vdesc = str(strcleaned.strip('\n').strip('\t').strip())
           vrating = str(item['rating'])
           vpaid = item['paid']
           insert = "INSERT INTO channels (url, name, developer, logo, rating, paid, descrip, screenshot_1,screenshot_2,screenshot_3,screenshot_4,screenshot_5,screenshot_6, cat_1, cat_2, cat_3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
           self.cursor.execute(insert, (vurl,vname,vdeveloper,vlogo,vrating,vpaid,vdesc,ss_1,ss_2,ss_3,ss_4,ss_5,ss_6,cat_1,cat_2,cat_3,))
        except mysql.connector.Error as err:
            print ("MySQL Error -------------------------------------------------------")
            print (err)
            print ("-------------------------------------------------------------------")

        self.cleanup()
        return item