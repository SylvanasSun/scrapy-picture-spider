# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PixivSpiderItem(scrapy.Item):
    author = scrapy.Field()
    release_date = scrapy.Field()
    img_name = scrapy.Field()
    img_src = scrapy.Field()
