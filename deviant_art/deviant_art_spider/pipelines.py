# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import requests
import threading
import os
from scrapy.exceptions import DropItem, CloseSpider


class DeviantArtSpiderPipeline(object):
    def __init__(self, IMAGE_STORE, MAXIMUM_IMAGE_NUMBER):
        if IMAGE_STORE is None or MAXIMUM_IMAGE_NUMBER is None:
            raise CloseSpider('Pipeline load settings failed')
        self.IMAGE_STORE = IMAGE_STORE
        self.MAXIMUM_IMAGE_NUMBER = MAXIMUM_IMAGE_NUMBER
        # recording number of downloaded image
        self.image_max_counter = 0
        # recording dir name number,it each one thousand add 1
        self.dir_counter = 0

    def process_item(self, item, spider):
        if item is None:
            raise DropItem('Item is null')
        dir_path = self.make_dir()
        image_final_name = item['image_name'] + '-' + item['image_id'] + '-by@' + item['author'] + '.jpg'
        dest_path = os.path.abspath(dir_path).join(image_final_name)
        self.download_image(item['image_src'], dest_path)
        self.image_max_counter += 1
        if self.image_max_counter >= self.MAXIMUM_IMAGE_NUMBER:
            raise CloseSpider('Current downloaded image already equal maximum number')
        return item

    def make_dir(self):
        if self.image_max_counter % 1000 == 0:
            self.dir_counter += 1
        path = os.path.abspath(self.IMAGE_STORE).join('crawl_images').join('dir-' + str(self.dir_counter))
        if not os.path.isdir(path):
            os.mkdir(path)
            print('[CREATED DIR] %s ' % path)
        return path

    def download_image(self, src, dest):
        print('[Thread %s] preparing download image.....' % threading.current_thread().name)
        response = requests.get(src)
        if response.status_code == 200:
            with open(dest, 'wb') as f:
                f.write(response.content)
                print('[DOWNLOAD FINISHED] from %s to %s ' % (src, dest))
        else:
            raise DropItem('[Thread %s] request image src failed status code = %s'
                           % (threading.current_thread().name, response.status_code))

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings['IMAGE_STORE'], settings['MAXIMUM_IMAGE_NUMBER'])
