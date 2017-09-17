#!/usr/bin/env python
# -*- coding:utf-8 -*-
import urllib
import socket
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.extensions.closespider import CloseSpider
from scrapy.http import Request, FormRequest
from pixiv_spider.items import PixivSpiderItem
from bs4 import BeautifulSoup


class PixivSpider(CrawlSpider):
    name = 'pixiv_spider'
    allowed_domains = 'www.pixiv.net'
    start_urls = ['https://www.pixiv.net/']

    rules = (
        # just crawl daily recommend
        Rule(LxmlLinkExtractor(allow=('.+\?mode=daily.*',)), callback='parse_page', follow=True)
    )

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
    }

    # Override function start_requests for realize custom request
    def start_requests(self):
        # cookiejar is param of cookie Middleware
        # it need to keep passing it along on subsequent requests
        return [
            Request(url='https://accounts.pixiv.net/login', meta={'cookiejar': 1}, callback=self.post_login)
        ]

    # username and password from command line input
    def __init__(self, username=None, password=None, *args, **kwargs):
        super(PixivSpider, self).__init__(*args, **kwargs)
        self.username = username
        self.password = password

    def post_login(self, response):
        # check username and password
        if self.username is None or self.password is None:
            raise CloseSpider('username or password is null!')

        print('Preparing login, username = %s password = %s' % (self.username, self.password))
        post_key = response.css('#old-login input[name=post_key]::attr(value)').extract_first()

        # FormRequest for dealing with HTML forms
        # function from_response for simulate a user login
        return FormRequest.from_response(
            response,
            url='https://accounts.pixiv.net/login',
            meta={'cookiejar': response.meta['cookiejar']},
            headers=self.headers,
            formdata={
                'pixiv_id': self.username,
                'password': self.password,
                'post_key': post_key,
                'mode': 'login'
            },
            callable=self.after_login,
            dont_filter=True
        )

    def after_login(self, response):
        # no jump to index represent login failed
        if response.url == 'https://accounts.pixiv.net/login':
            raise CloseSpider('username or password is invalid!')
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parser_page(self, response):
        print('Preparing parse, [url]: %s ' % response.url)
        soup = BeautifulSoup(response.body, 'lxml')
        div_list = soup.find_all(attrs={'class': 'ranking-image-item'})
        items = []
        # set timeout of open url is 5 second
        socket.setdefaulttimeout(5)
        for div in div_list:
            img_detail_url = self.allowed_domains + div.find('a')['href']
            print('Preparing parse image: %s ' % img_detail_url)
            # parsing and packing image detail
            self.packing_item(img_detail_url, items)
        return items

    def packing_item(self, img_detail_url, items):
        try:
            img_detail_page = urllib.request.urlopen(img_detail_url).read()
        except urllib.error.URLError as e:
            print(e)
            img_detail_page = urllib.request.urlopen(img_detail_url).read()
        img_detail_soup = BeautifulSoup(img_detail_page, 'lxml')
        item = PixivSpiderItem()
        # extract url of image src
        img_src = img_detail_soup.find(attrs={'class': 'original-image'})['data-src']
        # extract date of uri
        date_start_index = img_src.find('original') + 13
        img_date = img_src[date_start_index:date_start_index + 10].replace('/', '-')
        # extract image id of uri
        img_id = img_src[img_src.rfind('/') + 1:img_src.rfind('_')]
        # extract image name and author
        img_name = img_detail_soup.find('div', attrs={'class': 'works_display'}).find('img')['alt']
        author = img_detail_soup.find('a', attrs={'class': 'user-name'}).text
        # packing to item
        item['img_src'] = img_src
        item['author'] = author
        item['release_date'] = img_date
        item['img_id'] = img_id
        item['img_name'] = img_name
        items.append(item)
