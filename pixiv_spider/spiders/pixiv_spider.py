#!/usr/bin/env python
# -*- coding:utf-8 -*-
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request, FormRequest
from pixiv_spider.items import PixivSpiderItem


class PixivSpider(CrawlSpider):
    name = 'pixiv_spider'
    allowed_domains = 'www.pixiv.net'
    start_urls = ['https://www.pixiv.net/']

    rules = (
        Rule(LxmlLinkExtractor(allow=('/ranking.php?mode=daily/\w*+',)), callback='', follow=True)
    )

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Referer": "https://www.pixiv.net/"
    }

    # Override function start_requests for realize custom request
    def start_requests(self):
        return [
            Request(url='https://accounts.pixiv.net/login', meta={'cookiejar': 1}, callback=self.post_login)
        ]

    def __init__(self, username, password, *args, **kwargs):
        super(PixivSpider, self).__init__(*args, **kwargs)
        self.username = username
        self.password = password

