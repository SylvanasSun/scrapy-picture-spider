# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DeviantArtSpiderItem(scrapy.Item):
    author = scrapy.Field()
    image_name = scrapy.Field()
    image_id = scrapy.Field()
    image_src = scrapy.Field()
    # each one thousand picture belong the same group
    group_id = scrapy.Field()
