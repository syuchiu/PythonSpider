# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import six

from dangdang.items import DangdangItem, CommentItem


class DangdangPipeline(object):
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DBNAME'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWD'),
            port=crawler.settings.get('MYSQL_PORT')
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        # if isinstance(item, DangdangItem):
        #     table_name = item.pop('table_name')
        # elif isinstance(item, CommentItem):
        #     table_name = item.pop('table_name')
        #
        data = dict(item)
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (item.table_name, keys, values)
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()
        return item

    def close_spider(self, spider):
        self.db.close()

    # def process_item(self, item, spider):
    #     if isinstance(item, DangdangItem):
    #         table_name = item.pop('table_name')
    #         col_str = ''
    #         row_str = ''
    #         for key in item.keys():
    #             col_str = col_str + " " + key + ","
    #             row_str = "{}'{}',".format(row_str,
    #                                        item[key] if "'" not in item[key] else item[key].replace("'", "\\'"))
    #
    #             sql = "INSERT INTO {} ({}) VALUES ({}) ON DUPLICATE KEY UPDATE ".format(table_name, col_str[1:-1],
    #                                                                                     row_str[:-1])
    #         for (key, value) in six.iteritems(item):
    #             sql += "{} = '{}', ".format(key, value if "'" not in value else value.replace("'", "\\'"))
    #         sql = sql[:-2]
    #         self.cursor.execute(sql)  # 执行SQL
    #         self.cnx.commit()  # 写入操作
    #     elif isinstance(item, CommentItem):
    #         pass
    #     return item
