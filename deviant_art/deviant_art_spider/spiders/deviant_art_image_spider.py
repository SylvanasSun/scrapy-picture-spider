#!/usr/bin/env python
# -*- coding:utf-8 -*-
import threading

import requests
import socket
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request
from bs4 import BeautifulSoup
from deviant_art.deviant_art_spider.items import DeviantArtSpiderItem
from scrapy.crawler import Crawler

# global time out is 10 second
socket.setdefaulttimeout(10)

# this constant from settings.py which represent max number for crawl image
MAXIMUM_IMAGE_NUMBER = Crawler.settings['MAXIMUM_IMAGE_NUMBER']

# recording number of crawl image
image_counter = 0

# recording group id(each 1000 image is same group)
group_counter = 0

lock = threading.Lock()

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
        "Referer": "https://www.deviantart.com/"
    }

    def parse_page(self, response):
        url = response.url
        self.headers['Referer'] = url
        self.logger.debug('[PREPARING PARSE PAGE] %s ' % url)
        body = requests.get(url, headers=self.headers).content
        soup = BeautifulSoup(body, 'lxml')
        if soup is None:
            self.logger.debug('[PARSE FAILED] read %s body failed' % url)
            return None
        all_a_tag = soup.find_all('a', class_='torpedo-thumb-link')
        if all_a_tag is not None and len(all_a_tag) > 0:
            for a_tag in all_a_tag:
                detail_link = a_tag['href']
                self.logger.debug('[PREPARING PARSE DETAIL PAGE] %s ' % detail_link)
                request = Request(
                    url=detail_link,
                    headers=self.headers,
                    callback=self.parse_detail_page
                )
                request.meta['item'] = DeviantArtSpiderItem()
                yield request
        else:
            self.logger.debug('[PARSE FAILED] get <a> tag failed')
            return None

    def parse_detail_page(self, response):
        pass
