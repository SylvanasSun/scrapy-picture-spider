#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import socket
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request
from bs4 import BeautifulSoup
from deviant_art.deviant_art_spider.items import DeviantArtSpiderItem
from scrapy.crawler import Crawler

'''
    This class is spider for url of https://www.deviantart.com 
    which can crawl image and download to your computer from whats-hot area 
'''


class DeviantArtImageSpider(CrawlSpider):
    name = 'deviant_art_image_spider'

    allowed_domains = 'deviantart.com'

    start_urls = ['https://www.deviantart.com/whats-hot/?offset=0']

    rules = (
        Rule(LxmlLinkExtractor(allow='/whats-hot/\?offset=\d+', ), callback='parse_page', follow=True),
    )

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36"
                      " (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Referer": "https://www.deviantart.com/whats-hot/"
    }

    # this constant from settings.py which represent max number for crawl image
    MAXIMUM_IMAGE_NUMBER = Crawler.settings['MAXIMUM_IMAGE_NUMBER']

    # recording number of crawl image
    image_counter = 0

    # recording group id(each 1000 image is same group)
    group_counter = 0

    def parse_page(self, response):
        pass
