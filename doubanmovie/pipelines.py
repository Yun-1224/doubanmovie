# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from logging import log

import pymysql
import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

from doubanmovie import settings


class DoubanmoviePipeline(object):
    def __init__(self):
        # 打开文件
        self.file = open('data.json', 'w', encoding='utf-8')

    # 该方法用于处理数据
    def process_item(self, item, spider):
        # 读取item中的数据
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        # 写入文件
        self.file.write(line)
        # 返回item
        return item

    # 该方法在spider被开启时被调用。
    def open_spider(self, spider):
        pass

    # 该方法在spider被关闭时被调用。
    def close_spider(self, spider):
        self.file.close()


class ImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        yield scrapy.Request(item['img_url'])

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]

        if not image_paths:
            raise DropItem("Item contains no images")

        item['img_url'] = image_paths
        return item


class DBPipeline(object):
    def __init__(self):
        # 连接数据库
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=3306,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8',
            use_unicode=True)

        # 通过cursor执行增删查改
        self.cursor = self.connect.cursor();

    def process_item(self, item, spider):
        try:
            self.cursor.execute(
                """insert into doubanmovie(name, info, rating, num ,quote, img_url,id_num)
                value (%s, %s, %s, %s, %s, %s,%s)""",
                (item['name'],
                 item['info'],
                 item['rating'],
                 item['num'],
                 item['quote'],
                 item['img_url'],
                 item['id_num']
                 ))
            # 提交sql语句
            self.connect.commit()
        except Exception as error:
            # 出现错误时打印错误日志
            log(error)
        return item

