# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import csv
import time

import pandas as pd
import pymongo
from scrapy.conf import settings


class ZhihuPipeline(object):
    def __init__(self):
        host = settings["MONGODB_HOST"]
        port = settings["MONGODB_PORT"]
        dbname = settings["MONGODB_DBNAME"]
        sheetname = settings["MONGODB_SHEETNAME"]

        # 创建MONGODB数据库链接
        client = pymongo.MongoClient(host=host, port=port)
        # 指定数据库
        db = client[dbname]
        # 存放数据的数据库表名
        self.post = db[sheetname]

    def process_item(self, item, spider):
        data = dict(item)
        self.post.insert(data)
        return item


class PipelineToCSV:
    def __init__(self):
        self.flag = 1
        # header_list = ['answer_count', 'follower_count', 'name', 'url_token', 'url', 'headline']
        # # csv文件的位置,无需事先创建
        self.store_file = 'data.csv'
        # # 打开(创建)文件
        # self.file = codecs.open(self.store_file, 'w', 'utf_8_sig')
        # # csv写法
        # self.writer = csv.writer(self.file)
        # self.writer.writerow(header_list)

    def process_item(self, item, spider):
        # 字典中的key值即为csv中列名
        dataframe = pd.DataFrame([dict(item)])
        if self.flag:
            # 将DataFrame存储为csv,index表示是否显示行名，default=True
            dataframe.to_csv(self.store_file, sep=',', mode='a', index=False, encoding="utf_8_sig")
            self.flag = 0
        else:
            dataframe.to_csv(self.store_file, sep=',', mode='a', header=False, index=False, encoding="utf_8_sig")
        # 判断字段值不为空再写入文件
        # if item['image_name']:
        #     self.writer.writerow((item['image_name'].encode('utf8', 'ignore'), item['image_urls']))
        # return item

    def close_spider(self, spider):
        # 关闭爬虫时顺便将文件保存退出
        # self.file.close()
        pass