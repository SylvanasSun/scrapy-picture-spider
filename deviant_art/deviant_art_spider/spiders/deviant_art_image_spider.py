#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket

import requests
from bs4 import BeautifulSoup
# this import package is right,if PyCharm give out warning please ignore
from deviant_art_spider.items import DeviantArtSpiderItem
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from pybloom_live import BloomFilter

# global time out is 10 second
socket.setdefaulttimeout(10)

'''
    This class is spider for url of https://www.deviantart.com 
    which can crawl image and download to your computer from whats-hot area 
'''


class DeviantArtImageSpider(CrawlSpider):
    name = 'deviant_art_image_spider'

    # i don't want scrapy filter url
    allowed_domains = ''

    start_urls = ['https://www.deviantart.com/whats-hot/']

    rules = (
        Rule(LxmlLinkExtractor(
            allow={'https://www.deviantart.com/whats-hot/[\?\w+=\d+]*', }),
            callback='parse_page',
            follow=True
        ),
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36"
                      " (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Referer": "https://www.deviantart.com/"
    }

    filter = BloomFilter(capacity=15000)

    def parse_page(self, response):
        soup = self._init_soup(response, '[PREPARING PARSE PAGE]')
        if soup is None:
            return None
        all_a_tag = soup.find_all('a', class_='torpedo-thumb-link')
        if all_a_tag is not None and len(all_a_tag) > 0:
            for a_tag in all_a_tag:
                detail_link = a_tag['href']
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
        if response.url in self.filter:
            self.logger.debug('[REPETITION] already parse url %s ' % response.url)
            return None
        soup = self._init_soup(response, '[PREPARING DETAIL PAGE]')
        if soup is None:
            return None
        yield self.packing_item(response.meta['item'], soup)
        self.filter.add(response.url)
        # continue search more detail page of current page link
        all_div_tag = soup.find_all('div', class_='tt-crop thumb')
        if all_div_tag is not None and len(all_div_tag) > 0:
            for div_tag in all_div_tag:
                detail_link = div_tag.find('a')['href']
                request = Request(
                    url=detail_link,
                    headers=self.headers,
                    callback=self.parse_detail_page
                )
                request.meta['item'] = DeviantArtSpiderItem()
                yield request
        else:
            self.logger.debug('[PARSE FAILED] get <div> tag failed')
            return None

    def packing_item(self, item, soup):
        self.logger.debug('[PREPARING PACKING ITEM]..........')
        img = soup.find('img', class_='dev-content-full')
        img_alt = img['alt']
        item['image_name'] = img_alt[:img_alt.find('by') - 1]
        item['author'] = img_alt[img_alt.find('by') + 2:]
        item['image_id'] = img['data-embed-id']
        item['image_src'] = img['src']
        self.logger.debug('[PACKING ITEM FINISHED] %s ' % item)
        return item

    def _init_soup(self, response, log):
        url = response.url
        self.headers['Referer'] = url
        self.logger.debug(log + ' ' + url)
        body = requests.get(url, headers=self.headers).content
        soup = BeautifulSoup(body, 'lxml')
        if soup is None:
            self.logger.debug('[PARSE FAILED] read %s body failed' % url)
            return None
        return soup
