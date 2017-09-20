#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

import requests
from bs4 import BeautifulSoup

'''
    This module for crawl ip in the http://www.ip3366.net/free/ and download to computer 
'''


class ProxiesSpider(object):
    def __init__(self, max_page_number=10):
        self.seed = 'http://www.ip3366.net/free/'
        self.max_page_number = max_page_number
        self.crawled_proxies = []
        self.verified_proxies = []
        self.headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/45.0.2454.101 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        self.tocrawl_url = []

    def crawl(self):
        self.tocrawl_url.append(self.seed)
        page_counter = 1
        while self.tocrawl_url:
            # the parsing speed is too fast bring bug
            # beautiful soup parse html fail
            # so need sleep 1 second
            # time.sleep(1)
            if page_counter > self.max_page_number:
                break
            url = self.tocrawl_url.pop()
            body = requests.get(url=url, headers=self.headers, params={'page': page_counter}).content
            soup = BeautifulSoup(body, 'lxml')
            if soup is None:
                print('PARSE PAGE FAILED.......')
                continue
            self.parse_page(soup)
            print('Parse page %s done' % (url + '?page=' + str(page_counter)))
            page_counter += 1
            self.tocrawl_url.append(url)
        self.verify_proxies()
        self.download()

    def parse_page(self, soup):
        table = soup.find('table', class_='table table-bordered table-striped')
        tr_list = table.tbody.find_all('tr')
        for tr in tr_list:
            ip = tr.contents[1].text
            port = tr.contents[3].text
            protocol = tr.contents[7].text.lower()
            url = protocol + '://' + ip + ':' + port
            self.crawled_proxies.append({url: protocol})
            print('Add url %s to crawled_proxies' % url)

    def verify_proxies(self):
        print('Start verify proxies.......')
        while self.crawled_proxies:
            self.verify_proxy(self.crawled_proxies.pop())
        print('Verify proxies done.....')

    def verify_proxy(self, proxy):
        proxies = {}
        for key in proxy:
            proxies[str(proxy[key])] = key
        try:
            if requests.get('https://www.baidu.com/', proxies=proxies, timeout=2).status_code == 200:
                print('verify proxy success %s ' % proxies)
                self.verified_proxies.append(proxy)
        except:
            print('verify proxy fail %s ' % proxies)

    def download(self):
        current_path = os.getcwd()
        parent_path = os.path.dirname(current_path)
        with open(parent_path + '\proxies.txt', 'w') as f:
            for proxy in self.verified_proxies:
                for key in proxy.keys():
                    f.write(key + '\n')


if __name__ == '__main__':
    spider = ProxiesSpider()
    spider.crawl()
