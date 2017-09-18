# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import urllib


class PixivSpiderPipeline(object):
    def process_item(self, item, spider):
        print('[Preparing Download]: %s ' % item)
        if item is None:
            return item
        img_final_name = item['img_name'] + '-' + item['author'] + '-' + item['img_id'] + '.jpg'
        img_date = item['release_date']
        year = img_date[:img_date.find('-')]
        month_and_day = img_date[img_date.find('-') + 1:]
        img_path = os.path.abspath(year).join(month_and_day).join(img_final_name)
        img_path = self.make_dir(img_path)
        self.download_image(item['img_src'], img_path)
        return item

    def download_image(self, img_src, img_path):
        try:
            urllib.request.urlretrieve(img_src, img_path)
        except urllib.ContentTooShortError as e:
            print(e)
            urllib.request.urlretrieve(img_src, img_path)

    def make_dir(self, img_path, dir_path='.'):
        img_dir = os.path.abspath(dir_path).join('pixiv_image')
        if not os.path.isdir(img_dir):
            os.mkdir(img_dir)
        img_path = os.path.abspath(img_dir).join(img_path)
        if not os.path.isdir(img_path):
            os.mkdir(img_path)
        return img_path
