#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket
import requests
from bs4 import BeautifulSoup
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.extensions.closespider import CloseSpider
from scrapy.http import Request, FormRequest, HtmlResponse

from pixiv.pixiv_spider.items import PixivSpiderItem


class PixivSpider(CrawlSpider):
    name = 'pixiv_daily_spider'
    allowed_domains = 'pixiv.net'
    start_urls = ['https://www.pixiv.net/ranking.php?mode=daily']
    username = None
    password = None

    rules = (
        # just crawl daily recommend
        Rule(LxmlLinkExtractor(
            allow=('.+\?mode=daily', '.+\?mode=daily&date=*\d+',)),
            callback='parse_page',
            follow=True
        ),
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36"
                      " (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Referer": "https://www.pixiv.net/login.php?return_to=0"
    }

    # Override function start_requests for realize custom request
    def start_requests(self):
        socket.setdefaulttimeout(10)
        # cookiejar is param of cookie Middleware
        # it need to keep passing it along on subsequent requests
        return [
            Request(
                url='https://accounts.pixiv.net/login',
                meta={'cookiejar': 1},
                callback=self.post_login
            )
        ]

    def post_login(self, response):
        # username and password from settings.py
        self.set_username_and_password()
        username, password = PixivSpider.username, PixivSpider.password
        # check username and password
        if username is None or password is None:
            raise CloseSpider('username or password is null!')

        self.logger.debug('Preparing login, username = %s password = %s' % (username, password))
        post_key = response.css('#old-login input[name=post_key]::attr(value)').extract_first()
        # FormRequest for dealing with HTML forms
        # function from_response for simulate a user login
        self.headers['Referer'] = response.url
        return FormRequest.from_response(
            response,
            meta={'cookiejar': response.meta['cookiejar']},
            headers=self.headers,
            formdata={
                'pixiv_id': username,
                'password': password,
                'post_key': post_key,
                'mode': 'login'
            },
            callback=self.after_login,
            dont_filter=True
        )

    # username and password from settings.py
    def set_username_and_password(self):
        settings = self.settings
        PixivSpider.username = settings['USERNAME']
        PixivSpider.password = settings['PASSWORD']

    def after_login(self, response):
        # if no jump to index represent login failed
        if response.url == 'https://accounts.pixiv.net/login':
            raise CloseSpider('username or password is invalid!')
        self.headers['Referer'] = response.url
        for url in self.start_urls:
            # yield self.make_requests_from_url(url)
            yield Request(
                url=url,
                meta={'cookiejar': response.meta['cookiejar']},
                headers=self.headers,
                dont_filter=True
            )

    # because spider inherited from CrawlSpider(it can auto tracking)
    # so need override function _requests_to_follow for keep cookie
    def _requests_to_follow(self, response):
        if not isinstance(response, HtmlResponse):
            return
        seen = set()
        self.headers['Referer'] = response.url
        for n, rule in enumerate(self._rules):
            links = [l for l in rule.link_extractor.extract_links(response) if l not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                r = Request(
                    url=link.url,
                    callback=self._response_downloaded,
                    headers=self.headers,
                    dont_filter=True
                )
                # keep cookie
                r.meta.update(
                    rule=n,
                    link_text=link.text,
                    cookiejar=response.meta['cookiejar']
                )
                yield rule.process_request(r)

    def parse_page(self, response):
        self.logger.debug('[Preparing parse]: %s ' % response.url)
        soup = BeautifulSoup(response.body, 'lxml')
        div_list = soup.find_all(class_='ranking-image-item')
        # set timeout of open url is 10 second
        items = []
        self.headers['Referer'] = response.url
        for div in div_list:
            img_detail_url = 'https://www.' + self.allowed_domains + div.find('a')['href']
            self.logger.debug('[Preparing parse image detail]: %s ' % img_detail_url)
            items.append(self.parse_detail(img_detail_url))
        return items

    def parse_detail(self, detail_url):
        body = requests.get(url=detail_url, headers=self.headers).content
        detail_soup = BeautifulSoup(body, 'lxml')
        img_src_tag = detail_soup.find('img', class_='original-image')
        if img_src_tag is None:
            return None
        # extract image src
        img_src = img_src_tag['data-src']
        self.logger.debug('image original src: %s' % img_src)
        # extract image date
        date_start_index = img_src.find('original') + 13
        img_date = img_src[date_start_index:date_start_index + 10].replace('/', '-')
        # extract image id
        img_id = img_src[img_src.rfind('/') + 1:img_src.rfind('_')]
        # extract image name and author
        img_name = detail_soup.find('div', class_='works_display').find('img')['alt']
        author = detail_soup.find('a', class_='user-name').text
        # packing to item
        item = PixivSpiderItem()
        item['img_src'] = img_src
        item['release_date'] = img_date
        item['img_id'] = img_id
        item['img_name'] = img_name
        item['author'] = author
        return item
